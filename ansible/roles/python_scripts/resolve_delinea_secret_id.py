#!/usr/bin/env python3
# TODO: pending to do unitest.
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
import re
import sys
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import requests
from requests.exceptions import HTTPError, RequestException

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Custom exceptions
# ---------------------------------------------------------------------------


class DelineaError(Exception):
    """Raised for recoverable Delinea API or resolution errors."""


class ConfigurationError(Exception):
    """Raised when required environment configuration is missing or invalid."""


# ---------------------------------------------------------------------------
# Environment helpers
# ---------------------------------------------------------------------------


def _env(var: str) -> str:
    """Return a stripped environment variable value, defaulting to empty string."""
    return (os.getenv(var) or "").strip()


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Config:
    base_url: str
    username: str
    password: str
    search_text: str
    machine_filter: str
    secret_name_filter: str
    account_filter: str
    github_env: Optional[str]

    @classmethod
    def from_env(cls) -> "Config":
        """Build and validate a Config from environment variables.

        Returns:
            A fully validated, frozen Config instance.

        Raises:
            ConfigurationError: If required variables are missing or the
                combination of inputs is logically inconsistent.
        """
        base_url = _env("DELINEA_BASE_URL").rstrip("/")
        username = _env("DELINEA_USERNAME")
        password = _env("DELINEA_PASSWORD")

        if not all([base_url, username, password]):
            raise ConfigurationError(
                "Missing Delinea credentials — set DELINEA_BASE_URL, "
                "DELINEA_USERNAME, and DELINEA_PASSWORD"
            )

        search_text = _env("DELINEA_SECRET_PATH")
        machine_filter = _env("DELINEA_SECRET_MACHINE").lower()

        if not search_text and not machine_filter:
            raise ConfigurationError(
                "No search criteria — set DELINEA_SECRET_PATH or DELINEA_SECRET_MACHINE"
            )

        return cls(
            base_url=base_url,
            username=username,
            password=password,
            search_text=search_text,
            machine_filter=machine_filter,
            secret_name_filter=_env("DELINEA_SECRET_NAME").lower(),
            account_filter=_env("DELINEA_SECRET_ACCOUNT").lower(),
            # os.getenv used directly here — _env() returns "" for unset vars,
            # but github_env must be None (not "") when absent so callers can
            # distinguish "not in Actions" from "set to empty string".
            github_env=os.getenv("GITHUB_ENV"),
        )


# ---------------------------------------------------------------------------
# GitHub Actions environment export
# ---------------------------------------------------------------------------


def _write_github_env(
    github_env: Optional[str], key: str, sanitized_value: str
) -> None:
    """Export a sanitized non-sensitive value to the GitHub Actions environment file.

    When github_env is None (script is running outside of Actions), logs a
    warning and returns without error so local runs stay non-fatal.

    Args:
        github_env:       Path to the GITHUB_ENV file, or None if not in Actions.
        key:              Environment variable name to export.
        sanitized_value:  Validated numeric ID — not secret content.

    Raises:
        OSError: If the GITHUB_ENV file cannot be written.
    """
    if not github_env:
        log.warning("GITHUB_ENV not set — skipping environment variable export")
        return

    # codeql[py/clear-text-storage-sensitive-data] - sanitized_value is a validated
    # numeric identifier (not credentials), produced by _sanitize_secret_id().
    with open(github_env, "a", encoding="utf-8") as fh:  # noqa: SIM115
        fh.write("%s=%s\n" % (key, sanitized_value))


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------


def _sanitize_secret_id(value: str) -> str:
    """Validate and return a Delinea secret ID as a pure numeric string.

    Rejects anything that is not a non-empty sequence of digits, establishing
    an explicit sanitization boundary so security scanners can confirm that only
    opaque identifiers — never credential values — reach GITHUB_ENV.

    Args:
        value: Raw string representation of the secret ID from the API.

    Returns:
        The same digits-only string, safe to store in GITHUB_ENV.

    Raises:
        ValueError: If value contains non-numeric characters or is empty.
    """
    stripped = (value or "").strip()
    if not re.fullmatch(r"\d+", stripped):
        raise ValueError(
            "Unexpected secret ID format — expected numeric identifier, "
            "got: '%s'" % stripped[:20]
        )
    return stripped


# ---------------------------------------------------------------------------
# Delinea API client
# ---------------------------------------------------------------------------


