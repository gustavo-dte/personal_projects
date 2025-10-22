# Production Environment Configuration
environment     = "Production"
project_name    = "VM-Migration-SQL-Prod"
resource_owner  = "Platform Team"

# Resource Configuration
resource_group_name = "rg-vm-migration-sql-prod"
azure_location      = "East US"

# SQL Server Configuration
sql_server_name     = "sql-vm-migration-prod"
administrator_login = "sqladmin"

# SQL Databases Configuration - Enterprise sizes
sql_databases = [
  {
    name                        = "migration-db"
    collation                  = "SQL_Latin1_General_CP1_CI_AS"
    license_type              = "LicenseIncluded"
    max_size_gb               = 500
    sku_name                  = "S4"
    zone_redundant            = true
    auto_pause_delay_in_minutes = null
    min_capacity              = null
  },
  {
    name                        = "config-db"
    collation                  = "SQL_Latin1_General_CP1_CI_AS"
    license_type              = "LicenseIncluded"
    max_size_gb               = 100
    sku_name                  = "S2"
    zone_redundant            = true
    auto_pause_delay_in_minutes = null
    min_capacity              = null
  },
  {
    name                        = "audit-db"
    collation                  = "SQL_Latin1_General_CP1_CI_AS"
    license_type              = "LicenseIncluded"
    max_size_gb               = 250
    sku_name                  = "S3"
    zone_redundant            = true
    auto_pause_delay_in_minutes = null
    min_capacity              = null
  }
]

# Security Configuration - Restrictive for prod
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

# Advanced Threat Protection - Full monitoring
enable_threat_detection = true
threat_detection_policy = {
  retention_days       = 90
  email_account_admins = true
  email_addresses     = ["dba@company.com", "security@company.com"]
}

# Backup Configuration - Extended retention for prod
backup_policy = {
  retention_days               = 35
  geo_redundant_backup_enabled = true
  geo_backup_enabled          = true
}

# Full monitoring enabled
enable_monitoring = true

# Tagging
tags = {
  Environment   = "Production"
  Project       = "VM-Migration"
  Owner         = "Platform Team"
  CostCenter    = "IT-Infrastructure"
  BusinessUnit  = "IT"
  BackupPolicy  = "Daily"
  Compliance    = "SOX-Required"
  Criticality   = "High"
}