# Azure Service Bus Message Replication

A reliable, enterprise-grade Azure Function for dynamically replicating messages between Service Bus namespaces to support disaster recovery and cross-region resilience.

## ✨ **What Does This Do?**

This application automatically discovers and replicates messages from ALL topics and subscriptions in one Azure Service Bus namespace to another, helping you:

- **🔄 Disaster Recovery**: Keep your messages safe if one region goes down
- **🌍 Cross-Region Backup**: Maintain message copies across different Azure regions  
- **📈 Business Continuity**: Meet your RTO (Recovery Time Objective) requirements
- **💾 Zero Message Loss**: Ensure critical business messages aren't lost during outages
- **🎯 Dynamic Discovery**: Automatically replicates ALL topics and subscriptions without manual configuration

The application works as a timer-triggered Azure Function that runs every 30 seconds, dynamically discovers all topics and subscriptions, then replicates any pending messages to your secondary Service Bus namespace.

## 🏗️ **Architecture Overview**

1. **Timer Trigger**: The function runs every 30 seconds automatically
2. **Dynamic Discovery**: It discovers all topics and subscriptions in the source namespace
3. **Message Processing**: For each subscription, it retrieves up to 10 pending messages
4. **Message Replication**: Creates enhanced copies with tracking metadata
5. **Cross-Namespace Send**: Sends copies to the corresponding topic in the destination namespace
6. **Message Completion**: Marks original messages as complete only after successful replication
7. **Error Handling**: If sending fails, messages are abandoned for retry on the next cycle
8. **Comprehensive Logging**: All operations are logged for monitoring and troubleshooting

## 📊 **Quality Metrics**

This project maintains enterprise-grade quality standards:

- ✅ **Type Safety**: 100% mypy compliant (16 files checked)
- ✅ **Test Coverage**: 82% (exceeds 70% requirement)
- ✅ **Code Quality**: Ruff linting with zero issues
- ✅ **Security**: Bandit security scanning
- ✅ **CI/CD**: Comprehensive GitHub Actions pipeline
- ✅ **Pre-commit Hooks**: Automated quality checks

## 📁 **Project Structure**

```
personal_projects/
├── src/                          # Main source code
│   ├── main.py                   # Azure Function entry point & timer trigger
│   ├── config.py                 # Configuration management with Pydantic v2
│   ├── message_utils.py          # Message processing & enhancement utilities
│   ├── retry_utils.py            # Retry logic with exponential backoff
│   ├── logging_utils.py          # Centralized logging with Azure Monitor
│   ├── error_handlers.py         # Comprehensive error handling utilities
│   ├── exceptions.py             # Custom exception classes
│   ├── constants.py              # Application constants
│   └── function.json             # Azure Functions timer trigger config
├── tests/                        # Comprehensive unit tests (82% coverage)
│   ├── main_test.py              # Main functionality tests
│   ├── error_handlers_test.py    # Error handling tests
│   ├── message_utils_test.py     # Message utilities tests
│   ├── retry_utils_test.py       # Retry mechanism tests
│   ├── exceptions_test.py        # Custom exception tests
│   └── __init__.py               # Test package
├── .github/                      # GitHub Actions workflows
│   └── workflows/
│       └── ci.yml                # Comprehensive CI/CD pipeline
├── requirements.txt              # Runtime dependencies
├── dev-requirements.txt          # Development dependencies
├── pyproject.toml               # mypy and tool configuration
├── host.json                    # Azure Functions host configuration
├── local.settings.example.json  # Example local development settings
├── CLEANUP_SUMMARY.md           # Detailed cleanup and improvements log
├── .gitignore                   # Git ignore patterns
├── .editorconfig               # Editor configuration
└── .pre-commit-config.yaml      # Code quality hooks
```

## 🚀 **Getting Started**

### Prerequisites

Before you start, you'll need:

- **Python 3.11+** (Type-safe, modern Python)
- **Azure subscription** with two Service Bus namespaces (primary and secondary)
- **Azure Functions Core Tools** (for local development)
- **Access permissions** to create topics and subscriptions in both namespaces

### Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd cloud-application-servicebus-replication
   ```

2. **Set up Python environment:**
   ```bash
   # Create virtual environment
   python -m venv .venv

   # Activate it (Windows)
   .venv\Scripts\activate

   # Activate it (Linux/Mac)
   source .venv/bin/activate

   # Install runtime dependencies
   pip install -r requirements.txt
   
   # Install development dependencies (for testing and linting)
   pip install -r dev-requirements.txt
   ```

3. **Install development tools:**
   ```bash
   # Install pre-commit hooks for code quality
   pre-commit install
   
   # Run initial quality checks
   pre-commit run --all-files
   ```

4. **Verify installation:**
   ```bash
   # Run type checking
   mypy src/ tests/
   
   # Run linting
   ruff check src/ tests/
   
   # Run tests with coverage
   pytest tests/ --cov=src --cov-report=term-missing
   ```

## ⚙️ **Configuration**

### Required Environment Variables

You need to configure these environment variables for the application to work:

#### **Replication Settings**
```bash
# Direction of replication - REQUIRED
REPLICATION_TYPE=primary_to_secondary
# Options: "primary_to_secondary" or "secondary_to_primary"
```

#### **For Primary → Secondary Replication**
```bash
# Primary Service Bus (source) - REQUIRED for primary_to_secondary mode
PRIMARY_SERVICEBUS_CONN="Endpoint=sb://your-primary-sb.servicebus.windows.net/;SharedAccessKeyName=..."

# Secondary Service Bus (destination) - REQUIRED for primary_to_secondary mode  
SECONDARY_SERVICEBUS_CONN="Endpoint=sb://your-secondary-sb.servicebus.windows.net/;SharedAccessKeyName=..."
```

#### **For Secondary → Primary Replication**
```bash
# Primary Service Bus (destination) - REQUIRED for secondary_to_primary mode
PRIMARY_SERVICEBUS_CONN="Endpoint=sb://your-primary-sb.servicebus.windows.net/;SharedAccessKeyName=..."

# Secondary Service Bus (source) - REQUIRED for secondary_to_primary mode
SECONDARY_SERVICEBUS_CONN="Endpoint=sb://your-secondary-sb.servicebus.windows.net/;SharedAccessKeyName=..."
```

> **Note**: Topic names are automatically discovered. The function will replicate ALL topics and subscriptions from the source namespace to corresponding topics in the destination namespace.

#### **Timing Configuration (Optional)**
```bash
# Recovery Time Objective in minutes (default: 10)
RTO_MINUTES=30

# Additional buffer time in minutes (default: 2)
DELTA_MINUTES=5
```

#### **Monitoring (Optional)**
```bash
# Application Insights for telemetry
APPLICATIONINSIGHTS_CONNECTION_STRING="InstrumentationKey=..."
# OR
APPINSIGHTS_INSTRUMENTATIONKEY="your-instrumentation-key"
```

### Configuration Examples

#### **Example 1: East US → West US Complete Namespace Backup**
```bash
REPLICATION_TYPE=primary_to_secondary
PRIMARY_SERVICEBUS_CONN="Endpoint=sb://myapp-eastus.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=..."
SECONDARY_SERVICEBUS_CONN="Endpoint=sb://myapp-westus.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=..."
RTO_MINUTES=15
DELTA_MINUTES=3
```

#### **Example 2: Development Environment Complete Replication**
```bash
REPLICATION_TYPE=primary_to_secondary  
PRIMARY_SERVICEBUS_CONN="Endpoint=sb://myapp-dev.servicebus.windows.net/;SharedAccessKeyName=..."
SECONDARY_SERVICEBUS_CONN="Endpoint=sb://myapp-dev-backup.servicebus.windows.net/;SharedAccessKeyName=..."
RTO_MINUTES=5
```

#### **Example 3: Failback Scenario (Secondary → Primary)**
```bash
REPLICATION_TYPE=secondary_to_primary
PRIMARY_SERVICEBUS_CONN="Endpoint=sb://myapp-primary-restored.servicebus.windows.net/;SharedAccessKeyName=..."
SECONDARY_SERVICEBUS_CONN="Endpoint=sb://myapp-secondary.servicebus.windows.net/;SharedAccessKeyName=..."
RTO_MINUTES=10
```

### Local Development Setup

Create a `local.settings.json` file in the project root:

```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "REPLICATION_TYPE": "primary_to_secondary",
    "PRIMARY_SERVICEBUS_CONN": "your-primary-connection-string",
    "SECONDARY_SERVICEBUS_CONN": "your-secondary-connection-string",
    "RTO_MINUTES": "10",
    "DELTA_MINUTES": "2"
  }
}
```

> **Note**: Use `local.settings.example.json` as a template. The function will automatically discover and replicate all topics and subscriptions.

## Usage

### Running Locally

```bash
# Start the Azure Functions runtime
func start

