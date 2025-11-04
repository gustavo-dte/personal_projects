# Production Environment Configuration

resource_group_name = "rg-prod-sqldb"
location            = "eastus"

sql_server_name     = "sql-prod-vmmigration"
administrator_login = "sqladmin"

firewall_rules = [
  {
    name             = "AllowProductionNetwork"
    start_ip_address = "192.168.1.0"
    end_ip_address   = "192.168.1.255"
  }
]

allow_azure_services = true

databases = {
  "app-db" = {
    name           = "application-database"
    sku_name       = "S4"        # 200 DTUs - ~$465/month
    max_size_gb    = 500
    zone_redundant = true
  },
  "reporting-db" = {
    name           = "reporting-database"
    sku_name       = "S3"        # 100 DTUs - ~$233/month
    max_size_gb    = 250
    zone_redundant = true
  },
  "audit-db" = {
    name           = "audit-database"
    sku_name       = "S2"        # 50 DTUs - ~$75/month
    max_size_gb    = 100
    zone_redundant = true
  }
}

backup_retention_days       = 35
long_term_retention_weekly  = "P4W"
long_term_retention_monthly = "P12M"
long_term_retention_yearly  = "P10Y"

enable_threat_detection           = true
threat_detection_retention_days   = 90
threat_detection_email_admins     = true
threat_detection_email_addresses  = ["dba@company.com", "security@company.com"]

enable_auditing       = true
audit_retention_days  = 90

enable_monitoring     = true
log_retention_days    = 365

tags = {
  Environment         = "Production"
  Project             = "VM-Migration"
  ManagedBy           = "Terraform"
  CostCenter          = "IT-Infrastructure"
  BusinessCriticality = "High"
  Compliance          = "SOX-Required"
  BackupPolicy        = "Daily"
}
