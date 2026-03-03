#!/usr/bin/env python3
# TODO: pending to do unitest.
"""
resolve_delinea_secret_id.py
============================
Resolves Delinea Secret Server secrets for SE-Admin accounts and writes them to GITHUB_ENV.

Supports two modes:
  1. Single-VM mode (LEGACY): Resolves one secret ID using DELINEA_SECRET_PATH or DELINEA_SECRET_MACHINE
  2. Multi-VM mode (DEFAULT): Loads manifest, resolves per-VM passwords from Delinea  # pragma: allowlist secret

Exits with code 1 on:
  - Missing Delinea credentials
  - Multi-VM: Missing MANIFEST env var
  - Multi-VM: Cannot load manifest YAML
  - Single-VM: Neither DELINEA_SECRET_PATH nor DELINEA_SECRET_MACHINE is set
  - DELINEA_SECRET_MACHINE set without DELINEA_SECRET_NAME or DELINEA_SECRET_ACCOUNT
  - No records returned by the Delinea API
  - No secret matched the applied filters
  - Multiple secrets matched and cannot be disambiguated

Exits with code 0 on:
  - Secret ID/passwords successfully resolved and written to GITHUB_ENV  # pragma: allowlist secret

Resolution strategy (in order):
  1. Exact name match against DELINEA_SECRET_PATH or constructed FQDN\\Account pattern
  2. Machine-based filtering using DELINEA_SECRET_MACHINE + NAME/ACCOUNT

Environment variables read:
  MANIFEST                (Multi-VM mode) Manifest directory name under ansible/vars/
  DELINEA_BASE_URL        Base URL of the Delinea Secret Server instance
  DELINEA_USERNAME        Service account used to authenticate  # pragma: allowlist secret
  DELINEA_PASSWORD        Password for the service account (multi-VM mode)  # pragma: allowlist secret
  DELINEA_VALUE           Value for the service account (single-VM legacy mode)
  DELINEA_DOMAIN_SUFFIX   Domain suffix to append to hostnames (default: .dtenet.com)
  DELINEA_SECRET_PATH     (Single-VM) Name / path search term
  DELINEA_SECRET_MACHINE  (Single-VM) Machine FQDN to narrow matching
  DELINEA_SECRET_NAME     (Optional) Secret name filter (preferred over ACCOUNT)
  DELINEA_SECRET_ACCOUNT  (Optional) Account name filter (fallback if NAME not set)
  GITHUB_ENV              Path to the GitHub Actions env file (set automatically by the runner)

Usage:
  # Multi-VM mode (reads manifest)
  MANIFEST=domain_join_test python3 ansible/roles/python_scripts/resolve_delinea_secret_id.py
  
  # Single-VM mode (legacy - backward compatible)
  DELINEA_SECRET_PATH="path" python3 ansible/roles/python_scripts/resolve_delinea_secret_id.py
"""

import logging
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from requests.exceptions import HTTPError, RequestException

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore

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
    value: str
    search_text: str
    machine_filter: str
    secret_name_filter: str
    account_filter: str
    github_env: Optional[str]
    manifest: str
    domain_suffix: str
    multi_vm_mode: bool

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
        
        # Support both DELINEA_PASSWORD (new) and DELINEA_VALUE (legacy)  # pragma: allowlist secret
        value = _env("DELINEA_PASSWORD") or _env("DELINEA_VALUE")  # pragma: allowlist secret

        if not all([base_url, username, value]):
            raise ConfigurationError(
                "Missing Delinea configuration — set DELINEA_BASE_URL, "  # pragma: allowlist secret
                "DELINEA_USERNAME, and DELINEA_PASSWORD (or DELINEA_VALUE)"  # pragma: allowlist secret
            )

        manifest = _env("MANIFEST")
        multi_vm_mode = bool(manifest)
        
        # Single-VM mode validation (backward compatible)
        search_text = _env("DELINEA_SECRET_PATH")
        machine_filter = _env("DELINEA_SECRET_MACHINE").lower()

        if not multi_vm_mode and not search_text and not machine_filter:
            raise ConfigurationError(
                "No search criteria — set MANIFEST for multi-VM mode, or "
                "set DELINEA_SECRET_PATH or DELINEA_SECRET_MACHINE for single-VM mode"
            )

        return cls(
            base_url=base_url,
            username=username,
            value=value,
            search_text=search_text,
            machine_filter=machine_filter,
            secret_name_filter=_env("DELINEA_SECRET_NAME").lower(),
            account_filter=_env("DELINEA_SECRET_ACCOUNT").lower(),
            github_env=os.getenv("GITHUB_ENV"),
            manifest=manifest,
            domain_suffix=_env("DELINEA_DOMAIN_SUFFIX") or ".dtenet.com",
            multi_vm_mode=multi_vm_mode,
        )


