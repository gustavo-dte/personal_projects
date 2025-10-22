# Development Environment Configuration
environment     = "Development"
project_name    = "VM-Migration-SQL-Dev"
resource_owner  = "Development Team"

# Resource Configuration
resource_group_name = "rg-vm-migration-sql-dev"
azure_location      = "East US"

# SQL Server Configuration
sql_server_name     = "sql-vm-migration-dev"
administrator_login = "devadmin"

# SQL Databases Configuration - Smaller sizes for dev
sql_databases = [
  {
    name                        = "migration-db-dev"
    collation                  = "SQL_Latin1_General_CP1_CI_AS"
    license_type              = "LicenseIncluded"
    max_size_gb               = 32
    sku_name                  = "S1"
    zone_redundant            = false
    auto_pause_delay_in_minutes = null
    min_capacity              = null
  }
]

# Security Configuration - More permissive for dev
firewall_rules = [
  {
    name             = "AllowAzureServices"
    start_ip_address = "0.0.0.0"
    end_ip_address   = "0.0.0.0"
  },
  {
    name             = "AllowDeveloperNetwork"
    start_ip_address = "10.0.0.0"
    end_ip_address   = "10.0.255.255"
  }
]

# Backup Configuration - Shorter retention for dev
backup_policy = {
  retention_days               = 7
  geo_redundant_backup_enabled = false
  geo_backup_enabled          = false
}

# Tagging
tags = {
  Environment   = "Development"
  Project       = "VM-Migration"
  Owner         = "Development Team"
  CostCenter    = "IT-Development"
  BusinessUnit  = "IT"
  BackupPolicy  = "Weekly"
  Compliance    = "Non-Production"
}