# Cloud Platform VM Migration

This repository contains Ansible playbooks and roles for Azure VM migration operations, including Azure Migrate replication management and Azure Backup protection orchestration.

## Overview

This project provides automated workflows for:
- **Azure Migrate Operations**: Start replication, check replication status, perform migration cutover, list migrate projects
- **Azure Backup Protection**: Enable backup protection for VMs based on replication readiness
- **OS Version Validation**: Ensure VMs meet minimum OS requirements (Windows Server 2019+, RHEL 8+)
- **Manifest-driven Configuration**: Manage multiple VMs through manifest files

## Key Features

- **Idempotent Operations**: Safe to re-run - skips already configured VMs
- **Manifest-driven Configuration**: Centralized VM and environment management
- **Smart Backup Orchestration**: Only enables backup for VMs meeting replication thresholds
- **OS Compatibility Validation**: Configurable minimum OS version checks
- **Comprehensive Logging**: Detailed logs with GitHub Actions artifact upload

## Quick Start

1. **Prerequisites**: Install Ansible, Azure CLI, PowerShell 7, and Azure PowerShell modules
2. **Authentication**: Run `az login` or configure service principal/managed identity
3. **Configuration**: Update `ansible/vars/phase_1/manifest.yml` with your environment details
4. **Execute**: Run playbooks directly or use GitHub Actions workflows

## Main Components

- **`ansible/playbooks/`**: Ready-to-use playbooks for migration operations
- **`ansible/roles/`**: Reusable roles (azure_migrate, azure_backup, common)
- **`ansible/vars/`**: Manifest-specific configuration
- **`.github/workflows/`**: GitHub Actions for automated execution

## Contributing

To contribute to this project, you'll need to install several development tools and configure your environment. Please see our **[Contributing Guide](docs/CONTRIBUTING.md)** for:

- Required software installation (Ansible, Azure CLI, PowerShell, pre-commit)
- Development environment setup for Windows and macOS
- Pre-commit hook configuration

### 💡 Need Help?

- Check the [Contributing Guide](docs/CONTRIBUTING.md) for detailed instructions
- Review the [Ansible README](ansible/README.md) for playbook usage examples
- Contact the development team if you encounter setup difficulties

**Note:** All contributions must pass our automated checks including Ansible linting, YAML validation, and security scans before being merged.
