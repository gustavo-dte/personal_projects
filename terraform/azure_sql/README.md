# Azure SQL Database Terraform Module

This Terraform module creates and manages Azure SQL Database resources including SQL Server, databases, security configurations, monitoring, and backup policies for the VM Migration project.

## Architecture

The module creates the following resources:
- Azure SQL Server with authentication and security configurations
- Azure SQL Databases with configurable performance tiers
- Firewall rules and network access controls
- Advanced Threat Protection and auditing
- Backup and disaster recovery configurations
- Monitoring and diagnostic settings
- Resource tagging for governance

## Features

- **Multi-Database Support**: Create multiple databases on a single SQL Server
- **Security**: Advanced Threat Protection, firewall rules, Azure AD authentication
- **Monitoring**: Integration with Azure Monitor and Log Analytics
- **Backup**: Configurable backup retention and geo-redundancy
- **Environment Support**: Separate configurations for dev, staging, and production
- **Compliance**: Auditing and diagnostic logging for compliance requirements

## Module Structure

```
azure_sql/
├── main.tf                 # Main configuration and module calls
├── variables.tf            # Input variable definitions
├── outputs.tf              # Output value definitions
├── providers.tf            # Provider configuration
├── terraform.tfvars        # Default variable values
├── terraform-docs.yml      # Documentation configuration
├── environments/           # Environment-specific configurations
│   ├── dev.tfvars
│   └── prod.tfvars
├── modules/                # Reusable sub-modules
│   ├── sql-server/         # SQL Server module
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   └── sql-database/       # SQL Database module
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
└── scripts/                # Deployment automation
    ├── deploy.sh           # Bash deployment script
    └── deploy.ps1          # PowerShell deployment script
```

## Quick Start

### Prerequisites

