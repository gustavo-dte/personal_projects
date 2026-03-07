#!/usr/bin/env python3
"""
build_extra_vars.py
===================
Builds ansible_extra_vars.json from environment variables for the domain join workflow.

Environment variables read:
  MANIFEST_INPUT            Manifest directory name (required)
  DRY_RUN_INPUT             'true' / '1' / 'yes' → True (required)
  FORCE_REJOIN_INPUT        'true' / '1' / 'yes' → True (required)
  DOMAIN_ADMIN_VALUE_INPUT  Domain admin password (required, never logged)
  DOMAIN_OU_PATH_INPUT      Domain OU path (optional)

Output:
  ansible_extra_vars.json   Written to cwd with mode 0o600.

Exits 0 on success, 1 on any error.
"""

from __future__ import annotations

import json
import logging
import os
import sys
from pathlib import Path
from typing import Any

OUTPUT_FILE = "ansible_extra_vars.json"
REQUIRED_VARS = (
    "MANIFEST_INPUT",
    "DRY_RUN_INPUT",
    "FORCE_REJOIN_INPUT",
    "DOMAIN_ADMIN_VALUE_INPUT",
)

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)


def _env(name: str) -> str:
    return (os.getenv(name) or "").strip()


def _to_bool(value: str) -> bool:
    return value.strip().lower() in ("true", "1", "yes")


def _validate_env() -> None:
    missing = [v for v in REQUIRED_VARS if not _env(v)]
    if missing:
        log.error("[ERROR] Missing required environment variables: %s", ", ".join(missing))
        sys.exit(1)


def _build() -> dict[str, Any]:
    return {
        "manifest": _env("MANIFEST_INPUT"),
        "dry_run": _to_bool(_env("DRY_RUN_INPUT")),
        "force_rejoin": _to_bool(_env("FORCE_REJOIN_INPUT")),
        "domain_admin_value": _env("DOMAIN_ADMIN_VALUE_INPUT"),  # written to file, never logged
        "domain_ou_path": _env("DOMAIN_OU_PATH_INPUT"),
    }


def _write(data: dict[str, Any]) -> None:
    path = Path(OUTPUT_FILE)
    path.write_text(json.dumps(data), encoding="utf-8")
    path.chmod(0o600)
    log.info("[OK] %s written (mode 0600)", OUTPUT_FILE)


def main() -> None:
    _validate_env()
    data = _build()
    _write(data)
    log.info("[SUCCESS] ansible_extra_vars.json built — manifest=%s dry_run=%s force_rejoin=%s",
             data["manifest"], data["dry_run"], data["force_rejoin"])


if __name__ == "__main__":
    main()
