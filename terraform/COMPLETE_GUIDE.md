# Azure SQL Terraform Modules - Complete Structure

## 📁 Directory Structure Created

```
D:\DevOps\DTE\vmware\source_code\cloud-platform-vm-migration\terraform\
│
├── azure-sql-database/                    # SQL Database (PaaS) Module
│   ├── main.tf                           # Main configuration
│   ├── variables.tf                      # Input variables
│   ├── outputs.tf                        # Output values
│   ├── terraform.tfvars.example          # Example configuration
│   ├── README.md                         # Complete documentation
│   ├── .gitignore                        # Git ignore rules
│   └── environments/                     # Environment configs
│       ├── dev.tfvars                    # Development
│       └── prod.tfvars                   # Production
│
└── azure-sql-managed-instance/            # SQL Managed Instance Module
    ├── main.tf                           # Main configuration
    ├── variables.tf                      # Input variables
    ├── outputs.tf                        # Output values
    ├── terraform.tfvars.example          # Example configuration
    ├── README.md                         # Complete documentation
    ├── .gitignore                        # Git ignore rules
    └── environments/                     # Environment configs
        ├── test.tfvars                   # Test environment
        └── prod.tfvars                   # Production
```

## 🎯 Module 1: Azure SQL Database

### Purpose
Deploy Azure SQL Database (PaaS) for cloud-native applications with automatic scaling, high availability, and managed backups.

### Key Features
- ✅ SQL Server (logical server) creation
- ✅ Multiple database support
- ✅ Automatic password generation
- ✅ Transparent Data Encryption (TDE)
- ✅ Advanced Threat Protection
- ✅ SQL Auditing
- ✅ Firewall rules
- ✅ Short and long-term backup retention
- ✅ Zone redundancy
- ✅ Serverless support
- ✅ Log Analytics integration

### Quick Start
```bash
cd D:\DevOps\DTE\vmware\source_code\cloud-platform-vm-migration\terraform\azure-sql-database

# Copy example
cp terraform.tfvars.example terraform.tfvars

# Edit terraform.tfvars with your values
notepad terraform.tfvars

# Deploy
terraform init
terraform plan
terraform apply

# Or use environment file
terraform apply -var-file="environments/dev.tfvars"
```

### Cost Examples
| Environment | Configuration | Monthly Cost |
|-------------|---------------|--------------|
| **Dev** | S0 (10 DTUs, 32 GB) | ~$15 |
| **Test** | S2 (50 DTUs, 100 GB) | ~$75 |
| **Prod** | S4 (200 DTUs, 500 GB) x3 | ~$1,395 |

### Use Cases
- ✅ Modern cloud-native applications
- ✅ Microservices architectures
- ✅ SaaS applications
- ✅ Web applications
- ✅ Development and testing

## 🎯 Module 2: Azure SQL Managed Instance

### Purpose
Deploy Azure SQL Managed Instance for lift-and-shift migrations from on-premises SQL Server with 99.9% compatibility.

### Key Features
- ✅ Complete networking setup (VNet, Subnet, NSG, Route Table)
- ✅ SQL Managed Instance deployment
- ✅ Near 100% SQL Server compatibility
- ✅ SQL Agent support
- ✅ Cross-database queries
- ✅ Service Broker
- ✅ CLR support
- ✅ Linked servers
- ✅ Advanced Threat Protection
- ✅ Vulnerability Assessment
- ✅ Zone redundancy
- ✅ Azure Hybrid Benefit (55% savings)

### Quick Start
```bash
cd D:\DevOps\DTE\vmware\source_code\cloud-platform-vm-migration\terraform\azure-sql-managed-instance

# Copy example
cp terraform.tfvars.example terraform.tfvars

# Edit terraform.tfvars with your values
notepad terraform.tfvars

# Deploy (will take 4-6 hours!)
terraform init
terraform plan
terraform apply

# Or use environment file
terraform apply -var-file="environments/test.tfvars"
```

### Cost Examples
| Environment | Configuration | Without AHB | With AHB (55% off) |
|-------------|---------------|-------------|-------------------|
| **Test** | GP_Gen5_4 (128 GB) | ~$1,340 | ~$603 |
| **Prod** | BC_Gen5_16 (1 TB) | ~$5,360 | ~$2,412 |

### Use Cases
- ✅ Lift-and-shift from on-premises SQL Server
- ✅ Applications requiring SQL Agent
- ✅ Cross-database queries
- ✅ Service Broker workloads
- ✅ CLR assemblies
- ✅ Linked servers
- ✅ Database mail

## 📊 Decision Matrix: Which Module to Use?

| Requirement | SQL Database | Managed Instance |
|-------------|--------------|------------------|
| **SQL Compatibility** | 95% | 99.9% |
| **Lift-and-shift migrations** | ❌ | ✅ |
| **SQL Agent** | ❌ | ✅ |
| **Cross-DB queries** | Limited | ✅ |
| **CLR, Service Broker** | ❌ | ✅ |
| **Linked servers** | ❌ | ✅ |
| **Elastic scaling** | ✅ | ❌ |
| **Serverless option** | ✅ | ❌ |
| **Deployment time** | 5-10 min | 4-6 hours |
| **Starting cost** | $15/mo | $670/mo |
| **VNet required** | No | Yes |