# The timer function will start automatically and run every 30 seconds
# Monitor the console output for replication activity:
# - "Found X topics: [topic1, topic2, ...]" 
# - "Found X subscriptions for topic 'Y': [sub1, sub2, ...]"
# - "Processing topic/subscription"
# - "✅ Replicated message correlation_id from topic/subscription"

# Function endpoint (for monitoring only):
# http://localhost:7071/admin/functions/main
```

### GitHub Actions Workflow

This repository includes a comprehensive CI/CD pipeline that runs automatically on pushes and pull requests to the main branch.

#### **Automatic Workflow Triggers**

The workflow runs automatically when:
- Code is pushed to the `main` branch
- Pull requests are opened against the `main` branch
- Changes are made to workflow files

#### **Pipeline Stages**

1. **Test** - Runs the full test suite with pytest
2. **Security Scan** - Uses Bandit to scan for security vulnerabilities
3. **Code Quality** - Runs linting and code analysis with ruff
4. **Build** - Validates the application structure and creates deployment artifacts
5. **Integration Test** - Currently skipped (no integration tests directory exists)
6. **Notify** - Simple console logging of build status (not real notifications)

#### **Using GitHub Actions for Manual Deployment**

While the current workflow focuses on CI/CD, you can enhance it for manual deployments by adding workflow dispatch inputs. Here's how to modify the workflow file (`.github/workflows/ci.yml`):

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
  workflow_dispatch:  # Enable manual triggers
    inputs:
      environment:
        description: 'Target environment'
        required: true
        default: 'staging'
        type: choice
        options:
          - staging
          - production
      replication_type:
        description: 'Replication direction'
        required: true
        default: 'primary_to_secondary'
        type: choice
        options:
          - primary_to_secondary
          - secondary_to_primary
      rto_minutes:
        description: 'Recovery Time Objective (minutes)'
        required: false
        default: '10'
```

#### **Manual Workflow Execution**

To run the workflow manually:

1. Go to your repository on GitHub
2. Click the **Actions** tab
3. Select **CI/CD Pipeline** from the workflow list
4. Click **Run workflow**
5. Fill in the required parameters:
   - **Environment**: Choose staging or production
   - **Replication Type**: Select the direction of data flow
   - **RTO Minutes**: Set your recovery time objective

#### **Environment-Specific Configurations**

For production deployments, set up environment secrets in your GitHub repository:

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Add environment-specific secrets:

```bash
# Production Environment
PROD_SECONDARY_SERVICEBUS_CONN
PROD_SECONDARY_TOPIC_NAME
PROD_APPLICATIONINSIGHTS_CONNECTION_STRING

# Staging Environment
STAGING_SECONDARY_SERVICEBUS_CONN
STAGING_SECONDARY_TOPIC_NAME
STAGING_APPLICATIONINSIGHTS_CONNECTION_STRING
```

#### **Monitoring Workflow Results**

- **✅ Success**: All tests pass, code is clean, deployment ready
- **❌ Failure**: Check the logs for specific error messages
- **📊 Reports**: Security and code quality reports available in workflow artifacts

#### **Best Practices**

- Always test changes in staging before production
- Monitor the Application Insights dashboard after deployments
- Use descriptive commit messages to track changes
- Review security scan results before merging PRs

### Testing the Function

The function automatically discovers and processes all topics, so you can test by sending messages to any topic in your source namespace:

```python
# Quick test script - send to any topic
from azure.servicebus import ServiceBusClient, ServiceBusMessage

async def send_test_message():
    conn_str = "your-primary-connection-string"
    topic_name = "any-existing-topic"  # Function will discover this automatically

    async with ServiceBusClient.from_connection_string(conn_str) as client:
        sender = client.get_topic_sender(topic_name)
        message = ServiceBusMessage("Test message for replication")
        await sender.send_messages(message)
        print(f"Test message sent to {topic_name}!")

# The function will automatically:
# 1. Discover this topic in the next 30-second cycle
# 2. Find the message in any subscription 
# 3. Replicate it to the corresponding topic in the destination namespace
```

### Deployment to Azure

