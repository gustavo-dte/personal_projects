#!/usr/bin/env python3
"""
checkin_delinea_secrets.py
==========================
Version: 1.0.0 (2026-03-05)

Checks in (releases) Delinea Secret Server secrets that were checked out during
the domain join workflow. This script should be run at the end of the workflow
to unlock the secrets for other processes.

Reads secret IDs from environment variables that were set during checkout:
  - delinea_secret_id_<target_vm_name_lowercase>

Exits with code 0 on:
  - All checked-out secrets successfully checked in
  - All secrets are already checked in (no-op)
  - Partial success when FAILURE_MODE=continue

Exits with code 1 on:
  - Missing Delinea credentials
  - Missing MANIFEST env var
  - Cannot load manifest YAML
  - All check-ins failed when FAILURE_MODE=fail (default)

Environment variables read:
  MANIFEST                Manifest directory name under ansible/vars/
  DELINEA_BASE_URL        Base URL of the Delinea Secret Server instance
  DELINEA_USERNAME        Service account used to authenticate
  DELINEA_PASSWORD        Password for the service account
  FAILURE_MODE            'fail' (default) or 'continue' - exit code behavior

Usage:
  MANIFEST=domain_join_test python3 ansible/roles/python_scripts/checkin_delinea_secrets.py
"""

from __future__ import annotations

import logging
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from requests.exceptions import HTTPError, RequestException

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Custom exceptions
# ---------------------------------------------------------------------------


class DelineaError(Exception):
    """Raised for recoverable Delinea API errors."""


class ConfigurationError(Exception):
    """Raised when required environment configuration is missing or invalid."""


# ---------------------------------------------------------------------------
# Environment helpers
# ---------------------------------------------------------------------------


def _env(var: str) -> str:
    """Return a stripped environment variable value, defaulting to empty string.

    Args:
        var: Environment variable name.

    Returns:
        Stripped string value, or empty string when unset.
    """
    return (os.getenv(var) or "").strip()


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Config:
    """Immutable runtime configuration built from environment variables."""

    base_url: str
    username: str
    password: str  # pragma: allowlist secret
    manifest: str
    failure_mode: str  # 'fail' or 'continue'

    @classmethod
    def from_env(cls) -> Config:
        """Build and validate a Config from environment variables.

        Returns:
            A fully validated, frozen Config instance.

        Raises:
            ConfigurationError: If required variables are missing.
        """
        base_url = _env("DELINEA_BASE_URL").rstrip("/")
        username = _env("DELINEA_USERNAME")
        password = _env("DELINEA_PASSWORD") or _env("DELINEA_VALUE")  # pragma: allowlist secret
        manifest = _env("MANIFEST")

        if not all([base_url, username, password]):
            raise ConfigurationError(
                "Missing Delinea configuration — set DELINEA_BASE_URL, "
                "DELINEA_USERNAME, and DELINEA_PASSWORD"
            )

        if not manifest:
            raise ConfigurationError(
                "Missing MANIFEST environment variable — required for check-in operation"
            )

        failure_mode = _env("FAILURE_MODE").lower() or "fail"
        if failure_mode not in ("fail", "continue"):
            raise ConfigurationError(
                "Invalid FAILURE_MODE — must be 'fail' or 'continue'"
            )

        return cls(
            base_url=base_url,
            username=username,
            password=password,  # pragma: allowlist secret
            manifest=manifest,
            failure_mode=failure_mode,
        )


# ---------------------------------------------------------------------------
# Delinea API client
# ---------------------------------------------------------------------------


