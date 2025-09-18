# Logs

This directory stores runtime logs produced by the Azure Migrate and Azure Backup Ansible tasks and related PowerShell scripts.

## Log File Patterns

Different operations generate logs with specific prefixes:

- **Azure Migrate - Start Replication**: `AzMigrate_StartReplication_*.log`
- **Azure Migrate - List Projects**: `AzMigrate_ListProjects_*.log`
- **Azure Migrate - Get Replication Status**: `AzMigrate_GetReplicationStatus_*.log`
- **Azure Backup - Enable Protection**: `AzBackup_EnableBackupProtection_*.log`

## Examples

- **Source**: The task `roles/azure_migrate/tasks/start_replication.yml` writes logs using the `AzMigrate_StartReplication_` prefix
- **CI Usage**: GitHub Actions workflows upload these files as artifacts using `actions/upload-artifact@v4`
- **Cleanup**: Files here are generated per run and can be safely deleted. They are not intended to be committed to source control.

## Log Content

Each log file contains:
- **Operation title** and timestamp
- **STDOUT**: Standard output from PowerShell scripts and Azure CLI commands
- **STDERR**: Error output and warnings
- **Structured data**: JSON responses from Azure APIs (when applicable)
