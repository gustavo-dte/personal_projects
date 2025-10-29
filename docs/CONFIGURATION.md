# Configuration Guide

## Environment Variables

### Required Configuration

#### Replication Direction
```bash
# Direction of replication - REQUIRED
REPLICATION_TYPE=primary_to_secondary
# Options: "primary_to_secondary" or "secondary_to_primary"
```

#### Connection Strings

##### For Primary → Secondary Replication
```bash
# Primary Service Bus (source) - REQUIRED for primary_to_secondary mode
PRIMARY_SERVICEBUS_CONN="Endpoint=sb://your-primary.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=your-key"

# Secondary Service Bus (destination) - REQUIRED for primary_to_secondary mode
SECONDARY_SERVICEBUS_CONN="Endpoint=sb://your-secondary.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=your-key"
```

##### For Secondary → Primary Replication
```bash
# Primary Service Bus (destination) - REQUIRED for secondary_to_primary mode
PRIMARY_SERVICEBUS_CONN="Endpoint=sb://your-primary.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=your-key"

# Secondary Service Bus (source) - REQUIRED for secondary_to_primary mode
SECONDARY_SERVICEBUS_CONN="Endpoint=sb://your-secondary.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=your-key"
```

### Optional Configuration

#### Timing Settings
```bash
# Recovery Time Objective in minutes (default: 10)
RTO_MINUTES=10

# Additional buffer time in minutes (default: 2)
DELTA_MINUTES=2
```

#### Dead Letter Queue Settings
```bash
# Enable dead letter queue processing (default: true)
DLQ_ENABLED=true

# Maximum delivery attempts before dead lettering (default: 3)
MAX_DELIVERY_COUNT=3

# Time to live for messages in dead letter queue in minutes (default: 1440 = 24 hours)
DLQ_TTL_MINUTES=1440
```

#### Retry Configuration
```bash
# Maximum retry attempts for failed operations (default: 3)
MAX_RETRY_ATTEMPTS=3

# Base delay in seconds for exponential backoff (default: 1.0)
BASE_RETRY_DELAY=1.0
```

#### Monitoring Settings
```bash
# Application Insights connection string (optional)
APPLICATIONINSIGHTS_CONNECTION_STRING="InstrumentationKey=your-key;IngestionEndpoint=https://your-region.in.applicationinsights.azure.com/"

# Application Insights instrumentation key (legacy, optional)
APPINSIGHTS_INSTRUMENTATIONKEY="your-instrumentation-key"
```

## Configuration Examples

### Example 1: Basic Primary to Secondary
```bash
REPLICATION_TYPE=primary_to_secondary
PRIMARY_SERVICEBUS_CONN="Endpoint=sb://prod-east.servicebus.windows.net/;..."
SECONDARY_SERVICEBUS_CONN="Endpoint=sb://prod-west.servicebus.windows.net/;..."
RTO_MINUTES=10
DELTA_MINUTES=2
```

### Example 2: Failback Scenario (Secondary → Primary)
```bash
REPLICATION_TYPE=secondary_to_primary
PRIMARY_SERVICEBUS_CONN="Endpoint=sb://prod-east.servicebus.windows.net/;..."
SECONDARY_SERVICEBUS_CONN="Endpoint=sb://prod-west.servicebus.windows.net/;..."
RTO_MINUTES=5
DELTA_MINUTES=1
```

## Local Development Setup

Create a `local.settings.json` file:

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
    "DELTA_MINUTES": "2",
    "APPLICATIONINSIGHTS_CONNECTION_STRING": "your-app-insights-connection-string"
  }
}
```

## Validation Rules

- Both `PRIMARY_SERVICEBUS_CONN` and `SECONDARY_SERVICEBUS_CONN` are always required
- `RTO_MINUTES` must be between 1 and 1440 (24 hours)
- `DELTA_MINUTES` must be between 0 and 1440 (24 hours)
- `MAX_RETRY_ATTEMPTS` must be between 1 and 10
- `BASE_RETRY_DELAY` must be between 0.1 and 60.0 seconds
- `MAX_DELIVERY_COUNT` must be between 1 and 100
- `DLQ_TTL_MINUTES` must be between 1 and 43200 (30 days)

## Security Best Practices

1. **Use Managed Identity** when possible instead of connection strings
2. **Rotate keys regularly** for Service Bus access keys
3. **Use Key Vault** to store sensitive connection strings
4. **Limit permissions** to only what's needed (Send/Listen/Manage)
5. **Monitor access** through Azure Activity Logs
