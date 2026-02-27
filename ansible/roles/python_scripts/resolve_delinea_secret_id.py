#!/usr/bin/env python3
"""
resolve_delinea_secret_id.py
============================
Resolves the numeric Delinea Secret Server secret ID for the SE-Admin account
and writes it to GITHUB_ENV so subsequent workflow steps can use it.

Exits with code 1 on:
  - Missing Delinea credentials
  - Neither DELINEA_SECRET_PATH nor DELINEA_SECRET_MACHINE is set
  - DELINEA_SECRET_MACHINE set without DELINEA_SECRET_NAME or DELINEA_SECRET_ACCOUNT
  - No records returned by the Delinea API
  - No secret matched the applied filters
  - Multiple secrets matched and cannot be disambiguated

Exits with code 0 on:
  - Secret ID successfully resolved and written to GITHUB_ENV

Resolution strategy (in order):
  1. Exact name match against DELINEA_SECRET_PATH
  2. Machine-based filtering using DELINEA_SECRET_MACHINE + NAME/ACCOUNT

Environment variables read:
  DELINEA_BASE_URL        Base URL of the Delinea Secret Server instance
  DELINEA_USERNAME        Service account used to authenticate
  DELINEA_PASSWORD        Password for the service account
  DELINEA_SECRET_PATH     Name / path search term (used as search seed and exact-match target)
  DELINEA_SECRET_MACHINE  (Optional) Machine FQDN to narrow matching
  DELINEA_SECRET_NAME     (Optional) Secret name filter (preferred over ACCOUNT)
  DELINEA_SECRET_ACCOUNT  (Optional) Account name filter (fallback if NAME not set)
  GITHUB_ENV              Path to the GitHub Actions env file (set automatically by the runner)

Usage:
  python3 ansible/roles/python_scripts/resolve_delinea_secret_id.py
"""

import logging
import os
import sys
from typing import Any, Dict, List, Optional

import requests

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(level=logging.INFO, format="%(message)s")

# ---------------------------------------------------------------------------
# Helpers — environment
# ---------------------------------------------------------------------------


def _env(var: str) -> str:
    """Return a stripped environment variable value, defaulting to empty string."""
    return (os.getenv(var) or "").strip()


def _write_github_env(github_env: Optional[str], key: str, value: str) -> None:
    """Mask a value and export it to the GitHub Actions environment file."""
    sys.stdout.write(f"::add-mask::{value}\n")
    sys.stdout.flush()

    if not github_env:
        logging.warning("GITHUB_ENV not set — skipping environment variable export")
        return

    try:
        with open(github_env, "a", encoding="utf-8") as fh:  # lgtm[py/clear-text-storage-sensitive-data]
            fh.write(f"{key}={value}\n")
    except OSError as ex:
        logging.error(f"Failed to write to GITHUB_ENV: {ex}")
        sys.exit(1)


# ---------------------------------------------------------------------------
# Helpers — Delinea API
# ---------------------------------------------------------------------------


