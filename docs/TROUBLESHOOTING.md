# Troubleshooting Guide

## Common Issues

### Connection Problems

#### Issue: "Connection string is invalid"
**Symptoms:**
- Function fails to start
- Error message about invalid connection string format

**Solution:**
1. Verify connection string format:
   ```
   Endpoint=sb://your-namespace.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=your-key
   ```
2. Check that the namespace exists and is active
3. Verify the access key is correct and hasn't been rotated
4. Ensure connection string has proper permissions (Listen, Send, Manage)

#### Issue: "Namespace not found"
**Symptoms:**
- Connection timeouts
- DNS resolution errors

**Solution:**
1. Check namespace name spelling
2. Verify the namespace is in the correct Azure region
3. Ensure network connectivity (firewall rules, private endpoints)
4. Check if namespace has been deleted or moved

### Authentication Issues

#### Issue: "Unauthorized access"
**Symptoms:**
- 401 Unauthorized errors
- "The token has an invalid signature" errors

**Solution:**
1. Regenerate Service Bus access keys
2. Update connection strings with new keys
3. Check if using correct SharedAccessKeyName (usually `RootManageSharedAccessKey`)
4. Verify namespace-level vs entity-level permissions

#### Issue: "Token expired" 
**Symptoms:**
- Intermittent authentication failures
- Works initially then fails after time

**Solution:**
1. This is usually handled automatically by the SDK
2. Check for clock skew between systems
3. Verify system time is accurate
4. Consider using Managed Identity instead of connection strings

### Message Processing Issues

#### Issue: "Messages not being replicated"
**Symptoms:**
- No errors but no messages appear in destination
- Function runs successfully but no message flow

**Troubleshooting:**
1. Check if there are actually messages in the source subscriptions
2. Verify subscription filters aren't blocking messages
3. Check message time-to-live (TTL) settings
4. Verify destination topic exists and accepts messages

**Solution:**
```bash
# Check source subscription message counts
az servicebus topic subscription show \
  --resource-group your-rg \
  --namespace-name your-namespace \
  --topic-name your-topic \
  --name your-subscription \
  --query messageCount

# Check destination topic permissions
az servicebus topic authorization-rule list \
  --resource-group your-rg \
  --namespace-name your-dest-namespace \
  --topic-name your-topic
```

#### Issue: "Messages duplicated in destination"
**Symptoms:**
- Same message appears multiple times
- Duplicate message IDs in logs

**Solution:**
1. Check if function is running multiple instances
2. Verify Azure Functions scaling settings
3. Implement idempotency checks if needed
4. Check for retries on transient failures

### Performance Issues

#### Issue: "Function timeout errors"
**Symptoms:**
- Function exceeds maximum execution time
- Timeout exceptions in logs

**Solution:**
1. Reduce batch size of messages processed per execution
2. Optimize message processing logic
3. Consider using Azure Functions Premium plan for longer timeouts
4. Check for network latency issues

#### Issue: "High latency in message replication"
**Symptoms:**
- Messages take long time to appear in destination
- High execution duration in function logs

**Troubleshooting:**
1. Check network latency between regions
2. Monitor Service Bus throttling metrics
3. Verify function app performance tier
4. Check for competing consumers

### Configuration Issues

#### Issue: "Environment variable not found"
**Symptoms:**
- ConfigError exceptions
- Missing configuration values

**Solution:**
1. Verify all required environment variables are set
2. Check spelling and case sensitivity
3. For Azure Functions, verify Application Settings
4. For local development, check `local.settings.json`

#### Issue: "Invalid configuration values"
**Symptoms:**
- Pydantic validation errors
- Function fails to initialize

**Solution:**
1. Check value ranges (e.g., RTO_MINUTES: 1-1440)
2. Verify data types (numbers vs strings)
3. Check enum values (REPLICATION_TYPE must be exact match)

## Monitoring and Diagnostics

### Enable Detailed Logging

#### Application Insights
```bash
# Set Application Insights connection string
APPLICATIONINSIGHTS_CONNECTION_STRING="InstrumentationKey=your-key;..."

# Or use instrumentation key (legacy)
APPINSIGHTS_INSTRUMENTATIONKEY="your-key"
```

#### Function App Logging
```bash
# Enable Application Insights for Function App
az functionapp config appsettings set \
  --name your-function-app \
  --resource-group your-rg \
  --settings APPLICATIONINSIGHTS_CONNECTION_STRING="your-connection-string"
```

### Key Metrics to Monitor

#### Function Performance
- Execution count and duration
- Success/failure rate
- Memory and CPU usage
- Cold start frequency

#### Message Flow
- Messages processed per minute
- Replication latency (time from source to destination)
- Error rate and types
- Queue depth/backlog

#### Service Bus Metrics
- Incoming/outgoing messages
- Active message count
- Dead letter message count
- Throttling events

### Diagnostic Queries

#### Application Insights KQL Queries
```kql
// Function execution summary
requests
| where name contains "ServiceBusReplication"
| summarize 
    ExecutionCount = count(),
    AvgDuration = avg(duration),
    SuccessRate = avg(toint(success)) * 100
  by bin(timestamp, 5m)

// Error analysis
exceptions
| where outerMessage contains "replication"
| summarize ErrorCount = count() by type, outerMessage
| order by ErrorCount desc

// Message processing rate
traces
| where message contains "Message replicated successfully"
| summarize MessageCount = count() by bin(timestamp, 1m)
| render timechart
```

## Advanced Troubleshooting

### Debug Mode
Enable verbose logging by setting:
```bash
AZURE_FUNCTIONS_ENVIRONMENT=Development
```

### Network Diagnostics
```bash
# Test connectivity to Service Bus
nslookup your-namespace.servicebus.windows.net

# Test port connectivity
telnet your-namespace.servicebus.windows.net 5671
```

### Service Bus Diagnostics
```bash
# Check namespace status
az servicebus namespace show \
  --name your-namespace \
  --resource-group your-rg \
  --query status

# List topics and subscriptions
az servicebus topic list \
  --namespace-name your-namespace \
  --resource-group your-rg

az servicebus topic subscription list \
  --namespace-name your-namespace \
  --resource-group your-rg \
  --topic-name your-topic
```

## Getting Support

### Before Contacting Support
1. ✅ Check this troubleshooting guide
2. ✅ Review Application Insights logs
3. ✅ Verify configuration values
4. ✅ Test with minimal configuration
5. ✅ Check Azure Service Health

### Support Channels
- **GitHub Issues**: For bugs and feature requests
- **Azure Support**: For Service Bus and Azure Functions issues
- **Community Forums**: For general questions and discussions

### Information to Provide
When requesting support, include:
- Function app name and region
- Configuration values (sanitized)
- Error messages and correlation IDs
- Timestamps of issues
- Steps to reproduce
- Expected vs actual behavior