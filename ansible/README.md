# Ansible Runbook

This repository contains playbooks and roles for Azure Migrate operations and generating Terraform from existing Azure resources.

## Setup
- Install collections:
```bash
ansible-galaxy collection install -r requirements.yml
```

## Pre-flight
- Syntax check:
```bash
ansible-playbook -i localhost, playbooks/list-migrate-projects.yml --syntax-check
```
- Dry run (where meaningful):
```bash
ansible-playbook -i localhost, playbooks/list-migrate-projects.yml --check
```
- List tasks / tags:
```bash
ansible-playbook playbooks/list-migrate-projects.yml --list-tasks
ansible-playbook playbooks/list-migrate-projects.yml --list-tags
```

## Manifests
- See `ansible/vars/README.md` for how to structure and use `manifest.yml` files: [vars/README.md](vars/README.md)

## Playbooks and abilities

### 1) Azure Migrate – list projects (`playbooks/list-migrate-projects.yml`)
Lists Azure Migrate projects in a resource group.

```bash
ansible-playbook playbooks/list-migrate-projects.yml -e resource_group=rg-migrate
```

### 2) Azure Migrate – start replication (`playbooks/start-migration-replication.yml`)
Starts replication for VMs with idempotent handling - skips VMs that already have replication enabled.

- Key vars:
  - `manifest`: **Required** - Environment selector for loading manifest
  - All configuration loaded from manifest file

- Example:
```bash
ansible-playbook playbooks/start-migration-replication.yml -e "manifest=phase_1"
```

### 3) Join Windows Servers to Domain (`playbooks/join-windows-domain.yaml`)
Joins Windows servers to an Active Directory domain with idempotent handling - skips servers already in the target domain.

- Key vars:
  - `manifest`: **Required** - Environment selector for loading manifest (must contain `domainNameSetup` section)
  - `dry_run`: **Optional** - If `true`, shows what would be done without making changes (default: `false`)

- Manifest requirements:
  - Must include `domainNameSetup` section with domain configuration:
    ```yaml
    domainNameSetup:
      domain: "example.com"
      domain_admin_username: "admin@example.com"
      domain_ou_path: "OU=Computers,DC=example,DC=com"  # Optional
    ```
  - Target VMs must be listed in the `vms` section of the manifest

- Example (dry run):
```bash
ansible-playbook playbooks/join-windows-domain.yaml -e "manifest=phase_1" -e "dry_run=true"
```

- Example (actual domain join):
```bash
ansible-playbook playbooks/join-windows-domain.yaml -e "manifest=phase_1" -e "dry_run=false"
```

- See `roles/win-domain-join/README.md` for detailed documentation

## Credential Resolution Architecture

### Overview
The credential resolution system integrates **Delinea Secret Server** with **GitHub Actions** and **Ansible**, providing a secure, scalable approach to managing SE-Admin credentials at pipeline runtime.

### Component Flow

```
GitHub Actions Workflow
    ↓
resolve_delinea_secret_id.py (Multi-VM mode)
    ↓ (fetches credentials, writes env vars: winrm_value_<vmname>)
    ↓
build_extra_vars.py
    ↓ (creates ansible_extra_vars.json from env vars)
    ↓
join-windows-domain.yaml Playbook
    ↓ (reads json, uses credentials for WinRM tasks)
    ↓
win-domain-join Role
    ├─ prepare_vm_state.yaml (WinRM port probe → enable → test)
    ├─ disjoin_rename.yml (existing domain cleanup)
    └─ join.yml (domain join + verification)
```

### Delinea Resolution Modes

#### Multi-VM Mode (DEFAULT)
Activated when `MANIFEST` environment variable is set. Reads `ansible/vars/{manifest}/manifest.yml` and resolves passwords for all VMs with the following resolution strategy:

**Strategy 1: Explicit Secret ID** (preferred - fast)
- If `vm_delinea_secret_id` is set in manifest, uses that directly
- Skips dynamic search entirely

**Strategy 2: Dynamic Search** (fallback - flexible)
- Constructs hostname FQDN: `vm_winrm_connect_hostname` + optional domain suffix
- Searches Delinea API for secrets matching the FQDN
- Filters by username: `vm_winrm_username`
- Matches using two approaches:
  1. Exact name pattern: `FQDN\Username`
  2. Item slug inspection: machine hostname + account name fields

For each VM:
- Resolves password from Delinea Secret Server
- Masks password in GitHub Actions logs
- Writes to GITHUB_ENV as `winrm_value_{target_vm_name_lowercase}`

**Failure Handling:**
- Logs per-VM failures but continues processing remaining VMs
- Exits with error code 1 if no VMs succeed
- Exits with code 0 only if at least one VM resolves successfully

