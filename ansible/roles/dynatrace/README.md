# Dynatrace Role

This role configures the Dynatrace OneAgent extension on Azure VMs (both Windows and Linux).

## Description

The Dynatrace role:
1. **Verifies migration status** - Checks that the VM has completed migration (MigrationState = MigrationSucceeded)
2. **Checks VM state** - Ensures the VM is running before attempting extension installation
3. **Installs Dynatrace extension** - Configures the Dynatrace OneAgent extension on the VM
4. **Handles idempotency** - Skips installation if extension is already installed
5. **Supports dry-run** - Test mode to validate without making changes

## Requirements

- Azure subscription with appropriate permissions
- Azure VMs must be in "running" state
- VMs must have completed migration (MigrationState = MigrationSucceeded)
- Azure PowerShell modules: Az.Accounts, Az.Compute, Az.Migrate

## Role Variables

### Required Variables (from manifest)

```yaml
# VM configuration
vms:
  - name: vm-name-01
    target_resource_group: rg-example
    target_subscription_id: <subscription-guid>
    
# Azure Migrate project (for migration status check)
azure_migrate_project_name: azure-migrate-project
azure_migrate_project_resource_group: rg-migrate
azure_migrate_subscription_id: <subscription-guid>
```

### Optional Variables

```yaml
# Dynatrace configuration
dynatrace_environment_url: ""  # Dynatrace environment URL (optional)
dynatrace_api_token: ""        # Dynatrace API token (optional)
dynatrace_extension_version: "latest"  # Extension version

# Operation mode
dry_run: false
os_type: "windows"  # or "linux"
```

## Dependencies

- `common` role - Provides common utilities and manifest loading

## Example Usage

### In a Playbook

```yaml
- name: Configure Dynatrace on Windows VMs
  hosts: localhost
  roles:
    - role: common
    - role: dynatrace
      vars:
        os_type: windows
        dry_run: false
```

### Via GitHub Actions Workflow

1. Navigate to GitHub Actions
2. Select "Ansible-Configure-Dynatrace" workflow
3. Provide inputs:
   - **manifest**: Name of manifest directory (e.g., `demo`, `phase_1`)
   - **os_type**: Choose `windows`, `linux`, or `both`
   - **dry_run**: Check for test mode

## Migration Status Check

Before configuring Dynatrace, the role verifies the VM migration status using Azure Migrate:

### Required Migration State

```
MigrationState: MigrationSucceeded
```

### Behavior

- ✅ **If MigrationSucceeded**: Proceeds with Dynatrace configuration
- ❌ **If any other state**: Stops execution with detailed error message

Example states that will stop execution:
- `MigrationInProgress`
- `MigrationFailed`
- `NotStarted`
- `ReadyToMigrate`

## Extension Installation Process

### Windows VMs

1. Checks if VM is running
2. Verifies no existing Dynatrace extension
3. Installs `dynatrace.ruxit/oneAgentWindows` extension
4. Returns installation status

### Linux VMs

1. Checks if VM is running
2. Verifies no existing Dynatrace extension
3. Installs `dynatrace.ruxit/oneAgentLinux` extension
4. Returns installation status

## Return Values

The role returns a `dynatrace_result` object for each VM:

```yaml
dynatrace_result:
  VMName: "vm-name"
  Success: true
  ExtensionStatus: "Installed"  # or "AlreadyInstalled", "DryRun", "Failed", "Skipped"
  ExtensionVersion: "2.0"
  Message: "Dynatrace extension installed successfully"
  Error: null
  StartTime: "2024-01-01 10:00:00"
  EndTime: "2024-01-01 10:05:00"
```

### Extension Status Values

- `Installed` - Extension was successfully installed
- `AlreadyInstalled` - Extension was already present
- `DryRun` - Dry run mode, no changes made
- `Failed` - Installation failed
- `Skipped` - VM not running or other condition preventing installation

## Error Handling

### Migration Not Completed

```
❌ Cannot configure Dynatrace extension for VM 'vm-name'

Migration Status: MigrationInProgress
Migration Description: Migration in progress

Dynatrace extension can only be configured on VMs that have completed migration.
Current migration state must be 'MigrationSucceeded' to proceed.

Required: MigrationState = MigrationSucceeded
Current:  MigrationState = MigrationInProgress

Please complete the migration for this VM before attempting to configure Dynatrace.
```

### VM Not Running

```
WARNING: VM is not running (current state: stopped). 
Extension can only be installed on running VMs.
```

## Logging

All operations are logged to:
- Windows: `ansible/logs/Dynatrace_Windows_*.log`
- Linux: `ansible/logs/Dynatrace_Linux_*.log`

Logs include:
- VM name and resource group
- Migration status verification
- Extension installation details
- Success/failure status
- Timestamps

## Example Manifest

```yaml
# manifest.yml
azure_migrate_project_name: azure-migrate-automation
azure_migrate_project_resource_group: rg-migrate
target_subscription_id: <subscription-guid>

vms:
  - name: app-server-01
    target_resource_group: rg-production-ue
    target_subscription_id: <subscription-guid>
    
  - name: web-server-02
    target_resource_group: rg-production-ue
    target_subscription_id: <subscription-guid>
```

## Troubleshooting

### Extension Installation Fails

1. Verify VM is running: `az vm get-instance-view -g <rg> -n <vm-name>`
2. Check VM has internet connectivity
3. Verify Azure permissions for extension installation
4. Review detailed logs in `ansible/logs/`

### Migration Status Check Fails

1. Verify Azure Migrate project exists
2. Check project name and resource group are correct
3. Verify permissions on Azure Migrate project
4. Ensure VM was actually migrated using Azure Migrate

### Dry Run Recommended

Always test with `dry_run: true` first:

```bash
ansible-playbook playbooks/configure-dynatrace-windows.yml \
  -e "manifest=demo" \
  -e "dry_run=true"
```

## License

MIT

## Author Information

DTE Cloud Platform Team