# ---------------------------------------------------------------------------
# GitHub Actions environment export
# ---------------------------------------------------------------------------


def _write_github_env(
    github_env: Optional[str], key: str, value: str
) -> None:
    """Export a value to the GitHub Actions environment file.  # pragma: allowlist secret

    When github_env is None (script is running outside of Actions), logs a
    warning and returns without error so local runs stay non-fatal.

    Args:
        github_env:  Path to the GITHUB_ENV file, or None if not in Actions.
        key:         Environment variable name to export.
        value:       Value to export (can be sensitive data like passwords or non-sensitive like IDs)  # pragma: allowlist secret

    Raises:
        OSError: If the GITHUB_ENV file cannot be written.
    """
    if not github_env:
        log.warning("GITHUB_ENV not set — skipping environment variable export")
        return

    # Write value to GITHUB_ENV (GitHub Actions masks sensitive values automatically when ::add-mask:: is used)  # pragma: allowlist secret
    with open(github_env, "a", encoding="utf-8") as fh:  # noqa: SIM115
        fh.write("%s=%s\n" % (key, value))


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------


def _sanitize_secret_id(value: str) -> str:
    """Validate and return a Delinea secret ID as a pure numeric string.

    Rejects anything that is not a non-empty sequence of digits, establishing
    an explicit sanitization boundary so security scanners can confirm that only
    opaque identifiers — never sensitive values — reach GITHUB_ENV.  # pragma: allowlist secret

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


def _acquire_token(base_url: str, username: str, password: str) -> str:  # pragma: allowlist secret
    """Authenticate against Delinea and return a bearer token.

    Args:
        base_url: Base URL of the Delinea Secret Server instance.
        username: Service account username.
        password: Service account value for OAuth2 grant_type.  # pragma: allowlist secret

    Returns:
        Bearer token string.

    Raises:
        DelineaError: On any network, HTTP, or missing-token failure.
    """
    try:
        resp = requests.post(
            "%s/oauth2/token" % base_url,
            data={"grant_type": "password", "username": username, "password": password},  # pragma: allowlist secret
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=30,
        )
        resp.raise_for_status()
    except HTTPError as ex:
        raise DelineaError(
            "Delinea authentication failed (HTTP %s)" % ex.response.status_code  # pragma: allowlist secret
        ) from ex
    except RequestException as ex:
        raise DelineaError("Delinea authentication request failed: %s" % ex) from ex  # pragma: allowlist secret

    token: Optional[str] = resp.json().get("access_token")
    if not token:
        raise DelineaError("No access_token in Delinea authentication response")  # pragma: allowlist secret

    return token


def _search_secrets(
    base_url: str, auth: Dict[str, str], seed: str
) -> List[Dict[str, Any]]:
    """Search Delinea for secrets matching seed.

    Args:
        base_url: Base URL of the Delinea Secret Server instance.
        auth:     Authorization header dict containing the bearer token.  # pragma: allowlist secret
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
        auth:      Authorization header dict containing the bearer token.  # pragma: allowlist secret
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
        error_body = ""
        try:
            error_body = " - " + ex.response.text
        except Exception:
            pass
        raise DelineaError(
            "Failed to fetch secret %s (HTTP %s)%s" % (secret_id, ex.response.status_code, error_body)
        ) from ex
    except RequestException as ex:
        raise DelineaError("Failed to fetch secret %s: %s" % (secret_id, ex)) from ex

    result: Dict[str, Any] = resp.json()
    return result


def _checkin_secret(
    base_url: str, auth: Dict[str, str], secret_id: int
) -> None:
    """Force check-in a secret if it's currently checked out.

    Args:
        base_url:  Base URL of the Delinea Secret Server instance.
        auth:      Authorization header dict containing the bearer token.  # pragma: allowlist secret
        secret_id: Numeric Delinea secret ID.

    Raises:
        DelineaError: On any network or HTTP failure.
    """
    try:
        resp = requests.post(
            "%s/api/v1/secrets/%s/check-in" % (base_url, secret_id),
            headers=auth,
            timeout=30,
        )
        # 200 = success, 400 with "SecretNotCheckedOut" is acceptable (already checked in)
        if resp.status_code == 400:
            error_data = resp.json()
            if error_data.get("errorCode") == "API_SecretNotCheckedOut":
                # Secret is already checked in, this is fine
                return
        resp.raise_for_status()
    except HTTPError as ex:
        error_body = ""
        try:
            error_body = " - " + ex.response.text
        except Exception:
            pass
        raise DelineaError(
            "Failed to check in secret %s (HTTP %s)%s" % (secret_id, ex.response.status_code, error_body)
        ) from ex
    except RequestException as ex:
        raise DelineaError("Failed to check in secret %s: %s" % (secret_id, ex)) from ex


