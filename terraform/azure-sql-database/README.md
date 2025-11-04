# Azure SQL Database Terraform Module

This module deploys Azure SQL Database (PaaS) with comprehensive security, monitoring, and backup configurations.

## Features

- ✅ SQL Server (logical server) deployment
- ✅ Multiple database support
- ✅ Automatic password generation
- ✅ Transparent Data Encryption (TDE)
- ✅ Advanced Threat Protection
- ✅ SQL Auditing to Storage Account
- ✅ Firewall rules configuration
- ✅ Short-term and long-term backup retention
- ✅ Zone redundancy support
- ✅ Serverless database support
- ✅ Log Analytics integration
- ✅ Diagnostic settings

## Usage

### Quick Start

```bash
# 1. Copy example configuration
cp terraform.tfvars.example terraform.tfvars

# 2. Edit terraform.tfvars with your values

# 3. Initialize Terraform
terraform init

# 4. Plan deployment
terraform plan

# 5. Apply
terraform apply
```

### Using Environment Files

```bash
# Development
terraform plan -var-file="environments/dev.tfvars"
terraform apply -var-file="environments/dev.tfvars"

# Production
terraform plan -var-file="environments/prod.tfvars"
terraform apply -var-file="environments/prod.tfvars"
```

## Examples

### Simple Development Database

```hcl
resource_group_name = "rg-dev-sql"
location            = "eastus"
sql_server_name     = "sql-dev-myapp"

databases = {
  "dev-db" = {
    name        = "development"
    sku_name    = "S0"      # 10 DTUs - ~$15/month
    max_size_gb = 32
  }
}

enable_threat_detection = false
enable_auditing        = false
enable_monitoring      = false
```

### Production Multi-Database

```hcl
resource_group_name = "rg-prod-sql"
location            = "eastus"
sql_server_name     = "sql-prod-myapp"

databases = {
  "app-db" = {
    name           = "application"
    sku_name       = "S4"      # 200 DTUs - ~$465/month
    max_size_gb    = 500
    zone_redundant = true
  },
  "reporting-db" = {
    name           = "reporting"
    sku_name       = "S3"      # 100 DTUs - ~$233/month
    max_size_gb    = 250
    zone_redundant = true
  }
}

backup_retention_days       = 35
long_term_retention_weekly  = "P4W"
long_term_retention_monthly = "P12M"
long_term_retention_yearly  = "P10Y"

enable_threat_detection = true
enable_auditing        = true
enable_monitoring      = true
```

### Serverless Database (Cost Optimization)

```hcl
databases = {
  "serverless-db" = {
    name                        = "app-serverless"
    sku_name                    = "GP_S_Gen5_2"  # Serverless, 2 vCores
    max_size_gb                 = 100
    auto_pause_delay_in_minutes = 60             # Pause after 1 hour
    min_capacity                = 0.5            # Minimum 0.5 vCores
  }
}
```

## SKU Options

### DTU-Based (Predictable Workloads)

| SKU | DTUs | Max DB Size | Monthly Cost* | Use Case |
|-----|------|-------------|---------------|----------|
| B | 5 | 2 GB | ~$5 | Dev/Test |
| S0 | 10 | 250 GB | ~$15 | Small apps |
| S1 | 20 | 250 GB | ~$30 | Small apps |
| S2 | 50 | 250 GB | ~$75 | Medium apps |
| S3 | 100 | 1 TB | ~$150 | Medium apps |
| S4 | 200 | 1 TB | ~$465 | Production |
| P1 | 125 | 1 TB | ~$465 | Production |
| P2 | 250 | 1 TB | ~$930 | Enterprise |

### vCore-Based (Flexible Workloads)

| SKU | vCores | Monthly Cost* | Use Case |
|-----|--------|---------------|----------|
| GP_Gen5_2 | 2 | ~$336 | Standard |
| GP_Gen5_4 | 4 | ~$672 | Production |
| GP_Gen5_8 | 8 | ~$1,344 | Production |
| GP_S_Gen5_2 | 2 (Serverless) | ~$112** | Dev/Test |
| BC_Gen5_2 | 2 | ~$816 | High performance |

*Approximate costs in East US  
**Based on 8 hours/day usage

## Outputs

| Output | Description |
|--------|-------------|
| `sql_server_id` | SQL Server resource ID |
| `sql_server_fqdn` | Fully qualified domain name |
| `administrator_login` | Admin username |
| `administrator_password` | Admin password (if generated) |
| `database_ids` | Map of database IDs |
| `connection_string_template` | Connection string template |

## Security

### Authentication
- SQL Authentication (username/password)
- Auto-generated secure passwords
- Azure AD authentication support (configure separately)

### Network Security
- Configurable firewall rules
- Optional Azure services access
- Consider Private Endpoints for production

### Data Protection
- Transparent Data Encryption (TDE) enabled by default
- Advanced Threat Protection
- SQL Auditing to Storage Account
- Backup encryption

### Monitoring
- Log Analytics integration
- Diagnostic settings (9 log categories)
- Security alerts

## Backup & Recovery

### Automatic Backups
- **Full backups**: Weekly
- **Differential backups**: Every 12-24 hours  
- **Transaction log backups**: Every 5-10 minutes
- **Point-in-time restore**: 7-35 days

### Long-term Retention
- Weekly backups: Up to 10 years
- Monthly backups: Up to 10 years
- Yearly backups: Up to 10 years

### Restore Options
```bash
# Point-in-time restore
az sql db restore \
  --dest-name restored-db \
  --name original-db \
  --resource-group rg-name \
  --server sql-server \
  --time "2024-03-15T14:30:00Z"

# Geo-restore
az sql db restore \
  --dest-name restored-db \
  --name original-db \
  --resource-group rg-name \
  --server sql-server \
  --geo-backup-id /subscriptions/.../geoBackups/...
```

## Cost Optimization

1. **Right-size SKUs**: Monitor DTU/CPU usage and adjust
2. **Serverless for dev/test**: Auto-pause when inactive
3. **Reserved capacity**: Up to 54% savings with 3-year commitment
4. **Azure Hybrid Benefit**: Up to 40% savings with SQL licenses

## Requirements

- Terraform >= 1.0
- Azure Provider ~> 3.0
- Azure subscription with appropriate permissions

## Providers

| Provider | Version |
|----------|---------|
| azurerm | ~> 3.0 |
| random | ~> 3.4 |

## Resources Created

- `azurerm_resource_group` - Resource group
- `azurerm_mssql_server` - SQL Server
- `azurerm_mssql_database` - Databases
- `azurerm_mssql_firewall_rule` - Firewall rules
- `azurerm_storage_account` - Audit storage
- `azurerm_log_analytics_workspace` - Monitoring
- Various security and monitoring resources

## License

MIT

## Support

For issues or questions, refer to:
- [Azure SQL Database Documentation](https://docs.microsoft.com/azure/azure-sql/database/)
- [Terraform AzureRM Provider](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs)