1. **Create Azure Function App:**
   ```bash
   az functionapp create --resource-group myResourceGroup \
     --consumption-plan-location eastus \
     --runtime python --runtime-version 3.11 \
     --functions-version 4 \
     --name myapp-servicebus-replication \
     --storage-account mystorageaccount
   ```

2. **Deploy the function:**
   ```bash
   func azure functionapp publish myapp-servicebus-replication
   ```

3. **Configure environment variables in Azure:**
   ```bash
   az functionapp config appsettings set --name myapp-servicebus-replication \
     --resource-group myResourceGroup \
     --settings REPLICATION_TYPE=primary_to_secondary \
                PRIMARY_SERVICEBUS_CONN="primary-connection-string" \
                SECONDARY_SERVICEBUS_CONN="secondary-connection-string" \
                RTO_MINUTES=10 \
                DELTA_MINUTES=2
   ```

> **Note**: The function will automatically discover and replicate ALL topics and subscriptions. No need to specify individual topic names.

## 🧪 **Development & Testing**

### Development Workflow

This project follows enterprise-grade development practices:

```bash
# 1. Set up development environment
git clone <repo-url>
cd personal_projects
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# 2. Install dependencies
pip install -r requirements.txt
pip install -r dev-requirements.txt

# 3. Install pre-commit hooks
pre-commit install

# 4. Run quality checks
mypy src/ tests/           # Type checking
ruff check src/ tests/     # Linting
ruff format src/ tests/    # Code formatting
pytest tests/ --cov=src   # Run tests with coverage

# 5. Make changes and test
# Pre-commit hooks will run automatically on commit
git add .
git commit -m "Your changes"
```

### Testing Suite

The project includes **comprehensive test coverage (82%)**:

#### **Test Files**
- `tests/main_test.py` - Core functionality tests
- `tests/error_handlers_test.py` - Error handling validation
- `tests/message_utils_test.py` - Message processing utilities
- `tests/retry_utils_test.py` - Retry mechanism testing
- `tests/exceptions_test.py` - Custom exception testing

#### **Running Tests**
```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=src --cov-report=term-missing

# Run specific test file
pytest tests/main_test.py -v

# Run specific test
pytest tests/main_test.py::TestConfigLoading::test_config_creation_success -v
```

#### **Test Features**
- ✅ **Azure SDK Mocking**: Proper mocking of Service Bus context managers
- ✅ **Error Scenarios**: Comprehensive error handling tests
- ✅ **Configuration Validation**: Pydantic model testing
- ✅ **Dynamic Discovery**: Topic/subscription discovery testing
- ✅ **Message Processing**: End-to-end message replication tests

### Quality Assurance

#### **Pre-commit Hooks**
Automated quality checks run on every commit:
- **Trim trailing whitespace**
- **Ruff linting** (PEP 8, security, best practices)
- **Ruff formatting** (Black-compatible)
- **mypy type checking** (strict type safety)

#### **CI/CD Pipeline**
GitHub Actions workflow runs on every push/PR:
- **Multi-Python testing** (3.10, 3.11)
- **Type checking** with mypy
- **Security scanning** with Bandit
- **Code quality** with Ruff
- **Test coverage** enforcement (70% minimum)
- **Build validation** for Azure Functions

### Code Quality Standards

#### **Type Safety (mypy)**
- **100% type-safe** codebase
- **Strict type checking** enabled
- **Type annotations** required for all functions
- **Zero mypy errors** enforced in CI

#### **Code Style (Ruff)**
- **PEP 8 compliance** for code style
- **Security linting** (Bandit rules)
- **Import sorting** and organization
- **Complexity analysis** and best practices

#### **Test Coverage**
- **82% coverage** achieved (exceeds 70% requirement)
- **Comprehensive test scenarios** including error cases
- **Azure SDK mocking** for reliable testing
- **Integration-ready** test structure

## 🔧 **Configuration Deep Dive**

### Timer-Based Architecture

The function uses a **timer trigger** instead of Service Bus triggers for better control and reliability:

- **Schedule**: Runs every 30 seconds (`"*/30 * * * * *"` in function.json)
- **Discovery Phase**: Dynamically discovers all topics and subscriptions
- **Processing Phase**: Processes up to 10 messages per subscription per cycle  
- **Error Handling**: Failed messages are abandoned and retried in the next cycle
- **Resource Efficiency**: Processes multiple topics/subscriptions in a single function execution

