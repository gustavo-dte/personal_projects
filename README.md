# Azure Service Bus Message Replication

A reliable, enterprise-grade Azure Function for dynamically replicating messages between Service Bus namespaces to support disaster recovery and cross-region resilience.

## ✨ What Does This Do?

This application automatically discovers and replicates messages from ALL topics and subscriptions in one Azure Service Bus namespace to another, helping you:

- **🔄 Disaster Recovery**: Keep your messages safe if one region goes down
- **🌍 Cross-Region Backup**: Maintain message copies across different Azure regions  
- **📈 Business Continuity**: Meet your RTO (Recovery Time Objective) requirements
- **💾 Zero Message Loss**: Ensure critical business messages aren't lost during outages
- **🎯 Dynamic Discovery**: Automatically replicates ALL topics and subscriptions without manual configuration

## 📊 Quality Metrics

- ✅ **Type Safety**: 100% mypy compliant
- ✅ **Test Coverage**: 82% (exceeds 70% requirement)
- ✅ **Code Quality**: Ruff linting with zero issues
- ✅ **Security**: Bandit security scanning
- ✅ **CI/CD**: Comprehensive GitHub Actions pipeline

## 🚀 Quick Start

### Prerequisites
- **Python 3.11+**
- **Azure subscription** with two Service Bus namespaces (primary and secondary)
- **Azure Functions Core Tools** (for local development)

### Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd cloud-application-servicebus-replication
   ```

2. **Set up Python environment:**
   ```bash
   # Create and activate virtual environment
   python -m venv .venv
   
   # Windows
   .venv\Scripts\activate
   
   # Linux/Mac
   source .venv/bin/activate
   
   # Install dependencies (includes both runtime and development dependencies)
   pip install -r requirements.txt
   ```

3. **Install development tools:**
   ```bash
   # Install pre-commit hooks for code quality
   pre-commit install
   
   # Run initial quality checks
   pre-commit run --all-files
   ```

### Configuration

1. **Set required environment variables:**
   ```bash
   # Replication direction
   REPLICATION_TYPE=primary_to_secondary
   
   # Connection strings
   PRIMARY_SERVICEBUS_CONN="Endpoint=sb://your-primary.servicebus.windows.net/;..."
   SECONDARY_SERVICEBUS_CONN="Endpoint=sb://your-secondary.servicebus.windows.net/;..."
   ```

2. **For local development**, copy `local.settings.example.json` to `local.settings.json` and fill in your values.

### Run Locally

```bash
# Start the Azure Functions runtime
func start --python

# The function will run every 30 seconds and replicate messages
```

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [📋 Configuration Guide](./docs/CONFIGURATION.md) | Complete configuration reference and examples |
| [🚀 Deployment Guide](./docs/DEPLOYMENT.md) | Deploy to Azure Functions, containers, or Kubernetes |
| [🏗️ Architecture](./docs/ARCHITECTURE.md) | How the replication works under the hood |
| [💻 Development Guide](./docs/DEVELOPMENT.md) | Contributing, testing, and development workflow |
| [🔧 Troubleshooting](./docs/TROUBLESHOOTING.md) | Common issues and solutions |

## 📁 Project Structure

```
cloud-application-servicebus-replication/
├── src/                          # Main source code
│   ├── main.py                   # Azure Function entry point
│   ├── config.py                 # Configuration management
│   ├── message_utils.py          # Message processing utilities
│   └── ...                       # Additional modules
├── tests/                        # Comprehensive test suite (82% coverage)
├── docs/                         # Detailed documentation
├── .github/workflows/ci.yml      # CI/CD pipeline
├── requirements.txt              # Python dependencies (runtime + development)
└── README.md                     # This file
```

## 🤝 Contributing

We welcome contributions! Please see our [Development Guide](./docs/DEVELOPMENT.md) for:
- Development workflow and standards
- Testing requirements
- Code quality guidelines
- Pull request process

## 📞 Support

- **🐛 Bug Reports**: [Create an issue](https://github.com/your-org/cloud-application-servicebus-replication/issues)
- **💡 Feature Requests**: [Start a discussion](https://github.com/your-org/cloud-application-servicebus-replication/discussions)
- **❓ Questions**: Check [Troubleshooting Guide](./docs/TROUBLESHOOTING.md) first

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

⭐ **Star this repo** if you find it useful!