# Ansible Runbook

This repository contains playbooks and roles for Azure VM backup orchestration, Azure Migrate operations, and generating Terraform from existing Azure resources.

## Setup
- Install collections:
```bash
ansible-galaxy collection install -r requirements.yml
```

## Pre-flight
- Syntax check:
```bash
ansible-playbook -i localhost, playbooks/azure-backup-protection.yml --syntax-check
```
- Dry run (where meaningful):
```bash
ansible-playbook -i localhost, playbooks/azure-backup-protection.yml --check
```
- List tasks / tags:
```bash
ansible-playbook playbooks/azure-backup-protection.yml --list-tasks
ansible-playbook playbooks/azure-backup-protection.yml --list-tags
```

## Playbooks and abilities

### 1) Azure VM Backup Orchestrator (`playbooks/azure-backup-protection.yml`)
Orchestrates enabling Azure Backup protection based on Azure Migrate replication status.

- Key vars:
  - `manifest`: **Required** - Environment selector for loading manifest (e.g., 'phase_1', 'phase_2', 'phase_3')
  - All backup configuration is loaded from the manifest file:
    - `recovery_vault_name`: Name of the Recovery Services vault (global default)
    - `backup_policy_name`: Backup policy to apply (global default: `DefaultPolicy`)
    - `replication_threshold`: Azure Migrate replication threshold percentage (global default: 80)
    - VM-specific overrides: Each VM can override these settings in its `backup` section

- Example:
```bash
# Enable backup protection for VMs that meet replication threshold
# All backup configuration comes from the manifest file
ansible-playbook playbooks/azure-backup-protection.yml \
  -e "manifest=phase_1"
```

### 2) Azure Migrate – list projects (`playbooks/list-migrate-projects.yml`)
Lists Azure Migrate projects in a resource group.

```bash
ansible-playbook playbooks/list-migrate-projects.yml -e resource_group=rg-migrate
```

### 3) Azure Migrate – start replication (`playbooks/start-migration-replication.yml`)
Starts replication for VMs with idempotent handling - skips VMs that already have replication enabled.

- Key vars:
  - `manifest`: **Required** - Environment selector for loading manifest
  - All configuration loaded from manifest file

- Example:
```bash
ansible-playbook playbooks/start-migration-replication.yml -e "manifest=phase_1"
```

## Tips
- Increase verbosity: add `-vvv`
- Show diffs for templates/changes: add `--diff`
- Limit to specific hosts (if not localhost): `--limit` (not typically needed here)
