#!/usr/bin/env python3
"""
build_extra_vars_disjoin.py
===========================
Writes ansible_extra_vars.json for the disjoin-windows-domain workflow.

Variables written:
  manifest   — manifest directory name passed as WORKFLOW_MANIFEST env var
  dry_run    — boolean, passed as WORKFLOW_DRY_RUN env var ("true" / "false")

Environment variables read:
  WORKFLOW_MANIFEST   Value of the 'manifest' workflow input
  WORKFLOW_DRY_RUN    Value of the 'dry_run' workflow input  ("true" or "false")

Output:
  ansible_extra_vars.json  — written in the current working directory

Usage (from a workflow step):
  python3 ansible/roles/python_scripts/build_extra_vars_disjoin.py
"""

import json
import os
import sys

manifest = os.environ.get('WORKFLOW_MANIFEST', '').strip()
dry_run  = os.environ.get('WORKFLOW_DRY_RUN',  'true').strip().lower() == 'true'

if not manifest:
    print('❌ WORKFLOW_MANIFEST is not set.')
    sys.exit(1)

extra_vars = {
    'manifest': manifest,
    'dry_run':  dry_run,
}

with open('ansible_extra_vars.json', 'w', encoding='utf-8') as f:
    json.dump(extra_vars, f, indent=2)

print('✅ ansible_extra_vars.json written.')
