# Deployment Guide

## Prerequisites

- **Azure subscription** with appropriate permissions
- **Two Service Bus namespaces** (primary and secondary)
- **Azure Functions Core Tools** (for local development)
- **Azure CLI** (for deployment)

## Deployment Options

### Option 1: Azure Functions (Recommended)

#### 1. Create Function App
```bash
# Create resource group
az group create --name rg-servicebus-replication --location eastus2

# Create storage account (required for Functions)
az storage account create \
  --name stservicebusrepl \
  --resource-group rg-servicebus-replication \
  --location eastus2 \
  --sku Standard_LRS

# Create Function App
az functionapp create \
  --resource-group rg-servicebus-replication \
  --consumption-plan-location eastus2 \
  --runtime python \
  --runtime-version 3.11 \
  --functions-version 4 \
  --name func-servicebus-replication \
  --storage-account stservicebusrepl
```

#### 2. Configure Application Settings
```bash
az functionapp config appsettings set \
  --name func-servicebus-replication \
  --resource-group rg-servicebus-replication \
  --settings \
     REPLICATION_TYPE=primary_to_secondary \
     PRIMARY_SERVICEBUS_CONN="primary-connection-string" \
     SECONDARY_SERVICEBUS_CONN="secondary-connection-string" \
     RTO_MINUTES=10 \
     DELTA_MINUTES=2
```

#### 3. Deploy Code
```bash
# From your local development environment
func azure functionapp publish func-servicebus-replication --python
```

### Option 2: Container Deployment

#### 1. Build Container Image
```bash
# Create Dockerfile (already included in project)
docker build -t servicebus-replication .

# Tag for Azure Container Registry
docker tag servicebus-replication your-acr.azurecr.io/servicebus-replication:latest

# Push to registry
docker push your-acr.azurecr.io/servicebus-replication:latest
```

#### 2. Deploy to Container Instances
```bash
az container create \
  --resource-group rg-servicebus-replication \
  --name ci-servicebus-replication \
  --image your-acr.azurecr.io/servicebus-replication:latest \
  --environment-variables \
    REPLICATION_TYPE=primary_to_secondary \
    PRIMARY_SERVICEBUS_CONN="primary-connection-string" \
    SECONDARY_SERVICEBUS_CONN="secondary-connection-string" \
    RTO_MINUTES=10 \
    DELTA_MINUTES=2
```

### Option 3: Kubernetes Deployment

#### 1. Create Namespace and Secrets
```yaml
# k8s-namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: servicebus-replication
---
apiVersion: v1
kind: Secret
metadata:
  name: servicebus-secrets
  namespace: servicebus-replication
type: Opaque
stringData:
  primary-conn: "primary-connection-string"
  secondary-conn: "secondary-connection-string"
```

#### 2. Deploy Application
```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: servicebus-replication
  namespace: servicebus-replication
spec:
  replicas: 1
  selector:
    matchLabels:
      app: servicebus-replication
  template:
    metadata:
      labels:
        app: servicebus-replication
    spec:
      containers:
      - name: servicebus-replication
        image: your-acr.azurecr.io/servicebus-replication:latest
        env:
        - name: REPLICATION_TYPE
          value: "primary_to_secondary"
        - name: PRIMARY_SERVICEBUS_CONN
          valueFrom:
            secretKeyRef:
              name: servicebus-secrets
              key: primary-conn
        - name: SECONDARY_SERVICEBUS_CONN
          valueFrom:
            secretKeyRef:
              name: servicebus-secrets
              key: secondary-conn
        - name: RTO_MINUTES
          value: "10"
        - name: DELTA_MINUTES
          value: "2"
```

## Post-Deployment Verification

### 1. Check Function Logs
```bash
# Azure Functions
az functionapp logs tail --name func-servicebus-replication --resource-group rg-servicebus-replication

# Container Instances
az container logs --name ci-servicebus-replication --resource-group rg-servicebus-replication

# Kubernetes
kubectl logs -f deployment/servicebus-replication -n servicebus-replication
```

### 2. Monitor Message Flow
- Check Application Insights for custom metrics
- Monitor Service Bus queues/topics for message counts
- Verify messages are being replicated correctly

### 3. Test Failover Scenario
1. Stop primary Service Bus (or simulate outage)
2. Verify messages are still being processed from secondary
3. Check that no messages are lost during transition

## Production Considerations

### High Availability
- Deploy to multiple regions for redundancy
- Use Azure Functions Premium or Dedicated plans for guaranteed uptime
- Configure auto-scaling based on message volume

### Security
- Use Managed Identity instead of connection strings when possible
- Store secrets in Azure Key Vault
- Enable network isolation with Private Endpoints

### Monitoring
- Set up alerts for failed message replications
- Monitor function execution duration and success rate
- Track message throughput and latency metrics

### Backup and Recovery
- Regularly backup Service Bus configuration
- Document disaster recovery procedures
- Test recovery scenarios regularly

## Cost Optimization

### Azure Functions
- Use Consumption plan for variable workloads
- Use Premium plan for consistent high volume
- Monitor execution time to optimize cost

### Service Bus
- Choose appropriate tier (Basic/Standard/Premium) based on needs
- Configure message TTL to prevent unbounded growth
- Use partitioned topics for higher throughput at lower cost