#### Single-VM Mode (LEGACY - Backward Compat)
Activated when `MANIFEST` is NOT set and `DELINEA_CREDS_PATH` or `DELINEA_CREDS_MACHINE` is provided.
- Resolves a single secret ID
- Outputs `DELINEA_CREDS_ID` to GITHUB_ENV
- Primary for backward compatibility with older workflows

### Environment Variables (Multi-VM)

**Input (from GitHub Actions secrets):**
- `DELINEA_BASE_URL`: Delinea instance base URL
- `DELINEA_USERNAME`: Service account username
- `DELINEA_PASSWORD`: Service account password
- `MANIFEST`: Manifest directory name
- `DELINEA_DOMAIN_SUFFIX`: Optional domain suffix (default: `.dtenet.com`)

**Output (written to GITHUB_ENV by resolve_delinea_secret_id.py):**
- `winrm_value_{target_vm_name_lowercase}`: Resolved SE-Admin password (per VM)
- `DELINEA_FETCH_SUCCESS`: "true" if at least one VM succeeded

**Intermediate (read by build_extra_vars.py):**
- `MANIFEST_INPUT`: Copy of MANIFEST
- `DRY_RUN_INPUT`: Dry run flag
- `FORCE_REJOIN_INPUT`: Force rejoin flag
- `DOMAIN_ADMIN_VALUE_INPUT`: Domain admin password (from Delinea fetch)
- `DOMAIN_OU_PATH_INPUT`: OU path from manifest

### Manifest Integration

Manifest YAML must define VM credentials and Delinea mappings. Example:

```yaml
domainNameSetup:
  domain: "example.com"
  domain_admin_username: "admin@example.com"
  domain_ou_path: "OU=Computers,DC=example,DC=com"

vms:
  - target_vm_name: "web-server-01"
    azure_resource_group: "rg-prod"
    vm_winrm_connect_hostname: "web-server-01"      # Short hostname or FQDN
    vm_winrm_username: "se-admin"                     # Delinea search username
    vm_delinea_secret_id: "12345"                     # Optional: explicit secret ID

  - target_vm_name: "api-server-01"
    azure_resource_group: "rg-prod"
    vm_winrm_connect_hostname: "api-server-01"
    vm_winrm_username: "se-admin"
    # vm_delinea_secret_id: omitted → triggers dynamic search
```

**Dynamic Search Details:**
- If `vm_delinea_secret_id` is omitted, `vm_winrm_connect_hostname` + `vm_winrm_username` trigger a dynamic Delinea search
- Domain suffix is ONLY appended if hostname doesn't already contain it
- Allows flexible hostname formats: short names, FQDNs, or custom formats

### Build Extra Vars Process

`build_extra_vars.py` bridges environment variables and Ansible:

1. **Reads** 5 environment variables set by workflow
2. **Builds** JSON structure with Ansible variables
3. **Validates** required fields and boolean flags
4. **Writes** `ansible_extra_vars.json` with permissions 0o600 (read-write owner only)
5. **Exits** with code 1 on validation failure, 0 on success

Output JSON structure:
```json
{
  "manifest": "domain_join_test",
  "dry_run": false,
  "force_rejoin": false,
  "domain_admin_password": "...",
  "domain_ou_path": "OU=Computers,DC=example,DC=com"
}
```

Playbook reads via: `ansible-playbook ... -e @ansible_extra_vars.json`

### Architecture Improvements

**Fail-Fast Validation:**
- `resolve_delinea_secret_id.py` validates PyYAML availability immediately when multi-VM mode is detected
- Prevents silent failures deep in manifest loading
- Explicit error messaging guides users to install missing dependencies

**Separation of Concerns:**
- Complex JSON building logic extracted from GitHub Actions YAML into dedicated Python script
- Improves maintainability and enables unit testing
- Enables reuse across different workflows

**Single Credential Fetch Pattern:**
- Delinea credentials fetched ONCE at workflow start
- Reused across all VMs via environment variables
- Reduces API calls and latency
- Improves reliability (no repeated authentication)

**Secure Credential Handling:**
- Passwords masked in GitHub Actions logs via `::add-mask::`
- Written to GITHUB_ENV with proper masking
- Environment variables visible only to subsequent workflow steps
- No credentials appear in Git history or workflow logs

## Tips
- Increase verbosity: add `-vvv`
- Show diffs for templates/changes: add `--diff`
- Limit to specific hosts (if not localhost): `--limit` (not typically needed here)
- Debug Delinea resolution: Check workflow logs for `[INFO]` and `[ERROR]` messages from resolve_delinea_secret_id.py
- Verify extra vars: Review `ansible_extra_vars.json` permissions after build_extra_vars.py completes