def _acquire_token(base_url: str, username: str, password: str) -> str:
    """Authenticate against Delinea and return a bearer token. Exits with code 1 on failure."""
    try:
        resp = requests.post(
            f"{base_url}/oauth2/token",
            data={"grant_type": "password", "username": username, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=30,
        )
        resp.raise_for_status()
        token: Optional[str] = resp.json().get("access_token")
    except Exception as ex:
        logging.error(f"Could not acquire Delinea token: {ex}")
        sys.exit(1)

    if not token:
        logging.error("No access token returned by Delinea")
        sys.exit(1)

    return token


def _search_secrets(base_url: str, auth: Dict[str, str], seed: str) -> List[Dict[str, Any]]:
    """Search Delinea for secrets matching the given seed term. Exits with code 1 on failure."""
    try:
        resp = requests.get(
            f"{base_url}/api/v1/secrets",
            params={"filter.includeRestricted": "true", "filter.searchtext": seed},
            headers=auth,
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json().get("records") or []
    except Exception as ex:
        logging.error(f"Secret search failed: {ex}")
        sys.exit(1)


def _fetch_detail(base_url: str, auth: Dict[str, str], secret_id: int) -> Dict[str, Any]:
    """Fetch full detail for a single secret by ID. Exits with code 1 on failure."""
    try:
        resp = requests.get(
            f"{base_url}/api/v1/secrets/{secret_id}",
            headers=auth,
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as ex:
        logging.error(f"Failed to fetch detail for secret ID {secret_id}: {ex}")
        sys.exit(1)


def _item_val(items: List[Dict[str, Any]], *slugs: str) -> str:
    """Return the lowercased itemValue for the first slug that matches any item."""
    wanted = {s.lower() for s in slugs}
    for item in items:
        if str(item.get("slug", "")).strip().lower() in wanted:
            return str(item.get("itemValue", "")).strip().lower()
    return ""


# ---------------------------------------------------------------------------
# Helpers — matching logic
# ---------------------------------------------------------------------------


def _resolve_by_machine(
    base_url: str,
    auth: Dict[str, str],
    records: List[Dict[str, Any]],
    machine_filter: str,
    secret_name_filter: str,
    account_filter: str,
) -> str:
    """
    Filter records by machine FQDN and account/name, fetching full details when needed.
    Returns the matched secret ID. Exits with code 1 when no match or ambiguous match.
    """
    if not secret_name_filter and not account_filter:
        logging.error(
            "DELINEA_SECRET_MACHINE requires DELINEA_SECRET_NAME or DELINEA_SECRET_ACCOUNT"
        )
        sys.exit(1)

    desired_name = secret_name_filter or account_filter
    matches: List[Dict[str, Any]] = []

    for rec in records:
        name = str(rec.get("name") or "").strip()

        # Fast path: name is in "fqdn\account" format
        if "\\" in name:
            fqdn, acct = name.split("\\", 1)
            if fqdn.strip().lower() == machine_filter and acct.strip().lower() == desired_name:
                matches.append(rec)
                continue

        # Slow path: inspect item slugs from the full secret detail
        secret_id: Optional[int] = rec.get("id")
        if account_filter and secret_id:
            detail = _fetch_detail(base_url, auth, secret_id)
            items: List[Dict[str, Any]] = detail.get("items") or []
            if (
                _item_val(items, "machine", "host", "hostname", "fqdn", "server") == machine_filter
                and _item_val(items, "username", "user", "account", "login") == account_filter
            ):
                matches.append(rec)

    if not matches:
        logging.error("No matching records found — verify DELINEA_SECRET_MACHINE and filter values")
        sys.exit(1)

    if len(matches) > 1:
        logging.error(f"Ambiguous match — {len(matches)} records found; set DELINEA_SECRET_ID explicitly")
        sys.exit(1)

    return str(matches[0]["id"])


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    base_url = _env("DELINEA_BASE_URL").rstrip("/")
    username = _env("DELINEA_USERNAME")
    password = _env("DELINEA_PASSWORD")
    search_text = _env("DELINEA_SECRET_PATH")
    machine_filter = _env("DELINEA_SECRET_MACHINE").lower()
    secret_name_filter = _env("DELINEA_SECRET_NAME").lower()
    account_filter = _env("DELINEA_SECRET_ACCOUNT").lower()
    github_env: Optional[str] = os.getenv("GITHUB_ENV")

    if not all([base_url, username, password]):
        logging.error("Missing Delinea credentials — set DELINEA_BASE_URL, DELINEA_USERNAME, DELINEA_PASSWORD")
        sys.exit(1)

    if not search_text and not machine_filter:
        logging.error("No search criteria — set DELINEA_SECRET_PATH or DELINEA_SECRET_MACHINE")
        sys.exit(1)

    token = _acquire_token(base_url, username, password)
    auth: Dict[str, str] = {"Authorization": f"Bearer {token}"}

    # Use machine FQDN as search seed when available; it gives tighter results
    seed = machine_filter or search_text
    records = _search_secrets(base_url, auth, seed)

    if not records:
        logging.error(f'No records returned for search term "{seed}"')
        sys.exit(1)

    # Strategy 1: exact name match (fastest, no extra API calls)
    search_text_lower = search_text.lower()
    exact = next(
        (r for r in records if str(r.get("name", "")).strip().lower() == search_text_lower),
        None,
    )
    if exact and exact.get("id"):
        logging.info("Resolved DELINEA_SECRET_ID via exact name match")
        _write_github_env(github_env, "DELINEA_SECRET_ID", str(exact["id"]))
        return

    # Strategy 2: machine-based filtering
    if machine_filter:
        secret_id = _resolve_by_machine(
            base_url, auth, records, machine_filter, secret_name_filter, account_filter
        )
        logging.info("Resolved DELINEA_SECRET_ID via machine filter")
        _write_github_env(github_env, "DELINEA_SECRET_ID", secret_id)
        return

    logging.error("No exact name match found and DELINEA_SECRET_MACHINE is not set")
    sys.exit(1)


if __name__ == "__main__":
    main()