## 🚀 Deployment Instructions

### Prerequisites

1. **Azure CLI**
   ```bash
   az --version
   az login
   az account set --subscription "Your-Subscription-Name"
   ```

2. **Terraform**
   ```bash
   terraform --version  # Should be >= 1.0
   ```

3. **Permissions**
   - Contributor role on subscription
   - Or specific resource permissions

### Step-by-Step Deployment

#### For SQL Database

```bash
# 1. Navigate to directory
cd terraform/azure-sql-database

# 2. Create configuration file
cp terraform.tfvars.example terraform.tfvars

# 3. Edit configuration
# Set:
# - resource_group_name
# - sql_server_name (must be globally unique)
# - databases configuration
# - firewall_rules

# 4. Initialize
terraform init

# 5. Validate
terraform validate

# 6. Plan
terraform plan -out=tfplan

# 7. Review plan carefully

# 8. Apply
terraform apply tfplan

# 9. Get outputs
terraform output
terraform output -raw administrator_password  # If auto-generated
```

#### For SQL Managed Instance

```bash
# 1. Navigate to directory
cd terraform/azure-sql-managed-instance

# 2. Create configuration file
cp terraform.tfvars.example terraform.tfvars

# 3. Edit configuration
# Set:
# - resource_group_name
# - managed_instance_name (must be unique)
# - vnet_address_space
# - subnet_address_prefix (minimum /28, recommended /24)
# - vcores, storage_size_in_gb
# - license_type (use "BasePrice" for Azure Hybrid Benefit)

# 4. Initialize
terraform init

# 5. Validate
terraform validate

# 6. Plan (review networking carefully)
terraform plan -out=tfplan

# 7. Apply (will take 4-6 hours)
terraform apply tfplan

# 8. Monitor deployment
terraform show

# 9. Get outputs after completion
terraform output
terraform output -raw administrator_password
```

## 📝 Configuration Examples

### SQL Database - Development

```hcl
# environments/dev.tfvars
resource_group_name = "rg-dev-sqldb"
sql_server_name     = "sql-dev-myapp"

databases = {
  "dev-db" = {
    name        = "development"
    sku_name    = "S0"
    max_size_gb = 32
  }
}

enable_threat_detection = false
enable_auditing        = false
enable_monitoring      = false
```

### SQL Database - Production

```hcl
# environments/prod.tfvars
resource_group_name = "rg-prod-sqldb"
sql_server_name     = "sql-prod-myapp"

databases = {
  "app-db" = {
    name           = "application"
    sku_name       = "S4"
    max_size_gb    = 500
    zone_redundant = true
  },
  "reporting-db" = {
    name           = "reporting"
    sku_name       = "S3"
    max_size_gb    = 250
    zone_redundant = true
  }
}

backup_retention_days      = 35
enable_threat_detection    = true
enable_auditing           = true
enable_monitoring         = true
```

### SQL Managed Instance - Test

```hcl
# environments/test.tfvars
resource_group_name   = "rg-test-sqlmi"
managed_instance_name = "sqlmi-test"

sku_name             = "GP_Gen5"
vcores               = 4
storage_size_in_gb   = 128
license_type         = "LicenseIncluded"

zone_redundant_enabled = false
```

### SQL Managed Instance - Production

```hcl
# environments/prod.tfvars
resource_group_name   = "rg-prod-sqlmi"
managed_instance_name = "sqlmi-prod"

sku_name             = "BC_Gen5"
vcores               = 16
storage_size_in_gb   = 1024
license_type         = "BasePrice"  # 55% savings!

zone_redundant_enabled         = true
enable_threat_detection        = true
enable_vulnerability_assessment = true
```

## 🔐 Security Considerations

### Password Management

**Option 1: Auto-generate (Recommended)**
```hcl
# Leave password null in tfvars
# Password will be auto-generated and stored in state

# Retrieve password
terraform output -raw administrator_password
```

**Option 2: Azure Key Vault**
```hcl
data "azurerm_key_vault_secret" "sql_password" {
  name         = "sql-admin-password"
  key_vault_id = "/subscriptions/.../vaults/my-keyvault"
}

administrator_login_password = data.azurerm_key_vault_secret.sql_password.value
```

**Option 3: Environment Variable**
```bash
export TF_VAR_administrator_login_password="YourSecureP@ssw0rd!"
terraform apply
```

### Network Security

**SQL Database:**
- Configure firewall rules restrictively
- Use Private Endpoints for production
- Enable VNet service endpoints

**SQL Managed Instance:**
- Deployed in dedicated subnet (VNet isolation)
- NSG rules automatically configured
- Use VNet peering or VPN for access

