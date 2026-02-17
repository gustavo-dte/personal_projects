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

## Tips
- Increase verbosity: add `-vvv`
- Show diffs for templates/changes: add `--diff`
- Limit to specific hosts (if not localhost): `--limit` (not typically needed here)
