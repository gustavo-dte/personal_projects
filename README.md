# Azure Service Bus Message Replication

A reliable Azure Function for dynamically replicating messages between Service Bus namespaces to support disaster recovery and cross-region resilience.

## What Does This Do?

This application automatically discovers and replicates messages from ALL topics and subscriptions in one Azure Service Bus namespace to another, helping you:

- **Disaster Recovery**: Keep your messages safe if one region goes down
- **Cross-Region Backup**: Maintain message copies across different Azure regions  
- **Business Continuity**: Meet your RTO (Recovery Time Objective) requirements
- **Zero Message Loss**: Ensure critical business messages aren't lost during outages
- **Dynamic Discovery**: Automatically replicates ALL topics and subscriptions without manual configuration

The application works as a timer-triggered Azure Function that runs every 30 seconds, dynamically discovers all topics and subscriptions, then replicates any pending messages to your secondary Service Bus namespace.

## How It Works

1. **Timer Trigger**: The function runs every 30 seconds automatically
2. **Dynamic Discovery**: It discovers all topics and subscriptions in the source namespace
3. **Message Processing**: For each subscription, it retrieves up to 10 pending messages
4. **Message Replication**: Creates enhanced copies with tracking metadata
5. **Cross-Namespace Send**: Sends copies to the corresponding topic in the destination namespace
6. **Message Completion**: Marks original messages as complete only after successful replication
7. **Error Handling**: If sending fails, messages are abandoned for retry on the next cycle
8. **Comprehensive Logging**: All operations are logged for monitoring and troubleshooting

## Project Structure

```
personal_projects/
├── src/                          # Main source code
│   ├── main.py                   # Azure Function entry point & timer trigger
│   ├── config.py                 # Configuration management with Pydantic
│   ├── message_utils.py          # Message processing & enhancement utilities
│   ├── retry_utils.py            # Retry logic with exponential backoff
│   ├── logging_utils.py          # Centralized logging with Azure Monitor
│   ├── error_handlers.py         # Comprehensive error handling utilities
│   ├── exceptions.py             # Custom exception classes
│   ├── constants.py              # Application constants
│   └── function.json             # Azure Functions timer trigger config
├── tests/                        # Unit tests
│   ├── main_test.py              # Main test suite
│   ├── constants_test.py         # Constants tests
│   └── __init__.py               # Test package
├── .github/                      # GitHub Actions workflows
│   ├── workflows/                # CI/CD pipeline configurations
│   ├── CODEOWNERS               # Code review assignments
│   └── PULL_REQUEST_TEMPLATE.md # PR template
├── requirements.txt              # Python dependencies
├── host.json                    # Azure Functions host configuration
├── local.settings.example.json  # Example local development settings
├── .gitignore                   # Git ignore patterns
├── .editorconfig               # Editor configuration
└── .pre-commit-config.yaml      # Code quality hooks
```

## Getting Started

### Prerequisites

Before you start, you'll need:

- Python 3.11 or higher
- An Azure subscription with two Service Bus namespaces (primary and secondary)
- Azure Functions Core Tools (for local development)
- Access to create topics and subscriptions in both namespaces

### Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd cloud-application-servicebus-replication
   ```

2. **Set up Python environment:**
   ```bash
   # Create virtual environment
   python -m venv venv

   # Activate it (Windows)
   venv\Scripts\activate

   # Activate it (Linux/Mac)
   source venv/bin/activate

   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Install development tools:**
   ```bash
   # Install pre-commit hooks for code quality
   pip install pre-commit
   pre-commit install
   ```

## Configuration

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

## Understanding the Configuration

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
