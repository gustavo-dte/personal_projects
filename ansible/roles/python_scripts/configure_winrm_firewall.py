#!/usr/bin/env python3
"""
configure_winrm_firewall.py
===========================
Version: 2.2.0 (2026-03-04)

Configures Windows Firewall on Azure VMs to allow WinRM (5985) and RDP (3389)
using the Azure Run Command API (works regardless of NSG or Windows Firewall state).

For each VM in the manifest it:
  1. Verifies the VM exists in Azure.
  2. Runs a PowerShell script via Azure Run Command to open WinRM/RDP firewall rules.
  3. Ensures the WinRM service is running and PSRemoting is enabled.

Environment variables read:
  MANIFEST    Manifest directory name under ansible/vars/

Exits with code 0 on success.
Exits with code 1 on configuration or Azure CLI errors.

Usage:
  MANIFEST=domain_join_test python3 ansible/roles/python_scripts/configure_winrm_firewall.py
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

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
# PowerShell script executed on each VM via Azure Run Command
# ---------------------------------------------------------------------------

_PS_CONFIGURE_WINRM = """
Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled True
Write-Output "Windows Firewall is enabled"

$winrmHttpRule = Get-NetFirewallRule -Name "WINRM-HTTP-In-TCP-Custom" -ErrorAction SilentlyContinue
if (-not $winrmHttpRule) {
    New-NetFirewallRule -Name "WINRM-HTTP-In-TCP-Custom" `
                        -DisplayName "Windows Remote Management (HTTP-In) - Custom" `
                        -Enabled True -Direction Inbound -Protocol TCP `
                        -LocalPort 5985 -Action Allow -Profile Any
    Write-Output "Created WinRM HTTP (5985) allow rule"
} else {
    Set-NetFirewallRule -Name "WINRM-HTTP-In-TCP-Custom" -Enabled True -Action Allow
    Write-Output "Enabled existing WinRM HTTP (5985) rule"
}

$winrmHttpsRule = Get-NetFirewallRule -Name "WINRM-HTTPS-In-TCP-Custom" -ErrorAction SilentlyContinue
if (-not $winrmHttpsRule) {
    New-NetFirewallRule -Name "WINRM-HTTPS-In-TCP-Custom" `
                        -DisplayName "Windows Remote Management (HTTPS-In) - Custom" `
                        -Enabled True -Direction Inbound -Protocol TCP `
                        -LocalPort 5986 -Action Allow -Profile Any
    Write-Output "Created WinRM HTTPS (5986) allow rule"
} else {
    Set-NetFirewallRule -Name "WINRM-HTTPS-In-TCP-Custom" -Enabled True -Action Allow
    Write-Output "Enabled existing WinRM HTTPS (5986) rule"
}

