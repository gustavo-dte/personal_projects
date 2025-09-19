# Cloud Platform VM Migration

This repository contains Ansible playbooks and roles for automated Azure VM migration operations.

## Main Components

- **`ansible/playbooks/`**: Ready-to-use playbooks for migration operations
- **`ansible/roles/`**: Reusable roles (azure_migrate, azure_backup, common)
- **`ansible/vars/`**: Manifest-specific configuration
- **`.github/workflows/`**: GitHub Actions for automated execution

## How to Run Playbooks

1. Navigate to the [Actions](https://github.com/dteenergy/cloud-platform-vm-migration/actions) tab.
2. Select the desired workflow, and click `Run workflow`.
3. Provide any required inputs (such as manifest names) and execute.

![Run Workflow](docs/assets/playbook.png)

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
