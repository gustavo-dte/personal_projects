# Azure SQL Managed Instance Terraform Module

This module creates and configures an Azure SQL Managed Instance with comprehensive security, monitoring, and high availability features.

## Features

- **SQL Managed Instance**: Fully managed SQL Server instance in Azure
- **High Availability**: Zone redundancy and failover group support
- **Security**: Azure AD authentication, TDE, Advanced Threat Protection, Vulnerability Assessment
- **Monitoring**: Integration with Azure Monitor and Log Analytics
- **Network Isolation**: Deployed in a dedicated subnet with optional public endpoint
- **Managed Identity**: System or user-assigned managed identity support

## Usage

### Basic Usage

```hcl
module "sql_managed_instance" {
  source = "./modules/sql-managed-instance"

  managed_instance_name        = "my-sql-mi"
  resource_group_name          = "my-rg"
  location                     = "eastus"
  subnet_id                    = azurerm_subnet.sql_mi_subnet.id
  
  administrator_login          = "sqladmin"
  administrator_login_password = var.sql_admin_password
  
  sku_name             = "GP_Gen5"
  vcores               = 8
  storage_size_in_gb   = 64
  license_type         = "BasePrice"  # Azure Hybrid Benefit
  
  tags = {
    Environment = "Production"
    Project     = "MyApp"
  }
}
```

### Advanced Usage with All Features

```hcl
module "sql_managed_instance" {
  source = "./modules/sql-managed-instance"

  # Basic Configuration
  managed_instance_name        = "my-sql-mi-prod"
  resource_group_name          = "my-rg-prod"
  location                     = "eastus"
  subnet_id                    = azurerm_subnet.sql_mi_subnet.id
  
  # Authentication
  administrator_login          = "sqladmin"
  administrator_login_password = var.sql_admin_password
  
  # SKU and Performance
  sku_name             = "BC_Gen5"  # Business Critical
  vcores               = 16
  storage_size_in_gb   = 256
  license_type         = "BasePrice"  # Azure Hybrid Benefit
  
  # High Availability
  zone_redundant_enabled = true
  
  # Azure AD Authentication
  azure_ad_admin = {
    login_username              = "admin@contoso.com"
    object_id                   = "12345678-1234-1234-1234-123456789012"
    azuread_authentication_only = false
  }
  
  # Transparent Data Encryption with Customer-Managed Key
  enable_tde           = true
  tde_key_vault_key_id = azurerm_key_vault_key.sql_tde.id
  
  # Managed Identity
  identity_type = "SystemAssigned"
  
  # Security
  minimum_tls_version          = "1.2"
  public_data_endpoint_enabled = false
  
  # Advanced Threat Protection
  enable_threat_detection = true
  threat_detection_policy = {
    retention_days       = 90
    email_account_admins = true
    email_addresses      = ["security@contoso.com"]
    storage_endpoint     = azurerm_storage_account.security.primary_blob_endpoint
    storage_account_access_key = azurerm_storage_account.security.primary_access_key
  }
  
  # Vulnerability Assessment
  enable_vulnerability_assessment = true
  vulnerability_assessment_config = {
    storage_container_path = "${azurerm_storage_account.security.primary_blob_endpoint}vulnerability-assessment"
    storage_account_access_key = azurerm_storage_account.security.primary_access_key
    recurring_scans = {
      enabled                   = true
      email_subscription_admins = true
      emails                    = ["security@contoso.com"]
    }
  }
  
  # Maintenance Configuration
  maintenance_configuration_name = "SQL_EastUS_MI_1"
  
  tags = {
    Environment         = "Production"
    Project             = "MyApp"
    BusinessCriticality = "Tier1"
  }
}
```

### Failover Group Configuration