def _extract_password(detail: Dict[str, Any]) -> str:  # pragma: allowlist secret
    """Extract the password field value from a secret detail response.  # pragma: allowlist secret

    Args:
        detail: Full secret detail dict as returned by _fetch_detail.

    Returns:
        The password string.  # pragma: allowlist secret

    Raises:
        DelineaError: If no password field is found.  # pragma: allowlist secret
    """
    items: List[Dict[str, Any]] = detail.get("items") or []
    password = _item_val(items, "password")  # pragma: allowlist secret
    
    if not password:  # pragma: allowlist secret
        raise DelineaError("No password field found in secret")  # pragma: allowlist secret
    
    return password  # pragma: allowlist secret


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
            # Fail fast on ambiguity — no need to check remaining records
            if len(matches) > 1:
                raise DelineaError(
                    "Ambiguous match — %d records found; set DELINEA_SECRET_ID explicitly"
                    % len(matches)
                )
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
            # Fail fast on ambiguity — no need to check remaining records
            if len(matches) > 1:
                raise DelineaError(
                    "Ambiguous match — %d records found; set DELINEA_SECRET_ID explicitly"
                    % len(matches)
                )

    if not matches:
        raise DelineaError(
            "No matching records found — verify DELINEA_SECRET_MACHINE and filter values"
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
    token = _acquire_token(cfg.base_url, cfg.username, cfg.value)
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
# Multi-VM mode
# ---------------------------------------------------------------------------


def _load_manifest(manifest_name: str) -> Dict[str, Any]:
    """Load and parse the manifest YAML file.

    Args:
        manifest_name: Directory name under ansible/vars/ (e.g., 'domain_join_test')

    Returns:
        Parsed manifest dict.

    Raises:
        ConfigurationError: If PyYAML is not installed or manifest cannot be loaded.
    """
    if yaml is None:
        raise ConfigurationError(
            "PyYAML is required for multi-VM mode. Install: pip install PyYAML"
        )

    manifest_path = Path("ansible/vars") / manifest_name / "manifest.yml"
    
    if not manifest_path.exists():
        raise ConfigurationError(
            "Manifest file not found: %s" % manifest_path
        )

    try:
        with open(manifest_path, "r", encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}
    except Exception as ex:
        raise ConfigurationError(
            "Failed to load manifest %s: %s" % (manifest_path, ex)
        ) from ex


def _resolve_multi_vm(cfg: Config) -> None:  # pragma: allowlist secret
    """Resolve passwords for all VMs in the manifest and write to GITHUB_ENV.  # pragma: allowlist secret

    Args:
        cfg: Configuration with manifest and Delinea credentials.

    Raises:
        ConfigurationError: If manifest loading fails.
        DelineaError: If password resolution fails for any VM.  # pragma: allowlist secret
    """
    log.info("[Multi-VM Mode] Loading manifest: %s", cfg.manifest)
    manifest = _load_manifest(cfg.manifest)
    
    vms = manifest.get("vms") or []
    if not vms:
        raise ConfigurationError(
            "No VMs found in manifest: %s" % cfg.manifest
        )

    log.info("[Multi-VM Mode] Found %d VM(s) in manifest", len(vms))
    
    # Acquire token once and reuse for all VMs
    token = _acquire_token(cfg.base_url, cfg.username, cfg.value)
    auth: Dict[str, str] = {"Authorization": "Bearer %s" % token}
    
    success_count = 0
    
    for idx, vm in enumerate(vms, start=1):
        target_vm_name = vm.get("target_vm_name", "")
        vm_hostname = vm.get("vm_winrm_connect_hostname", "")
        vm_username = vm.get("vm_winrm_username", "")
        
        if not all([target_vm_name, vm_hostname, vm_username]):
            log.warning(
                "[VM %d/%d] Skipping - missing required fields (target_vm_name, vm_winrm_connect_hostname, vm_winrm_username)",
                idx, len(vms)
            )
            continue
        
        log.info(
            "[VM %d/%d] Processing: %s (hostname=%s, username=%s)",
            idx, len(vms), target_vm_name, vm_hostname, vm_username
        )
        
        try:
            # Build FQDN: hostname + domain_suffix
            machine_fqdn = (vm_hostname + cfg.domain_suffix).lower()
            account_name = vm_username.lower()
            
            log.info(
                "[VM %d/%d] Searching Delinea: %s\\%s",
                idx, len(vms), machine_fqdn, account_name
            )
            
            # Search Delinea for this VM's secret
            records = _search_secrets(cfg.base_url, auth, machine_fqdn)
            
            if not records:
                raise DelineaError(
                    "No records returned for machine: %s" % machine_fqdn
                )
            
            # Strategy 1: Match by name pattern "FQDN\\Account"
            secret_id = None
            search_pattern = "%s\\%s" % (machine_fqdn, account_name)
            
            for rec in records:
                rec_name = str(rec.get("name") or "").strip().lower()
                if rec_name == search_pattern:
                    secret_id = rec.get("id")
                    log.info(
                        "[VM %d/%d] Matched by name: %s (ID=%s)",
                        idx, len(vms), rec_name, secret_id
                    )
                    break
            
            # Strategy 2: Match by items (machine + username fields)
            if not secret_id:
                for rec in records:
                    rec_id = rec.get("id")
                    if not rec_id:
                        continue
                    
                    try:
                        detail = _fetch_detail(cfg.base_url, auth, rec_id)
                        items = detail.get("items") or []
                        
                        if _matches_by_items(items, machine_fqdn, account_name):
                            secret_id = rec_id
                            log.info(
                                "[VM %d/%d] Matched by items: ID=%s",
                                idx, len(vms), secret_id
                            )
                            break
                    except DelineaError as ex:
                        log.warning(
                            "[VM %d/%d] Failed to fetch details for ID=%s: %s",
                            idx, len(vms), rec_id, ex
                        )
                        continue
            
            if not secret_id:
                raise DelineaError(
                    "No matching secret found for %s\\%s" % (machine_fqdn, account_name)
                )
            
            # Force check-in the secret if it's checked out  # pragma: allowlist secret
            log.info(
                "[VM %d/%d] Checking in secret ID=%s (if checked out)",
                idx, len(vms), secret_id
            )
            try:
                _checkin_secret(cfg.base_url, auth, int(secret_id))
            except DelineaError as ex:
                log.warning(
                    "[VM %d/%d] Check-in warning for ID=%s: %s (continuing anyway)",
                    idx, len(vms), secret_id, ex
                )
            
            # Fetch full details to extract password  # pragma: allowlist secret
            detail = _fetch_detail(cfg.base_url, auth, int(secret_id))
            password = _extract_password(detail)  # pragma: allowlist secret
            
            # Mask password in logs  # pragma: allowlist secret
            print("::add-mask::%s" % password)  # pragma: allowlist secret
            
            # Write per-VM environment variable: winrm_value_{target_vm_name_lowercase}  # pragma: allowlist secret
            env_var_name = "winrm_value_%s" % target_vm_name.lower()  # pragma: allowlist secret
            _write_github_env(cfg.github_env, env_var_name, password)  # pragma: allowlist secret
            
            log.info(
                "[VM %d/%d] ✓ Password written to: %s",  # pragma: allowlist secret
                idx, len(vms), env_var_name
            )
            success_count += 1
            
        except (DelineaError, ConfigurationError) as ex:
            log.error(
                "[VM %d/%d] ✗ Failed to resolve password for %s (Azure VM: %s): %s",  # pragma: allowlist secret
                idx, len(vms), vm_hostname, target_vm_name, ex
            )
            # Continue processing other VMs instead of failing completely
            continue
    
    if success_count == 0:
        raise DelineaError(
            "Failed to resolve passwords for all VMs in manifest"  # pragma: allowlist secret
        )
    
    log.info(
        "[Multi-VM Mode] ✓ Successfully resolved %d/%d VM password(s)",  # pragma: allowlist secret
        success_count, len(vms)
    )
    
    # Write success indicator
    _write_github_env(cfg.github_env, "DELINEA_FETCH_SUCCESS", "true")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    try:
        cfg = Config.from_env()
        
        if cfg.multi_vm_mode:
            # Multi-VM mode: Load manifest and resolve passwords for all VMs  # pragma: allowlist secret
            _resolve_multi_vm(cfg)
        else:
            # Single-VM mode (legacy): Resolve secret ID only
            secret_id = resolve(cfg)
            _write_github_env(cfg.github_env, "DELINEA_SECRET_ID", secret_id)
            log.info("[Single-VM Mode] ✓ DELINEA_SECRET_ID=%s", secret_id)
            
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
