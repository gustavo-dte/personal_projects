#!/usr/bin/env python3
"""
resolve_delinea_secret_id.py
============================
Resolves Delinea Secret Server passwords for SE-Admin accounts and writes them to GITHUB_ENV.

Modes:
  Multi-VM (default): MANIFEST env var set → loads manifest, resolves per-VM passwords.
  Single-VM (legacy): DELINEA_CREDS_PATH or DELINEA_CREDS_MACHINE set → resolves one secret ID.

Exits 0 on success, 1 on any error. Passwords are never logged.

Environment variables:
  MANIFEST               Multi-VM manifest directory under ansible/vars/
  DELINEA_BASE_URL       Delinea Secret Server base URL
  DELINEA_USERNAME       Service account username
  DELINEA_PASSWORD       Service account password (preferred)
  DELINEA_VALUE          Service account password (legacy fallback)
  DELINEA_DOMAIN_SUFFIX  Domain suffix for FQDN construction (default: .dtenet.com)
  DELINEA_CREDS_PATH     Single-VM: exact secret name to match
  DELINEA_CREDS_MACHINE  Single-VM: machine FQDN filter
  DELINEA_CREDS_NAME     Single-VM: secret name filter (used with MACHINE)
  DELINEA_ACCOUNT        Single-VM: account name filter (fallback to CREDS_NAME)
  GITHUB_ENV             Path to GitHub Actions env file (set automatically by runner)
"""

from __future__ import annotations

import logging
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests
import yaml
from requests.exceptions import HTTPError, RequestException

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class DelineaError(Exception):
    """Delinea API or secret resolution failure."""


class ConfigurationError(Exception):
    """Missing or invalid environment configuration."""


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------


def _env(name: str) -> str:
    return (os.getenv(name) or "").strip()


@dataclass(frozen=True)
class Config:
    base_url: str
    username: str
    password: str
    search_text: str
    machine_filter: str
    secret_name_filter: str
    account_filter: str
    github_env: str | None
    manifest: str
    domain_suffix: str
    multi_vm_mode: bool

    @classmethod
    def from_env(cls) -> Config:
        base_url = _env("DELINEA_BASE_URL").rstrip("/")
        username = _env("DELINEA_USERNAME")
        password = _env("DELINEA_PASSWORD") or _env("DELINEA_VALUE")

        if not all([base_url, username, password]):
            raise ConfigurationError(
                "Missing Delinea config — set DELINEA_BASE_URL, DELINEA_USERNAME, DELINEA_PASSWORD"
            )

        manifest = _env("MANIFEST")
        search_text = _env("DELINEA_CREDS_PATH")
        machine_filter = _env("DELINEA_CREDS_MACHINE").lower()

        if not manifest and not search_text and not machine_filter:
            raise ConfigurationError(
                "No search criteria — set MANIFEST, DELINEA_CREDS_PATH, or DELINEA_CREDS_MACHINE"
            )

        return cls(
            base_url=base_url,
            username=username,
            password=password,
            search_text=search_text,
            machine_filter=machine_filter,
            secret_name_filter=_env("DELINEA_CREDS_NAME").lower(),
            account_filter=_env("DELINEA_ACCOUNT").lower(),
            github_env=os.getenv("GITHUB_ENV"),
            manifest=manifest,
            domain_suffix=_env("DELINEA_DOMAIN_SUFFIX") or ".dtenet.com",
            multi_vm_mode=bool(manifest),
        )


# ---------------------------------------------------------------------------
# GitHub env export
# ---------------------------------------------------------------------------


def _mask_value(value: str) -> None:
    """Instruct the GitHub Actions runner to mask a value in all future log output."""
    # ::add-mask:: is a GitHub Actions workflow command. Writing it to stdout
    # causes the runner to redact the value wherever it appears in logs.
    # https://docs.github.com/en/actions/writing-workflows/choosing-what-your-workflow-does/workflow-commands-for-github-actions#masking-a-value-in-a-log
    print(f"::add-mask::{value}", flush=True)


