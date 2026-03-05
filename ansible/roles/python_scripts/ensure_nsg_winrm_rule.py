#!/usr/bin/env python3
"""
ensure_nsg_winrm_rule.py
========================
Version: 2.1.0 (2026-03-04)

Ensures a WinRM inbound NSG rule (port 5985) exists for all VMs in a manifest.

For each VM it:
  1. Looks up the VM's NIC via Azure CLI.
  2. Finds the NSG attached to that NIC.
  3. Creates the 'allow-winrm' rule if it does not already exist.

Environment variables read:
  MANIFEST    Manifest directory name under ansible/vars/

Exits with code 0 on success (warnings are non-fatal).
Exits with code 1 on configuration or unrecoverable errors.

Usage:
  MANIFEST=domain_join_test python3 ansible/roles/python_scripts/ensure_nsg_winrm_rule.py
"""

from __future__ import annotations

import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import yaml
except ImportError:
    print("[ERROR] PyYAML is required. Install: pip install PyYAML")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

NSG_RULE_NAME = "allow-winrm"
WINRM_PORT = "5985"
WINRM_SOURCE_PREFIX = "10.0.0.0/8"

# ---------------------------------------------------------------------------
# Custom exceptions
# ---------------------------------------------------------------------------


class ManifestError(Exception):
    """Raised when the manifest cannot be loaded or is missing required fields."""


class NsgError(Exception):
    """Raised when an NSG operation fails."""


# ---------------------------------------------------------------------------
# Azure CLI helpers
# ---------------------------------------------------------------------------


def _az(
    *args: str,
    subscription_id: Optional[str] = None,
) -> subprocess.CompletedProcess[str]:
    """Run an az CLI command and return the completed process.

    Passes os.environ so managed-identity credentials from the GitHub Actions
    runner are always inherited.

    Args:
        *args:           Command arguments forwarded to the az binary.
        subscription_id: Optional subscription to add --subscription flag.

    Returns:
        CompletedProcess with stdout, stderr, and returncode populated.
    """
    cmd: List[str] = ["az", *args]
    if subscription_id:
        cmd.extend(["--subscription", subscription_id])
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False,
        env=os.environ.copy(),
    )


# ---------------------------------------------------------------------------
# Manifest helpers
# ---------------------------------------------------------------------------


def _load_manifest(manifest_name: str) -> Dict[str, Any]:
    """Load and return the manifest YAML for manifest_name.

    Args:
        manifest_name: Directory name under ansible/vars/.

    Returns:
        Parsed manifest as a dict (empty dict if the file is blank).

    Raises:
        SystemExit: If the file does not exist.
    """
    path = Path("ansible/vars") / manifest_name / "manifest.yml"
    if not path.exists():
        log.error("[ERROR] Manifest not found: %s", path)
        sys.exit(1)
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


# ---------------------------------------------------------------------------
# Subscription context
# ---------------------------------------------------------------------------


def _set_subscription(subscription_id: str) -> None:
    """Set the active Azure CLI subscription.

    Args:
        subscription_id: Azure subscription GUID to activate.

    Raises:
        SystemExit: If the az account set command fails.
    """
    log.info("[INFO] Setting Azure subscription context: %s", subscription_id)
    result = _az("account", "set", "--subscription", subscription_id)
    if result.returncode != 0:
        log.error("[ERROR] Failed to set subscription: %s", result.stderr.strip())
        sys.exit(1)


# ---------------------------------------------------------------------------
# NIC / NSG helpers
# ---------------------------------------------------------------------------


def _get_nic_id(
    resource_group: str,
    vm_name: str,
    subscription_id: Optional[str] = None,
) -> Optional[str]:
    """Return the first NIC resource ID for a VM, or None on failure.

    Args:
        resource_group:  Azure resource group containing the VM.
        vm_name:         Azure VM name.
        subscription_id: Optional subscription GUID.

    Returns:
        NIC resource ID string, or None if not found.
    """
    result = _az(
        "vm",
        "nic",
        "list",
        "--resource-group",
        resource_group,
        "--vm-name",
        vm_name,
        "--query",
        "[0].id",
        "-o",
        "tsv",
        subscription_id=subscription_id,
    )
    if result.returncode != 0 or not result.stdout.strip():
        log.warning("[WARN] Could not get NIC for VM %s", vm_name)
        return None
    return result.stdout.strip()


