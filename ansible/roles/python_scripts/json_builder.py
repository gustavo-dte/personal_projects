#!/usr/bin/env python3
# TODO: pending to do unitest.
"""
json_builder.py
===============
Writes ansible_extra_vars.json for domain join / disjoin workflows.

Usage:
  python3 ansible/roles/python_scripts/json_builder.py join
  python3 ansible/roles/python_scripts/json_builder.py disjoin

Actions:
  join     — Build extra_vars for the join-windows-domain workflow.
             Reads: WORKFLOW_MANIFEST, WORKFLOW_DRY_RUN, WORKFLOW_FORCE_REJOIN,
                    WORKFLOW_SKIP_HOSTNAME_SETUP, SECRET_DOMAIN_ADMIN_PASSWORD,
                    SECRET_DOMAIN_OU_PATH, WORKFLOW_RENAME_USERNAME

  disjoin  — Build extra_vars for the disjoin-windows-domain workflow.
             Reads: WORKFLOW_MANIFEST, WORKFLOW_DRY_RUN, WORKFLOW_RENAME_USERNAME

Output:
  ansible_extra_vars.json — written to the current working directory.

Note:
  The SE-Admin WinRM password is intentionally excluded from both extra_vars.
  It is fetched live from Delinea inside the Ansible playbook pre_tasks so it
  is always current and never cached in the extra-vars file.

  The rename step (change VM hostname) runs as Administrator using the SE-Admin
  Delinea password. WORKFLOW_RENAME_USERNAME defaults to 'Administrator' and
  can be overridden per workflow if the local admin account has a different name.
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
RENAME_USERNAME = "Administrator"
VALID_ACTIONS = ("join", "disjoin")

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Custom exceptions
# ---------------------------------------------------------------------------


class ConfigurationError(Exception):
    """Raised when required environment configuration is missing or invalid."""


# ---------------------------------------------------------------------------
# Environment helpers
# ---------------------------------------------------------------------------


def _env(var: str) -> str:
    """Return a stripped environment variable value, defaulting to empty string."""
    return (os.getenv(var) or "").strip()


def _env_bool(var: str, default: str = "false") -> bool:
    """Read an environment variable and interpret it as a boolean.

    Any value (case-insensitive) equal to 'true' returns True; everything
    else — including unset — returns False, unless default is overridden.
    """
    return (os.getenv(var) or default).strip().lower() == "true"


def _require_env(var: str) -> str:
    """Return the value of a required environment variable.

    Args:
        var: Name of the environment variable.

    Returns:
        Stripped, non-empty value of the variable.

    Raises:
        ConfigurationError: If the variable is unset or empty.
    """
    value = _env(var)
    if not value:
        raise ConfigurationError("%s is not set" % var)
    return value


# ---------------------------------------------------------------------------
# Builders
# ---------------------------------------------------------------------------


def _build_join_vars() -> Dict[str, Any]:
    """Build the extra_vars dictionary for the join workflow.

    Returns:
        Dictionary of extra_vars ready for JSON serialization.

    Raises:
        ConfigurationError: If WORKFLOW_MANIFEST is not set or if
                          SECRET_DOMAIN_ADMIN_PASSWORD is missing in non-dry-run mode.
    """
    dry_run = _env_bool("WORKFLOW_DRY_RUN", default="true")
    domain_admin_password = _env("SECRET_DOMAIN_ADMIN_PASSWORD")
    
    if not domain_admin_password:
        if dry_run:
            log.warning(
                "SECRET_DOMAIN_ADMIN_PASSWORD is not set — domain join will fail at runtime"
            )
        else:
            raise ConfigurationError(
                "SECRET_DOMAIN_ADMIN_PASSWORD is required for production domain join operations"
            )

    return {
        "manifest": _require_env("WORKFLOW_MANIFEST"),
        "dry_run": dry_run,
        "force_rejoin": _env_bool("WORKFLOW_FORCE_REJOIN"),
        "skip_hostname_setup": _env_bool("WORKFLOW_SKIP_HOSTNAME_SETUP"),
        "winrm_username": WINRM_USERNAME,
        "rename_winrm_username": _env("WORKFLOW_RENAME_USERNAME") or RENAME_USERNAME,
        "domain_admin_password": domain_admin_password,
        "domain_ou_path": _env("SECRET_DOMAIN_OU_PATH"),
    }


def _build_disjoin_vars() -> Dict[str, Any]:
    """Build the extra_vars dictionary for the disjoin workflow.

    Returns:
        Dictionary of extra_vars ready for JSON serialization.

    Raises:
        ConfigurationError: If WORKFLOW_MANIFEST is not set.
    """
    return {
        "manifest": _require_env("WORKFLOW_MANIFEST"),
        "dry_run": _env_bool("WORKFLOW_DRY_RUN", default="true"),
        "rename_winrm_username": _env("WORKFLOW_RENAME_USERNAME") or RENAME_USERNAME,
    }


# ---------------------------------------------------------------------------
# Dispatch table
# ---------------------------------------------------------------------------

_BUILDERS: Dict[str, Callable[[], Dict[str, Any]]] = {
    "join": _build_join_vars,
    "disjoin": _build_disjoin_vars,
}


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------


def build_extra_vars(action: str) -> Dict[str, Any]:
    """Return the extra_vars dictionary for the given workflow action.

    Args:
        action: Workflow action — one of 'join' or 'disjoin' (case-insensitive).

    Returns:
        Dictionary of extra_vars ready for JSON serialization.

    Raises:
        ConfigurationError: If action is invalid or required env vars are missing.
    """
    normalized = action.strip().lower()
    if normalized not in _BUILDERS:
        raise ConfigurationError(
            'Invalid action "%s" — must be one of: %s'
            % (action, ", ".join(VALID_ACTIONS))
        )
    return _BUILDERS[normalized]()


def write_extra_vars(extra_vars: Dict[str, Any], output_file: str) -> None:
    """Serialize extra_vars to a JSON file.

    Args:
        extra_vars:  Dictionary to serialize.
        output_file: Destination file path.

    Raises:
        OSError: If the file cannot be created or written.
    """
    with open(output_file, "w", encoding="utf-8") as fh:
        json.dump(extra_vars, fh, indent=2)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    if len(sys.argv) < 2:
        log.error("Usage: %s <join|disjoin>", sys.argv[0])
        sys.exit(1)

    action = sys.argv[1]

    try:
        extra_vars = build_extra_vars(action)
        write_extra_vars(extra_vars, OUTPUT_FILE)
    except ConfigurationError as ex:
        log.error("Configuration error: %s", ex)
        sys.exit(1)
    except OSError as ex:
        log.error("Failed to write to '%s': %s", OUTPUT_FILE, ex)
        sys.exit(1)

    log.info("%s written for %s workflow", OUTPUT_FILE, action.strip().lower())


if __name__ == "__main__":
    main()
