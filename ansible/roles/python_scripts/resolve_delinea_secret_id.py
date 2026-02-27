#!/usr/bin/env python3
"""
resolve_delinea_secret_id.py
============================
Resolves the numeric Delinea Secret Server secret ID for the SE-Admin account
and writes it to GITHUB_ENV so subsequent workflow steps can use it.

Exits with code 1 (failure) when:
  - DELINEA_SECRET_ID is already set  →  caller should short-circuit before invoking this
  - Delinea credentials are missing
  - Neither DELINEA_SECRET_PATH nor DELINEA_SECRET_MACHINE is set
  - The Delinea API returns no matching records
  - DELINEA_SECRET_MACHINE is set but neither DELINEA_SECRET_NAME nor DELINEA_SECRET_ACCOUNT is set
  - No secret matched the machine + account/name filters
  - Multiple secrets matched and cannot be disambiguated

Exits with code 0 (success) when:
  - Secret ID is successfully resolved and written to GITHUB_ENV

Environment variables read:
  DELINEA_BASE_URL        Base URL of the Delinea Secret Server instance
  DELINEA_USERNAME        Service account used to authenticate
  DELINEA_PASSWORD        Password for the service account
  DELINEA_SECRET_PATH     Name / path search term  (fallback when ID is not set)
  DELINEA_SECRET_MACHINE  (Optional) Machine FQDN to narrow matching
  DELINEA_SECRET_NAME     (Optional) Secret name filter (preferred over ACCOUNT)
  DELINEA_SECRET_ACCOUNT  (Optional) Account name filter (fallback if NAME not set)
  GITHUB_ENV              Path to the GitHub Actions env file (set automatically by the runner)

Usage (from a workflow step):
  python3 ansible/roles/python_scripts/resolve_delinea_secret_id.py
"""

import logging
import os
import requests
import sys
from typing import Any, Dict, List, Optional

logging.basicConfig(level=logging.INFO, format='%(message)s')

base_url: str = (os.getenv('DELINEA_BASE_URL', '') or '').strip().rstrip('/')
username: str = (os.getenv('DELINEA_USERNAME', '') or '').strip()
password: str = os.getenv('DELINEA_PASSWORD', '') or ''
search_text: str = (os.getenv('DELINEA_SECRET_PATH', '') or '').strip()
machine_filter: str = (os.getenv('DELINEA_SECRET_MACHINE', '') or '').strip().lower()
secret_name_filter: str = (os.getenv('DELINEA_SECRET_NAME', '') or '').strip().lower()
account_filter: str = (os.getenv('DELINEA_SECRET_ACCOUNT', '') or '').strip().lower()
github_env: Optional[str] = os.getenv('GITHUB_ENV')

if not base_url or not username or not password:
    logging.error('Skipping resolution, missing Delinea credentials.')
    sys.exit(1)

if not search_text and not machine_filter:
    logging.error('Skipping resolution, no search criteria set.')
    sys.exit(1)

try:
    resp: requests.Response = requests.post(
        f"{base_url}/oauth2/token",
        data={
            'grant_type': 'password',
            'username':   username,
            'password':   password,
        },
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        timeout=30,
    )
    resp.raise_for_status()
    token: Optional[str] = resp.json().get('access_token')
except Exception as ex:
    logging.error('Could not acquire Delinea token: %s', ex)
    sys.exit(1)

if not token:
    logging.error('No access token returned.')
    sys.exit(1)

auth: Dict[str, str] = {'Authorization': f'Bearer {token}'}

seed: str = machine_filter or search_text
try:
    resp = requests.get(
        f"{base_url}/api/v1/secrets",
        params={
            'filter.includeRestricted': 'true',
            'filter.searchtext':        seed,
        },
        headers=auth,
        timeout=30,
    )
    resp.raise_for_status()
    records: List[Dict[str, Any]] = resp.json().get('records') or []
except Exception as ex:
    logging.error('Secret search failed: %s', ex)
    sys.exit(1)