def _write_github_env(github_env: str | None, key: str, value: str, sensitive: bool = False) -> None:
    if not github_env:
        log.warning("[WARN] GITHUB_ENV not set — skipping export of %s", key)
        return
    if sensitive:
        _mask_value(value)
    with open(github_env, "a", encoding="utf-8") as fh:
        fh.write(f"{key}={value}\n")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _sanitize_secret_id(value: str) -> str:
    stripped = (value or "").strip()
    if not re.fullmatch(r"\d+", stripped):
        raise ValueError(f"Expected numeric secret ID, got: '{stripped[:20]}'")
    return stripped


def _item_val(items: list[dict[str, Any]], *slugs: str) -> str:
    wanted = {s.lower() for s in slugs}
    for item in items:
        if str(item.get("slug", "")).strip().lower() in wanted:
            return str(item.get("itemValue", "")).strip()
    return ""


def _matches_by_name(name: str, machine: str, account: str) -> bool:
    if "\\" not in name:
        return False
    fqdn, acct = name.split("\\", 1)
    return fqdn.strip().lower() == machine and acct.strip().lower() == account


def _matches_by_items(items: list[dict[str, Any]], machine: str, account: str) -> bool:
    m = _item_val(items, "machine", "host", "hostname", "fqdn", "server").lower()
    a = _item_val(items, "username", "user", "account", "login").lower()
    return m == machine and a == account


# ---------------------------------------------------------------------------
# Delinea API
# ---------------------------------------------------------------------------


