# ============================================================================
# Azure SQL Database Terraform Configuration
# ============================================================================

terraform {
  required_version = ">= 1.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.4"
    }
  }
}

provider "azurerm" {
  features {}
}

# ============================================================================
# DATA SOURCES
# ============================================================================

data "azurerm_client_config" "current" {}

# ============================================================================
# RESOURCE GROUP
# ============================================================================

resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location
  tags     = var.tags
}

# ============================================================================
# LOG ANALYTICS WORKSPACE (for monitoring)
# ============================================================================

resource "azurerm_log_analytics_workspace" "main" {
  count               = var.enable_monitoring ? 1 : 0
  name                = "${var.sql_server_name}-logs"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "PerGB2018"
  retention_in_days   = var.log_retention_days
  tags                = var.tags
}

# ============================================================================
# STORAGE ACCOUNT (for auditing)
# ============================================================================

resource "random_string" "storage_suffix" {
  length  = 8
  special = false
  upper   = false
}

resource "azurerm_storage_account" "audit" {
  count                    = var.enable_auditing ? 1 : 0
  name                     = "sqlaudit${random_string.storage_suffix.result}"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "GRS"
  
  blob_properties {
    versioning_enabled = true
    
    delete_retention_policy {
      days = 90
    }
  }

  tags = var.tags
}

# ============================================================================
# GENERATE SECURE PASSWORD (if not provided)
# ============================================================================

resource "random_password" "sql_admin" {
  count   = var.administrator_login_password == null ? 1 : 0
  length  = 24
  special = true
  override_special = "!@#$%&*()-_=+[]{}:?"
}

# ============================================================================
# SQL SERVER
# ============================================================================

resource "azurerm_mssql_server" "main" {
  name                         = var.sql_server_name
  resource_group_name          = azurerm_resource_group.main.name
  location                     = azurerm_resource_group.main.location
  version                      = var.sql_server_version
  administrator_login          = var.administrator_login
  administrator_login_password = var.administrator_login_password != null ? var.administrator_login_password : random_password.sql_admin[0].result
  minimum_tls_version          = var.minimum_tls_version

  tags = var.tags
}

# ============================================================================
# FIREWALL RULES
# ============================================================================

resource "azurerm_mssql_firewall_rule" "main" {
  for_each = { for rule in var.firewall_rules : rule.name => rule }

  name             = each.value.name
  server_id        = azurerm_mssql_server.main.id
  start_ip_address = each.value.start_ip_address
  end_ip_address   = each.value.end_ip_address
}

resource "azurerm_mssql_firewall_rule" "azure_services" {
  count = var.allow_azure_services ? 1 : 0

  name             = "AllowAzureServices"
  server_id        = azurerm_mssql_server.main.id
  start_ip_address = "0.0.0.0"
  end_ip_address   = "0.0.0.0"
}

# ============================================================================
# AZURE AD ADMINISTRATOR (Optional)
# ============================================================================

resource "azurerm_mssql_server_transparent_data_encryption" "main" {
  server_id = azurerm_mssql_server.main.id
}

# ============================================================================
# SERVER AUDITING POLICY
# ============================================================================

resource "azurerm_mssql_server_extended_auditing_policy" "main" {
  count                  = var.enable_auditing ? 1 : 0
  server_id              = azurerm_mssql_server.main.id
  storage_endpoint       = azurerm_storage_account.audit[0].primary_blob_endpoint
  storage_account_access_key = azurerm_storage_account.audit[0].primary_access_key
  retention_in_days      = var.audit_retention_days
  log_monitoring_enabled = var.enable_monitoring
}

# ============================================================================
# SERVER SECURITY ALERT POLICY (Advanced Threat Protection)
# ============================================================================

resource "azurerm_mssql_server_security_alert_policy" "main" {
  count = var.enable_threat_detection ? 1 : 0

  resource_group_name = azurerm_resource_group.main.name
  server_name         = azurerm_mssql_server.main.name
  state               = "Enabled"
  retention_days      = var.threat_detection_retention_days
  email_account_admins = var.threat_detection_email_admins
  email_addresses     = var.threat_detection_email_addresses
  
  storage_endpoint           = var.enable_auditing ? azurerm_storage_account.audit[0].primary_blob_endpoint : null
  storage_account_access_key = var.enable_auditing ? azurerm_storage_account.audit[0].primary_access_key : null
}

# ============================================================================
# SQL DATABASES
# ============================================================================

resource "azurerm_mssql_database" "main" {
  for_each = var.databases

  name           = each.value.name
  server_id      = azurerm_mssql_server.main.id
  collation      = each.value.collation
  license_type   = each.value.license_type
  max_size_gb    = each.value.max_size_gb
  sku_name       = each.value.sku_name
  zone_redundant = each.value.zone_redundant

  # Serverless configuration (only for serverless SKUs)
  auto_pause_delay_in_minutes = can(regex("^GP_S_", each.value.sku_name)) ? each.value.auto_pause_delay_in_minutes : null
  min_capacity                = can(regex("^GP_S_", each.value.sku_name)) ? each.value.min_capacity : null

  # Short-term backup retention
  short_term_retention_policy {
    retention_days           = var.backup_retention_days
    backup_interval_in_hours = 12
  }

  # Long-term backup retention
  long_term_retention_policy {
    weekly_retention  = var.long_term_retention_weekly
    monthly_retention = var.long_term_retention_monthly
    yearly_retention  = var.long_term_retention_yearly
    week_of_year      = var.long_term_retention_week_of_year
  }

  tags = merge(var.tags, {
    DatabaseName = each.value.name
  })
}

# ============================================================================
# DATABASE TRANSPARENT DATA ENCRYPTION
# ============================================================================

resource "azurerm_mssql_database_transparent_data_encryption" "main" {
  for_each = var.databases

  database_id = azurerm_mssql_database.main[each.key].id
}

# ============================================================================
# DATABASE EXTENDED AUDITING
# ============================================================================

resource "azurerm_mssql_database_extended_auditing_policy" "main" {
  for_each = var.enable_auditing ? var.databases : {}

  database_id                = azurerm_mssql_database.main[each.key].id
  storage_endpoint           = azurerm_storage_account.audit[0].primary_blob_endpoint
  storage_account_access_key = azurerm_storage_account.audit[0].primary_access_key
  retention_in_days          = var.audit_retention_days
  log_monitoring_enabled     = var.enable_monitoring
}

# ============================================================================
# DATABASE DIAGNOSTIC SETTINGS
# ============================================================================

resource "azurerm_monitor_diagnostic_setting" "database" {
  for_each = var.enable_monitoring ? var.databases : {}

  name                       = "${each.value.name}-diagnostics"
  target_resource_id         = azurerm_mssql_database.main[each.key].id
  log_analytics_workspace_id = azurerm_log_analytics_workspace.main[0].id

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

  metric {
    category = "Basic"
    enabled  = true
  }

  metric {
    category = "InstanceAndAppAdvanced"
    enabled  = true
  }

  metric {
    category = "WorkloadManagement"
    enabled  = true
  }
}
