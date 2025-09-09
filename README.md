# Cloud Application ServiceBus Replication

> **Beta**: This project is under active development. Features and APIs may change.

## Overview

Cloud Application ServiceBus Replication provides a robust solution for replicating messages across Azure ServiceBus instances using topics and subscriptions, enabling reliable cloud-native communication and disaster recovery for enterprise applications.

## Features

- 🔄 **Message Replication**: Seamlessly replicate messages between ServiceBus namespaces using topics and subscriptions.
- ⚡ **High Availability**: Designed for fault tolerance and business continuity.
- 🔒 **Secure by Default**: Follows Azure security best practices.
- 🛠️ **Extensible**: Easily integrate with existing cloud workflows.
- 🧪 **Pre-commit & CI/CD**: Automated checks and workflows for code quality.

## Getting Started

### Prerequisites

- Python 3.11+
- Azure ServiceBus access
- [Poetry](https://python-poetry.org/) or [pip](https://pip.pypa.io/en/stable/)

### Installation

```fish
# Clone the repository
git clone https://github.com/dteenergy/cloud-application-servicebus-replication.git
cd cloud-application-servicebus-replication

# (Optional) Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt  # or use Poetry
```

### Configuration

- Update your Azure credentials and ServiceBus settings in your environment or configuration files as needed.

## Usage

```fish
# Run the main application
python src/main.py
```

## Development

### Pre-commit Hooks

This project uses [pre-commit](https://pre-commit.com/) for code quality checks. To set up:

```fish
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

### Linting & Formatting

- [Ruff](https://github.com/astral-sh/ruff): Fast Python linter & formatter
- [mypy](http://mypy-lang.org/): Static type checker

```fish
ruff src/
mypy src/
```

### Testing

Add your tests in the `tests/` directory and run them using your preferred test runner.

## CI/CD

GitHub Actions automate checks for every push and pull request:

- Pre-commit validation
- Author assignment
- Secure secrets management

## Project Structure

```
cloud-application-servicebus-replication/
├── src/
│   └── main.py
├── pyproject.toml
├── .pre-commit-config.yaml
├── .github/
│   └── workflows/
│       ├── on-pull-request.yaml
│       └── on-push.yaml
└── README.md
```

## Resources

- [Azure ServiceBus Documentation](https://learn.microsoft.com/en-us/azure/service-bus-messaging/)
- [DTE Energy GitHub](https://github.com/dteenergy)

> [!TIP]
> For questions or support, open an issue in this repository.