def _acquire_token(base_url: str, username: str, password: str) -> str:
    """Authenticate against Delinea and return a bearer token.

    Args:
        base_url: Base URL of the Delinea Secret Server instance.
        username: Service account username.
        password: Service account password.

    Returns:
        Bearer token string.

    Raises:
        DelineaError: On any network, HTTP, or missing-token failure.
    """
    try:
        resp = requests.post(
            "%s/oauth2/token" % base_url,
            data={"grant_type": "password", "username": username, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=30,
        )
        resp.raise_for_status()
    except HTTPError as ex:
        raise DelineaError(
            "Delinea authentication failed (HTTP %s)" % ex.response.status_code
        ) from ex
    except RequestException as ex:
        raise DelineaError("Delinea authentication request failed: %s" % ex) from ex

    token: Optional[str] = resp.json().get("access_token")
    if not token:
        raise DelineaError("No access_token in Delinea authentication response")

    return token


def _search_secrets(
    base_url: str, auth: Dict[str, str], seed: str
) -> List[Dict[str, Any]]:
    """Search Delinea for secrets matching seed.

    Args:
        base_url: Base URL of the Delinea Secret Server instance.
        auth:     Authorization header dict containing the bearer token.
        seed:     Search term passed to the Delinea API.

    Returns:
        List of secret record dicts returned by the API (may be empty).

    Raises:
        DelineaError: On any network or HTTP failure.
    """
    try:
        resp = requests.get(
            "%s/api/v1/secrets" % base_url,
            params={"filter.includeRestricted": "true", "filter.searchtext": seed},
            headers=auth,
            timeout=30,
        )
        resp.raise_for_status()
    except HTTPError as ex:
        raise DelineaError(
            "Secret search failed (HTTP %s)" % ex.response.status_code
        ) from ex
    except RequestException as ex:
        raise DelineaError("Secret search request failed: %s" % ex) from ex

    records: List[Dict[str, Any]] = resp.json().get("records") or []
    return records


def _fetch_detail(
    base_url: str, auth: Dict[str, str], secret_id: int
) -> Dict[str, Any]:
    """Fetch full detail for a single secret by numeric ID.

    Args:
        base_url:  Base URL of the Delinea Secret Server instance.
        auth:      Authorization header dict containing the bearer token.
        secret_id: Numeric Delinea secret ID.

    Returns:
        Full secret detail dict as returned by the API.

    Raises:
        DelineaError: On any network or HTTP failure.
    """
    try:
        resp = requests.get(
            "%s/api/v1/secrets/%s" % (base_url, secret_id),
            headers=auth,
            timeout=30,
        )
        resp.raise_for_status()
    except HTTPError as ex:
        raise DelineaError(
            "Failed to fetch secret %s (HTTP %s)" % (secret_id, ex.response.status_code)
        ) from ex
    except RequestException as ex:
        raise DelineaError("Failed to fetch secret %s: %s" % (secret_id, ex)) from ex

    result: Dict[str, Any] = resp.json()
    return result


# ---------------------------------------------------------------------------
# Matching helpers
# ---------------------------------------------------------------------------


def _item_val(items: List[Dict[str, Any]], *slugs: str) -> str:
    """Return the lowercased itemValue for the first item whose slug matches any of *slugs*.

    Returns an empty string when no slug matches, so callers can use simple
    equality checks without None guards.
    """
    wanted = {s.lower() for s in slugs}
    for item in items:
        if str(item.get("slug", "")).strip().lower() in wanted:
            return str(item.get("itemValue", "")).strip().lower()
    return ""


def _matches_by_name(name: str, machine_filter: str, desired_name: str) -> bool:
    """Return True when a secret name in 'fqdn\\account' format matches both filters."""
    if "\\" not in name:
        return False
    fqdn, acct = name.split("\\", 1)
    return (
        fqdn.strip().lower() == machine_filter and acct.strip().lower() == desired_name
    )


def _matches_by_items(
    items: List[Dict[str, Any]], machine_filter: str, desired_name: str
) -> bool:
    """Return True when item slugs satisfy both the machine and account/name filters."""
    machine_val = _item_val(items, "machine", "host", "hostname", "fqdn", "server")
    account_val = _item_val(items, "username", "user", "account", "login")
    return machine_val == machine_filter and account_val == desired_name


# ---------------------------------------------------------------------------
# Resolution strategies
# ---------------------------------------------------------------------------


def _resolve_by_exact_name(
    records: List[Dict[str, Any]], search_text: str
) -> Optional[str]:
    """Return the secret ID when a record name exactly matches search_text.

    This is the fast path — no extra API calls are required.

    Args:
        records:     List of secret record dicts from the Delinea search API.
        search_text: The exact name to match against (comparison is case-insensitive).

    Returns:
        Sanitized numeric ID string, or None if no exact match exists.

    Raises:
        ValueError: If the matched record's ID fails sanitization.
    """
    needle = search_text.lower()
    match = next(
        (r for r in records if str(r.get("name", "")).strip().lower() == needle),
        None,
    )
    if match and match.get("id"):
        return _sanitize_secret_id(str(match["id"]))
    return None


def _resolve_by_machine(
    base_url: str,
    auth: Dict[str, str],
    records: List[Dict[str, Any]],
    machine_filter: str,
    secret_name_filter: str,
    account_filter: str,
) -> str:
    """Filter records by machine FQDN and account/name, fetching full details when needed.

    Attempts the fast path (name in 'fqdn\\account' format) first for each
    record, then falls back to inspecting item slugs via the detail endpoint.

    Args:
        base_url:           Base URL of the Delinea Secret Server instance.
        auth:               Authorization header dict containing the bearer token.
        records:            List of secret record dicts from the Delinea search API.
        machine_filter:     Lowercased machine FQDN to match against.
        secret_name_filter: Lowercased secret name filter (preferred over account_filter).
        account_filter:     Lowercased account name filter (fallback when name filter absent).

    Returns:
        Sanitized numeric secret ID string.

    Raises:
        ConfigurationError: If neither secret_name_filter nor account_filter is set.
        DelineaError:       If no match is found or the match is ambiguous.
        ValueError:         If the matched ID fails sanitization.
    """
    if not secret_name_filter and not account_filter:
        raise ConfigurationError(
            "DELINEA_SECRET_MACHINE requires DELINEA_SECRET_NAME or DELINEA_SECRET_ACCOUNT"
        )

    desired_name = secret_name_filter or account_filter
    matches: List[Dict[str, Any]] = []

    for rec in records:
        name = str(rec.get("name") or "").strip()

        # Fast path: name already encodes machine and account as 'fqdn\account'.
        if _matches_by_name(name, machine_filter, desired_name):
            matches.append(rec)
            continue

        # Slow path: inspect item slugs from the full secret detail.
        # Only attempted when the name is not in 'fqdn\account' format.
        sid: Optional[int] = rec.get("id")
        if not sid:
            continue

        try:
            detail = _fetch_detail(base_url, auth, sid)
        except DelineaError as ex:
            log.warning("Skipping secret — could not fetch details: %s", ex)
            continue

        items: List[Dict[str, Any]] = detail.get("items") or []
        if _matches_by_items(items, machine_filter, desired_name):
            matches.append(rec)

    if not matches:
        raise DelineaError(
            "No matching records found — verify DELINEA_SECRET_MACHINE and filter values"
        )

    if len(matches) > 1:
        raise DelineaError(
            "Ambiguous match — %d records found; set DELINEA_SECRET_ID explicitly"
            % len(matches)
        )

    return _sanitize_secret_id(str(matches[0]["id"]))


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------


def resolve(cfg: Config) -> str:
    """Resolve and return the sanitized Delinea secret ID for the given config.

    Tries resolution strategies in order, returning as soon as one succeeds.

    Args:
        cfg: Fully validated configuration built from environment variables.

    Returns:
        Sanitized numeric secret ID string.

    Raises:
        DelineaError:       On API or resolution failures.
        ConfigurationError: On invalid input combinations detected at resolution time.
        ValueError:         If the resolved ID fails sanitization.
    """
    token = _acquire_token(cfg.base_url, cfg.username, cfg.password)
    auth: Dict[str, str] = {"Authorization": "Bearer %s" % token}

    # Use the machine FQDN as the search seed when available — it gives tighter results.
    seed = cfg.machine_filter or cfg.search_text
    records = _search_secrets(cfg.base_url, auth, seed)

    if not records:
        raise DelineaError('No records returned for search term "%s"' % seed)

    # Strategy 1: exact name match — fastest, no extra API calls.
    if cfg.search_text:
        secret_id = _resolve_by_exact_name(records, cfg.search_text)
        if secret_id:
            log.info("Resolved DELINEA_SECRET_ID via exact name match")
            return secret_id

    # Strategy 2: machine + account/name filtering.
    if cfg.machine_filter:
        secret_id = _resolve_by_machine(
            cfg.base_url,
            auth,
            records,
            cfg.machine_filter,
            cfg.secret_name_filter,
            cfg.account_filter,
        )
        log.info("Resolved DELINEA_SECRET_ID via machine filter")
        return secret_id

    raise DelineaError(
        "No exact name match found and DELINEA_SECRET_MACHINE is not set"
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    try:
        cfg = Config.from_env()
        secret_id = resolve(cfg)
        _write_github_env(cfg.github_env, "DELINEA_SECRET_ID", secret_id)
    except ConfigurationError as ex:
        log.error("Configuration error: %s", ex)
        sys.exit(1)
    except DelineaError as ex:
        log.error("Delinea resolution failed: %s", ex)
        sys.exit(1)
    except ValueError as ex:
        log.error("Secret ID validation failed: %s", ex)
        sys.exit(1)
    except OSError as ex:
        log.error("Failed to write to GITHUB_ENV: %s", ex)
        sys.exit(1)


if __name__ == "__main__":
    main()
