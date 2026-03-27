#!/usr/bin/env python3
"""
ensure_nsg_winrm_rule.py
========================
Version: 3.0.0 (2026-03-26)

Ensures a WinRM inbound NSG rule (port 5985) exists for all VMs in a manifest.

Strategy (in order):
  1. Check NIC-level NSG — use it if present.
  2. Check subnet-level NSG — use it if present.
  3. No NSG found anywhere — create a new NSG, attach it to the NIC, add rule.

Environment variables read:
  MANIFEST    Manifest directory name under ansible/vars/
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import yaml
except ImportError:
    print("[ERROR] PyYAML is required. Install: pip install PyYAML")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

NSG_RULE_NAME = "allow-winrm"
WINRM_PORT = "5985"
WINRM_SOURCE_PREFIX = "10.0.0.0/8"


def _az(*args: str, subscription_id: Optional[str] = None) -> subprocess.CompletedProcess[str]:
    cmd: List[str] = ["az", *args]
    if subscription_id:
        cmd.extend(["--subscription", subscription_id])
    return subprocess.run(cmd, capture_output=True, text=True, check=False, env=os.environ.copy())


def _load_manifest(manifest_name: str) -> Dict[str, Any]:
    path = Path("ansible/vars") / manifest_name / "manifest.yml"
    if not path.exists():
        log.error("[ERROR] Manifest not found: %s", path)
        sys.exit(1)
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def _set_subscription(subscription_id: str) -> None:
    log.info("[INFO] Setting Azure subscription context: %s", subscription_id)
    result = _az("account", "set", "--subscription", subscription_id)
    if result.returncode != 0:
        log.error("[ERROR] Failed to set subscription: %s", result.stderr.strip())
        sys.exit(1)


def _get_nic_details(
    resource_group: str,
    vm_name: str,
    subscription_id: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Return NIC id, NIC-level NSG id, and subnet id for the first NIC of a VM."""
    result = _az(
        "vm", "nic", "list",
        "--resource-group", resource_group,
        "--vm-name", vm_name,
        "--query", "[0].id",
        "-o", "tsv",
        subscription_id=subscription_id,
    )
    if result.returncode != 0 or not result.stdout.strip():
        log.warning("[WARN] Could not get NIC for VM %s (rc=%s): %s",
                    vm_name, result.returncode, result.stderr.strip())
        return None

    nic_id = result.stdout.strip()
    nic_name = nic_id.split("/")[-1]
    log.info("[INFO] Found NIC: %s", nic_name)

    result = _az(
        "network", "nic", "show",
        "--ids", nic_id,
        "--query", "{nsg: networkSecurityGroup.id, subnet: ipConfigurations[0].subnet.id}",
        "-o", "json",
        subscription_id=subscription_id,
    )
    if result.returncode != 0:
        log.warning("[WARN] Could not show NIC details for %s: %s",
                    nic_name, result.stderr.strip())
        return None

    try:
        details = json.loads(result.stdout)
    except (json.JSONDecodeError, ValueError):
        log.warning("[WARN] Could not parse NIC details for %s", nic_name)
        return None

    return {
        "nic_id": nic_id,
        "nic_name": nic_name,
        "nsg_id": (details.get("nsg") or "").strip() or None,
        "subnet_id": (details.get("subnet") or "").strip() or None,
    }


def _get_subnet_nsg_id(
    subnet_id: str,
    subscription_id: Optional[str] = None,
) -> Optional[str]:
    """Return the NSG ID attached to a subnet, or None."""
    result = _az(
        "network", "vnet", "subnet", "show",
        "--ids", subnet_id,
        "--query", "networkSecurityGroup.id",
        "-o", "tsv",
        subscription_id=subscription_id,
    )
    if result.returncode != 0 or not result.stdout.strip():
        return None
    return result.stdout.strip()


def _parse_nsg_id(nsg_id: str) -> Tuple[str, str]:
    """Extract (nsg_name, nsg_resource_group) from a full NSG resource ID."""
    parts = nsg_id.split("/")
    return parts[-1], parts[4]


def _get_vm_location(
    resource_group: str,
    vm_name: str,
    subscription_id: Optional[str] = None,
) -> str:
    result = _az(
        "vm", "show",
        "--resource-group", resource_group,
        "--name", vm_name,
        "--query", "location",
        "-o", "tsv",
        subscription_id=subscription_id,
    )
    if result.returncode != 0 or not result.stdout.strip():
        log.warning("[WARN] Could not get location for %s — defaulting to eastus", vm_name)
        return "eastus"
    return result.stdout.strip()


