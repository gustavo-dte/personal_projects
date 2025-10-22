# Generate random password for SQL Server administrator
resource "random_password" "sql_admin_password" {
  count   = var.administrator_login_password == null ? 1 : 0
  length  = 16
  special = true
}

# Azure SQL Server Module
module "sql_server" {
  source = "./modules/sql-server"

  # Basic Configuration
  sql_server_name     = var.sql_server_name
  resource_group_name = var.resource_group_name
  location           = var.azure_location
  sql_server_version = var.sql_server_version

  # Authentication
  administrator_login          = var.administrator_login
  administrator_login_password = var.administrator_login_password != null ? var.administrator_login_password : random_password.sql_admin_password[0].result

  # Security
  firewall_rules         = var.firewall_rules
  allow_azure_services   = var.allow_azure_services
  azure_ad_admin        = var.azure_ad_admin
  enable_threat_detection = var.enable_threat_detection
  threat_detection_policy = var.threat_detection_policy

  # Monitoring
  enable_monitoring           = var.enable_monitoring
  log_analytics_workspace_id  = var.log_analytics_workspace_id
  storage_account_id         = var.storage_account_id

  # Tagging
  tags = merge(var.tags, {
    Component = "SQL-Server"
  })
}

# Azure SQL Database Module
module "sql_databases" {
  source = "./modules/sql-database"

  count = length(var.sql_databases)

  # Server Configuration
  sql_server_id       = module.sql_server.sql_server_id
  resource_group_name = var.resource_group_name
  location           = var.azure_location

  # Database Configuration
  database_name                = var.sql_databases[count.index].name
  collation                   = var.sql_databases[count.index].collation
  license_type               = var.sql_databases[count.index].license_type
  max_size_gb                = var.sql_databases[count.index].max_size_gb
  sku_name                   = var.sql_databases[count.index].sku_name
  zone_redundant             = var.sql_databases[count.index].zone_redundant
  auto_pause_delay_in_minutes = var.sql_databases[count.index].auto_pause_delay_in_minutes
  min_capacity               = var.sql_databases[count.index].min_capacity

  # Security and Backup
  backup_policy           = var.backup_policy
  enable_threat_detection = var.enable_threat_detection
  threat_detection_policy = var.threat_detection_policy

  # Monitoring
  enable_monitoring           = var.enable_monitoring
  log_analytics_workspace_id  = var.log_analytics_workspace_id
  storage_account_id         = var.storage_account_id

  # Tagging
  tags = merge(var.tags, {
    Component    = "SQL-Database"
    DatabaseName = var.sql_databases[count.index].name
  })

  depends_on = [module.sql_server]
}