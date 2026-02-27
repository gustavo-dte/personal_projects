#!/usr/bin/env python3
"""
json_builder.py
===============
Writes ansible_extra_vars.json for domain join/disjoin workflows.

Usage:
  python3 ansible/roles/python_scripts/json_builder.py join
  python3 ansible/roles/python_scripts/json_builder.py disjoin

Actions:
  join     — Build extra_vars for join-windows-domain workflow
             Reads: WORKFLOW_MANIFEST, WORKFLOW_DRY_RUN, WORKFLOW_FORCE_REJOIN,
                    WORKFLOW_SKIP_HOSTNAME_SETUP, SECRET_DOMAIN_ADMIN_PASSWORD,
                    SECRET_DOMAIN_OU_PATH
             Writes: manifest, dry_run, force_rejoin, skip_hostname_setup,
                     winrm_username, domain_admin_password, domain_ou_path

  disjoin  — Build extra_vars for disjoin-windows-domain workflow
             Reads: WORKFLOW_MANIFEST, WORKFLOW_DRY_RUN
             Writes: manifest, dry_run

Output:
  ansible_extra_vars.json — written in the current working directory

Note:
  SE-Admin WinRM password is intentionally NOT included in join extra_vars.
  It is fetched live from Delinea inside the Ansible playbook pre_tasks
  so it is always current and never cached in the extra-vars file.
"""

import json
import logging
import os
import sys
from typing import Any, Dict

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')


def build_join_vars() -> Dict[str, Any]:
    """Build extra_vars dictionary for join workflow."""
    manifest: str = os.environ.get('WORKFLOW_MANIFEST', '').strip()
    dry_run: bool = os.environ.get('WORKFLOW_DRY_RUN', 'true').strip().lower() == 'true'
    force_rejoin: bool = os.environ.get('WORKFLOW_FORCE_REJOIN', 'false').strip().lower() == 'true'
    skip_hostname: bool = os.environ.get('WORKFLOW_SKIP_HOSTNAME_SETUP', 'false').strip().lower() == 'true'
    domain_passwd: str = os.environ.get('SECRET_DOMAIN_ADMIN_PASSWORD', '')
    domain_ou: str = os.environ.get('SECRET_DOMAIN_OU_PATH', '')

    if not manifest:
        logging.error('WORKFLOW_MANIFEST is not set.')
        sys.exit(1)

    return {
        'manifest':              manifest,
        'dry_run':               dry_run,
        'force_rejoin':          force_rejoin,
        'skip_hostname_setup':   skip_hostname,
        'winrm_username':        'SE-Admin',
        'domain_admin_password': domain_passwd,
        'domain_ou_path':        domain_ou,
    }


def build_disjoin_vars() -> Dict[str, Any]:
    """Build extra_vars dictionary for disjoin workflow."""
    manifest: str = os.environ.get('WORKFLOW_MANIFEST', '').strip()
    dry_run: bool = os.environ.get('WORKFLOW_DRY_RUN', 'true').strip().lower() == 'true'

    if not manifest:
        logging.error('WORKFLOW_MANIFEST is not set.')
        sys.exit(1)

    return {
        'manifest': manifest,
        'dry_run':  dry_run,
    }


def main() -> None:
    """Main entry point."""
    if len(sys.argv) < 2:
        logging.error('Usage: %s <join|disjoin>', sys.argv[0])
        sys.exit(1)

    action: str = sys.argv[1].lower().strip()

    if action == 'join':
        extra_vars: Dict[str, Any] = build_join_vars()
    elif action == 'disjoin':
        extra_vars = build_disjoin_vars()
    else:
        logging.error('Invalid action "%s". Must be "join" or "disjoin".', action)
        sys.exit(1)

    output_file: str = 'ansible_extra_vars.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(extra_vars, f, indent=2)

    logging.info('%s written for %s workflow.', output_file, action)


if __name__ == '__main__':
    main()
