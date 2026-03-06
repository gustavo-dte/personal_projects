#!/usr/bin/env python3
"""
configure_winrm_firewall.py
===========================
Version: 2.4.0 (2026-03-05)

Configures Windows Firewall on Azure VMs to allow WinRM (5985) and RDP (3389)
using the Azure VM Extension (CustomScriptExtension). Does NOT use
az vm run-command invoke at any point.

For each VM in the manifest it:
  1. Verifies the VM exists in Azure using target_vm_name (Azure resource name).
  2. Runs a PowerShell script via az vm extension set (idempotent) to open
     WinRM/RDP firewall rules and ensure the WinRM service is running.

Key fixes vs 2.3.0:
  - VM existence check and extension deployment now use target_vm_name
    (the Azure resource name, e.g. VMCUWINWEBD09) instead of name
    (the source hostname, e.g. dca-tst1856).
  - az vm extension create -> az vm extension set (idempotent).
  - az vm extension delete now passes --yes and handles --subscription correctly.
  - Per-VM resource group and subscription supported via vm_resource_group /
    vm_subscription_id manifest fields (fall back to manifest-level defaults).

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
# PowerShell script executed on each VM via Azure VM Extension
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


def _az(*args: str) -> subprocess.CompletedProcess[str]:
    """Run an az CLI command and return the completed process.

    Explicitly passes os.environ so the GitHub Actions managed-identity
    credentials (AZURE_CLIENT_ID, etc.) are always inherited.

    Args:
        *args: Command arguments forwarded to the az binary.
               Include --subscription in args directly when needed.

    Returns:
        CompletedProcess with stdout, stderr, and returncode populated.
    """
    cmd: List[str] = ["az", *args]
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
        vm_name:         Azure VM name (target_vm_name from manifest).
        subscription_id: Optional subscription GUID.

    Returns:
        Tuple of (exists, error_message). error_message is empty on success.
    """
    args = [
        "vm", "show",
        "--resource-group", resource_group,
        "--name", vm_name,
        "--query", "name",
        "-o", "tsv",
    ]
    if subscription_id:
        args.extend(["--subscription", subscription_id])
    result = _az(*args)
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
    args = [
        "vm", "list",
        "--resource-group", resource_group,
        "--query", "[].name",
        "-o", "tsv",
    ]
    if subscription_id:
        args.extend(["--subscription", subscription_id])
    result = _az(*args)
    if result.returncode == 0 and result.stdout.strip():
        return [vm.strip() for vm in result.stdout.strip().split("\n") if vm.strip()]
    return []


def _delete_extension_if_exists(
    resource_group: str,
    vm_name: str,
    extension_name: str,
    subscription_id: Optional[str] = None,
) -> None:
    """Delete an existing CustomScriptExtension if it exists (idempotent).

    Args:
        resource_group:  Azure resource group name.
        vm_name:         Azure VM name.
        extension_name:  Extension name to delete.
        subscription_id: Optional subscription GUID.
    """
    args = [
        "vm", "extension", "delete",
        "--resource-group", resource_group,
        "--vm-name", vm_name,
        "--name", extension_name,
        "--yes",
    ]
    if subscription_id:
        args.extend(["--subscription", subscription_id])
    result = _az(*args)
    if result.returncode != 0:
        log.debug(
            "[DEBUG] Extension %s not found or already deleted (rc=%s)",
            extension_name,
            result.returncode,
        )


