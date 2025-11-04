# Test Environment Configuration for SQL Managed Instance

resource_group_name = "rg-test-sqlmi"
location            = "eastus"

# Network Configuration
vnet_address_space     = "10.1.0.0/16"
subnet_address_prefix  = "10.1.1.0/24"

# Managed Instance Configuration
managed_instance_name = "sqlmi-test-vmmigration"
administrator_login   = "sqladmin"

# Performance - General Purpose for test
sku_name             = "GP_Gen5"
vcores               = 4
storage_size_in_gb   = 128
license_type         = "LicenseIncluded"

# Database settings
collation   = "SQL_Latin1_General_CP1_CI_AS"
timezone_id = "Eastern Standard Time"

# Security
minimum_tls_version          = "1.2"
public_data_endpoint_enabled = false
proxy_override               = "Proxy"

# High Availability - disabled for test
zone_redundant_enabled = false
storage_account_type   = "LRS"

# Threat Detection
enable_threat_detection           = true
threat_detection_retention_days   = 30
threat_detection_email_admins     = true
threat_detection_email_addresses  = ["testadmin@company.com"]

# Auditing
enable_auditing = true

# Vulnerability Assessment - optional for test
enable_vulnerability_assessment = false

tags = {
  Environment = "Test"
  Project     = "VM-Migration"
  ManagedBy   = "Terraform"
  CostCenter  = "IT-Testing"
}
