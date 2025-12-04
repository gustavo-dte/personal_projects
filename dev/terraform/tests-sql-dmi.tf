/*
 * Copyright (c) DTE Energy Corporate Services, LLC. All rights reserved.
 * Internal Use Only
 *
 * Test deployment for Azure SQL Managed Instance
 * Note: Resources created directly to avoid module data source timing issues
 */

#------------------------------------------------------------------------------
# Local variables for SQL MI configuration
#------------------------------------------------------------------------------
locals {
  sqlmi_environment             = "dev"
  sqlmi_location_short          = "cu"
  sqlmi_server_name             = "sqlmi-test-corpapps-dev"
  sqlmi_resource_name           = "dte-sqlmi-${local.sqlmi_location_short}-${local.sqlmi_environment}-${local.sqlmi_server_name}"
  sqlmi_endpoint_name           = "${local.sqlmi_resource_name}-pep"
  sqlmi_service_name            = "${local.sqlmi_endpoint_name}sc"
  sqlmi_audit_log_name          = "${local.sqlmi_resource_name}-audit-logs"
  sqlmi_short_term_retention    = 5  # Tier4 default
  sqlmi_long_term_retention = {
    weekly_retention  = "P1W"
    monthly_retention = "P1M"
    yearly_retention  = null
    week_of_year      = null
  }
}

#------------------------------------------------------------------------------
# Log Analytics Workspace for SQL MI diagnostics
#------------------------------------------------------------------------------
resource "azurerm_log_analytics_workspace" "sqlmi_law" {
  name                = "law-corpapps-sqlmi-dev-cu"
  location            = azurerm_resource_group.vm_migration_test.location
  resource_group_name = azurerm_resource_group.vm_migration_test.name
  sku                 = "PerGB2018"
  retention_in_days   = 30

  tags = local.tags
}

#------------------------------------------------------------------------------
# User Assigned Managed Identity for SQL MI
#------------------------------------------------------------------------------
resource "azurerm_user_assigned_identity" "sqlmi_umi" {
  name                = "umi-sqlmi-corpapps-dev"
  location            = azurerm_resource_group.vm_migration_test.location
  resource_group_name = azurerm_resource_group.vm_migration_test.name

  tags = local.tags
}

#------------------------------------------------------------------------------
# SQL Managed Instance
#------------------------------------------------------------------------------
resource "azurerm_mssql_managed_instance" "sqlmi_server" {
  name                = local.sqlmi_resource_name
  resource_group_name = azurerm_resource_group.vm_migration_test.name
  location            = azurerm_resource_group.vm_migration_test.location
  subnet_id           = module.primary_sqlmi_fbk_network.subnet_ids["main"]

  # Identity and access
  identity {
    type = "UserAssigned"
    identity_ids = [
      azurerm_user_assigned_identity.sqlmi_umi.id
    ]
  }

  administrator_login          = "sqladminuser"
  administrator_login_password = "P@ssw0rd!Secure2024#" # pragma: allowlist secret

  # Zone redundancy (false for Tier4)
  zone_redundant_enabled = false

  # Compute configuration
  sku_name           = "GP_Gen5"
  vcores             = 4
  storage_size_in_gb = 32

  # Locale
  collation   = "SQL_Latin1_General_CP1_CI_AS"
  timezone_id = "Eastern Standard Time"

  # License
  license_type                 = "LicenseIncluded"
  public_data_endpoint_enabled = false

  lifecycle {
    ignore_changes = [
      administrator_login,
      administrator_login_password,
    ]
  }

  tags = local.tags

  depends_on = [
    azurerm_user_assigned_identity.sqlmi_umi
  ]
}

#------------------------------------------------------------------------------
# SQL Managed Instance Databases
#------------------------------------------------------------------------------
resource "azurerm_mssql_managed_database" "sqlmi_databases" {
  for_each = toset(["TestDatabase01", "TestDatabase02"])

  name                      = each.key
  managed_instance_id       = azurerm_mssql_managed_instance.sqlmi_server.id
  short_term_retention_days = local.sqlmi_short_term_retention

  long_term_retention_policy {
    weekly_retention  = local.sqlmi_long_term_retention.weekly_retention
    monthly_retention = local.sqlmi_long_term_retention.monthly_retention
    yearly_retention  = local.sqlmi_long_term_retention.yearly_retention
    week_of_year      = local.sqlmi_long_term_retention.week_of_year
  }

  depends_on = [
    azurerm_mssql_managed_instance.sqlmi_server
  ]
}

#------------------------------------------------------------------------------
# SQL Managed Instance Private Endpoint
#------------------------------------------------------------------------------
resource "azurerm_private_endpoint" "sqlmi_pep" {
  name                = local.sqlmi_endpoint_name
  resource_group_name = azurerm_resource_group.vm_migration_test.name
  location            = azurerm_resource_group.vm_migration_test.location
  subnet_id           = module.primary_network.subnet_ids["main"]

  private_service_connection {
    name                           = local.sqlmi_service_name
    private_connection_resource_id = azurerm_mssql_managed_instance.sqlmi_server.id
    subresource_names              = ["managedInstance"]
    is_manual_connection           = false
  }

  lifecycle {
    ignore_changes = [
      private_dns_zone_group
    ]
  }

  tags = local.tags

  depends_on = [
    azurerm_mssql_managed_instance.sqlmi_server
  ]
}

#------------------------------------------------------------------------------
# Diagnostic Settings for SQL MI Audit Logs
#------------------------------------------------------------------------------
resource "azurerm_monitor_diagnostic_setting" "sqlmi_audit_logs" {
  name                       = local.sqlmi_audit_log_name
  target_resource_id         = azurerm_mssql_managed_instance.sqlmi_server.id
  log_analytics_workspace_id = azurerm_log_analytics_workspace.sqlmi_law.id

  enabled_log {
    category = "SQLSecurityAuditEvents"
  }

  depends_on = [
    azurerm_mssql_managed_instance.sqlmi_server,
    azurerm_log_analytics_workspace.sqlmi_law
  ]
}