def _run_command_via_extension(
    resource_group: str,
    vm_name: str,
    extension_name: str,
    subscription_id: Optional[str] = None,
) -> Optional[str]:
    """Deploy the WinRM PowerShell configuration via az vm extension set.

    Uses az vm extension set (idempotent - creates or updates) instead of
    az vm run-command invoke. The extension runs via the Azure VM Agent
    and does NOT block or corrupt the VM if it fails.

    Args:
        resource_group:  Azure resource group containing the VM.
        vm_name:         Azure VM name (target_vm_name from manifest).
        extension_name:  Name for the CustomScriptExtension instance.
        subscription_id: Optional subscription GUID.

    Returns:
        Output message string on success, None on failure.
    """
    # Delete any stale copy first so the new timestamp forces re-execution.
    _delete_extension_if_exists(resource_group, vm_name, extension_name, subscription_id)
    time.sleep(2)

    settings = json.dumps({
        "commandToExecute": (
            'powershell.exe -ExecutionPolicy Bypass -NonInteractive -Command "{0}"'.format(
                _PS_CONFIGURE_WINRM.replace('"', '\\"').replace("\n", " ")
            )
        ),
        "timestamp": int(time.time()),
    })

    # az vm extension set is idempotent (creates or updates).
    # It does NOT use run-command invoke and will not hang the VM on failure.
    args = [
        "vm", "extension", "set",
        "--resource-group", resource_group,
        "--vm-name", vm_name,
        "--name", extension_name,
        "--publisher", "Microsoft.Compute",
        "--version", "1.10",
        "--settings", settings,
    ]
    if subscription_id:
        args.extend(["--subscription", subscription_id])

    log.info("[INFO] Deploying CustomScriptExtension on VM %s ...", vm_name)
    result = _az(*args)

    if result.returncode != 0:
        log.error(
            "[ERROR] Failed to set extension on VM %s (rc=%s): %s",
            vm_name,
            result.returncode,
            result.stderr[:300] if result.stderr else "Unknown error",
        )
        return None

    # Poll until extension provisioning reaches a terminal state.
    log.info("[INFO] Waiting for extension to complete on VM %s ...", vm_name)
    max_wait = 120
    check_interval = 5
    elapsed = 0

    while elapsed < max_wait:
        time.sleep(check_interval)
        elapsed += check_interval

        status_args = [
            "vm", "extension", "show",
            "--resource-group", resource_group,
            "--vm-name", vm_name,
            "--name", extension_name,
            "--query", "provisioningState",
            "-o", "tsv",
        ]
        if subscription_id:
            status_args.extend(["--subscription", subscription_id])
        status_result = _az(*status_args)

        if status_result.returncode == 0:
            state = status_result.stdout.strip().lower()
            log.debug("[DEBUG] Extension state: %s (elapsed %ds)", state, elapsed)

            if state == "succeeded":
                output_args = [
                    "vm", "extension", "show",
                    "--resource-group", resource_group,
                    "--vm-name", vm_name,
                    "--name", extension_name,
                    "--query", "instanceView.substatuses[].message",
                    "-o", "tsv",
                ]
                if subscription_id:
                    output_args.extend(["--subscription", subscription_id])
                output_result = _az(*output_args)
                if output_result.returncode == 0 and output_result.stdout:
                    return output_result.stdout.strip()[:500]
                return "Extension completed successfully"

            elif state == "failed":
                log.error("[ERROR] Extension failed on VM %s", vm_name)
                error_args = [
                    "vm", "extension", "show",
                    "--resource-group", resource_group,
                    "--vm-name", vm_name,
                    "--name", extension_name,
                    "--query", "instanceView.statuses[].message",
                    "-o", "tsv",
                ]
                if subscription_id:
                    error_args.extend(["--subscription", subscription_id])
                error_result = _az(*error_args)
                if error_result.returncode == 0 and error_result.stdout:
                    log.error("[ERROR] Extension error detail: %s", error_result.stdout.strip())
                return None

    log.error("[ERROR] Extension timed out after %ds on VM %s", max_wait, vm_name)
    return None


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    """Entry point: configure Windows Firewall on every VM listed in the manifest."""
    log.info("[INFO] configure_winrm_firewall.py v2.4.0 (2026-03-05)")

    manifest_name = os.environ.get("MANIFEST", "").strip()
    if not manifest_name:
        log.error("[ERROR] MANIFEST environment variable is not set")
        sys.exit(1)

    # Verify Azure CLI authentication before proceeding.
    auth_check = _az("account", "show", "-o", "json")
    if auth_check.returncode != 0:
        log.error("[ERROR] Azure CLI authentication failed. Run 'az login' first.")
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
        # source hostname (e.g. dca-tst1856) - used for logging only
        source_vm_name: str = vm.get("name", "")
        # Azure resource name (e.g. VMCUWINWEBD09) - used for all az vm calls
        azure_vm_name: str = vm.get("target_vm_name", source_vm_name)

        if not azure_vm_name:
            log.warning("[WARN] VM entry has no 'target_vm_name' or 'name' field, skipping")
            continue

        # Per-VM overrides fall back to manifest-level defaults
        vm_resource_group: str = vm.get("vm_resource_group", target_rg)
        vm_subscription: str = vm.get("vm_subscription_id", subscription_id)

        log.info(
            "[INFO] Configuring WinRM on Azure VM: %s (source: %s, RG: %s)",
            azure_vm_name,
            source_vm_name or "(not set)",
            vm_resource_group,
        )

        vm_exists, error_msg = _vm_exists(vm_resource_group, azure_vm_name, vm_subscription)
        if not vm_exists:
            log.error(
                "[ERROR] Azure VM '%s' not found in resource group '%s'",
                azure_vm_name,
                vm_resource_group,
            )
            log.error(
                "        Verify with: az vm show --resource-group %s --name %s --subscription %s",
                vm_resource_group,
                azure_vm_name,
                vm_subscription,
            )
            if error_msg:
                log.error("        Azure CLI error: %s", error_msg[:500])

            current_sub = _az("account", "show", "--query", "id", "-o", "tsv")
            if current_sub.returncode == 0 and current_sub.stdout.strip():
                log.error("        Current subscription : %s", current_sub.stdout.strip())
            log.error("        Expected subscription: %s", vm_subscription or "Not set")
            log.error("")

            existing_vms = _list_vms_in_rg(vm_resource_group, vm_subscription)
            if existing_vms:
                log.error("        Existing VMs in resource group '%s':", vm_resource_group)
                for existing in existing_vms:
                    log.error("          - %s", existing)
                    if existing.lower() == azure_vm_name.lower() and existing != azure_vm_name:
                        log.error(
                            "        >>> CASE MISMATCH: manifest target_vm_name='%s' but Azure has '%s'",
                            azure_vm_name,
                            existing,
                        )
            else:
                log.error("        No VMs found in resource group (or permission issue)")

            log.error("")
            log.error("        Possible causes:")
            log.error("        1. target_vm_name in manifest does not match the Azure resource name exactly")
            log.error("        2. VM is deallocated or in a transitioning state")
            log.error("        3. Managed identity lacks Reader/VM Contributor on this VM")
            log.error("        4. VM was recently created and ARM is still syncing")
            sys.exit(1)

        extension_name = "configure-winrm-firewall"
        output = _run_command_via_extension(vm_resource_group, azure_vm_name, extension_name, vm_subscription)

        if output is None:
            sys.exit(1)

        log.info("[OK] WinRM configured on Azure VM %s", azure_vm_name)
        if output:
            log.info("     Output: %s", output)

        time.sleep(2)

    log.info("[INFO] All VMs configured successfully")


if __name__ == "__main__":
    main()
