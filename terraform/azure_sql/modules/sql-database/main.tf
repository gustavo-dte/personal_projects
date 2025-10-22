# SQL Database
resource "azurerm_mssql_database" "main" {
  name           = var.database_name
  server_id      = var.sql_server_id
  collation      = var.collation
  license_type   = var.license_type
  max_size_gb    = var.max_size_gb
  sku_name       = var.sku_name
  zone_redundant = var.zone_redundant

  # Serverless configuration (only for applicable SKUs)
  auto_pause_delay_in_minutes = contains(["GP_S_", "HS_"], substr(var.sku_name, 0, 4)) ? var.auto_pause_delay_in_minutes : null
  min_capacity               = contains(["GP_S_", "HS_"], substr(var.sku_name, 0, 4)) ? var.min_capacity : null

  # Backup configuration
  short_term_retention_policy {
    retention_days = var.backup_policy.retention_days
  }

  long_term_retention_policy {
    weekly_retention  = "P1W"
    monthly_retention = "P1M"
    yearly_retention  = "P1Y"
    week_of_year     = 1
  }

  tags = var.tags
}

# Transparent Data Encryption
resource "azurerm_mssql_database_transparent_data_encryption" "main" {
  database_id = azurerm_mssql_database.main.id
}

# Extended Auditing Policy
resource "azurerm_mssql_database_extended_auditing_policy" "main" {
  count                      = var.enable_monitoring ? 1 : 0
  database_id                = azurerm_mssql_database.main.id
  storage_endpoint           = var.storage_account_id != null ? "https://${split("/", var.storage_account_id)[8]}.blob.core.windows.net/" : null
  storage_account_access_key = var.threat_detection_policy.storage_account_access_key
  retention_in_days         = var.threat_detection_policy.retention_days
  log_monitoring_enabled    = var.log_analytics_workspace_id != null
  enabled                   = true
}

# Database Threat Detection Policy
resource "azurerm_mssql_database_threat_detection_policy" "main" {
  count = var.enable_threat_detection ? 1 : 0

  database_name              = azurerm_mssql_database.main.name
  server_name               = split("/", var.sql_server_id)[8]
  resource_group_name       = var.resource_group_name
  state                     = "Enabled"
  retention_days            = var.threat_detection_policy.retention_days
  disabled_alerts           = var.threat_detection_policy.disabled_alerts
  email_account_admins      = var.threat_detection_policy.email_account_admins
  email_addresses           = var.threat_detection_policy.email_addresses
  storage_endpoint          = var.threat_detection_policy.storage_endpoint
  storage_account_access_key = var.threat_detection_policy.storage_account_access_key
}

# Diagnostic Settings for monitoring
resource "azurerm_monitor_diagnostic_setting" "main" {
  count                      = var.enable_monitoring && var.log_analytics_workspace_id != null ? 1 : 0
  name                       = "${var.database_name}-diagnostics"
  target_resource_id         = azurerm_mssql_database.main.id
  log_analytics_workspace_id = var.log_analytics_workspace_id

  enabled_log {
    category = "SQLInsights"
  }

  enabled_log {
    category = "AutomaticTuning"
  }

  enabled_log {
    category = "QueryStoreRuntimeStatistics"
  }

  enabled_log {
    category = "QueryStoreWaitStatistics"
  }

  enabled_log {
    category = "Errors"
  }

  enabled_log {
    category = "DatabaseWaitStatistics"
  }

  enabled_log {
    category = "Timeouts"
  }

  enabled_log {
    category = "Blocks"
  }

  enabled_log {
    category = "Deadlocks"
  }
}