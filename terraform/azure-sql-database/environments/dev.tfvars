# Development Environment Configuration

resource_group_name = "rg-dev-sqldb"
location            = "eastus"

sql_server_name     = "sql-dev-vmmigration"
administrator_login = "devadmin"

firewall_rules = [
  {
    name             = "AllowDeveloperNetwork"
    start_ip_address = "10.0.0.0"
    end_ip_address   = "10.0.255.255"
  }
]

allow_azure_services = true

databases = {
  "dev-db" = {
    name           = "development-database"
    sku_name       = "S0"
    max_size_gb    = 32
    zone_redundant = false
  }
}

backup_retention_days      = 7
long_term_retention_weekly = "P1W"

enable_threat_detection = false
enable_auditing        = false
enable_monitoring      = false

tags = {
  Environment = "Development"
  Project     = "VM-Migration"
  ManagedBy   = "Terraform"
  CostCenter  = "Engineering"
}
