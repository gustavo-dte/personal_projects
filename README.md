# Cloud Platform GitHub template for App Pattern

This repository serves as a template for building app patterns and related automation configurations.

This template contains starter Terraform code for known environments - dev, test, prod. There are matching folder for each environment, and each environment is configured with dedicated subscription and a Terraform workspace.

## Usage

To create an app pattern from this template, use GitHub's "Use template" feature to copy this template to new repository. After that, the new repository can be cloned and modified as needed.

## Contributing

To contribute to this project, you'll need to install several development tools and configure your environment. Please see our **[Contributing Guide](docs/CONTRIBUTING.md)** for:

- Required software installation (pre-commit, Terraform, terraform-docs, tflint)
- Development environment setup for Windows and macOS
- Pre-commit hook configuration

### 💡 Need Help?

- Check the [Contributing Guide](docs/CONTRIBUTING.md) for detailed instructions
- Review existing issues and pull requests for context
- Contact the development team if you encounter setup difficulties

**Note:** All contributions must pass our automated checks including Terraform validation, linting, and security scans before being merged.
