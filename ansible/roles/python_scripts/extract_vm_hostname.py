#!/usr/bin/env python3
"""
extract_vm_hostname.py
======================
Extracts the first VM's hostname from a manifest YAML file and constructs
the FQDN for Delinea Secret Server lookup. Writes DELINEA_SECRET_MACHINE
to GITHUB_ENV for subsequent workflow steps.

Exits with code 1 on:
  - MANIFEST_FILE not set
  - Manifest file not found or unreadable
  - Manifest YAML parse failure
  - No VMs found in manifest
  - No hostname found in first VM entry

Exits with code 0 on:
  - DELINEA_SECRET_MACHINE successfully written to GITHUB_ENV

Environment variables read:
  MANIFEST_FILE    Path to the manifest YAML file
  GITHUB_ENV       Path to the GitHub Actions env file (set automatically by the runner)

Usage:
  MANIFEST_FILE="ansible/vars/my-manifest/manifest.yml" \\
    python3 ansible/roles/python_scripts/extract_vm_hostname.py
"""

from __future__ import annotations

import logging
import os
import sys
from typing import Any, Dict, List, Optional

import yaml

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DOMAIN_SUFFIX = "dtenet.com"

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Custom exceptions
# ---------------------------------------------------------------------------


class ManifestError(Exception):
    """Raised when the manifest cannot be loaded or does not contain expected data."""


# ---------------------------------------------------------------------------
# Manifest helpers
# ---------------------------------------------------------------------------


def load_manifest(manifest_file: str) -> Dict[str, Any]:
    """Load and parse a YAML manifest file.

    Args:
        manifest_file: Absolute or relative path to the manifest YAML.

    Returns:
        Parsed manifest as a dictionary (empty dict if the file is blank).

    Raises:
        ManifestError: If the file cannot be read or the YAML is invalid.
    """
    try:
        with open(manifest_file, encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}
    except OSError as ex:
        raise ManifestError(
            "Cannot read manifest file '%s': %s" % (manifest_file, ex)
        ) from ex
    except yaml.YAMLError as ex:
        raise ManifestError(
            "Failed to parse manifest YAML '%s': %s" % (manifest_file, ex)
        ) from ex


def extract_hostname(manifest: Dict[str, Any]) -> str:
    """Extract the first VM's hostname from a parsed manifest.

    Prefers vm_winrm_connect_hostname over name so that the WinRM-reachable
    address is used when it differs from the VM's display name.

    Args:
        manifest: Parsed manifest dictionary.

    Returns:
        Hostname string (not yet qualified with the domain suffix).

    Raises:
        ManifestError: If no VMs are listed or the first VM has no hostname.
    """
    vms: List[Dict[str, Any]] = manifest.get("vms") or []
    if not vms:
        raise ManifestError("No VMs found in manifest")

    first_vm: Dict[str, Any] = vms[0]
    hostname: Optional[str] = first_vm.get("vm_winrm_connect_hostname") or first_vm.get("name")

    if not hostname:
        raise ManifestError(
            "No hostname found in first VM entry "
            "(missing both 'vm_winrm_connect_hostname' and 'name')"
        )

    return hostname.strip()


# ---------------------------------------------------------------------------
# GitHub Actions environment export
# ---------------------------------------------------------------------------


def _write_github_env(github_env: Optional[str], key: str, value: str) -> None:
    """Export a value to the GitHub Actions environment file.

    When github_env is None (script is running outside of Actions), logs a
    warning and returns without error so local runs stay non-fatal.

    Args:
        github_env: Path to the GITHUB_ENV file, or None if not in Actions.
        key:        Environment variable name to export.
        value:      Value to assign (non-sensitive, e.g. hostname/FQDN).

    Raises:
        OSError: If the GITHUB_ENV file cannot be written.
    """
    if not github_env:
        log.warning("[WARN] GITHUB_ENV not set — skipping environment variable export")
        return

    with open(github_env, "a", encoding="utf-8") as fh:
        fh.write("%s=%s\n" % (key, value))


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------


def run(manifest_file: str, github_env: Optional[str]) -> None:
    """Load the manifest, extract the hostname, and export the FQDN.

    Args:
        manifest_file: Path to the manifest YAML file.
        github_env:    Path to the GITHUB_ENV file, or None if not in Actions.

    Raises:
        ManifestError: On manifest load or parse failures.
        OSError:       If the GITHUB_ENV file cannot be written.
    """
    manifest = load_manifest(manifest_file)
    hostname = extract_hostname(manifest)
    vm_fqdn = "%s.%s" % (hostname, DOMAIN_SUFFIX)

    log.info("[INFO] Extracted VM hostname: %s", hostname)
    log.info("[INFO] Setting DELINEA_SECRET_MACHINE=%s", vm_fqdn)

    _write_github_env(github_env, "DELINEA_SECRET_MACHINE", vm_fqdn)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    """Entry point: extract hostname and write DELINEA_SECRET_MACHINE to GITHUB_ENV."""
    manifest_file: str = os.getenv("MANIFEST_FILE", "").strip()
    github_env: Optional[str] = os.getenv("GITHUB_ENV")

    if not manifest_file:
        log.error("[ERROR] MANIFEST_FILE environment variable is not set")
        sys.exit(1)

    if not os.path.isfile(manifest_file):
        log.error("[ERROR] Manifest file not found: %s", manifest_file)
        sys.exit(1)

    try:
        run(manifest_file, github_env)
    except ManifestError as ex:
        log.error("[ERROR] Manifest error: %s", ex)
        sys.exit(1)
    except OSError as ex:
        log.error("[ERROR] Failed to write to '%s': %s", github_env, ex)
        sys.exit(1)


if __name__ == "__main__":
    main()
