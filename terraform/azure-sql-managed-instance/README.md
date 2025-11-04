# Azure SQL Managed Instance Terraform Module

This module deploys Azure SQL Managed Instance with complete networking, security, and monitoring configurations. SQL Managed Instance provides near 100% compatibility with SQL Server for lift-and-shift migrations.

## ⚠️ Important Notes

- **Deployment Time**: 4-6 hours for initial deployment
- **Minimum Cost**: ~$670/month (GP_Gen5_4 with Azure Hybrid Benefit)
- **Network Requirements**: Dedicated subnet with delegation
- **Update Time**: 1-2 hours for configuration changes

## Features

- ✅ Complete networking setup (VNet, Subnet, NSG, Route Table)
- ✅ SQL Managed Instance deployment
- ✅ Automatic password generation
- ✅ Azure AD authentication support
- ✅ Advanced Threat Protection
- ✅ Vulnerability Assessment
- ✅ SQL Auditing
- ✅ Zone redundancy support
- ✅ Managed Identity
- ✅ Azure Hybrid Benefit support (55% savings)

## Architecture

```
┌─────────────────────────────────────────────────────┐
│              Virtual Network (VNet)                  │
│  ┌───────────────────────────────────────────────┐  │
│  │     Dedicated Subnet (Delegated to MI)       │  │
│  │                                               │  │
│  │  ┌──────────────────────────────────────┐    │  │
│  │  │  SQL Managed Instance                │    │  │
│  │  │  ├─ System Databases                 │    │  │
│  │  │  ├─ User Databases                   │    │  │
│  │  │  ├─ SQL Agent Jobs                   │    │  │
│  │  │  ├─ Linked Servers                   │    │  │
│  │  │  └─ Service Broker                   │    │  │
│  │  └──────────────────────────────────────┘    │  │
│  │                                               │  │
│  │  Network Security Group (NSG)                │  │
│  │  Route Table                                 │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

## Usage

### Quick Start

```bash
# 1. Copy example configuration
cp terraform.tfvars.example terraform.tfvars

# 2. Edit terraform.tfvars with your values

# 3. Initialize Terraform
terraform init

# 4. Plan deployment (review carefully)
terraform plan

# 5. Apply (will take 4-6 hours)
terraform apply

# 6. Monitor deployment
terraform show
```

### Using Environment Files

```bash
# Test Environment (4 vCores, ~$1,340/month or ~$603 with AHB)
terraform plan -var-file="environments/test.tfvars"
terraform apply -var-file="environments/test.tfvars"

# Production Environment (16 vCores, ~$5,360/month or ~$2,412 with AHB)
terraform plan -var-file="environments/prod.tfvars"
terraform apply -var-file="environments/prod.tfvars"
```

## Examples

### Test Environment

```hcl
resource_group_name = "rg-test-sqlmi"
location            = "eastus"

managed_instance_name = "sqlmi-test"
administrator_login   = "sqladmin"

# General Purpose - 4 vCores
sku_name             = "GP_Gen5"
vcores               = 4
storage_size_in_gb   = 128
license_type         = "LicenseIncluded"

zone_redundant_enabled = false
enable_threat_detection = true
enable_auditing        = true
```

**Cost**: ~$1,340/month (~$603 with Azure Hybrid Benefit)

### Production Environment

```hcl
resource_group_name = "rg-prod-sqlmi"
location            = "eastus"

managed_instance_name = "sqlmi-prod"
administrator_login   = "sqladmin"

# Business Critical - 16 vCores
sku_name             = "BC_Gen5"
vcores               = 16
storage_size_in_gb   = 1024
license_type         = "BasePrice"  # Azure Hybrid Benefit!

zone_redundant_enabled = true
storage_account_type   = "ZRS"