### Processing Flow

1. **Timer Activation** (every 30 seconds)
2. **Namespace Discovery** → List all topics in source namespace
3. **Subscription Discovery** → For each topic, list all subscriptions  
4. **Message Retrieval** → Get up to 10 pending messages per subscription
5. **Message Enhancement** → Add replication metadata
6. **Cross-Namespace Send** → Send to corresponding topic in destination
7. **Message Completion** → Mark original messages as processed
8. **Cycle Complete** → Wait for next timer activation

### Replication Types

- **`primary_to_secondary`**: Messages flow from primary region to secondary region (typical disaster recovery setup)
- **`secondary_to_primary`**: Messages flow from secondary region to primary region (for failback scenarios)

> **Important**: The function dynamically discovers ALL topics and subscriptions in the source namespace. Ensure that corresponding topics exist in the destination namespace for successful replication.

### Message Enhancement

The application enhances each replicated message with metadata:
- **Original Message ID**: Preserved for traceability  
- **Replication Correlation ID**: Unique identifier for the replication operation
- **Replication Timestamp**: When the replication occurred
- **Enhanced Properties**: All original message properties are preserved

### Time-to-Live (TTL) Calculation

The application automatically calculates TTL for replicated messages:
```
Message TTL = RTO_MINUTES + DELTA_MINUTES
```

- **RTO_MINUTES**: Your Recovery Time Objective (how long you can afford to be down)
- **DELTA_MINUTES**: Extra buffer time to account for processing delays
- **Default TTL**: 12 minutes (10 RTO + 2 delta)

### Retry Behavior

When message sending fails, the function:
1. Waits with exponential backoff (1s, 2s, 4s...)
2. Retries up to 3 times by default
3. Logs all retry attempts for monitoring
4. Raises an exception if all retries fail

## Troubleshooting

### Common Issues

**1. "Missing required environment variables" error**
- Check that you have the correct variables set for your replication type
- For primary_to_secondary: need PRIMARY_SERVICEBUS_CONN and SECONDARY_SERVICEBUS_CONN
- For secondary_to_primary: need PRIMARY_SERVICEBUS_CONN and SECONDARY_SERVICEBUS_CONN

**2. Authentication errors**
- Verify your Service Bus connection strings have the correct permissions (Send, Listen, Manage)
- Make sure the connection strings include SharedAccessKey or are using managed identity

**3. Topic not found errors**
- Ensure corresponding topics exist in both Service Bus namespaces
- The function discovers topics from the source but requires matching topics in the destination
- Check that topic names match exactly (case-sensitive)

**4. Function not processing messages**
- Check the timer trigger configuration in function.json (default: every 30 seconds)
- Verify messages are actually pending in subscriptions (not just in topics)
- Review Azure Functions logs for any discovery or processing errors

**5. "No new messages" frequently logged**
- This is normal when subscriptions are empty
- The function checks all subscriptions every 30 seconds
- Messages appear only when there are pending messages in subscriptions

### Monitoring and Logging

The application provides detailed logging for troubleshooting:

- **Info logs**: Topic/subscription discovery, successful replications, processing status
- **Warning logs**: Retry attempts, configuration issues, empty subscriptions
- **Error logs**: Failed operations, authentication problems, missing topics

Key log messages to monitor:
- `"Found X topics: [...]"` - Topic discovery successful
- `"Found X subscriptions for topic 'Y': [...]"` - Subscription discovery
- `"✅ Replicated message correlation_id from topic/subscription"` - Successful replication

## 🚀 **Deployment Guide**

### Azure Functions Deployment

#### **Prerequisites**
- Azure CLI installed and authenticated
- Azure Functions Core Tools v4
- Resource group and storage account created

#### **1. Create Function App**
```bash
# Create Function App with Python 3.11
az functionapp create \
  --resource-group myResourceGroup \
  --consumption-plan-location eastus \
  --runtime python \
  --runtime-version 3.11 \
  --functions-version 4 \
  --name myapp-servicebus-replication \
  --storage-account mystorageaccount \
  --os-type linux
```

