#!/usr/bin/env python3
"""
build_extra_vars.py
===================
Builds ansible_extra_vars.json from environment variables for the domain join workflow.

Reads workflow inputs and secrets from environment variables and writes them
to a JSON file that is passed to the ansible-playbook command via -e @ansible_extra_vars.json.

Environment variables read:
  MANIFEST_INPUT            Manifest directory name (required)
  DRY_RUN_INPUT             Dry run flag: 'true', '1', 'yes' → boolean (required)
  FORCE_REJOIN_INPUT        Force rejoin flag: 'true', '1', 'yes' → boolean (required)
  DOMAIN_ADMIN_VALUE_INPUT  Domain admin password from GitHub secret (required)
  DOMAIN_OU_PATH_INPUT      Domain OU path from GitHub secret (optional, can be empty)

Output:
  ansible_extra_vars.json   Written to current working directory (mode 0o600)

Exits with code 0 on success.
Exits with code 1 on missing required variables or JSON validation failure.

Usage:
  export MANIFEST_INPUT="domain_join_test"
  export DRY_RUN_INPUT="false"
  export FORCE_REJOIN_INPUT="true"
  export DOMAIN_ADMIN_VALUE_INPUT="P@ssw0rd!"
  export DOMAIN_OU_PATH_INPUT="OU=Computers,DC=dtenet,DC=com"
  python3 ansible/roles/python_scripts/build_extra_vars.py
"""

from __future__ import annotations

import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

OUTPUT_FILE = "ansible_extra_vars.json"
REQUIRED_VARS = ("MANIFEST_INPUT", "DRY_RUN_INPUT", "FORCE_REJOIN_INPUT", "DOMAIN_ADMIN_VALUE_INPUT")

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


def str_to_bool(value: str) -> bool:
    """Convert string to boolean. 'true', '1', 'yes' → True (case-insensitive)."""
    return str(value).strip().lower() in ("true", "1", "yes")


def validate_required_vars() -> None:
    """Check that all required environment variables are set."""
    missing = [var for var in REQUIRED_VARS if not os.environ.get(var, "").strip()]
    if missing:
        log.error(f"Missing required environment variables: {', '.join(missing)}")
        sys.exit(1)


def build_extra_vars() -> Dict[str, Any]:
    """Build the extra_vars dictionary from environment variables."""
    validate_required_vars()

    extra_vars = {
        "manifest": os.environ["MANIFEST_INPUT"].strip(),
        "dry_run": str_to_bool(os.environ["DRY_RUN_INPUT"]),
        "force_rejoin": str_to_bool(os.environ["FORCE_REJOIN_INPUT"]),
        "domain_admin_value": os.environ["DOMAIN_ADMIN_VALUE_INPUT"],
        "domain_ou_path": os.environ.get("DOMAIN_OU_PATH_INPUT", "").strip(),
    }

    return extra_vars


def write_extra_vars(extra_vars: Dict[str, Any]) -> None:
    """Write extra_vars to JSON file with restricted permissions."""
    output_path = Path(OUTPUT_FILE)

    # Write JSON
    json_str = json.dumps(extra_vars)
    output_path.write_text(json_str, encoding="utf-8")

    # Set permissions to 0o600 (read/write for owner only)
    output_path.chmod(0o600)

    log.info(f"[OK] Written {OUTPUT_FILE}")


def validate_json() -> None:
    """Validate that the output JSON is syntactically correct."""
    try:
        output_path = Path(OUTPUT_FILE)
        json.loads(output_path.read_text(encoding="utf-8"))
        log.info(f"[OK] JSON validation passed")
    except (json.JSONDecodeError, FileNotFoundError) as e:
        log.error(f"[FAIL] JSON validation failed: {e}")
        sys.exit(1)


def main() -> None:
    """Entry point."""
    try:
        extra_vars = build_extra_vars()
        write_extra_vars(extra_vars)
        validate_json()
        log.info("[SUCCESS] ansible_extra_vars.json built successfully")
    except Exception as e:
        log.error(f"[ERROR] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