enable_threat_detection         = true
enable_auditing                = true
enable_vulnerability_assessment = true
```

**Cost**: ~$5,360/month (~$2,412 with Azure Hybrid Benefit - 55% savings!)

## SKU Options

### General Purpose (GP_Gen5)
- **Use Case**: Standard workloads, development, testing
- **Storage**: Up to 16 TB
- **Network latency**: 5-10ms
- **Cost**: Lower than Business Critical

### Business Critical (BC_Gen5)
- **Use Case**: Mission-critical production workloads
- **Storage**: Up to 4 TB (Gen5)
- **Network latency**: <2ms
- **Features**: Built-in high availability, read replicas
- **Cost**: ~2x General Purpose

### vCore Options

| vCores | Memory | Use Case | Monthly Cost (GP)* | Monthly Cost (BC)* |
|--------|--------|----------|-------------------|-------------------|
| 4 | 20.4 GB | Dev/Test | $1,340 ($603 AHB) | $2,720 ($1,224 AHB) |
| 8 | 40.8 GB | Small Prod | $2,680 ($1,206 AHB) | $5,440 ($2,448 AHB) |
| 16 | 81.6 GB | Medium Prod | $5,360 ($2,412 AHB) | $10,720 ($4,824 AHB) |
| 32 | 163.2 GB | Large Prod | $10,720 ($4,824 AHB) | $21,440 ($9,648 AHB) |

*Approximate costs in East US region  
**AHB = Azure Hybrid Benefit (55% savings)**

## Network Requirements

### Subnet Requirements

```hcl
# Minimum subnet size: /28 (16 IPs)
# Recommended: /24 (256 IPs) for growth
subnet_address_prefix = "10.0.1.0/24"

# Subnet MUST be delegated to Microsoft.Sql/managedInstances
# This is automatically configured in the module
```

### NSG Rules (Automatically Configured)

The module automatically creates all required NSG rules:
- Management traffic (ports 9000, 9003, 1438, 1440, 1452)
- TDS connections (port 1433)
- Redirect connections (ports 11000-11999)
- Health probes
- Internal subnet traffic

### VNet Peering (Optional)

To connect to other VNets:

```hcl
# After deployment, add VNet peering
resource "azurerm_virtual_network_peering" "sqlmi_to_app" {
  name                      = "sqlmi-to-app"
  resource_group_name       = azurerm_resource_group.main.name
  virtual_network_name      = azurerm_virtual_network.main.name
  remote_virtual_network_id = azurerm_virtual_network.app.id
  
  allow_virtual_network_access = true
  allow_forwarded_traffic      = true
}
```

## Security

### Authentication

1. **SQL Authentication** (username/password)
2. **Azure AD Authentication** (configure via variables)

```hcl
enable_azure_ad_auth      = true
azure_ad_admin_login      = "dba@company.com"
azure_ad_admin_object_id  = "12345678-1234-..."
```

### Data Protection

- **TDE**: Transparent Data Encryption (enabled by default)
- **Advanced Threat Protection**: Detects anomalous activities
- **Vulnerability Assessment**: Identifies security issues
- **Auditing**: Logs to Storage Account

### Network Security

- **VNet Isolation**: No public access by default
- **NSG Rules**: Restrictive by default
- **Private Connectivity**: Use VNet peering or VPN

### Managed Identity

System-assigned managed identity is created automatically:

```bash
# Get principal ID for Key Vault access
terraform output identity_principal_id
```

## Backup & Recovery

### Automatic Backups

- **Full backups**: Weekly
- **Differential backups**: Every 12 hours
- **Transaction log backups**: Every 5-10 minutes
- **Retention**: 7-35 days (configurable)

### Point-in-Time Restore

```bash
az sql midb restore \
  --resource-group rg-prod-sqlmi \
  --managed-instance sqlmi-prod \
  --name MyDatabase \
  --dest-name MyDatabase-Restored \
  --time "2024-03-15T14:30:00Z"
```

### Long-Term Retention

Configure via Azure Portal or CLI after deployment.

## Monitoring

### Connection String

```bash
# Get connection string
terraform output connection_string_template

# Example output:
Server=tcp:sqlmi-prod.abc123.database.windows.net,1433;
Initial Catalog=MyDatabase;
User ID=sqladmin;
Password=<your-password>;
Encrypt=True;
```

### Health Check

```bash
# Check instance status
az sql mi show \
  --resource-group rg-prod-sqlmi \
  --name sqlmi-prod \
  --query "state"
```

### Performance Monitoring

Connect to the instance and use:
- SQL Server Management Studio (SSMS)
- Azure Data Studio
- Query Store
- Extended Events
- DMVs (Dynamic Management Views)

## Cost Optimization

### 1. Azure Hybrid Benefit (55% Savings!)

```hcl
license_type = "BasePrice"  # Requires SQL Server licenses with active SA
```

**Requirements**:
- Active Software Assurance on SQL Server licenses
- One SQL Server Enterprise core license = 4 vCores in Azure
- One SQL Server Standard core license = 1 vCore in Azure

### 2. Right-Sizing

Monitor resource utilization and adjust:

```bash
# Check current configuration
az sql mi show --resource-group rg-prod-sqlmi --name sqlmi-prod

