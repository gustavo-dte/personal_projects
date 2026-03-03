
Join Windows Servers to an Active Directory domain using Ansible. This role provides idempotent domain join operations that check current domain membership before attempting to join, and handles server reboot and verification after successful domain join.

## Table of Contents

- [Requirements](#requirements)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [Parameters](#parameters)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)

## Requirements

- `ansible >= 2.9`
- Collections:
  - `microsoft.ad` (for `membership` and `computer` modules — domain join and pre-create AD computer object)
  - `ansible.windows` (for `win_reboot`, `win_hostname`, `win_shell`, etc.)
- Windows target VMs must be accessible via WinRM (port 5985 or 5986; configurable per VM via `vm_winrm_port`)
- Domain admin credentials with permission to join computers to the domain and to create computer objects in the target OU
- For the **pre-create flow** (recommended): set `domain_ou_path` in the manifest; the role creates the AD computer object in that OU before disjoin/rename/join. Optional remove-stale (delete-by-name) is disabled when using pre-create to avoid affecting the wrong object.

## Quick Start

```bash
# Dry run - shows what would be done
ansible-playbook ansible/playbooks/join-windows-domain.yaml \
  -e "manifest=test_vm_migration" \
  -e "dry_run=true"

# Actual domain join
ansible-playbook ansible/playbooks/join-windows-domain.yaml \
  -e "manifest=test_vm_migration" \
  -e "dry_run=false"
```

## Usage

The role reads configuration from `manifest_data.domainNameSetup` when a `manifest` is passed through the playbook or CI workflows.

### Manifest-driven Configuration

Add the following to your manifest file (e.g., `ansible/vars/test_vm_migration/manifest.yml`):

```yaml
domainNameSetup:
  domain: "example.com"  # Required: FQDN of the domain
  domain_admin_username: "admin@example.com"  # Required: Domain admin username (UPN format)
  domain_ou_path: "OU=Azure,OU=DCA,OU=Servers,DC=example,DC=com"  # Required for pre-create flow (DN format)

vms:
  - name: dca-dev7048                    # List key (e.g. current hostname or logical name)
    target_vm_name: vmcuwinwebd01       # Name after rename and for domain join
    vm_ip: 10.0.0.10                    # Or omit and use Azure lookup via target_vm_name
    vm_winrm_port: 5985                 # 5985 (HTTP) or 5986 (HTTPS)
    vm_winrm_username: cpoeadmin         # Username only; role uses computername\username
    vm_winrm_connect_hostname: dca-dev7048  # Optional: use when current hostname differs from target_vm_name (for first WinRM auth)
    # vm_winrm_password in manifest only for local testing; use GitHub Secrets / Vault in production
```

**Note:** For production use, domain credentials should be stored in Azure Key Vault or Ansible Vault, not in the manifest file.

### Role Behavior

- **Pre-create AD object (when `domain_ou_path` is set)**: Creates the AD computer object for the target name in the target OU *before* disjoin. Stops the playbook if creation or verification fails. Used to avoid delete-by-name (which could affect the source VM). Pre-create runs only when `domain_ou_path` is set in the manifest.
- **Domain migration flow**: (Pre-create if `domain_ou_path` set) → Disjoin (if VM is in a domain and not already in target) → Rename (if hostname ≠ target) → Join. Step 2 (Rename) and Step 3 (Join) run only when hostname or domain differ from target (or `force_rejoin=true`).
- **WinRM and firewall**: The role turns off the Windows Firewall **Public** profile early so WinRM remains reachable when the NIC is in Public profile; when the VM is in WORKGROUP it also turns off **Private** (before rename/join).
- **Idempotent**: Skips Disjoin if already in WORKGROUP or target domain (unless `force_rejoin=true`). Skips Rename if hostname already matches target. Skips Join when already in target domain (unless `force_rejoin=true`).
- **Reboot handling**: Reboots after disjoin (when disjoin ran), after rename (when rename ran), and after join; configurable via `restart_on_success`. For both **post-disjoin** and **post-join** reboots on Azure VMs, uses **Azure CLI restart as primary** (more reliable); falls back to `win_reboot` (WinRM) when Azure is skipped or fails. Waits for WinRM to come back after each reboot.
- **Verification**: Verifies domain membership after the final reboot and displays final domain/computer name.
- **Dry-run**: When `dry_run: true`, sets placeholder facts and shows what would be done without connecting to VMs.
- **Disjoin-only mode**: When `disjoin_only: true`, the playbook only disjoins VMs from the domain (move to WORKGROUP) using the same manifest; use the disjoin playbook/workflow for that path.

### Playbook & CI

- **Join playbook**: `ansible/playbooks/join-windows-domain.yaml` — full flow (pre-create → disjoin → rename → join). Pass `manifest=...` and `domain_admin_password` (e.g. via GitHub Secrets).
- **Disjoin-only playbook**: `ansible/playbooks/disjoin-windows-domain.yaml` — passes `disjoin_only: true` so the role only disjoins VMs (move to WORKGROUP). Use when you need to disjoin without rename/join.
- **Workflow**: `.github/workflows/ansible-join-windows-domain.yaml` — GitHub Actions workflow for the join playbook. Requires repository secrets: `DOMAIN_ADMIN_PASSWORD`, and `WINRM_PASSWORD` (optional: `WINRM_USERNAME`, default `SE-Admin`).  # pragma: allowlist secret

## Parameters

### Required Variables

**Manifest variables:**
- `domainNameSetup.domain` - FQDN of the Active Directory domain
- `domainNameSetup.domain_admin_username` - Domain admin account (UPN format recommended)
- `domainNameSetup.domain_ou_path` - **Required for the pre-create flow.** OU where the AD computer object is created (DN format). Example: `OU=Azure,OU=DCA,OU=Servers,DC=dtenet,DC=com`. If set, the playbook runs pre-create and stops if create/verify fails; if not set, pre-create is skipped (not recommended for migration).

**Playbook/CI variables:**
- `manifest` - Manifest name (directory in `ansible/vars/`)
- `domain_admin_password` - Domain admin password (passed via GitHub Secrets or Ansible Vault, not in manifest)

### Optional Variables

**Playbook variables:**
- `dry_run` (default: `false`) - If `true`, shows what would be done without making changes
- `force_rejoin` (default: `false`) - If `true`, forces disjoin and rejoin even if VM is already in the target domain
- `use_azure_restart` (default: `true`) - If `true`, uses Azure CLI `az vm restart` as primary for post-disjoin and post-join reboots (more reliable for Azure VMs); falls back to WinRM `win_reboot` when Azure is skipped or fails. Set to `false` to use WinRM only.
- `winrm_username` (default: `SE-Admin`) - Local Windows admin username for WinRM authentication
- `winrm_password` (default: empty) - Local Windows admin password for WinRM authentication

**Per-VM manifest variables:**
- `target_vm_name` - Computer name after rename and for domain join (required when `name` is a logical/key different from final name)
- `vm_winrm_port` (default: `5985`) - WinRM port (5985 HTTP or 5986 HTTPS)
- `vm_winrm_username` - Per-VM WinRM username (overrides playbook-level `winrm_username`)
- `vm_winrm_password` - Per-VM WinRM password (overrides playbook-level `winrm_password`); in production use GitHub Secrets key `winrm_password_<target_vm_name_lower>` or Vault
- `vm_winrm_connect_hostname` - Optional. Current hostname for first WinRM connection when it differs from `target_vm_name` (e.g. migration: connect as `dca-dev7048\user` then rename to `vmcuwinwebd01`)

**Important:** The role builds WinRM username as `computername\username`. Pass only the username (e.g. `cpoeadmin`). For the first connection, the role uses the actual VM hostname (or `vm_winrm_connect_hostname` if set) so authentication succeeds before rename.

## Examples

### Basic Domain Join

```bash
ansible-playbook ansible/playbooks/join-windows-domain.yaml \
  -e "manifest=test_vm_migration" \
  -e "dry_run=false"
```

### Force Rejoin (Testing)

```bash
# Force disjoin and rejoin even if already in target domain
ansible-playbook ansible/playbooks/join-windows-domain.yaml \
  -e "manifest=test_vm_migration" \
  -e "dry_run=false" \
  -e "force_rejoin=true"
```

### With Command-Line Credentials

```bash
# If credentials are NOT in manifest
ansible-playbook ansible/playbooks/join-windows-domain.yaml \
  -e "manifest=test_vm_migration" \
  -e "dry_run=false" \
  -e "winrm_username=cpoeadmin" \
  -e "winrm_password=your_local_admin_password"
```

## Troubleshooting

### WinRM Connectivity

- Ensure target VMs are accessible via WinRM on the port set in the manifest (`vm_winrm_port`, default 5985; 5986 for HTTPS).
- Verify Azure NSG allows that port from the runner (e.g. 5985 or 5986).
- The role disables the Windows Firewall **Public** profile (and **Private** when in WORKGROUP) on the target VM so WinRM stays reachable; if you cannot change firewall, ensure the VM’s firewall allows WinRM for the correct profile.
- The role waits for servers to come back online after each reboot.

### Domain Join Issues

- **Pre-create flow**: The role creates the AD computer object in the target OU *before* disjoining. This avoids delete-by-name (which could kick the source VM off the domain). Set `domain_ou_path` in the manifest (e.g. `OU=Azure,OU=DCA,OU=Servers,DC=dtenet,DC=com` for dtenet.com/Servers/DCA/Azure). The playbook stops if create or verify fails.
- **"The account already exists"**: The pre-create flow creates a new object with the target name. Delete-by-name is disabled to protect the source VM. If you hit "account already exists", the object may exist from a previous run—ensure it is in the correct OU or coordinate with the AD team.
- **Already in domain**: Use `force_rejoin=true` to force disjoin and rejoin
- **Idempotency**: The role checks domain membership before joining. If a server is already in the target domain, it will skip the join operation (unless `force_rejoin=true`)
- **Domain credentials**: For security, use Azure Key Vault (via managed identity in GitHub Actions) or Ansible Vault for storing domain admin credentials
- **OU path format**: Must be in distinguished name format, leaf-to-root. For dtenet.com/Servers/DCA/Azure use `OU=Azure,OU=DCA,OU=Servers,DC=dtenet,DC=com`.

### Security

- **Secrets in logs**: Tasks that use `domain_admin_password` or WinRM passwords use `no_log: true` so credentials are not written to Ansible output or logs.
- **Credential storage**: Pass `domain_admin_password` and WinRM passwords via playbook variables, GitHub Secrets, or Ansible Vault—not in the manifest file.
- **WinRM TLS**: The role uses `ansible_winrm_server_cert_validation: ignore` for connectivity. Where possible, use a CA-signed certificate on the WinRM endpoint and set validation to avoid man-in-the-middle risk.

### Reboot Behavior

- The role reboots after disjoin (when disjoin ran), after rename (when rename ran), and after join. Both post-disjoin and post-join reboots use Azure CLI restart as primary when `use_azure_restart` is true. Controlled via `restart_on_success` (default `true`) and `wait_for_reboot` (default `true`).
- After each reboot it waits for WinRM to come back; after the final (post-join) reboot it verifies domain membership.
- **Post-rename reboot**: After the rename reboot, the role waits an extra `post_rename_reboot_settle_seconds` (default 90) before the first WinRM connection, and retries the hostname verification up to 3 times with 60s delay. This prevents "credentials rejected" when Windows is not fully ready to accept auth immediately after the hostname change.

### Testing Workflow

1. **Dry run first**: Always start with `dry_run=true` to verify configuration
2. **Check manifest**: Ensure `domainNameSetup` section is properly configured
3. **Verify VMs**: Ensure target VMs are listed in the `vms` section of the manifest
4. **Run workflow**: Use GitHub Actions workflow for automated execution
5. **Verify results**: Check workflow logs and verify domain membership on target VMs

### Dependencies

- **GH Runners**: Must be active and have appropriate managed identity for Azure authentication (when VMs are looked up from Azure).
- **Network connectivity**: Runner must reach target VMs on the WinRM port (default 5985; use `vm_winrm_port: 5986` for HTTPS).
- **Domain access**: Domain admin credentials must be able to join computers and, for pre-create, create computer objects in the target OU.
