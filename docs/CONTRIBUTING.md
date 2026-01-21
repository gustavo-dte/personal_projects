# Contributing

This repository uses several pre-commit hooks to maintain code quality. Pre-commit hooks help maintain code quality by automatically checking and formatting code before commits.

For **Windows** Users, these commands must be executed in [Git Bash](https://git-scm.com/downloads/win)

## 1. Install Required Software

Before contributing to this project, you'll need to install the following tools on your development machine.

### terraform

Terraform is used for infrastructure as code management.

**macOS:**

```bash
# Using Homebrew (recommended)
brew tap hashicorp/tap
brew install hashicorp/tap/terraform

# Using tfenv for version management
brew install tfenv
tfenv install 1.6.0
tfenv use 1.6.0
```

**Windows:**

```powershell
# Using Chocolatey (recommended)
choco install terraform

# Manual installation:
# 1. Download from https://www.terraform.io/downloads
# 2. Extract the executable to a directory in your PATH
# 3. Add the directory to your system PATH environment variable
```

**Verify installation:**

```bash
terraform version
```

### terraform-docs

Generates documentation from Terraform modules in various output formats.

**macOS:**

```bash
# Using Homebrew (recommended)
brew install terraform-docs

# Using Go (if you have Go installed)
go install github.com/terraform-docs/terraform-docs@latest
```

**Windows:**

```powershell
# Using Chocolatey
choco install terraform-docs

# Using Scoop
scoop bucket add terraform-docs https://github.com/terraform-docs/scoop-bucket
scoop install terraform-docs

# Using Go (if you have Go installed)
go install github.com/terraform-docs/terraform-docs@latest

# Manual installation:
# 1. Download the latest release from GitHub releases page
# 2. Extract the executable to a directory in your PATH
# 3. Rename the file to terraform-docs.exe if needed
```

**Verify installation:**

```bash
terraform-docs version
```

### tflint

A Terraform linter focused on possible errors, best practices, etc.

**macOS:**

```bash
# Using Homebrew (recommended)
brew install tflint

# Using curl
curl -s https://raw.githubusercontent.com/terraform-linters/tflint/master/install_linux.sh | bash
```

**Windows:**

```powershell
# Using Chocolatey (recommended)
choco install tflint

# Manual installation:
# 1. Download the latest Windows release from GitHub
# 2. Extract tflint.exe to a directory in your PATH
# 3. Verify the executable is accessible from command prompt
```

**Verify installation:**

```bash
tflint --version
```

### pre-commit

Pre-commit manages and maintains multi-language pre-commit hooks for version control.

**macOS:**

```bash
# Using pip (recommended)
pip install pre-commit

# Using Homebrew
brew install pre-commit
```

**Windows:**

```powershell
# Using pip (recommended)
pip install pre-commit
```

**Verify installation:**

```bash
pre-commit --version
```

## 2. Install pre-commit Hooks

```bash
# Install the pre-commit hooks defined in .pre-commit-config.yaml
pre-commit install

# Optional: Run hooks against all files to verify setup
pre-commit run --all-files
```

## 3. Running pre-commit

### Automatic Execution

Pre-commit hooks run automatically on every `git commit`. If any hook fails, the commit is rejected and you'll need to fix the issues.

```bash
git add .
git commit -m "Your commit message"
# Hooks will run automatically
```