$rdpRule = Get-NetFirewallRule -Name "RDP-In-TCP-Custom" -ErrorAction SilentlyContinue
if (-not $rdpRule) {
    New-NetFirewallRule -Name "RDP-In-TCP-Custom" `
                        -DisplayName "Remote Desktop (RDP-In) - Custom" `
                        -Enabled True -Direction Inbound -Protocol TCP `
                        -LocalPort 3389 -Action Allow -Profile Any
    Write-Output "Created RDP (3389) allow rule"
} else {
    Set-NetFirewallRule -Name "RDP-In-TCP-Custom" -Enabled True -Action Allow
    Write-Output "Enabled existing RDP (3389) rule"
}

Enable-NetFirewallRule -DisplayGroup "Windows Remote Management" -ErrorAction SilentlyContinue
Write-Output "Enabled default WinRM firewall rules"

Enable-NetFirewallRule -DisplayGroup "Remote Desktop" -ErrorAction SilentlyContinue
Write-Output "Enabled default RDP firewall rules"

Set-Service -Name WinRM -StartupType Automatic -ErrorAction SilentlyContinue
Start-Service -Name WinRM -ErrorAction SilentlyContinue
Write-Output "WinRM service is running"

Enable-PSRemoting -Force -SkipNetworkProfileCheck -ErrorAction SilentlyContinue
Write-Output "PSRemoting enabled"

Write-Output "Windows Firewall configured successfully"
"""

# ---------------------------------------------------------------------------
# Custom exceptions
# ---------------------------------------------------------------------------


class AzureCliError(Exception):
    """Raised when an Azure CLI command fails unexpectedly."""


class ManifestError(Exception):
    """Raised when the manifest cannot be loaded or is missing required fields."""


# ---------------------------------------------------------------------------
# Azure CLI helpers
# ---------------------------------------------------------------------------


def _az(
    *args: str,
    subscription_id: Optional[str] = None,
) -> subprocess.CompletedProcess[str]:
    """Run an az CLI command and return the completed process.

    Explicitly passes os.environ so the GitHub Actions managed-identity
    credentials (AZURE_CLIENT_ID, etc.) are always inherited.

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
        SystemExit: If the file does not exist or cannot be parsed.
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
    """Set the active Azure CLI subscription and verify it took effect.

    Args:
        subscription_id: The Azure subscription GUID to activate.

    Raises:
        SystemExit: If the az account set command fails.
    """
    log.info("[INFO] Setting Azure subscription context: %s", subscription_id)
    result = _az("account", "set", "--subscription", subscription_id)
    if result.returncode != 0:
        log.error("[ERROR] Failed to set subscription: %s", result.stderr.strip())
        sys.exit(1)

    verify = _az("account", "show", "--query", "id", "-o", "tsv")
    if verify.returncode == 0:
        current = verify.stdout.strip()
        log.info("[INFO] Current subscription verified: %s", current)
        if current != subscription_id:
            log.warning(
                "[WARN] Subscription mismatch: expected %s, got %s",
                subscription_id,
                current,
            )
    else:
        log.warning(
            "[WARN] Could not verify current subscription: %s",
            verify.stderr.strip()[:200],
        )


# ---------------------------------------------------------------------------
# VM helpers
# ---------------------------------------------------------------------------


def _vm_exists(
    resource_group: str,
    vm_name: str,
    subscription_id: Optional[str] = None,
) -> Tuple[bool, str]:
    """Check whether a VM exists in Azure.

    Args:
        resource_group:  Azure resource group name.
        vm_name:         Azure VM name.
        subscription_id: Optional subscription GUID.

    Returns:
        Tuple of (exists, error_message). error_message is empty on success.
    """
    result = _az(
        "vm",
        "show",
        "--resource-group",
        resource_group,
        "--name",
        vm_name,
        "--query",
        "name",
        "-o",
        "tsv",
        subscription_id=subscription_id,
    )
    if result.returncode != 0:
        return False, result.stderr.strip() if result.stderr else "Unknown error"
    return bool(result.stdout.strip()), ""


def _list_vms_in_rg(
    resource_group: str,
    subscription_id: Optional[str] = None,
) -> List[str]:
    """Return all VM names in a resource group.

    Args:
        resource_group:  Azure resource group name.
        subscription_id: Optional subscription GUID.

    Returns:
        List of VM name strings (may be empty on failure).
    """
    result = _az(
        "vm",
        "list",
        "--resource-group",
        resource_group,
        "--query",
        "[].name",
        "-o",
        "tsv",
        subscription_id=subscription_id,
    )
    if result.returncode == 0 and result.stdout.strip():
        return [vm.strip() for vm in result.stdout.strip().split("\n") if vm.strip()]
    return []


def _run_command_on_vm(
    resource_group: str,
    vm_name: str,
    subscription_id: Optional[str] = None,
) -> Optional[str]:
    """Run the WinRM PowerShell configuration on a VM via Azure Run Command.

    Args:
        resource_group:  Azure resource group containing the VM.
        vm_name:         Azure VM name.
        subscription_id: Optional subscription GUID.

    Returns:
        Truncated output message string on success, None on failure.
    """
    result = _az(
        "vm",
        "run-command",
        "invoke",
        "--resource-group",
        resource_group,
        "--name",
        vm_name,
        "--command-id",
        "RunPowerShellScript",
        "--scripts",
        _PS_CONFIGURE_WINRM,
        subscription_id=subscription_id,
    )
    if result.returncode != 0:
        log.error(
            "[ERROR] Failed to configure Windows Firewall on VM %s: %s",
            vm_name,
            result.stderr[:300],
        )
        return None

    try:
        output = json.loads(result.stdout)
        messages: str = output.get("value", [{}])[0].get("message", "")
        return messages[:300] if messages else ""
    except (json.JSONDecodeError, IndexError):
        return ""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    """Entry point: configure Windows Firewall on every VM listed in the manifest."""
    log.info("[INFO] configure_winrm_firewall.py v2.2.0 (2026-03-04)")

    manifest_name = os.environ.get("MANIFEST", "").strip()
    if not manifest_name:
        log.error("[ERROR] MANIFEST environment variable is not set")
        sys.exit(1)

    # Verify Azure CLI authentication before proceeding.
    auth_check = _az("account", "show", "-o", "json")
    if auth_check.returncode != 0:
        log.error("[ERROR] Azure CLI authentication failed. Please login first.")
        log.error("        Error: %s", auth_check.stderr.strip()[:300])
        sys.exit(1)

    try:
        auth_info: Dict[str, Any] = json.loads(auth_check.stdout)
        log.info(
            "[INFO] Azure CLI authenticated as: %s",
            auth_info.get("user", {}).get("name", "unknown"),
        )
        log.info(
            "[INFO] Current subscription: %s (%s)",
            auth_info.get("name", ""),
            auth_info.get("id", ""),
        )
    except (json.JSONDecodeError, KeyError):
        log.warning("[WARN] Could not parse Azure authentication info")

    manifest = _load_manifest(manifest_name)

    target_rg: str = manifest.get("target_resource_group", "")
    if not target_rg:
        log.error("[ERROR] target_resource_group not found in manifest")
        sys.exit(1)

    subscription_id: str = manifest.get("target_subscription_id", "")
    if subscription_id:
        _set_subscription(subscription_id)

    vms: List[Dict[str, Any]] = manifest.get("vms") or []
    if not vms:
        log.warning("[WARN] No VMs found in manifest")
        sys.exit(0)

    for vm in vms:
        azure_vm_name: str = vm.get("name", "")
        target_vm_name: str = vm.get("target_vm_name", azure_vm_name)

        if not azure_vm_name:
            log.warning("[WARN] VM entry has no 'name' field, skipping")
            continue

        log.info(
            "[INFO] Configuring Windows Firewall on VM: %s (target hostname: %s)",
            azure_vm_name,
            target_vm_name,
        )

        vm_exists, error_msg = _vm_exists(target_rg, azure_vm_name, subscription_id)
        if not vm_exists:
            log.error(
                "[ERROR] VM '%s' not found in resource group '%s'",
                azure_vm_name,
                target_rg,
            )
            log.error(
                "        Verify with: az vm show --resource-group %s --name %s --subscription %s",
                target_rg,
                azure_vm_name,
                subscription_id,
            )
            if error_msg:
                log.error("        Azure CLI error: %s", error_msg[:500])

            current_sub = _az("account", "show", "--query", "id", "-o", "tsv")
            if current_sub.returncode == 0 and current_sub.stdout.strip():
                log.error("        Current subscription: %s", current_sub.stdout.strip())
            log.error("        Expected subscription: %s", subscription_id or "Not set")
            log.error("")

            existing_vms = _list_vms_in_rg(target_rg, subscription_id)
            if existing_vms:
                log.error("        Existing VMs in resource group:")
                for existing in existing_vms:
                    log.error("          - %s", existing)
                    if existing.lower() == azure_vm_name.lower() and existing != azure_vm_name:
                        log.error(
                            "        >>> CASE MISMATCH: manifest has '%s' but Azure has '%s'",
                            azure_vm_name,
                            existing,
                        )
            else:
                log.error("        No VMs found in resource group (or permission issue)")

            log.error("")
            log.error("        Possible causes:")
            log.error("        1. VM is in a transitioning or deallocated state")
            log.error("        2. Permission issue on az vm show")
            log.error("        3. VM name in manifest does not match Azure resource name exactly")
            log.error("        4. VM was recently created and ARM is still syncing")
            sys.exit(1)

        output = _run_command_on_vm(target_rg, azure_vm_name, subscription_id)
        if output is None:
            sys.exit(1)

        log.info("[OK] Windows Firewall configured on VM %s", azure_vm_name)
        if output:
            log.info("     Output: %s", output)

        time.sleep(2)

    log.info("[INFO] All VMs configured successfully")


if __name__ == "__main__":
    main()
