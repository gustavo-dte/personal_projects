#!/usr/bin/env python3
"""
configure_winrm_firewall.py
===========================
Version: 2.6.0 (2026-03-05)

Configures Windows Firewall on Azure VMs to allow WinRM (5985) and RDP (3389)
using az vm run-command invoke.

For each VM in the manifest it:
  1. Verifies the VM exists in Azure using target_vm_name (Azure resource name).
  2. Runs a PowerShell script via az vm run-command invoke to open
     WinRM/RDP firewall rules and ensure the WinRM service is running.

Key fixes vs 2.5.0:
  - Switched from CustomScriptExtension to run-command invoke (more reliable)
  - Uses Azure Fabric directly instead of VM Agent

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
# PowerShell script executed on each VM via Azure run-command invoke
# ---------------------------------------------------------------------------

_PS_CONFIGURE_WINRM = """
$ErrorActionPreference = 'Continue'
$VerbosePreference = 'Continue'

try {
    Write-Output "=== Starting WinRM Configuration ==="

    # Enable Windows Firewall
    try {
        Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled True -ErrorAction Stop
        Write-Output "[OK] Windows Firewall enabled"
    } catch {
        Write-Output "[WARN] Could not enable firewall: $_"
    }

    # Create WinRM HTTP rule
    try {
        $winrmHttpRule = Get-NetFirewallRule -Name "WINRM-HTTP-In-TCP-Custom" -ErrorAction SilentlyContinue
        if (-not $winrmHttpRule) {
            New-NetFirewallRule -Name "WINRM-HTTP-In-TCP-Custom" -DisplayName "Windows Remote Management (HTTP-In) - Custom" -Enabled True -Direction Inbound -Protocol TCP -LocalPort 5985 -Action Allow -Profile Any -ErrorAction Stop
            Write-Output "[OK] Created WinRM HTTP (5985) rule"
        } else {
            Set-NetFirewallRule -Name "WINRM-HTTP-In-TCP-Custom" -Enabled True -Action Allow -ErrorAction Stop
            Write-Output "[OK] WinRM HTTP (5985) rule already exists"
        }
    } catch {
        Write-Output "[WARN] WinRM HTTP rule error: $_"
    }

    # Create WinRM HTTPS rule
    try {
        $winrmHttpsRule = Get-NetFirewallRule -Name "WINRM-HTTPS-In-TCP-Custom" -ErrorAction SilentlyContinue
        if (-not $winrmHttpsRule) {
            New-NetFirewallRule -Name "WINRM-HTTPS-In-TCP-Custom" -DisplayName "Windows Remote Management (HTTPS-In) - Custom" -Enabled True -Direction Inbound -Protocol TCP -LocalPort 5986 -Action Allow -Profile Any -ErrorAction Stop
            Write-Output "[OK] Created WinRM HTTPS (5986) rule"
        } else {
            Set-NetFirewallRule -Name "WINRM-HTTPS-In-TCP-Custom" -Enabled True -Action Allow -ErrorAction Stop
            Write-Output "[OK] WinRM HTTPS (5986) rule already exists"
        }
    } catch {
        Write-Output "[WARN] WinRM HTTPS rule error: $_"
    }

    # Create RDP rule
    try {
        $rdpRule = Get-NetFirewallRule -Name "RDP-In-TCP-Custom" -ErrorAction SilentlyContinue
        if (-not $rdpRule) {
            New-NetFirewallRule -Name "RDP-In-TCP-Custom" -DisplayName "Remote Desktop (RDP-In) - Custom" -Enabled True -Direction Inbound -Protocol TCP -LocalPort 3389 -Action Allow -Profile Any -ErrorAction Stop
            Write-Output "[OK] Created RDP (3389) rule"
        } else {
            Set-NetFirewallRule -Name "RDP-In-TCP-Custom" -Enabled True -Action Allow -ErrorAction Stop
            Write-Output "[OK] RDP (3389) rule already exists"
        }
    } catch {
        Write-Output "[WARN] RDP rule error: $_"
    }

    # Enable default WinRM rules
    try {
        Enable-NetFirewallRule -DisplayGroup "Windows Remote Management" -ErrorAction SilentlyContinue
        Write-Output "[OK] Enabled default WinRM firewall rules"
    } catch {
        Write-Output "[WARN] Could not enable default WinRM rules: $_"
    }

    # Enable default RDP rules
    try {
        Enable-NetFirewallRule -DisplayGroup "Remote Desktop" -ErrorAction SilentlyContinue
        Write-Output "[OK] Enabled default RDP firewall rules"
    } catch {
        Write-Output "[WARN] Could not enable default RDP rules: $_"
    }

    # Configure WinRM service
    try {
        Set-Service -Name WinRM -StartupType Automatic -ErrorAction Stop
        Start-Service -Name WinRM -ErrorAction Stop
        Write-Output "[OK] WinRM service started"
    } catch {
        Write-Output "[WARN] Could not start WinRM service: $_"
    }

    # Enable PSRemoting
    try {
        $winrmService = Get-Service -Name WinRM -ErrorAction SilentlyContinue
        if ($winrmService.Status -ne 'Running') {
            Enable-PSRemoting -Force -SkipNetworkProfileCheck -ErrorAction Stop
            Write-Output "[OK] PSRemoting enabled"
        } else {
            Write-Output "[OK] PSRemoting already configured"
        }
    } catch {
        Write-Output "[WARN] Could not enable PSRemoting: $_"
    }

    Write-Output "=== WinRM Configuration Complete ==="
    exit 0

} catch {
    Write-Output "[ERROR] Unexpected error: $_"
    exit 1
}
"""

# ---------------------------------------------------------------------------
# Azure CLI helpers
# ---------------------------------------------------------------------------


def _az(*args: str) -> subprocess.CompletedProcess[str]:
    """Run an az CLI command and return the completed process."""
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
    """Load and return the manifest YAML for manifest_name."""
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
    """Set the active Azure CLI subscription and verify it took effect."""
    log.info("[INFO] Setting Azure subscription context: %s", subscription_id)
    result = _az("account", "set", "--subscription", subscription_id)
    if result.returncode != 0:
        log.error("[ERROR] Failed to set subscription: %s", result.stderr.strip())
        sys.exit(1)


# ---------------------------------------------------------------------------
# VM helpers
# ---------------------------------------------------------------------------


def _vm_exists(
    resource_group: str,
    vm_name: str,
    subscription_id: Optional[str] = None,
) -> Tuple[bool, str]:
    """Check whether a VM exists in Azure."""
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
    """Return all VM names in a resource group."""
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


def _run_command_via_runcommand(
    resource_group: str,
    vm_name: str,
    subscription_id: Optional[str] = None,
) -> Optional[str]:
    """Execute the WinRM PowerShell configuration via az vm run-command invoke.

    Uses az vm run-command invoke which executes directly via Azure Fabric
    and does not require the VM Agent to be working.
    """
    log.info("[INFO] Executing WinRM configuration via run-command invoke on VM %s ...", vm_name)

    # Build the command - escape single quotes for PowerShell
    ps_command = _PS_CONFIGURE_WINRM.replace("'", "''")

    args = [
        "vm", "run-command", "invoke",
        "--resource-group", resource_group,
        "--name", vm_name,
        "--command-id", "RunPowerShellScript",
        "--scripts", ps_command,
    ]
    if subscription_id:
        args.extend(["--subscription", subscription_id])

    result = _az(*args)

    if result.returncode != 0:
        log.error(
            "[ERROR] Failed to run command on VM %s (rc=%s): %s",
            vm_name,
            result.returncode,
            result.stderr[:500] if result.stderr else "Unknown error",
        )
        return None

    # Parse the JSON output to get the script output
    try:
        output_json = json.loads(result.stdout)
        if output_json.get("value") and len(output_json["value"]) > 0:
            script_output = output_json["value"][0].get("message", "")
            # Log the output for debugging
            log.info("[INFO] Script output: %s", script_output[:500])
            return script_output
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        log.warning("[WARN] Could not parse command output: %s", e)
        return result.stdout[:500] if result.stdout else "Command executed"

    return "Command executed successfully"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    """Entry point: configure Windows Firewall on every VM listed in the manifest."""
    log.info("[INFO] configure_winrm_firewall.py v2.6.0 (2026-03-05)")

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
            else:
                log.error("        No VMs found in resource group (or permission issue)")

            log.error("")
            log.error("        Possible causes:")
            log.error("        1. target_vm_name in manifest does not match the Azure resource name exactly")
            log.error("        2. VM is deallocated or in a transitioning state")
            log.error("        3. Managed identity lacks Reader/VM Contributor on this VM")
            log.error("        4. VM was recently created and ARM is still syncing")
            sys.exit(1)

        # Use run-command invoke instead of VM extension
        output = _run_command_via_runcommand(vm_resource_group, azure_vm_name, vm_subscription)

        if output is None:
            sys.exit(1)

        log.info("[OK] WinRM configured on Azure VM %s", azure_vm_name)
        if output:
            log.info("     Output: %s", output)

    log.info("[INFO] All VMs configured successfully")


if __name__ == "__main__":
    main()
