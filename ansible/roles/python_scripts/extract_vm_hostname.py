#!/usr/bin/env python3
"""
extract_vm_hostname.py
======================
Extracts the first VM's hostname from a manifest YAML file and constructs
the FQDN for Delinea Secret Server lookup. Writes DELINEA_SECRET_MACHINE
to GITHUB_ENV for subsequent workflow steps.

Exits with code 1 on:
  - MANIFEST_FILE not set
  - Manifest file not found
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

# TODO: Add unit tests before moving to stage or prod. Currently in dev environment.

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

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def load_manifest(manifest_file: str) -> Dict[str, Any]:
    """Load and parse a YAML manifest file. Exits with code 1 on failure."""
    try:
        with open(manifest_file, encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}
    except yaml.YAMLError as ex:
        logging.error(f"Failed to parse manifest YAML: {ex}")
        sys.exit(1)


def write_github_env(github_env: str, key: str, value: str) -> None:
    """Append a key=value pair to the GitHub Actions environment file. Exits with code 1 on failure."""
    try:
        # codeql[py/clear-text-storage-sensitive-data] - Value is non-sensitive (machine hostname/FQDN)
        with open(github_env, "a", encoding="utf-8") as fh:
            fh.write(f"{key}={value}\n")
    except OSError as ex:
        logging.error(f"Failed to write to GITHUB_ENV: {ex}")
        sys.exit(1)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    manifest_file: str = os.getenv("MANIFEST_FILE", "").strip()
    github_env: Optional[str] = os.getenv("GITHUB_ENV")

    if not manifest_file:
        logging.error("MANIFEST_FILE environment variable is not set")
        sys.exit(1)

    if not os.path.isfile(manifest_file):
        logging.error(f"Manifest file not found: {manifest_file}")
        sys.exit(1)

    manifest: Dict[str, Any] = load_manifest(manifest_file)

    vms: List[Dict[str, Any]] = manifest.get("vms") or []
    if not vms:
        logging.error("No VMs found in manifest")
        sys.exit(1)

    first_vm: Dict[str, Any] = vms[0]
    hostname: Optional[str] = first_vm.get("vm_winrm_connect_hostname") or first_vm.get("name")

    if not hostname:
        logging.error(
            "No hostname found in first VM entry "
            "(missing both vm_winrm_connect_hostname and name)"
        )
        sys.exit(1)

    vm_fqdn: str = f"{hostname}.{DOMAIN_SUFFIX}"

    logging.info(f"Extracted VM hostname: {hostname}")
    logging.info(f"Set DELINEA_SECRET_MACHINE={vm_fqdn}")

    if not github_env:
        logging.warning("GITHUB_ENV not set — skipping environment variable export")
        return

    write_github_env(github_env, "DELINEA_SECRET_MACHINE", vm_fqdn)


if __name__ == "__main__":
    main()