#### **2. Configure Application Settings**
```bash
# Set environment variables
az functionapp config appsettings set \
  --name myapp-servicebus-replication \
  --resource-group myResourceGroup \
  --settings \
    REPLICATION_TYPE=primary_to_secondary \
    PRIMARY_SERVICEBUS_CONN="Endpoint=sb://primary.servicebus.windows.net/;..." \
    SECONDARY_SERVICEBUS_CONN="Endpoint=sb://secondary.servicebus.windows.net/;..." \
    RTO_MINUTES=10 \
    DELTA_MINUTES=2 \
    APPLICATIONINSIGHTS_CONNECTION_STRING="InstrumentationKey=..."
```

#### **3. Deploy Function**
```bash
# Deploy from local development
func azure functionapp publish myapp-servicebus-replication

# Or deploy from CI/CD pipeline (GitHub Actions)
# The workflow automatically deploys on pushes to main branch
```

### Environment Management

#### **Development Environment**
```bash
# Local development with emulator
REPLICATION_TYPE=primary_to_secondary
PRIMARY_SERVICEBUS_CONN="Endpoint=sb://dev-primary.servicebus.windows.net/;..."
SECONDARY_SERVICEBUS_CONN="Endpoint=sb://dev-secondary.servicebus.windows.net/;..."
RTO_MINUTES=5
DELTA_MINUTES=1
```

#### **Staging Environment**
```bash
# Staging environment with real Azure resources
REPLICATION_TYPE=primary_to_secondary
PRIMARY_SERVICEBUS_CONN="Endpoint=sb://staging-primary.servicebus.windows.net/;..."
SECONDARY_SERVICEBUS_CONN="Endpoint=sb://staging-secondary.servicebus.windows.net/;..."
RTO_MINUTES=10
DELTA_MINUTES=2
APPLICATIONINSIGHTS_CONNECTION_STRING="staging-insights-connection"
```

#### **Production Environment**
```bash
# Production with full monitoring
REPLICATION_TYPE=primary_to_secondary
PRIMARY_SERVICEBUS_CONN="Endpoint=sb://prod-eastus.servicebus.windows.net/;..."
SECONDARY_SERVICEBUS_CONN="Endpoint=sb://prod-westus.servicebus.windows.net/;..."
RTO_MINUTES=15
DELTA_MINUTES=3
APPLICATIONINSIGHTS_CONNECTION_STRING="prod-insights-connection"
```

## 📊 **Monitoring & Observability**

### Application Insights Integration

The function automatically sends telemetry to Application Insights:

#### **Key Metrics to Monitor**
- **Replication Success Rate**: Percentage of successful message replications
- **Processing Latency**: Time taken to process each replication cycle
- **Error Rate**: Frequency of authentication or connectivity errors
- **Message Volume**: Number of messages processed per cycle

#### **Custom Dashboards**
Create Azure Monitor dashboards to track:
```kusto
// Successful replications over time
traces
| where message contains "✅ Replicated message"
| summarize count() by bin(timestamp, 5m)
| render timechart

// Error analysis
traces
| where severityLevel >= 3
| summarize count() by cloud_RoleName, message
| order by count_ desc
```

### Health Monitoring

#### **Function Health Checks**
- **Timer Execution**: Function should execute every 30 seconds
- **Discovery Success**: Should discover topics/subscriptions without errors
- **Connectivity**: Both Service Bus namespaces should be accessible
- **Message Processing**: Should process messages when available

#### **Alerting Rules**
Set up alerts for:
- Function execution failures
- Authentication errors
- High message processing latency (>2 minutes)
- Zero messages processed for extended periods (when expected)

### Performance Optimization

#### **Configuration Tuning**
```bash
# For high-volume scenarios
RTO_MINUTES=30        # Longer TTL for messages
DELTA_MINUTES=5       # More buffer time

# For low-latency scenarios  
RTO_MINUTES=5         # Shorter TTL for messages
DELTA_MINUTES=1       # Minimal buffer time
```

#### **Scaling Considerations**
- **Function App Plan**: Use Premium or Dedicated plans for guaranteed resources
- **Service Bus Scaling**: Consider partitioned topics for high throughput
- **Batch Processing**: Function processes up to 10 messages per subscription per cycle

## 🔗 **Integration Examples**

### Testing Message Replication