def _get_nsg_id(
    nic_id: str,
    subscription_id: Optional[str] = None,
) -> Optional[str]:
    """Return the NSG resource ID attached to a NIC, or None on failure.

    Args:
        nic_id:          Full NIC resource ID.
        subscription_id: Optional subscription GUID.

    Returns:
        NSG resource ID string, or None if not found.
    """
    nic_name = nic_id.split("/")[-1]
    result = _az(
        "network",
        "nic",
        "show",
        "--ids",
        nic_id,
        "--query",
        "networkSecurityGroup.id",
        "-o",
        "tsv",
        subscription_id=subscription_id,
    )
    if result.returncode != 0 or not result.stdout.strip():
        log.warning("[WARN] Could not get NSG for NIC %s", nic_name)
        return None
    return result.stdout.strip()


def _ensure_winrm_rule(
    nsg_name: str,
    nsg_rg: str,
    vm_name: str,
    subscription_id: Optional[str] = None,
) -> None:
    """Create the WinRM allow rule on an NSG if it does not already exist.

    Args:
        nsg_name:        NSG resource name.
        nsg_rg:          Resource group containing the NSG.
        vm_name:         Azure VM name (used for log messages only).
        subscription_id: Optional subscription GUID.

    Raises:
        SystemExit: If rule creation fails.
    """
    check = _az(
        "network",
        "nsg",
        "rule",
        "show",
        "--resource-group",
        nsg_rg,
        "--nsg-name",
        nsg_name,
        "--name",
        NSG_RULE_NAME,
        subscription_id=subscription_id,
    )
    if check.returncode == 0:
        log.info("[OK] WinRM NSG rule already exists for VM %s", vm_name)
        return

    log.info("[INFO] Creating WinRM NSG rule for VM %s", vm_name)
    create = _az(
        "network",
        "nsg",
        "rule",
        "create",
        "--resource-group",
        nsg_rg,
        "--nsg-name",
        nsg_name,
        "--name",
        NSG_RULE_NAME,
        "--priority",
        "1001",
        "--direction",
        "Inbound",
        "--access",
        "Allow",
        "--protocol",
        "Tcp",
        "--destination-port-ranges",
        WINRM_PORT,
        "--source-address-prefixes",
        WINRM_SOURCE_PREFIX,
        "--description",
        "Allow WinRM HTTP from internal network for GitHub Actions runner",
        subscription_id=subscription_id,
    )
    if create.returncode == 0:
        log.info("[OK] WinRM NSG rule created for VM %s", vm_name)
    else:
        log.error(
            "[ERROR] Failed to create WinRM NSG rule for %s: %s",
            vm_name,
            create.stderr.strip(),
        )
        sys.exit(1)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    """Entry point: ensure WinRM NSG rule exists for every VM in the manifest."""
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
        azure_vm_name: str = vm.get("target_vm_name", "")
        if not azure_vm_name:
            log.warning("[WARN] VM entry has no 'target_vm_name' field, skipping")
            continue

        log.info("[INFO] Checking NSG for VM: %s", azure_vm_name)

        nic_id = _get_nic_id(target_rg, azure_vm_name, subscription_id)
        if not nic_id:
            continue

        nsg_id = _get_nsg_id(nic_id, subscription_id)
        if not nsg_id:
            continue

        nsg_name = nsg_id.split("/")[-1]
        nsg_rg = nsg_id.split("/")[4]
        log.info("[INFO] Found NSG: %s in resource group: %s", nsg_name, nsg_rg)

        _ensure_winrm_rule(nsg_name, nsg_rg, azure_vm_name, subscription_id)


if __name__ == "__main__":
    main()