1. **Terraform**: Install [Terraform](https://www.terraform.io/downloads.html) >= 1.0
2. **Azure CLI**: Install and login with `az login`
3. **Permissions**: Ensure you have Contributor access to the target subscription

### Basic Deployment

1. **Clone the repository**:
   ```bash
   git checkout story/19034-SQL-DB-Instance
   cd terraform/azure_sql
   ```

2. **Configure variables**:
   ```bash
   cp terraform.tfvars.example terraform.tfvars
   # Edit terraform.tfvars with your specific values
   ```

3. **Deploy**:
   ```bash
   # Using the deployment script
   ./scripts/deploy.sh dev plan
   ./scripts/deploy.sh dev apply

   # Or manually
   terraform init
   terraform plan -var-file="environments/dev.tfvars"
   terraform apply
   ```

## Usage Examples

### Basic Configuration

```hcl
module "azure_sql" {
  source = "./terraform/azure_sql"

  # Basic Configuration
  resource_group_name = "rg-sql-example"
  azure_location      = "East US"
  sql_server_name     = "sql-server-example"

  # Authentication
  administrator_login          = "sqladmin"
  administrator_login_password = var.sql_admin_password

  # Single Database
  sql_databases = [
    {
      name         = "app-database"
      max_size_gb  = 100
      sku_name     = "S2"
    }
  ]

  # Basic Security
  firewall_rules = [
    {
      name             = "AllowAzureServices"
      start_ip_address = "0.0.0.0"
      end_ip_address   = "0.0.0.0"
    }
  ]

  tags = {
    Environment = "Production"
    Project     = "VM-Migration"
  }
}
```

### Production Configuration

```hcl
module "azure_sql" {
  source = "./terraform/azure_sql"

  # Configuration
  resource_group_name = "rg-vm-migration-sql-prod"
  azure_location      = "East US"
  sql_server_name     = "sql-vm-migration-prod"

  # Authentication
  administrator_login          = "sqladmin"
  administrator_login_password = var.sql_admin_password

  # Azure AD Authentication
  azure_ad_admin = {
    login_username = "admin@company.com"
    object_id      = "12345678-1234-1234-1234-123456789012"
    tenant_id      = var.azure_tenant_id
  }

  # Multiple Databases
  sql_databases = [
    {
      name                        = "migration-db"
      max_size_gb                = 500
      sku_name                   = "S4"
      zone_redundant             = true
    },
    {
      name                        = "config-db"
      max_size_gb                = 100
      sku_name                   = "S2"
      zone_redundant             = true
    },
    {
      name                        = "audit-db"
      max_size_gb                = 250
      sku_name                   = "S3"
      zone_redundant             = true
    }
  ]

  # Security Configuration
  firewall_rules = [
    {
      name             = "AllowAzureServices"
      start_ip_address = "0.0.0.0"
      end_ip_address   = "0.0.0.0"
    },
    {
      name             = "AllowProductionNetwork"
      start_ip_address = "192.168.1.0"
      end_ip_address   = "192.168.1.255"
    }
  ]

  # Advanced Security
  enable_threat_detection = true
  threat_detection_policy = {
    retention_days       = 90
    email_account_admins = true
    email_addresses     = ["dba@company.com", "security@company.com"]
  }

  # Enterprise Backup
  backup_policy = {
    retention_days               = 35
    geo_redundant_backup_enabled = true
    geo_backup_enabled          = true
  }

  # Full Monitoring
  enable_monitoring           = true
  log_analytics_workspace_id  = var.log_analytics_workspace_id
  storage_account_id         = var.storage_account_id

  tags = {
    Environment   = "Production"
    Project       = "VM-Migration"
    Owner         = "Platform Team"
    CostCenter    = "IT-Infrastructure"
    Compliance    = "SOX-Required"
    Criticality   = "High"
  }
}
```

## Environment Management

### Development Environment

For development workloads with cost optimization:

```bash
./scripts/deploy.sh dev plan
./scripts/deploy.sh dev apply
```

Features:
- Smaller database sizes (32GB)
- Basic SKUs (S1)
- No zone redundancy
- Shorter backup retention (7 days)
- Permissive firewall rules for development

### Production Environment

For production workloads with high availability:

```bash
./scripts/deploy.sh prod plan
./scripts/deploy.sh prod apply
```

Features:
- Large database sizes (500GB+)
- Premium SKUs (S4, P2)
- Zone redundancy enabled
- Extended backup retention (35 days)
- Restrictive firewall rules
- Full monitoring and alerting

## Security Configuration

### Authentication

The module supports multiple authentication methods:

1. **SQL Authentication**: Traditional username/password
2. **Azure AD Authentication**: Integration with Azure Active Directory
3. **Combined Mode**: Both SQL and Azure AD authentication

### Network Security

Configure firewall rules to control access:

```hcl
firewall_rules = [
  {
    name             = "AllowAzureServices"
    start_ip_address = "0.0.0.0"
    end_ip_address   = "0.0.0.0"
  },
  {
    name             = "AllowOfficeNetwork"
    start_ip_address = "203.0.113.0"
    end_ip_address   = "203.0.113.255"
  },
  {
    name             = "AllowSpecificServer"
    start_ip_address = "203.0.113.100"
    end_ip_address   = "203.0.113.100"
  }
]
```

### Advanced Threat Protection

Enable comprehensive security monitoring:

```hcl
enable_threat_detection = true
threat_detection_policy = {
  retention_days       = 90
  email_account_admins = true
  email_addresses     = ["security@company.com"]
  disabled_alerts     = []  # Enable all alert types
}
```

## Monitoring and Observability

### Diagnostic Settings

The module automatically configures diagnostic logging for:
- SQL Insights
- Automatic Tuning
- Query Store Statistics
- Error Logs
- Performance Metrics
- Security Events

### Log Analytics Integration

Connect to existing Log Analytics workspace:

```hcl
enable_monitoring           = true
log_analytics_workspace_id  = "/subscriptions/.../workspaces/my-workspace"
```

### Storage Account for Auditing

Configure audit log storage:

```hcl
storage_account_id = "/subscriptions/.../storageAccounts/auditlogs"
```

## Backup and Disaster Recovery

### Backup Configuration

```hcl
backup_policy = {
  retention_days               = 35    # Point-in-time restore window
  geo_redundant_backup_enabled = true  # Cross-region backup replication
  geo_backup_enabled          = true   # Geo-restore capability
}
```

### Long-term Retention

The module configures long-term retention policies:
- Weekly backups: 1 week retention
- Monthly backups: 1 month retention
- Yearly backups: 1 year retention

## Performance and Scaling

### SKU Selection Guide

| Workload Type | Recommended SKU | Max Size | Use Case |
|---------------|-----------------|----------|----------|
| Development   | S0, S1          | 32-250GB | Dev/Test environments |
| Small Production | S2, S3       | 250GB-1TB | Small applications |
| Medium Production | S4-S6, P1-P2 | 500GB-4TB | Medium applications |
| Enterprise    | P4-P15          | 1TB-10TB+ | High-performance workloads |

### Zone Redundancy

Enable for production workloads requiring high availability:

```hcl
zone_redundant = true  # Provides 99.995% availability SLA
```

## Cost Optimization

### Development Environments

- Use smaller SKUs (S0, S1)
- Disable zone redundancy
- Shorter backup retention
- Consider serverless for sporadic workloads

### Production Environments

- Right-size based on actual usage
- Use reserved capacity for predictable workloads
- Monitor and adjust performance tiers
- Implement automated scaling policies

## Troubleshooting

### Common Issues

1. **Authentication Failures**
   - Verify Azure credentials: `az account show`
   - Check service principal permissions
   - Validate firewall rules

2. **Terraform State Issues**
   - Initialize backend: `terraform init`
   - Import existing resources if needed
   - Use state locking for team environments

3. **Network Connectivity**
   - Verify firewall rules
   - Check NSG configurations
   - Test from allowed IP ranges

### Diagnostic Commands

```bash
# Check Azure connection
az account show

# Validate Terraform
terraform validate

# Plan with detailed logging
TF_LOG=DEBUG terraform plan

# Show current state
terraform show
```

## Compliance and Governance

### Tagging Strategy

Implement consistent tagging for governance:

```hcl
tags = {
  Environment   = "Production"
  Project       = "VM-Migration"
  Owner         = "Platform Team"
  CostCenter    = "IT-Infrastructure"
  BusinessUnit  = "IT"
  BackupPolicy  = "Daily"
  Compliance    = "SOX-Required"
  Criticality   = "High"
  DataClass     = "Confidential"
}
```

### Compliance Features

- **Auditing**: Comprehensive audit logging
- **Encryption**: TDE enabled by default
- **Access Control**: RBAC and firewall rules
- **Monitoring**: Real-time threat detection
- **Backup**: Geo-redundant backup policies

## Automation and CI/CD

### GitHub Actions Integration

```yaml
name: Deploy SQL Database
on:
  push:
    branches: [main]
    paths: ['terraform/azure_sql/**']

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: hashicorp/setup-terraform@v2
      - name: Terraform Plan
        run: |
          cd terraform/azure_sql
          terraform init
          terraform plan -var-file="environments/prod.tfvars"
```

### Azure DevOps Pipeline

```yaml
trigger:
  branches:
    include:
      - main
  paths:
    include:
      - terraform/azure_sql/*

pool:
  vmImage: 'ubuntu-latest'

steps:
- task: TerraformInstaller@0
  inputs:
    terraformVersion: 'latest'

- script: |
    cd terraform/azure_sql
    terraform init
    terraform plan -var-file="environments/prod.tfvars"
  displayName: 'Terraform Plan'
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes following the coding standards
4. Test in development environment
5. Update documentation
6. Submit a pull request

### Code Standards

- Use consistent naming conventions
- Include comprehensive variable descriptions
- Add appropriate tags to all resources
- Follow Terraform best practices
- Include examples in documentation

## Support

For issues and questions:
- Create GitHub issues for bugs or feature requests
- Contact the Platform Team for deployment support
- Refer to Azure SQL Database documentation for service-specific questions

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

*This module is part of the VM Migration infrastructure project. For more information, see the main project documentation.*