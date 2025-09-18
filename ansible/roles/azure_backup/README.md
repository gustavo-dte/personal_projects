## Azure Backup Role

### Table of contents
- [Description](#description)
- [Requirements](#requirements)
- [Role Variables (selected)](#role-variables-selected)
- [Outputs](#outputs)
- [Example Plays](#example-plays)
- [Notes](#notes)
- [Troubleshooting](#troubleshooting)
- [Local manual testing: running the playbook](#local-manual-testing-running-the-playbook)
- [Manifest-driven configuration](#manifest-driven-configuration)

### Description
Orchestrates Azure Backup protection for virtual machines based on Azure Migrate replication status:
- **enable_backup_protection**: Check Azure Migrate replication status first, then enable Azure Backup protection only for VMs that meet the configurable replication threshold.

The role follows this workflow:
1. Loads VMs from the manifest configuration
2. Checks Azure Migrate replication status using PowerShell (`Get-AzMigrateServerReplication`)
3. Identifies VMs that meet the replication threshold (configurable, default 80%)
4. Enables Azure Backup protection only for VMs that are ready (using Azure Collections)

Authentication uses Azure Collections authentication methods (Service Principal, Managed Identity, or Azure CLI session) for backup operations and PowerShell Az modules for Azure Migrate operations.

### Requirements
- **Ansible**: >= 2.14
- **Collections**: `azure.azcollection` >= 1.1.0
- **CLI/Modules on controller/runner**:
  - PowerShell 7 (`pwsh`)
  - Az PowerShell modules: `Az.Accounts`, `Az.Migrate`
- Azure credentials: Service Principal, Managed Identity, or Azure CLI session (run `az login` before using the role)
- **Azure Resources**:
  - Recovery Services vault must exist in the target resource group
  - Azure Migrate project with discovered and replicating VMs

### Role Variables (selected)
- **Required**
  - Required values are sourced from manifest (see Manifest-driven configuration): `target_resource_group`, `vms` list, `recovery_vault_name`, `azure_migrate_project_name`.

- **Behavior**
  - `backup_action`: Currently only `enable_backup_protection` (default: `enable_backup_protection`)
  - `backup_actions`: Allowed values list; used for validation

- **Azure Backup Configuration** (loaded from manifest)
  - `recovery_vault_name`: **Required** - Name of the Recovery Services vault (global default)
  - `backup_policy_name`: Backup policy to apply to VMs (global default: `DefaultPolicy`)
  - `replication_threshold`: Percentage threshold for Azure Migrate replication completion (global default: 80)
  - VM-specific overrides: Each VM can override these settings in its `backup` section

- **Selection and iteration**
  - Manifest-driven: the role loads `ansible/vars/{manifest}/manifest.yml` and processes VMs from `vms` list.

### Outputs
- `enable_backup_protection` registers and displays:
  - `replication_status_results` (Azure Migrate replication status for each VM)
  - `vms_ready_for_backup` (list of VMs that meet the replication threshold)
  - `enable_protection_results` (Azure CLI command results for backup protection)
  - Summary statistics and detailed per-VM results for both replication status and backup protection

### Example Plays

#### Enable Azure Backup protection (manifest-driven)
```yaml
- hosts: localhost
  gather_facts: false
  roles:
    - role: azure_backup
      vars:
        backup_action: enable_backup_protection      # action: enable backup protection
        manifest: "{{ manifest }}"                   # pass through manifest variable (never hardcode)
        # All backup configuration is loaded from manifest file:
        # - recovery_vault_name (global default, can be overridden per VM)
        # - backup_policy_name (global default: DefaultPolicy, can be overridden per VM)
        # - replication_threshold (global default: 80, can be overridden per VM)
```

**Command line usage:**
```bash
# User specifies which manifest to load at runtime
# All backup configuration comes from the manifest file
ansible-playbook my-playbook.yml -e "manifest=phase_1"
```

### Notes
- The role performs early validation and will fail if required variables are missing.
- **Authentication**: This role expects Azure authentication to be handled externally. Run `az login` before executing the playbook locally, or use GitHub Actions which handles authentication automatically.
- **Two-stage process**: First checks Azure Migrate replication status using PowerShell, then enables backup protection using Azure Collections.
- Only VMs that meet the replication threshold will have backup protection enabled.
- The role uses `Get-AzMigrateServerReplication` PowerShell cmdlet to check replication status.
- The role uses `azure.azcollection.azure_rm_backupazurevm` module to enable Azure Backup protection.
- **Built-in Idempotency**: The Azure Collections module automatically handles idempotency and will not re-enable protection for already protected VMs.
- **Better Error Handling**: Azure Collections provide structured error responses and better integration with Ansible.

### Troubleshooting
- Azure CLI not found: ensure Azure CLI is installed and available in PATH.
- PowerShell not found: ensure PowerShell 7 (`pwsh`) is installed and available in PATH.
- Missing modules errors (e.g., `Az.Migrate`): install with `Install-Module -Name Az.Migrate -Scope CurrentUser -Force`.
- Authentication failures: run `az login` to authenticate with Azure before running the role.
- Recovery Services vault not found: confirm the vault exists in the target resource group and the account has proper permissions.
- Azure Migrate project not found: confirm the project exists and contains discovered/replicating VMs.
- VM replication not found: ensure VMs are discovered and replicating in the Azure Migrate project.
- Permission errors: ensure the authenticated account has Backup Contributor permissions on the Recovery Services vault and Azure Migrate Contributor permissions on the migrate project.

### Local manual testing: running the playbook
The examples below show how to run the role's playbook locally. **Important**: Authenticate to Azure first using `az login` before running these commands.

#### Prerequisites
- Ansible installed (>= 2.14)
- Azure Collections (`azure.azcollection`) installed: `ansible-galaxy collection install azure.azcollection`
- PowerShell 7 (`pwsh`) installed
- Az PowerShell modules: `Az.Accounts`, `Az.Migrate`
- Azure authentication configured (Service Principal, Managed Identity, or `az login`)
- Recovery Services vault must exist in the target resource group
- Azure Migrate project with discovered and replicating VMs
- Appropriate Azure permissions (Backup Contributor and Azure Migrate Contributor)

#### Enable Azure Backup protection (manifest-driven)
```bash
# Enable backup protection using manifest configuration
ansible-playbook ansible/playbooks/azure-backup-protection.yml -e "manifest=phase_1"
```

### Manifest-driven configuration
The role loads manifest from `ansible/vars/{manifest}/manifest.yml` at runtime. Structure:

```yaml
# Global defaults
azure_migrate_project_name: my-migrate-proj
azure_migrate_project_resource_group: rg-migrate
target_subscription_id: 00000000-0000-0000-0000-000000000000
target_resource_group: rg-target

# Azure Backup defaults (global)
recovery_vault_name: my-recovery-vault
backup_policy_name: DefaultPolicy
replication_threshold: 80

# List of VMs to check for replication status and enable backup protection
vms:
  - name: app01
    portfolio: Team1
    tier: 4
    # Uses global backup defaults

  - name: app02
    portfolio: Team2
    tier: 2
    backup:
      recovery_vault_name: my-special-vault  # Override global default
      backup_policy_name: CustomPolicy       # Override global default
      replication_threshold: 90              # Override global default

  - name: db01
    portfolio: Team2
    tier: 2
    # Uses global backup defaults
```

Notes:
- The role extracts VM names from the `vms` list in the manifest
- VMs are first checked for Azure Migrate replication status using global or VM-specific `replication_threshold`
- Only VMs that meet the replication threshold will have backup protection enabled
- Each VM can override global backup settings in its `backup` section
- Global backup configuration is defined at the manifest root level
- The role uses the global `azure_migrate_project_name`, `target_resource_group` and `target_subscription_id` settings