def _acquire_token(base_url: str, username: str, password: str) -> str:
    try:
        resp = requests.post(
            f"{base_url}/oauth2/token",
            data={"grant_type": "password", "username": username, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=30,
        )
        resp.raise_for_status()
    except HTTPError as ex:
        raise DelineaError(f"Authentication failed (HTTP {ex.response.status_code})") from ex
    except RequestException as ex:
        raise DelineaError(f"Authentication request failed: {ex}") from ex

    token: str | None = resp.json().get("access_token")
    if not token:
        raise DelineaError("No access_token in authentication response")
    return token


def _search_secrets(base_url: str, auth: dict[str, str], seed: str) -> list[dict[str, Any]]:
    try:
        resp = requests.get(
            f"{base_url}/api/v1/secrets",
            params={"filter.includeRestricted": "true", "filter.searchtext": seed},
            headers=auth,
            timeout=30,
        )
        resp.raise_for_status()
    except HTTPError as ex:
        raise DelineaError(f"Secret search failed (HTTP {ex.response.status_code})") from ex
    except RequestException as ex:
        raise DelineaError(f"Secret search request failed: {ex}") from ex

    return resp.json().get("records") or []


def _fetch_detail(base_url: str, auth: dict[str, str], secret_id: int) -> dict[str, Any]:
    try:
        resp = requests.get(f"{base_url}/api/v1/secrets/{secret_id}", headers=auth, timeout=30)
        resp.raise_for_status()
    except HTTPError as ex:
        # Do NOT include response body — may contain sensitive data
        raise DelineaError(f"Failed to fetch secret {secret_id} (HTTP {ex.response.status_code})") from ex
    except RequestException as ex:
        raise DelineaError(f"Failed to fetch secret {secret_id}: {ex}") from ex

    return resp.json()


def _extract_password(detail: dict[str, Any]) -> str:
    items: list[dict[str, Any]] = detail.get("items") or []
    pw = _item_val(items, "password")
    if not pw:
        raise DelineaError("No password field found in secret")
    return pw


# ---------------------------------------------------------------------------
# Resolution strategies
# ---------------------------------------------------------------------------


def _resolve_by_exact_name(records: list[dict[str, Any]], search_text: str) -> str | None:
    needle = search_text.lower()
    match = next((r for r in records if str(r.get("name", "")).strip().lower() == needle), None)
    if match and match.get("id"):
        return _sanitize_secret_id(str(match["id"]))
    return None


def _resolve_by_machine(
    base_url: str,
    auth: dict[str, str],
    records: list[dict[str, Any]],
    machine_filter: str,
    secret_name_filter: str,
    account_filter: str,
) -> str:
    if not secret_name_filter and not account_filter:
        raise ConfigurationError("DELINEA_CREDS_MACHINE requires DELINEA_CREDS_NAME or DELINEA_ACCOUNT")

    desired = secret_name_filter or account_filter
    matches: list[dict[str, Any]] = []

    for rec in records:
        name = str(rec.get("name") or "").strip()

        if _matches_by_name(name, machine_filter, desired):
            matches.append(rec)
            if len(matches) > 1:
                raise DelineaError("Ambiguous match — multiple records found; set DELINEA_CREDS_ID explicitly")
            continue

        sid: int | None = rec.get("id")
        if not sid:
            continue

        try:
            detail = _fetch_detail(base_url, auth, sid)
        except DelineaError as ex:
            log.warning("[WARN] Skipping secret %s — could not fetch details: %s", sid, ex)
            continue

        if _matches_by_items(detail.get("items") or [], machine_filter, desired):
            matches.append(rec)
            if len(matches) > 1:
                raise DelineaError("Ambiguous match — multiple records found; set DELINEA_CREDS_ID explicitly")

    if not matches:
        raise DelineaError("No matching secret found — verify DELINEA_CREDS_MACHINE and filter values")

    return _sanitize_secret_id(str(matches[0]["id"]))


# ---------------------------------------------------------------------------
# Single-VM mode (legacy)
# ---------------------------------------------------------------------------


def _resolve_single_vm(cfg: Config) -> str:
    token = _acquire_token(cfg.base_url, cfg.username, cfg.password)
    auth = {"Authorization": f"Bearer {token}"}

    seed = cfg.machine_filter or cfg.search_text
    records = _search_secrets(cfg.base_url, auth, seed)

    if not records:
        raise DelineaError(f'No records returned for search term "{seed}"')

    if cfg.search_text:
        secret_id = _resolve_by_exact_name(records, cfg.search_text)
        if secret_id:
            log.info("[INFO] Resolved via exact name match")
            return secret_id

    if cfg.machine_filter:
        secret_id = _resolve_by_machine(
            cfg.base_url, auth, records,
            cfg.machine_filter, cfg.secret_name_filter, cfg.account_filter,
        )
        log.info("[INFO] Resolved via machine filter")
        return secret_id

    raise DelineaError("No exact name match found and DELINEA_CREDS_MACHINE is not set")


# ---------------------------------------------------------------------------
# Multi-VM mode
# ---------------------------------------------------------------------------


def _load_manifest(manifest_name: str) -> dict[str, Any]:
    path = Path("ansible/vars") / manifest_name / "manifest.yml"
    if not path.exists():
        raise ConfigurationError(f"Manifest not found: {path}")
    try:
        with open(path, encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}
    except Exception as ex:
        raise ConfigurationError(f"Failed to load manifest {path}: {ex}") from ex


def _resolve_multi_vm(cfg: Config) -> None:
    log.info("[INFO] [Multi-VM] Loading manifest: %s", cfg.manifest)
    manifest = _load_manifest(cfg.manifest)

    vms: list[dict[str, Any]] = manifest.get("vms") or []
    if not vms:
        raise ConfigurationError(f"No VMs found in manifest: {cfg.manifest}")

    log.info("[INFO] [Multi-VM] Found %d VM(s)", len(vms))

    token = _acquire_token(cfg.base_url, cfg.username, cfg.password)
    auth = {"Authorization": f"Bearer {token}"}

    for idx, vm in enumerate(vms, start=1):
        target_vm_name: str = vm.get("target_vm_name", "")
        vm_hostname: str = vm.get("vm_winrm_connect_hostname", "")
        vm_username: str = vm.get("vm_winrm_username", "")
        explicit_id: str = str(vm.get("vm_delinea_secret_id", "")).strip()
        total = len(vms)

        if not all([target_vm_name, vm_hostname, vm_username]):
            # Missing fields = misconfigured manifest → fail immediately
            raise ConfigurationError(
                f"[VM {idx}/{total}] Missing required fields "
                f"(target_vm_name, vm_winrm_connect_hostname, vm_winrm_username)"
            )

        log.info("[INFO] [VM %d/%d] %s (hostname=%s)", idx, total, target_vm_name, vm_hostname)

        if explicit_id:
            secret_id = explicit_id
            log.info("[INFO] [VM %d/%d] Using explicit secret ID from manifest", idx, total)
        else:
            suffix = cfg.domain_suffix
            fqdn = vm_hostname.lower() if vm_hostname.lower().endswith(suffix.lower()) else (vm_hostname + suffix).lower()
            account = vm_username.lower()
            log.info("[INFO] [VM %d/%d] Searching Delinea: %s\\%s", idx, total, fqdn, account)

            records = _search_secrets(cfg.base_url, auth, fqdn)
            if not records:
                raise DelineaError(f"[VM {idx}/{total}] No records returned for: {fqdn}")

            # Strategy 1: name pattern "fqdn\account"
            secret_id = ""
            pattern = f"{fqdn}\\{account}"
            for rec in records:
                if str(rec.get("name") or "").strip().lower() == pattern:
                    secret_id = str(rec.get("id", "")).strip()
                    log.info("[INFO] [VM %d/%d] Matched by name", idx, total)
                    break

            # Strategy 2: item slugs
            if not secret_id:
                for rec in records:
                    rec_id: int | None = rec.get("id")
                    if not rec_id:
                        continue
                    detail = _fetch_detail(cfg.base_url, auth, rec_id)
                    if _matches_by_items(detail.get("items") or [], fqdn, account):
                        secret_id = str(rec_id).strip()
                        log.info("[INFO] [VM %d/%d] Matched by items", idx, total)
                        break

            if not secret_id:
                raise DelineaError(f"[VM {idx}/{total}] No matching secret for {fqdn}\\{account}")

        detail = _fetch_detail(cfg.base_url, auth, int(secret_id))
        password = _extract_password(detail)  # never logged

        env_var = f"winrm_value_{target_vm_name.lower()}"
        _write_github_env(cfg.github_env, env_var, password, sensitive=True)
        log.info("[INFO] [VM %d/%d] Password written to env var: %s", idx, total, env_var)

    _write_github_env(cfg.github_env, "DELINEA_FETCH_SUCCESS", "true")
    log.info("[INFO] [Multi-VM] All %d VM(s) resolved successfully", len(vms))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    try:
        cfg = Config.from_env()
        if cfg.multi_vm_mode:
            _resolve_multi_vm(cfg)
        else:
            secret_id = _resolve_single_vm(cfg)
            _write_github_env(cfg.github_env, "DELINEA_CREDS_ID", secret_id)
            log.info("[INFO] [Single-VM] DELINEA_CREDS_ID written to GITHUB_ENV")
    except ConfigurationError as ex:
        log.error("[ERROR] Configuration error: %s", ex)
        sys.exit(1)
    except DelineaError as ex:
        log.error("[ERROR] Delinea resolution failed: %s", ex)
        sys.exit(1)
    except ValueError as ex:
        log.error("[ERROR] Secret ID validation failed: %s", ex)
        sys.exit(1)
    except OSError as ex:
        log.error("[ERROR] Failed to write to GITHUB_ENV: %s", ex)
        sys.exit(1)


if __name__ == "__main__":
    main()
