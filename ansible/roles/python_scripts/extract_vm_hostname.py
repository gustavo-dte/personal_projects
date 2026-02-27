#!/usr/bin/env python3
"""
extract_vm_hostname.py
======================
Extracts the first VM's hostname from a manifest YAML file and constructs
the FQDN for Delinea Secret Server lookup. Writes DELINEA_SECRET_MACHINE
to GITHUB_ENV for subsequent workflow steps.

Exits with code 1 (failure) when:
  - MANIFEST_FILE environment variable is not set
  - Manifest file does not exist
  - No VMs found in manifest
  - No hostname found in first VM entry (missing both vm_winrm_connect_hostname and name)

Exits with code 0 (success) when:
  - VM hostname is successfully extracted and DELINEA_SECRET_MACHINE is written to GITHUB_ENV

Environment variables read:
  MANIFEST_FILE    Path to the manifest YAML file (e.g., ansible/vars/manifest_name/manifest.yml)
  GITHUB_ENV       Path to the GitHub Actions env file (set automatically by the runner)

Usage (from a workflow step):
  MANIFEST_FILE="ansible/vars/my-manifest/manifest.yml" python3 ansible/roles/python_scripts/extract_vm_hostname.py
"""

import logging
import os
import sys
import yaml
from typing import Any, Dict, List, Optional

logging.basicConfig(level=logging.INFO, format='%(message)s')

manifest_file: str = os.getenv('MANIFEST_FILE', '').strip()
github_env: Optional[str] = os.getenv('GITHUB_ENV')

if not manifest_file:
    logging.error('MANIFEST_FILE environment variable is not set.')
    sys.exit(1)

if not os.path.isfile(manifest_file):
    logging.error('Manifest file not found: %s', manifest_file)
    sys.exit(1)

try:
    # lgtm[py/clear-text-logging-sensitive-data]
    with open(manifest_file, 'r', encoding='utf-8') as f:
        manifest: Any = yaml.safe_load(f)
except Exception as ex:
    logging.error('Failed to parse manifest YAML: %s', ex)
    sys.exit(1)

vms: List[Dict[str, Any]] = manifest.get('vms', [])
if not vms:
    logging.error('No VMs found in manifest.')
    sys.exit(1)

first_vm: Dict[str, Any] = vms[0]
# Prefer vm_winrm_connect_hostname, fallback to name
hostname: Optional[str] = first_vm.get('vm_winrm_connect_hostname') or first_vm.get('name')

if not hostname:
    logging.error('No hostname found in first VM entry (missing both vm_winrm_connect_hostname and name).')
    sys.exit(1)

# Construct FQDN for Delinea lookup
vm_fqdn: str = f"{hostname}.dtenet.com"

logging.info('Extracted VM hostname: %s', hostname)
logging.info('Set DELINEA_SECRET_MACHINE=%s', vm_fqdn)

if github_env:
    try:
        # lgtm[py/clear-text-logging-sensitive-data]
        with open(github_env, 'a', encoding='utf-8') as f:
            f.write(f'DELINEA_SECRET_MACHINE={vm_fqdn}\n')
    except Exception as ex:
        logging.error('Failed to write to GITHUB_ENV: %s', ex)
        sys.exit(1)
else:
    logging.warning('GITHUB_ENV not set, skipping environment variable export.')

sys.exit(0)