def _acquire_token(base_url: str, username: str, password: str) -> str:  # pragma: allowlist secret
    """Authenticate against Delinea and return a bearer token.

    Args:
        base_url:  Base URL of the Delinea Secret Server instance.
        username:  Service account username.
        password:  Service account password for OAuth2 grant_type.  # pragma: allowlist secret

    Returns:
        Bearer token string.

    Raises:
        DelineaError: On any network, HTTP, or missing-token failure.
    """
    try:
        resp = requests.post(
            "%s/oauth2/token" % base_url,
            data={
                "grant_type": "password",
                "username": username,
                "password": password,  # pragma: allowlist secret
            },
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


def _checkin_secret(
    base_url: str,
    auth: Dict[str, str],
    delinea_id: int,
) -> None:
    """Force check-in a secret if it is currently checked out.

    Args:
        base_url:   Base URL of the Delinea Secret Server instance.
        auth:       Authorization header dict containing the bearer token.
        delinea_id: Numeric Delinea secret ID.

    Raises:
        DelineaError: On any network or HTTP failure (except already-checked-in).
    """
    try:
        resp = requests.post(
            "%s/api/v1/secrets/%s/check-in?forceCheckIn=true" % (base_url, delinea_id),
            headers=auth,
            timeout=30,
        )
        if resp.status_code == 400:
            error_data = resp.json()
            if error_data.get("errorCode") == "API_SecretNotCheckedOut":
                log.info(
                    "[INFO] Secret ID=%s was not checked out (already released)",
                    delinea_id,
                )
                return
        resp.raise_for_status()
        log.info("[INFO] Successfully checked in secret ID=%s", delinea_id)
    except HTTPError as ex:
        error_body = ""
        try:
            error_body = " - " + ex.response.text
        except Exception:  # noqa: BLE001
            pass
        raise DelineaError(
            "Failed to force check in secret %s (HTTP %s)%s"
            % (delinea_id, ex.response.status_code, error_body)
        ) from ex
    except RequestException as ex:
        raise DelineaError(
            "Failed to force check in secret %s: %s" % (delinea_id, ex)
        ) from ex


# ---------------------------------------------------------------------------
# Manifest loading
# ---------------------------------------------------------------------------


def _load_manifest(manifest_name: str) -> Dict[str, Any]:
    """Load and parse the manifest YAML file.

    Args:
        manifest_name: Directory name under ansible/vars/ (e.g., 'domain_join_test')

    Returns:
        Parsed manifest dict.

    Raises:
        ConfigurationError: If PyYAML is not installed or the manifest cannot be loaded.
    """
    if yaml is None:
        raise ConfigurationError(
            "PyYAML is required for this operation. Install: pip install PyYAML"
        )

    manifest_path = Path("ansible/vars") / manifest_name / "manifest.yml"

    if not manifest_path.exists():
        raise ConfigurationError("Manifest file not found: %s" % manifest_path)

    try:
        with open(manifest_path, encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}
    except Exception as ex:
        raise ConfigurationError(
            "Failed to load manifest %s: %s" % (manifest_path, ex)
        ) from ex


# ---------------------------------------------------------------------------
# Check-in orchestration
# ---------------------------------------------------------------------------


def checkin_all_secrets(cfg: Config) -> None:
    """Check in all secrets that were checked out during the workflow.

    Reads the manifest to get VM list, then checks in each secret whose ID
    was stored in the environment during checkout.

    Args:
        cfg: Configuration with manifest name and Delinea credentials.

    Raises:
        ConfigurationError: If manifest loading fails or no VMs are present.
        DelineaError:       If all check-ins fail and FAILURE_MODE=fail.
    """
    log.info("[INFO] Loading manifest: %s", cfg.manifest)
    manifest = _load_manifest(cfg.manifest)

    vms: List[Dict[str, Any]] = manifest.get("vms") or []
    if not vms:
        raise ConfigurationError("No VMs found in manifest: %s" % cfg.manifest)

    log.info("[INFO] Found %d VM(s) in manifest", len(vms))

    token = _acquire_token(cfg.base_url, cfg.username, cfg.password)  # pragma: allowlist secret
    auth: Dict[str, str] = {"Authorization": "Bearer %s" % token}

    total = len(vms)
    success_count = 0
    error_count = 0

    for idx, vm in enumerate(vms, start=1):
        target_vm_name: str = vm.get("target_vm_name", "")

        if not target_vm_name:
            log.warning(
                "[WARN] [VM %d/%d] Skipping — missing target_vm_name",
                idx,
                total,
            )
            continue

        # Look for the secret ID in environment variables
        secret_id_var_name = "delinea_secret_id_%s" % target_vm_name.lower()
        secret_id_str = _env(secret_id_var_name)

        if not secret_id_str:
            log.warning(
                "[WARN] [VM %d/%d] No secret ID found in %s — skipping check-in for %s",
                idx,
                total,
                secret_id_var_name,
                target_vm_name,
            )
            continue

        try:
            secret_id = int(secret_id_str)
        except ValueError:
            log.error(
                "[ERROR] [VM %d/%d] Invalid secret ID '%s' for %s — skipping",
                idx,
                total,
                secret_id_str,
                target_vm_name,
            )
            error_count += 1
            continue

        log.info(
            "[INFO] [VM %d/%d] Checking in secret ID=%d for VM: %s",
            idx,
            total,
            secret_id,
            target_vm_name,
        )

        try:
            _checkin_secret(cfg.base_url, auth, secret_id)
            success_count += 1

        except DelineaError as ex:
            log.error(
                "[ERROR] [VM %d/%d] Failed to check in secret ID=%d for %s: %s",
                idx,
                total,
                secret_id,
                target_vm_name,
                ex,
            )
            error_count += 1
            if cfg.failure_mode == "fail":
                # In fail mode, re-raise the error to exit immediately
                raise

    log.info(
        "[INFO] Check-in summary: %d succeeded, %d failed, %d total",
        success_count,
        error_count,
        total,
    )

    if error_count > 0 and success_count == 0 and cfg.failure_mode == "fail":
        raise DelineaError("All check-in operations failed")

    if error_count > 0:
        log.warning(
            "[WARN] Some check-ins failed (%d errors) — continuing due to FAILURE_MODE=%s",
            error_count,
            cfg.failure_mode,
        )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    """Entry point: check in all Delinea secrets from the workflow."""
    try:
        cfg = Config.from_env()
        checkin_all_secrets(cfg)
        log.info("[INFO] Check-in complete")

    except ConfigurationError as ex:
        log.error("[ERROR] Configuration error: %s", ex)
        sys.exit(1)
    except DelineaError as ex:
        log.error("[ERROR] Delinea check-in failed: %s", ex)
        sys.exit(1)


if __name__ == "__main__":
    main()