if not records:
    logging.error('No records found for "%s".', seed)
    sys.exit(1)

def item_val(items: Optional[List[Dict[str, Any]]], *slugs: str) -> str:
    wanted = {s.lower() for s in slugs}
    for item in items or []:
        if str(item.get('slug', '')).strip().lower() in wanted:
            return str(item.get('itemValue', '')).strip().lower()
    return ''


def fetch_detail(delinea_id: Any) -> Dict[str, Any]:
    resp: requests.Response = requests.get(
        f"{base_url}/api/v1/secrets/{delinea_id}",
        headers=auth,
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def write_delinea_id(delinea_id: Any) -> None:
    if github_env:
        # lgtm[py/clear-text-logging-sensitive-data]
        sys.stdout.write(f"::add-mask::{delinea_id}\n")
        sys.stdout.flush()
        
        # lgtm[py/clear-text-storage-sensitive-data]
        env_handler = logging.FileHandler(github_env, mode='a', encoding='utf-8')
        env_handler.setFormatter(logging.Formatter('%(message)s'))
        env_logger = logging.getLogger('github_env')
        env_logger.setLevel(logging.INFO)
        env_logger.addHandler(env_handler)
        # lgtm[py/clear-text-storage-sensitive-data]
        env_logger.info("DELINEA_SECRET_ID=%s", delinea_id)
        env_handler.close()
        env_logger.removeHandler(env_handler)


# Strategy 1: Try exact name match first (fastest, simplest)
exact: Optional[Dict[str, Any]] = next(
    (r for r in records if str(r.get('name', '')).strip().lower() == search_text.lower()),
    None,
)

if exact and exact.get('id'):
    delinea_id: Any = exact['id']
    logging.info('Resolved DELINEA_SECRET_ID via exact name match.')
    write_delinea_id(delinea_id)
    sys.exit(0)

# Strategy 2: If no exact match and machine filter is set, do machine-based filtering
if machine_filter:
    if not secret_name_filter and not account_filter:
        logging.error('DELINEA_SECRET_MACHINE requires DELINEA_SECRET_NAME or DELINEA_SECRET_ACCOUNT.')
        sys.exit(1)

    desired_name: str = secret_name_filter or account_filter
    matches: List[Dict[str, Any]] = []

    for rec in records:
        name: str = str(rec.get('name', '') or '').strip()
        matched: bool = False
        
        # First, try simple name-based matching if name contains backslash
        if '\\' in name:
            fqdn: str
            acct: str
            fqdn, acct = name.split('\\', 1)
            if fqdn.strip().lower() == machine_filter and acct.strip().lower() == desired_name:
                matches.append(rec)
                matched = True
        
        # If no match yet and we have account_filter, check detailed items
        if not matched and account_filter:
            sid: Any = rec.get('id')
            if sid:
                try:
                    detail: Dict[str, Any] = fetch_detail(sid)
                    items: List[Dict[str, Any]] = detail.get('items') or rec.get('items') or []
                    if (
                        item_val(items, 'machine', 'host', 'hostname', 'fqdn', 'server') == machine_filter
                        and item_val(items, 'username', 'user', 'account', 'login') == account_filter
                    ):
                        matches.append(rec)
                except Exception:
                    continue

    matches = list({str(m.get('id')): m for m in matches if m.get('id')}.values())

    if len(matches) == 0:
        logging.error('No matching records found. Check filter values.')
        sys.exit(1)

    if len(matches) > 1:
        logging.error('Multiple matches (%s). Set DELINEA_SECRET_ID explicitly.', len(matches))
        sys.exit(1)

    delinea_id = matches[0].get('id')
    logging.info('Resolved DELINEA_SECRET_ID via machine filter.')
    write_delinea_id(delinea_id)
    sys.exit(0)

# If we reach here, no match was found
logging.error('No exact name match found and no machine filter criteria provided.')
sys.exit(1)
