#!/usr/bin/env python3
"""
build_extra_vars_join.py
========================
Writes ansible_extra_vars.json for the join-windows-domain workflow.

Variables written:
  manifest              — manifest directory name
  dry_run               — boolean
  force_rejoin          — boolean
  winrm_username        — hardcoded to "SE-Admin"
  domain_admin_password — cpoe-automation password (from SECRET_DOMAIN_ADMIN_PASSWORD)
  domain_ou_path        — (optional) OU path for the computer object

SE-Admin WinRM password is intentionally NOT included here.
It is fetched live from Delinea inside the Ansible playbook pre_tasks
so it is always current and never cached in the extra-vars file.

Environment variables read:
  WORKFLOW_MANIFEST               Value of the 'manifest' workflow input
  WORKFLOW_DRY_RUN                Value of the 'dry_run' workflow input  ("true" or "false")
  WORKFLOW_FORCE_REJOIN           Value of the 'force_rejoin' workflow input  ("true" or "false")
  SECRET_DOMAIN_ADMIN_PASSWORD    cpoe-automation domain account password (from GitHub Secret)
  SECRET_DOMAIN_OU_PATH           (Optional) OU path  (from GitHub Secret)

Output:
  ansible_extra_vars.json  — written in the current working directory

Usage (from a workflow step):
  python3 ansible/roles/python_scripts/build_extra_vars_join.py
"""

import json
import os
import sys

manifest      = os.environ.get('WORKFLOW_MANIFEST',            '').strip()
dry_run       = os.environ.get('WORKFLOW_DRY_RUN',       'true').strip().lower() == 'true'
force_rejoin  = os.environ.get('WORKFLOW_FORCE_REJOIN',  'false').strip().lower() == 'true'
domain_passwd = os.environ.get('SECRET_DOMAIN_ADMIN_PASSWORD', '')
domain_ou     = os.environ.get('SECRET_DOMAIN_OU_PATH',        '')

if not manifest:
    print('❌ WORKFLOW_MANIFEST is not set.')
    sys.exit(1)

extra_vars = {
    'manifest':              manifest,
    'dry_run':               dry_run,
    'force_rejoin':          force_rejoin,
    'winrm_username':        'SE-Admin',
    'domain_admin_password': domain_passwd,
    'domain_ou_path':        domain_ou,
}

with open('ansible_extra_vars.json', 'w', encoding='utf-8') as f:
    json.dump(extra_vars, f, indent=2)

print('✅ ansible_extra_vars.json written.')