# Update vCores (takes 1-2 hours)
az sql mi update \
  --resource-group rg-prod-sqlmi \
  --name sqlmi-prod \
  --capacity 8
```

### 3. Dev/Test Pricing

Use General Purpose for non-production:

```hcl
sku_name = "GP_Gen5"  # Instead of BC_Gen5
vcores   = 4          # Instead of 16
```

### 4. Reserved Capacity

Purchase 1-year or 3-year reserved capacity:
- **1-year**: ~30% savings
- **3-year**: ~54% savings

## Migration to SQL Managed Instance

### From On-Premises SQL Server

1. **Assessment**
   ```bash
   # Use Data Migration Assistant (DMA)
   # Check compatibility issues
   ```

2. **Backup & Upload**
   ```bash
   # Backup database
   BACKUP DATABASE MyDB TO DISK = 'C:\Backups\MyDB.bak'
   
   # Upload to Azure Blob Storage
   az storage blob upload \
     --account-name mystorageaccount \
     --container-name backups \
     --name MyDB.bak \
     --file C:\Backups\MyDB.bak
   ```

3. **Restore to MI**
   ```bash
   az sql midb restore \
     --resource-group rg-prod-sqlmi \
     --managed-instance sqlmi-prod \
     --name MyDB \
     --backup-uri "https://mystorageaccount.blob.core.windows.net/backups/MyDB.bak"
   ```

### Using Azure Database Migration Service

```bash
# Create migration project
az dms project create \
  --resource-group rg-migration \
  --service-name mydms \
  --name mydbmigration \
  --source-platform SQL \
  --target-platform SQLMI
```

## Troubleshooting

### Deployment Taking Too Long

**Normal**: First deployment takes 4-6 hours.

```bash
# Check status
az sql mi show \
  --resource-group rg-prod-sqlmi \
  --name sqlmi-prod \
  --query "state"
```

### Cannot Connect

1. **Check subnet NSG rules** (automatically configured)
2. **Verify VNet connectivity**
3. **Ensure client is in VNet or peered VNet**

```bash
# Test from VM in same VNet
sqlcmd -S sqlmi-prod.abc123.database.windows.net -U sqladmin -P <password>
```

### High Costs

Review configuration:

```bash
# Check current settings
terraform show | grep -A 10 "mssql_managed_instance"

# Consider:
# - Downgrade from BC to GP
# - Reduce vCores
# - Enable Azure Hybrid Benefit
```

### Subnet Issues

```
Error: Subnet must be delegated to Microsoft.Sql/managedInstances
```

**Solution**: Module handles this automatically. If using existing subnet, ensure delegation is configured.

## Outputs

| Output | Description |
|--------|-------------|
| `managed_instance_id` | Resource ID |
| `managed_instance_fqdn` | Fully qualified domain name |
| `administrator_login` | Admin username |
| `administrator_password` | Admin password (if generated) |
| `dns_zone_id` | DNS zone ID |
| `identity_principal_id` | Managed identity principal ID |
| `connection_string_template` | Connection string template |
| `deployment_notes` | Deployment summary |

## Requirements

- Terraform >= 1.0
- Azure Provider ~> 3.0
- Azure subscription with appropriate permissions
- **Patience**: 4-6 hours for initial deployment

## Providers

| Provider | Version |
|----------|---------|
| azurerm | ~> 3.0 |
| random | ~> 3.4 |

## Resources Created

- `azurerm_resource_group` - Resource group
- `azurerm_virtual_network` - Virtual network
- `azurerm_subnet` - Dedicated MI subnet
- `azurerm_network_security_group` - NSG with required rules
- `azurerm_route_table` - Route table
- `azurerm_mssql_managed_instance` - SQL Managed Instance
- `azurerm_storage_account` - For auditing and VA
- Various security and monitoring resources

## License

MIT

## Support

For issues or questions:
- [Azure SQL MI Documentation](https://docs.microsoft.com/azure/azure-sql/managed-instance/)
- [Terraform AzureRM Provider](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs)
- [Migration Guide](https://docs.microsoft.com/azure/azure-sql/migration-guides/)

---

**⚠️ Remember**: Initial deployment takes 4-6 hours. Plan accordingly!
