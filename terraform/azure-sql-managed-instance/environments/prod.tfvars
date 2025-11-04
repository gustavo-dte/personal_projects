# Production Environment Configuration for SQL Managed Instance

resource_group_name = "rg-prod-sqlmi"
location            = "eastus"

# Network Configuration
vnet_address_space     = "10.0.0.0/16"
subnet_address_prefix  = "10.0.1.0/24"

# Managed Instance Configuration
managed_instance_name = "sqlmi-prod-vmmigration"
administrator_login   = "sqladmin"

# Performance - Business Critical for production
sku_name             = "BC_Gen5"
vcores               = 16
storage_size_in_gb   = 1024
license_type         = "BasePrice"  # Azure Hybrid Benefit - 55% savings!

# Database settings
collation   = "SQL_Latin1_General_CP1_CI_AS"
timezone_id = "Eastern Standard Time"

# Security
minimum_tls_version          = "1.2"
public_data_endpoint_enabled = false
proxy_override               = "Redirect"  # Better performance

# High Availability
zone_redundant_enabled = true
storage_account_type   = "ZRS"

# Azure AD Authentication
enable_azure_ad_auth      = false  # Set to true and configure below
# azure_ad_admin_login      = "dba@company.com"
# azure_ad_admin_object_id  = "12345678-1234-1234-1234-123456789012"

# Threat Detection
enable_threat_detection           = true
threat_detection_retention_days   = 90
threat_detection_email_admins     = true
threat_detection_email_addresses  = ["dba@company.com", "security@company.com"]

# Auditing
enable_auditing = true

# Vulnerability Assessment
enable_vulnerability_assessment = true

# Maintenance Window
maintenance_configuration_name = "SQL_Default"

tags = {
  Environment         = "Production"
  Project             = "VM-Migration"
  ManagedBy           = "Terraform"
  CostCenter          = "IT-Infrastructure"
  BusinessCriticality = "High"
  Compliance          = "SOX-Required"
  BackupPolicy        = "Automated"
}
