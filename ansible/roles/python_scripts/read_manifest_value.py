#!/usr/bin/env python3
"""
read_manifest_value.py
======================
Reads a single top-level key from a manifest YAML and prints it to stdout.
Designed for use in GitHub Actions workflow steps to extract manifest values
without embedding Python inline.

Environment variables read:
  MANIFEST      Manifest directory name under ansible/vars/
  MANIFEST_KEY  Top-level key to read from the manifest (e.g. target_subscription_id)

Exits with code 0 and prints the value on success.
Exits with code 1 if MANIFEST or MANIFEST_KEY are unset, manifest not found,
or the key is missing or empty.

Usage:
  MANIFEST=domain_join_test MANIFEST_KEY=target_subscription_id \\
    python3 ansible/roles/python_scripts/read_manifest_value.py
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("[ERROR] PyYAML is required. Install: pip install PyYAML")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    """Entry point: read one manifest key and print its value to stdout."""
    manifest_name = os.environ.get("MANIFEST", "").strip()
    manifest_key = os.environ.get("MANIFEST_KEY", "").strip()

    if not manifest_name:
        log.error("[ERROR] MANIFEST environment variable is not set")
        sys.exit(1)

    if not manifest_key:
        log.error("[ERROR] MANIFEST_KEY environment variable is not set")
        sys.exit(1)

    path = Path("ansible/vars") / manifest_name / "manifest.yml"
    if not path.exists():
        log.error("[ERROR] Manifest not found: %s", path)
        sys.exit(1)

    with open(path, encoding="utf-8") as fh:
        manifest = yaml.safe_load(fh) or {}

    value = manifest.get(manifest_key, "")
    if not value:
        log.error(
            "[ERROR] Key '%s' not found or empty in manifest '%s'",
            manifest_key,
            manifest_name,
        )
        sys.exit(1)

    # Print only the value so shell callers can capture it directly:
    #   SUB_ID=$(MANIFEST=x MANIFEST_KEY=y python3 read_manifest_value.py)
    print(str(value).strip())


if __name__ == "__main__":
    main()
