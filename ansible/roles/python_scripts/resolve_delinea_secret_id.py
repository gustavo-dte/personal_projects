#!/usr/bin/env python3
"""
resolve_delinea_secret_id.py
============================
Resolves the numeric Delinea Secret Server secret ID for the SE-Admin account
and writes it to GITHUB_ENV so subsequent workflow steps can use it.

Skips silently (exit 0) when:
  - DELINEA_SECRET_ID is already set  →  caller should short-circuit before invoking this
  - Delinea credentials are missing
  - Neither DELINEA_SECRET_PATH nor DELINEA_SECRET_MACHINE is set
  - The Delinea API returns no matching records

Exits with code 1 (hard failure) when:
  - DELINEA_SECRET_MACHINE is set but neither DELINEA_SECRET_NAME nor DELINEA_SECRET_ACCOUNT is set
  - No secret matched the machine + account/name filters
  - Multiple secrets matched and cannot be disambiguated

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
import os
import sys
import urllib.parse
import urllib.request

# ── Read environment ───────────────────────────────────────────────────────────
base_url           = (os.getenv('DELINEA_BASE_URL',       '') or '').strip().rstrip('/')
username           = (os.getenv('DELINEA_USERNAME',       '') or '').strip()
password           =  os.getenv('DELINEA_PASSWORD',       '') or ''
search_text        = (os.getenv('DELINEA_SECRET_PATH',    '') or '').strip()
machine_filter     = (os.getenv('DELINEA_SECRET_MACHINE', '') or '').strip().lower()
secret_name_filter = (os.getenv('DELINEA_SECRET_NAME',    '') or '').strip().lower()
account_filter     = (os.getenv('DELINEA_SECRET_ACCOUNT', '') or '').strip().lower()
github_env         =  os.getenv('GITHUB_ENV')

# ── Pre-flight checks ──────────────────────────────────────────────────────────
if not base_url or not username or not password:
    print('⚠️ Skipping secret ID resolution — missing Delinea credentials.')
    sys.exit(0)

if not search_text and not machine_filter:
    print('⚠️ Skipping secret ID resolution — no DELINEA_SECRET_PATH or DELINEA_SECRET_MACHINE set.')
    sys.exit(0)

# ── Acquire OAuth2 token ───────────────────────────────────────────────────────
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
    print(f'⚠️ Could not acquire Delinea token: {ex}')
    sys.exit(0)

if not token:
    print('⚠️ No access token returned — skipping.')
    sys.exit(0)

auth = {'Authorization': f'Bearer {token}'}

# ── Search secrets ─────────────────────────────────────────────────────────────
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
    print(f'⚠️ Secret search failed: {ex}')
    sys.exit(0)

if not records:
    print(f'⚠️ No secrets found for "{seed}" — falling back to path-based lookup.')
    sys.exit(0)

# ── Helpers ────────────────────────────────────────────────────────────────────
def item_val(items, *slugs):
    """Return the itemValue for the first matching slug (case-insensitive)."""
    wanted = {s.lower() for s in slugs}
    for item in items or []:
        if str(item.get('slug', '')).strip().lower() in wanted:
            return str(item.get('itemValue', '')).strip().lower()
    return ''


def fetch_detail(secret_id):
    """Fetch full secret detail from Delinea."""
    with urllib.request.urlopen(
        urllib.request.Request(
            f"{base_url}/api/v1/secrets/{secret_id}",
            headers=auth,
            method='GET',
        ),
        timeout=30,
    ) as resp:
        return json.loads(resp.read())


def write_secret_id(secret_id):
    """Write the resolved secret ID to GITHUB_ENV and mask it in logs.
    
    Note: The secret ID is a numeric identifier used to fetch the actual password
    from Delinea Secret Server. While not sensitive itself, we mask it to prevent
    enumeration attacks. The ID must be stored (not hashed) so Ansible can use it.
    """
    if github_env:
        # Mask the secret ID in GitHub Actions logs
        print(f"::add-mask::{secret_id}")
        
        # Write to GITHUB_ENV for use by subsequent workflow steps
        # lgtm[py/clear-text-storage-sensitive-data]
        # CodeQL: This is an identifier (not the password itself) that must be
        # stored in clear text for Ansible to fetch the actual secret from Delinea
        with open(github_env, 'a', encoding='utf-8') as f:
            # lgtm[py/clear-text-storage-sensitive-data]
            f.write(f"DELINEA_SECRET_ID={secret_id}\n")


# ── Machine-scoped match ───────────────────────────────────────────────────────
if machine_filter:
    if not secret_name_filter and not account_filter:
        print('⚠️ DELINEA_SECRET_MACHINE is set but neither DELINEA_SECRET_NAME nor DELINEA_SECRET_ACCOUNT is set.')
        sys.exit(1)

    desired_name = secret_name_filter or account_filter
    matches = []

    # Strategy 1: "FQDN\AccountName" pattern in the record name field
    for rec in records:
        name = str(rec.get('name', '') or '').strip()
        if '\\' in name:
            fqdn, acct = name.split('\\', 1)
            if fqdn.strip().lower() == machine_filter and acct.strip().lower() == desired_name:
                matches.append(rec)

    # Strategy 2: fetch full secret detail and match machine + username fields
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

    # De-duplicate by ID (a record could match both strategies)
    matches = list({str(m.get('id')): m for m in matches if m.get('id')}.values())

    if len(matches) == 0:
        print(
            "❌ No secret matched the provided machine and name/account filters. "
            "Provide DELINEA_SECRET_ID explicitly or correct DELINEA_SECRET_MACHINE + DELINEA_SECRET_NAME."
        )
        sys.exit(1)

    if len(matches) > 1:
        ids_count = len(matches)
        print(
            f"❌ Multiple secrets ({ids_count}) matched the provided machine and name/account filters. "
            "Set DELINEA_SECRET_ID explicitly to disambiguate."
        )
        sys.exit(1)

    secret_id = matches[0].get('id')
    print(f"✅ Resolved DELINEA_SECRET_ID using the provided machine and name/account filters.")
    write_secret_id(secret_id)
    sys.exit(0)

# ── Exact name match (path-based fallback) ─────────────────────────────────────
exact = next(
    (r for r in records if str(r.get('name', '')).strip().lower() == search_text.lower()),
    None,
)

if not exact or not exact.get('id'):
    print('⚠️ No exact name match for the provided path — falling back to path-based lookup.')
    sys.exit(0)

secret_id = exact['id']
print(f"✅ Resolved DELINEA_SECRET_ID from the provided path.")
write_secret_id(secret_id)
