# SQL Server
resource "azurerm_mssql_server" "main" {
  name                         = var.sql_server_name
  resource_group_name          = var.resource_group_name
  location                     = var.location
  version                      = var.sql_server_version
  administrator_login          = var.administrator_login
  administrator_login_password = var.administrator_login_password

  tags = var.tags
}

# Extended Auditing Policy (if monitoring enabled)
resource "azurerm_mssql_server_extended_auditing_policy" "main" {
  count                      = var.enable_monitoring ? 1 : 0
  server_id                  = azurerm_mssql_server.main.id
  storage_endpoint           = var.storage_account_id != null ? "https://${split("/", var.storage_account_id)[8]}.blob.core.windows.net/" : null
  storage_account_access_key = var.threat_detection_policy.storage_account_access_key
  retention_in_days         = var.threat_detection_policy.retention_days
  log_monitoring_enabled    = var.log_analytics_workspace_id != null
  enabled                   = true
}

# Firewall Rules
resource "azurerm_mssql_firewall_rule" "main" {
  for_each = { for rule in var.firewall_rules : rule.name => rule }

  name             = each.value.name
  server_id        = azurerm_mssql_server.main.id
  start_ip_address = each.value.start_ip_address
  end_ip_address   = each.value.end_ip_address
}

# Azure Services Access Rule
resource "azurerm_mssql_firewall_rule" "azure_services" {
  count = var.allow_azure_services ? 1 : 0

  name             = "AllowAzureServices"
  server_id        = azurerm_mssql_server.main.id
  start_ip_address = "0.0.0.0"
  end_ip_address   = "0.0.0.0"
}

# Azure AD Administrator (if configured)
resource "azurerm_mssql_server_transparent_data_encryption" "main" {
  server_id = azurerm_mssql_server.main.id
}

# Security Alert Policy (Advanced Threat Protection)
resource "azurerm_mssql_server_security_alert_policy" "main" {
  count = var.enable_threat_detection ? 1 : 0

  resource_group_name        = var.resource_group_name
  server_name               = azurerm_mssql_server.main.name
  state                     = "Enabled"
  retention_days            = var.threat_detection_policy.retention_days
  disabled_alerts           = var.threat_detection_policy.disabled_alerts
  email_account_admins      = var.threat_detection_policy.email_account_admins
  email_addresses           = var.threat_detection_policy.email_addresses
  storage_endpoint          = var.threat_detection_policy.storage_endpoint
  storage_account_access_key = var.threat_detection_policy.storage_account_access_key
}