```python
# test_replication.py - Send test messages
import asyncio
from azure.servicebus import ServiceBusClient, ServiceBusMessage

async def test_replication():
    """Send test message and verify replication."""
    
    # Send to primary namespace
    primary_conn = "Endpoint=sb://primary.servicebus.windows.net/;..."
    async with ServiceBusClient.from_connection_string(primary_conn) as client:
        sender = client.get_topic_sender("test-topic")
        message = ServiceBusMessage(
            body="Test message for replication",
            content_type="application/json",
            subject="test-replication"
        )
        await sender.send_messages(message)
        print("✅ Test message sent to primary namespace")
    
    # Wait for replication (30-60 seconds)
    await asyncio.sleep(60)
    
    # Check secondary namespace
    secondary_conn = "Endpoint=sb://secondary.servicebus.windows.net/;..."
    async with ServiceBusClient.from_connection_string(secondary_conn) as client:
        receiver = client.get_subscription_receiver("test-topic", "test-subscription")
        async with receiver:
            messages = await receiver.receive_messages(max_message_count=1, max_wait_time=10)
            if messages:
                print("✅ Message successfully replicated to secondary namespace")
                await receiver.complete_message(messages[0])
            else:
                print("❌ Message not found in secondary namespace")

# Run the test
asyncio.run(test_replication())
```

### Disaster Recovery Simulation

```python
# dr_simulation.py - Simulate failover scenario
import asyncio
from azure.servicebus import ServiceBusClient

async def simulate_failover():
    """Simulate primary region failure and failover to secondary."""
    
    print("🔄 Simulating disaster recovery scenario...")
    
    # 1. Send messages to primary (before failure)
    print("📤 Sending messages to primary region...")
    # ... send test messages ...
    
    # 2. Wait for replication
    print("⏳ Waiting for replication to complete...")
    await asyncio.sleep(60)
    
    # 3. Simulate primary failure (stop sending to primary)
    print("💥 Simulating primary region failure...")
    
    # 4. Switch application to read from secondary
    print("🔄 Switching to secondary region...")
    secondary_conn = "Endpoint=sb://secondary.servicebus.windows.net/;..."
    
    # 5. Verify messages are available in secondary
    async with ServiceBusClient.from_connection_string(secondary_conn) as client:
        receiver = client.get_subscription_receiver("critical-topic", "app-subscription")
        async with receiver:
            messages = await receiver.receive_messages(max_message_count=10, max_wait_time=30)
            print(f"✅ Found {len(messages)} messages in secondary region")
            
    print("🎉 Disaster recovery simulation complete!")

# Run the simulation
asyncio.run(simulate_failover())
```

## 📈 **Recent Improvements**

### Code Quality Enhancements
- ✅ **Type Safety**: Complete mypy compliance across 16 files
- ✅ **Test Coverage**: Improved from 67% to 82%
- ✅ **Linting**: Zero ruff violations, security-compliant
- ✅ **Dependencies**: Separated runtime vs development dependencies
- ✅ **CI/CD**: Enhanced GitHub Actions pipeline with comprehensive checks

### Development Experience
- ✅ **Pre-commit Hooks**: Automated quality checks
- ✅ **Testing Suite**: Comprehensive unit tests with Azure SDK mocking
- ✅ **Documentation**: Complete README with examples and troubleshooting
- ✅ **Error Handling**: Robust exception handling with proper typing

For detailed information about all improvements, see [CLEANUP_SUMMARY.md](./CLEANUP_SUMMARY.md).

## 🤝 **Contributing**

### Development Workflow
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Install development dependencies (`pip install -r dev-requirements.txt`)
4. Install pre-commit hooks (`pre-commit install`)
5. Make your changes and ensure tests pass
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Quality Standards
- **Type Safety**: All code must pass mypy checks
- **Test Coverage**: Maintain >70% test coverage
- **Code Style**: Follow ruff linting rules
- **Documentation**: Update README for any user-facing changes

---

**🎯 Enterprise-Ready Azure Service Bus Replication Solution**  
*Built with modern Python, comprehensive testing, and production-grade quality standards.*
- `"❌ Failed to replicate message correlation_id"` - Replication failures
- `"No new messages for topic/subscription"` - Normal when no pending messages

View logs in:
- **Local development**: Console output with real-time updates
- **Azure**: Application Insights or Function App logs
- **CI/CD**: GitHub Actions workflow logs

## Development

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=src tests/

# Run specific test file
python -m pytest tests/main_test.py -v
```

### Code Quality

The project uses several tools for code quality:

```bash
# Format code
ruff format src/ tests/

# Lint code
ruff check src/ tests/

# Type checking
mypy src/

# Run all pre-commit hooks
pre-commit run --all-files
```