## 💰 Cost Optimization Tips

### 1. Azure Hybrid Benefit
```hcl
# SQL Database: Up to 40% savings
license_type = "BasePrice"

# SQL Managed Instance: Up to 55% savings
license_type = "BasePrice"
```

### 2. Right-Size SKUs
- Monitor DTU/vCore usage
- Scale down during off-hours
- Use serverless for dev/test (SQL DB)

### 3. Reserved Capacity
- 1-year commitment: ~30% savings
- 3-year commitment: ~54% savings

### 4. Dev/Test Pricing
- Use lower SKUs for non-production
- Disable zone redundancy
- Reduce backup retention

## 📈 Monitoring & Maintenance

### Check Deployment Status

```bash
# SQL Database
az sql server show \
  --resource-group rg-prod-sqldb \
  --name sql-prod-myapp

# SQL Managed Instance
az sql mi show \
  --resource-group rg-prod-sqlmi \
  --name sqlmi-prod \
  --query "state"
```

### View Resources

```bash
# List all resources in Terraform state
terraform state list

# Show specific resource
terraform state show azurerm_mssql_server.main
terraform state show azurerm_mssql_managed_instance.main
```

### Update Configuration

```bash
# Make changes to .tfvars file

# Plan changes
terraform plan

# Apply changes
terraform apply

# Note: MI updates can take 1-2 hours
```

## 🔧 Troubleshooting

### SQL Database Issues

**Connection Failed**
```bash
# Check firewall rules
az sql server firewall-rule list \
  --resource-group rg-prod-sqldb \
  --server sql-prod-myapp

# Add your IP
az sql server firewall-rule create \
  --resource-group rg-prod-sqldb \
  --server sql-prod-myapp \
  --name AllowMyIP \
  --start-ip-address $(curl -s ifconfig.me) \
  --end-ip-address $(curl -s ifconfig.me)
```

**High DTU Usage**
```bash
# Check metrics
az monitor metrics list \
  --resource /subscriptions/.../databases/mydb \
  --metric dtu_consumption_percent
```

### SQL Managed Instance Issues

**Deployment Taking Long**
- Normal: 4-6 hours for first deployment
- Updates: 1-2 hours

**Cannot Connect**
- Verify client is in same VNet or peered VNet
- Check NSG rules (automatically configured)
- Ensure subnet delegation is correct

**Subnet Error**
```
Subnet must be /28 or larger
```
Solution: Use minimum /28, recommended /24

## 📚 Additional Resources

### Documentation
- [Azure SQL Database Docs](https://docs.microsoft.com/azure/azure-sql/database/)
- [SQL Managed Instance Docs](https://docs.microsoft.com/azure/azure-sql/managed-instance/)
- [Terraform AzureRM Provider](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs)

### Tools
- [DTU Calculator](https://dtucalculator.azurewebsites.net/)
- [Azure Pricing Calculator](https://azure.microsoft.com/pricing/calculator/)
- [Data Migration Assistant](https://www.microsoft.com/download/details.aspx?id=53595)

### Migration Guides
- [Migration Overview](https://docs.microsoft.com/azure/azure-sql/migration-guides/)
- [SQL Server to Azure SQL DB](https://docs.microsoft.com/azure/azure-sql/migration-guides/database/sql-server-to-sql-database-guide)
- [SQL Server to SQL MI](https://docs.microsoft.com/azure/azure-sql/migration-guides/managed-instance/sql-server-to-managed-instance-guide)

## ✅ Checklist

### Before Deployment

- [ ] Azure CLI installed and configured
- [ ] Terraform installed (>= 1.0)
- [ ] Azure subscription selected
- [ ] Appropriate permissions verified
- [ ] Configuration file created and edited
- [ ] Unique names chosen (SQL server/MI names)
- [ ] Network requirements understood (for MI)
- [ ] Cost estimates reviewed
- [ ] Backup strategy planned

### After Deployment

- [ ] Verify deployment successful
- [ ] Test connectivity
- [ ] Save administrator password securely
- [ ] Configure monitoring alerts
- [ ] Set up backup verification
- [ ] Document connection strings
- [ ] Update application configurations
- [ ] Test failover procedures (if HA configured)

## 🎓 Next Steps

### For SQL Database
1. Deploy dev environment first
2. Test connectivity and functionality
3. Configure monitoring and alerts
4. Deploy production with full security
5. Set up CI/CD pipeline

### For SQL Managed Instance
1. Plan migration from on-premises
2. Deploy test instance first
3. Test database restore process
4. Validate application compatibility
5. Plan cutover window (4-6 hours)
6. Deploy production instance
7. Execute migration

## 📞 Support

For issues or questions:
- Check README.md in each module directory
- Review Terraform documentation
- Check Azure SQL documentation
- Create support ticket in Azure Portal

---

**Created:** November 2024  
**Terraform Version:** >= 1.0  
**Azure Provider:** ~> 3.0  
**Status:** Production Ready ✅