```hcl
# Primary Managed Instance
module "sql_mi_primary" {
  source = "./modules/sql-managed-instance"

  managed_instance_name        = "sql-mi-eastus"
  resource_group_name          = "rg-eastus"
  location                     = "eastus"
  subnet_id                    = azurerm_subnet.sql_mi_primary.id
  
  administrator_login          = "sqladmin"
  administrator_login_password = var.sql_admin_password
  
  sku_name             = "GP_Gen5"
  vcores               = 8
  storage_size_in_gb   = 64
}

# Secondary Managed Instance
module "sql_mi_secondary" {
  source = "./modules/sql-managed-instance"

  managed_instance_name        = "sql-mi-westus"
  resource_group_name          = "rg-westus"
  location                     = "westus"
  subnet_id                    = azurerm_subnet.sql_mi_secondary.id
  
  administrator_login          = "sqladmin"
  administrator_login_password = var.sql_admin_password
  
  sku_name             = "GP_Gen5"
  vcores               = 8
  storage_size_in_gb   = 64
  
  dns_zone_partner_id  = module.sql_mi_primary.managed_instance_id
  
  # Failover Group
  failover_group_config = {
    name                        = "sql-mi-fog"
    partner_managed_instance_id = module.sql_mi_primary.managed_instance_id
    failover_policy_mode        = "Automatic"
    grace_minutes               = 60
    readonly_endpoint_enabled   = true
  }
  
  depends_on = [module.sql_mi_primary]
}
```

## SKU Options

### General Purpose (GP)
- **GP_Gen5**: 5th generation General Purpose
- **GP_Gen8IM**: 8th generation Intel General Purpose
- **GP_Gen8IH**: 8th generation Intel Hybrid General Purpose

### Business Critical (BC)
- **BC_Gen5**: 5th generation Business Critical
- **BC_Gen8IM**: 8th generation Intel Business Critical
- **BC_Gen8IH**: 8th generation Intel Hybrid Business Critical

## Network Requirements

SQL Managed Instance requires a dedicated subnet with specific requirements:

1. Subnet must be delegated to `Microsoft.Sql/managedInstances`
2. Minimum subnet size: /28 (16 IP addresses)
3. Network Security Group (NSG) must allow specific ports
4. Route table must be configured for internet connectivity

### Example Subnet Configuration

```hcl
resource "azurerm_subnet" "sql_mi" {
  name                 = "sql-mi-subnet"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.1.0/24"]
  
  delegation {
    name = "managedinstancedelegation"
    
    service_delegation {
      name    = "Microsoft.Sql/managedInstances"
      actions = [
        "Microsoft.Network/virtualNetworks/subnets/join/action",
        "Microsoft.Network/virtualNetworks/subnets/prepareNetworkPolicies/action",
        "Microsoft.Network/virtualNetworks/subnets/unprepareNetworkPolicies/action"
      ]
    }
  }
}
```

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| managed_instance_name | Name of the SQL Managed Instance | string | n/a | yes |
| resource_group_name | Name of the resource group | string | n/a | yes |
| location | Azure region | string | n/a | yes |
| subnet_id | Subnet ID for managed instance | string | n/a | yes |
| administrator_login | Administrator login | string | n/a | yes |
| administrator_login_password | Administrator password | string | n/a | yes |
| sku_name | SKU name | string | "GP_Gen5" | no |
| vcores | Number of vCores | number | 4 | no |
| storage_size_in_gb | Storage size in GB | number | 32 | no |
| license_type | License type | string | "LicenseIncluded" | no |
| zone_redundant_enabled | Enable zone redundancy | bool | false | no |
| public_data_endpoint_enabled | Enable public endpoint | bool | false | no |
| minimum_tls_version | Minimum TLS version | string | "1.2" | no |

## Outputs

| Name | Description |
|------|-------------|
| managed_instance_id | The ID of the managed instance |
| managed_instance_name | The name of the managed instance |
| managed_instance_fqdn | The FQDN of the managed instance |
| dns_zone_id | DNS zone ID |
| identity | Managed identity configuration |
| failover_group_id | Failover group ID (if configured) |

## Important Notes

1. **Deployment Time**: Managed Instance deployment can take 4-6 hours for initial creation
2. **Cost**: Managed Instance is a premium service with higher costs compared to single databases
3. **Azure Hybrid Benefit**: Use `license_type = "BasePrice"` to save up to 55% with existing SQL Server licenses
4. **Network Isolation**: Managed Instance is deployed in a dedicated subnet and requires proper network configuration
5. **Maintenance Window**: Configure maintenance windows to control when updates are applied

## Examples

See the [examples](../../examples/) directory for complete working examples.

## License

MIT
