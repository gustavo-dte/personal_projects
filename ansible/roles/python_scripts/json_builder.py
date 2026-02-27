#!/usr/bin/env python3
"""
json_builder.py
===============
Writes ansible_extra_vars.json for domain join / disjoin workflows.

Usage:
  python3 ansible/roles/python_scripts/json_builder.py join
  python3 ansible/roles/python_scripts/json_builder.py disjoin

Actions:
  join     — Build extra_vars for join-windows-domain workflow.
             Reads: WORKFLOW_MANIFEST, WORKFLOW_DRY_RUN, WORKFLOW_FORCE_REJOIN,
                    WORKFLOW_SKIP_HOSTNAME_SETUP, SECRET_DOMAIN_ADMIN_PASSWORD,
                    SECRET_DOMAIN_OU_PATH

  disjoin  — Build extra_vars for disjoin-windows-domain workflow.
             Reads: WORKFLOW_MANIFEST, WORKFLOW_DRY_RUN

Output:
  ansible_extra_vars.json — written to the current working directory

Note:
  The SE-Admin WinRM password is intentionally excluded from join extra_vars.
  It is fetched live from Delinea inside the Ansible playbook pre_tasks so it
  is always current and never cached in the extra-vars file.
"""

import json
import logging
import os
import sys
from typing import Any, Callable, Dict

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

OUTPUT_FILE = "ansible_extra_vars.json"
WINRM_USERNAME = "SE-Admin"

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(level=logging.INFO, format="%(message)s")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _env_bool(var: str, default: str = "false") -> bool:
    """Read an environment variable and interpret it as a boolean."""
    return os.environ.get(var, default).strip().lower() == "true"


def _env_str(var: str) -> str:
    """Read a stripped environment variable value, defaulting to empty string."""
    return os.environ.get(var, "").strip()


def _require_manifest() -> str:
    """Read and validate WORKFLOW_MANIFEST from the environment. Exits with code 1 if not set."""
    manifest = _env_str("WORKFLOW_MANIFEST")
    if not manifest:
        logging.error("WORKFLOW_MANIFEST is not set")
        sys.exit(1)
    return manifest


# ---------------------------------------------------------------------------
# Builders
# ---------------------------------------------------------------------------


def _build_join_vars() -> Dict[str, Any]:
    """Build extra_vars dictionary for the join workflow."""
    domain_admin_password = os.environ.get("SECRET_DOMAIN_ADMIN_PASSWORD", "")
    if not domain_admin_password:
        logging.warning("SECRET_DOMAIN_ADMIN_PASSWORD is not set — domain join will fail at runtime")

    return {
        "manifest":              _require_manifest(),
        "dry_run":               _env_bool("WORKFLOW_DRY_RUN", default="true"),
        "force_rejoin":          _env_bool("WORKFLOW_FORCE_REJOIN"),
        "skip_hostname_setup":   _env_bool("WORKFLOW_SKIP_HOSTNAME_SETUP"),
        "winrm_username":        WINRM_USERNAME,
        "domain_admin_password": domain_admin_password,
        "domain_ou_path":        _env_str("SECRET_DOMAIN_OU_PATH"),
    }


def _build_disjoin_vars() -> Dict[str, Any]:
    """Build extra_vars dictionary for the disjoin workflow."""
    return {
        "manifest": _require_manifest(),
        "dry_run":  _env_bool("WORKFLOW_DRY_RUN", default="true"),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

_BUILDERS: Dict[str, Callable[[], Dict[str, Any]]] = {
    "join":    _build_join_vars,
    "disjoin": _build_disjoin_vars,
}


def main() -> None:
    if len(sys.argv) < 2:
        logging.error(f"Usage: {sys.argv[0]} <join|disjoin>")
        sys.exit(1)

    action: str = sys.argv[1].strip().lower()

    if action not in _BUILDERS:
        logging.error(f'Invalid action "{action}" — must be one of: {", ".join(_BUILDERS)}')
        sys.exit(1)

    extra_vars: Dict[str, Any] = _BUILDERS[action]()

    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as fh:
            json.dump(extra_vars, fh, indent=2)
    except OSError as ex:
        logging.error(f"Failed to write {OUTPUT_FILE}: {ex}")
        sys.exit(1)

    logging.info(f"{OUTPUT_FILE} written for {action} workflow")


if __name__ == "__main__":
    main()
