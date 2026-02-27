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

import json
import logging
import os
import sys
import urllib.parse
import urllib.request

logging.basicConfig(level=logging.INFO, format='%(message)s')

base_url           = (os.getenv('DELINEA_BASE_URL',       '') or '').strip().rstrip('/')
username           = (os.getenv('DELINEA_USERNAME',       '') or '').strip()
password           =  os.getenv('DELINEA_PASSWORD',       '') or ''
search_text        = (os.getenv('DELINEA_SECRET_PATH',    '') or '').strip()
machine_filter     = (os.getenv('DELINEA_SECRET_MACHINE', '') or '').strip().lower()
secret_name_filter = (os.getenv('DELINEA_SECRET_NAME',    '') or '').strip().lower()
account_filter     = (os.getenv('DELINEA_SECRET_ACCOUNT', '') or '').strip().lower()
github_env         =  os.getenv('GITHUB_ENV')

if not base_url or not username or not password:
    logging.warning('Skipping resolution, missing Delinea credentials.')
    sys.exit(1)

if not search_text and not machine_filter:
    logging.warning('Skipping resolution, no search criteria set.')
    sys.exit(1)

try:
    with urllib.request.urlopen(
        urllib.request.Request(
            f"{base_url}/oauth2/token",
            data=urllib.parse.urlencode({
                'grant_type': 'password',
                'username':   username,
                'password':   password,
            }).encode(),
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            method='POST',
        ),
        timeout=30,
    ) as resp:
        token = json.loads(resp.read()).get('access_token')
except Exception as ex:
    logging.warning(f'Could not acquire Delinea token: {ex}')
    sys.exit(1)

if not token:
    logging.warning('No access token returned.')
    sys.exit(1)

auth = {'Authorization': f'Bearer {token}'}

seed = machine_filter or search_text
try:
    with urllib.request.urlopen(
        urllib.request.Request(
            f"{base_url}/api/v1/secrets?"
            + urllib.parse.urlencode({
                'filter.includeRestricted': 'true',
                'filter.searchtext':        seed,
            }),
            headers=auth,
            method='GET',
        ),
        timeout=30,
    ) as resp:
        records = json.loads(resp.read()).get('records') or []
except Exception as ex:
    logging.warning(f'Secret search failed: {ex}')
    sys.exit(1)

if not records:
    logging.warning(f'No records found for "{seed}".')
    sys.exit(1)

def item_val(items, *slugs):
    wanted = {s.lower() for s in slugs}
    for item in items or []:
        if str(item.get('slug', '')).strip().lower() in wanted:
            return str(item.get('itemValue', '')).strip().lower()
    return ''


def fetch_detail(delinea_id):
    with urllib.request.urlopen(
        urllib.request.Request(
            f"{base_url}/api/v1/secrets/{delinea_id}",
            headers=auth,
            method='GET',
        ),
        timeout=30,
    ) as resp:
        return json.loads(resp.read())


def write_delinea_id(delinea_id):
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
        env_logger.info(f"DELINEA_SECRET_ID={delinea_id}")
        env_handler.close()
        env_logger.removeHandler(env_handler)


if machine_filter:
    if not secret_name_filter and not account_filter:
        logging.error('DELINEA_SECRET_MACHINE requires DELINEA_SECRET_NAME or DELINEA_SECRET_ACCOUNT.')
        sys.exit(1)

    desired_name = secret_name_filter or account_filter
    matches = []

    for rec in records:
        name = str(rec.get('name', '') or '').strip()
        if '\\' in name:
            fqdn, acct = name.split('\\', 1)
            if fqdn.strip().lower() == machine_filter and acct.strip().lower() == desired_name:
                matches.append(rec)

    if not matches and account_filter:
        for rec in records:
            sid = rec.get('id')
            if not sid:
                continue
            try:
                detail = fetch_detail(sid)
            except Exception:
                continue
            items = detail.get('items') or rec.get('items') or []
            if (
                item_val(items, 'machine', 'host', 'hostname', 'fqdn', 'server') == machine_filter
                and item_val(items, 'username', 'user', 'account', 'login') == account_filter
            ):
                matches.append(rec)

    matches = list({str(m.get('id')): m for m in matches if m.get('id')}.values())

    if len(matches) == 0:
        logging.error('No matching records found. Check filter values.')
        sys.exit(1)

    if len(matches) > 1:
        logging.error(f'Multiple matches ({len(matches)}). Set DELINEA_SECRET_ID explicitly.')
        sys.exit(1)

    delinea_id = matches[0].get('id')
    logging.info('Resolved DELINEA_SECRET_ID.')
    write_delinea_id(delinea_id)
    sys.exit(0)

exact = next(
    (r for r in records if str(r.get('name', '')).strip().lower() == search_text.lower()),
    None,
)

if not exact or not exact.get('id'):
    logging.warning('No exact name match found.')
    sys.exit(1)

delinea_id = exact['id']
logging.info('Resolved DELINEA_SECRET_ID.')
write_delinea_id(delinea_id)
