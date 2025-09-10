# Azure Service Bus Message Replication

A reliable Azure Function for replicating messages between Service Bus namespaces to support disaster recovery and cross-region resilience.

## What Does This Do?

This application automatically replicates messages from one Azure Service Bus namespace to another, helping you:

- **Disaster Recovery**: Keep your messages safe if one region goes down
- **Cross-Region Backup**: Maintain message copies across different Azure regions
- **Business Continuity**: Meet your RTO (Recovery Time Objective) requirements
- **Zero Message Loss**: Ensure critical business messages aren't lost during outages

The application works as an Azure Function that gets triggered when messages arrive in your primary Service Bus topic, then replicates them to your secondary Service Bus in another region.

## How It Works

1. A message arrives in your primary Service Bus topic
2. The Azure Function is triggered automatically 
3. The function reads the message and creates a copy
4. The copy is sent to your secondary Service Bus topic in another region
5. The replicated message gets a configurable TTL (Time To Live) based on your RTO requirements
6. If sending fails, the function retries with exponential backoff
7. All operations are logged for monitoring and troubleshooting

## Project Structure

```
cloud-application-servicebus-replication/
├── src/                          # Main source code
│   ├── main.py                   # Azure Function entry point
│   ├── config.py                 # Configuration management
│   ├── message_utils.py          # Message processing utilities
│   ├── retry_utils.py            # Retry logic with backoff
│   ├── logging_utils.py          # Centralized logging
│   ├── error_handlers.py         # Error handling utilities
│   ├── exceptions.py             # Custom exception classes
│   ├── constants.py              # Application constants
│   └── function.json             # Azure Functions binding config
├── tests/                        # Unit tests
│   ├── main_test.py              # Main test suite
│   ├── test_constants.py         # Test-specific constants
│   └── README.md                 # Testing documentation
├── .github/                      # GitHub Actions workflows
│   ├── workflows/
│   │   ├── ci.yml                # Main CI/CD pipeline
│   │   ├── on-pull-request.yaml  # PR validation
│   │   └── on-push.yaml          # Push validation
│   ├── CODEOWNERS               # Code review assignments
│   └── PULL_REQUEST_TEMPLATE.md # PR template
├── requirements.txt              # Python dependencies
├── pyproject.toml               # Project configuration
├── host.json                    # Azure Functions host config
├── local.settings.json          # Local development settings
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
# Primary Service Bus (source) - optional for primary_to_secondary mode
PRIMARY_SERVICEBUS_CONN="Endpoint=sb://your-primary-sb.servicebus.windows.net/;SharedAccessKeyName=..."
PRIMARY_TOPIC_NAME="your-source-topic"

# Secondary Service Bus (destination) - REQUIRED for primary_to_secondary mode  
SECONDARY_SERVICEBUS_CONN="Endpoint=sb://your-secondary-sb.servicebus.windows.net/;SharedAccessKeyName=..."
SECONDARY_TOPIC_NAME="your-destination-topic"
```

#### **For Secondary → Primary Replication**
```bash
# Primary Service Bus (destination) - REQUIRED for secondary_to_primary mode
PRIMARY_SERVICEBUS_CONN="Endpoint=sb://your-primary-sb.servicebus.windows.net/;SharedAccessKeyName=..."
PRIMARY_TOPIC_NAME="your-destination-topic"

# Secondary Service Bus (source) - optional for secondary_to_primary mode
SECONDARY_SERVICEBUS_CONN="Endpoint=sb://your-secondary-sb.servicebus.windows.net/;SharedAccessKeyName=..."
SECONDARY_TOPIC_NAME="your-source-topic"
```

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

#### **Example 1: East US → West US Backup**
```bash
REPLICATION_TYPE=primary_to_secondary
SECONDARY_SERVICEBUS_CONN="Endpoint=sb://myapp-westus.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=..."
SECONDARY_TOPIC_NAME="orders-backup"
RTO_MINUTES=15
DELTA_MINUTES=3
```

#### **Example 2: Development Environment**
```bash
REPLICATION_TYPE=primary_to_secondary
SECONDARY_SERVICEBUS_CONN="Endpoint=sb://myapp-dev-backup.servicebus.windows.net/;SharedAccessKeyName=..."
SECONDARY_TOPIC_NAME="dev-messages-backup"
RTO_MINUTES=5
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
    "SECONDARY_SERVICEBUS_CONN": "your-secondary-connection-string",
    "SECONDARY_TOPIC_NAME": "your-destination-topic",
    "RTO_MINUTES": "10",
    "DELTA_MINUTES": "2"
  }
}
```

## Usage

### Running Locally

```bash
# Start the Azure Functions runtime
func start

# The function will be available at:
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
3. **Code Quality** - Runs linting and code analysis
4. **Build** - Validates the application builds correctly
5. **Integration Test** - Tests Service Bus integration (when credentials provided)
6. **Notify** - Sends notifications about build status

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

You can test message replication by sending a message to your primary topic:

```python
# Quick test script
from azure.servicebus import ServiceBusClient, ServiceBusMessage

async def send_test_message():
    conn_str = "your-primary-connection-string"
    topic_name = "your-source-topic"
    
    async with ServiceBusClient.from_connection_string(conn_str) as client:
        sender = client.get_topic_sender(topic_name)
        message = ServiceBusMessage("Test message for replication")
        await sender.send_messages(message)
        print("Test message sent!")
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
                SECONDARY_SERVICEBUS_CONN="connection-string" \
                SECONDARY_TOPIC_NAME="backup-topic"
   ```

## Understanding the Configuration

### Replication Types

- **`primary_to_secondary`**: Messages flow from primary region to secondary region (typical disaster recovery setup)
- **`secondary_to_primary`**: Messages flow from secondary region to primary region (for failback scenarios)

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
- For primary_to_secondary: need SECONDARY_SERVICEBUS_CONN and SECONDARY_TOPIC_NAME
- For secondary_to_primary: need PRIMARY_SERVICEBUS_CONN and PRIMARY_TOPIC_NAME

**2. Authentication errors**
- Verify your Service Bus connection strings have the correct permissions
- Make sure the connection strings include SharedAccessKey or are using managed identity

**3. Topic/subscription not found**
- Ensure the topics exist in both Service Bus namespaces
- Check that topic names match exactly (case-sensitive)

**4. Function not triggering**
- Verify the Service Bus trigger is configured correctly in function.json
- Check that messages are actually arriving in the source topic
- Review Azure Functions logs for any binding errors

### Monitoring and Logging

The application provides detailed logging for troubleshooting:

- **Info logs**: Normal operation, successful replications
- **Warning logs**: Retry attempts, configuration issues  
- **Error logs**: Failed operations, authentication problems

View logs in:
- **Local development**: Console output
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