def _create_and_attach_nsg(
    vm_name: str,
    nic_id: str,
    resource_group: str,
    location: str,
    subscription_id: Optional[str] = None,
) -> Optional[Tuple[str, str]]:
    """Create a new NSG and attach it to the NIC. Returns (nsg_name, nsg_rg)."""
    nsg_name = f"nsg-{vm_name}-winrm"
    log.info("[INFO] Creating new NSG: %s in RG: %s location: %s", nsg_name, resource_group, location)

    create = _az(
        "network", "nsg", "create",
        "--resource-group", resource_group,
        "--name", nsg_name,
        "--location", location,
        subscription_id=subscription_id,
    )
    if create.returncode != 0:
        log.error("[ERROR] Failed to create NSG %s: %s", nsg_name, create.stderr.strip())
        return None

    log.info("[INFO] Attaching NSG %s to NIC %s", nsg_name, nic_id.split("/")[-1])
    attach = _az(
        "network", "nic", "update",
        "--ids", nic_id,
        "--network-security-group", nsg_name,
        subscription_id=subscription_id,
    )
    if attach.returncode != 0:
        log.error("[ERROR] Failed to attach NSG to NIC: %s", attach.stderr.strip())
        return None

    log.info("[OK] NSG %s created and attached", nsg_name)
    return nsg_name, resource_group


def _ensure_winrm_rule(
    nsg_name: str,
    nsg_rg: str,
    vm_name: str,
    subscription_id: Optional[str] = None,
) -> None:
    """Create the WinRM allow rule on the NSG if it does not already exist."""
    check = _az(
        "network", "nsg", "rule", "show",
        "--resource-group", nsg_rg,
        "--nsg-name", nsg_name,
        "--name", NSG_RULE_NAME,
        subscription_id=subscription_id,
    )
    if check.returncode == 0:
        log.info("[OK] WinRM rule already exists on NSG %s for VM %s", nsg_name, vm_name)
        return

    log.info("[INFO] Creating WinRM rule on NSG %s for VM %s", nsg_name, vm_name)
    create = _az(
        "network", "nsg", "rule", "create",
        "--resource-group", nsg_rg,
        "--nsg-name", nsg_name,
        "--name", NSG_RULE_NAME,
        "--priority", "1001",
        "--direction", "Inbound",
        "--access", "Allow",
        "--protocol", "Tcp",
        "--destination-port-ranges", WINRM_PORT,
        "--source-address-prefixes", WINRM_SOURCE_PREFIX,
        "--description", "Allow WinRM HTTP from internal network for GitHub Actions runner",
        subscription_id=subscription_id,
    )
    if create.returncode == 0:
        log.info("[OK] WinRM rule created on NSG %s for VM %s", nsg_name, vm_name)
    else:
        log.error("[ERROR] Failed to create WinRM rule for %s: %s",
                  vm_name, create.stderr.strip())
        sys.exit(1)


def main() -> None:
    manifest_name = os.environ.get("MANIFEST", "").strip()
    if not manifest_name:
        log.error("[ERROR] MANIFEST environment variable is not set")
        sys.exit(1)

    manifest = _load_manifest(manifest_name)

    target_rg: str = manifest.get("target_resource_group", "")
    if not target_rg:
        log.error("[ERROR] target_resource_group not found in manifest")
        sys.exit(1)

    subscription_id: str = manifest.get("target_subscription_id", "")
    if subscription_id:
        _set_subscription(subscription_id)

    vms: List[Dict[str, Any]] = manifest.get("vms") or []
    for vm in vms:
        azure_vm_name: str = vm.get("target_vm_name", "") or vm.get("name", "")
        if not azure_vm_name:
            log.warning("[WARN] VM entry missing target_vm_name and name — skipping")
            continue

        vm_rg: str = vm.get("target_resource_group", "") or target_rg
        log.info("[INFO] Processing VM: %s (RG: %s)", azure_vm_name, vm_rg)

        # Step 1 — resolve NIC
        nic = _get_nic_details(vm_rg, azure_vm_name, subscription_id)
        if not nic:
            log.warning("[WARN] Skipping VM %s — could not resolve NIC", azure_vm_name)
            continue

        nsg_name: Optional[str] = None
        nsg_rg: Optional[str] = None

        # Step 2 — NIC-level NSG
        if nic["nsg_id"]:
            nsg_name, nsg_rg = _parse_nsg_id(nic["nsg_id"])
            log.info("[INFO] Using NIC-level NSG: %s (RG: %s)", nsg_name, nsg_rg)

        # Step 3 — subnet-level NSG
        elif nic["subnet_id"]:
            log.info("[INFO] No NIC-level NSG — checking subnet")
            subnet_nsg_id = _get_subnet_nsg_id(nic["subnet_id"], subscription_id)
            if subnet_nsg_id:
                nsg_name, nsg_rg = _parse_nsg_id(subnet_nsg_id)
                log.info("[INFO] Using subnet-level NSG: %s (RG: %s)", nsg_name, nsg_rg)

        # Step 4 — no NSG anywhere, create and attach
        if not nsg_name:
            log.info("[INFO] No NSG found — creating and attaching new NSG to NIC")
            location = _get_vm_location(vm_rg, azure_vm_name, subscription_id)
            result = _create_and_attach_nsg(
                azure_vm_name, nic["nic_id"], vm_rg, location, subscription_id
            )
            if not result:
                log.warning("[WARN] Could not create NSG for VM %s — skipping", azure_vm_name)
                continue
            nsg_name, nsg_rg = result

        # Step 5 — ensure WinRM rule exists
        _ensure_winrm_rule(nsg_name, nsg_rg, azure_vm_name, subscription_id)


if __name__ == "__main__":
    main()