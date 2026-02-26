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

## Tips
- Increase verbosity: add `-vvv`
- Show diffs for templates/changes: add `--diff`
- Limit to specific hosts (if not localhost): `--limit` (not typically needed here)
