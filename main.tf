/*
 * Copyright (c) DTE Energy Corporate Services, LLC. All rights reserved.
 * Internal Use Only
 */

/*
 * Create the SQL Managed instance
 */
resource "azurerm_mssql_managed_instance" "sqlmi_server" {
  name                = local.resource_name
  resource_group_name = var.resource_group_name
  location            = var.location
  subnet_id           = var.sql_subnet_id

  // Identity and access
  identity {
    type = "UserAssigned"
    identity_ids = [
      data.azurerm_user_assigned_identity.umi_sqmi_server.id // Use the user managed identity if specified
    ]
  }
  administrator_login          = var.admin_username
  administrator_login_password = var.admin_password

  // Zone redundant based on application criticality
  zone_redundant_enabled = local.zone_redundant

  // compute
  sku_name           = var.sku_name // based on application criticality
  vcores             = var.vcores
  storage_size_in_gb = var.storage_size_in_gb

  // Locale
  collation   = var.collation
  timezone_id = var.timezone

  // Lincese
  license_type                 = var.license_type
  public_data_endpoint_enabled = false

  // Dont care if the user name or password change
  lifecycle {
    ignore_changes = [
      administrator_login,          // Ignore changes to the admin login
      administrator_login_password, // Ignore changes to the admin password
    ]
    prevent_destroy = true // Prevent data loss
  }

  tags = var.tags
}

/*
 * Creates databases, if any.
 */
resource "azurerm_mssql_managed_database" "sqlmi_server_databases" {
  for_each = var.databases

  name                = each.key
  managed_instance_id = azurerm_mssql_managed_instance.sqlmi_server.id

  short_term_retention_days = local.short_term_retention_days

  long_term_retention_policy { // based on application criticality
    weekly_retention  = local.long_term_retention.weekly_retention
    monthly_retention = local.long_term_retention.monthly_retention
    yearly_retention  = local.long_term_retention.yearly_retention
    week_of_year      = local.long_term_retention.week_of_year
  }

  lifecycle {
    prevent_destroy = true // Prevent data loss
  }

  depends_on = [
    azurerm_mssql_managed_instance.sqlmi_server
  ]
}

/*
 * Set up the vulnerability assessment for the SQL Managed Instance
 * @Ketan Patel is researching this more to see if this is the correct path.
 */
resource "azurerm_mssql_managed_instance_vulnerability_assessment" "sqlmi_server_va" {
  count                      = var.enable_vulnerability_assessment ? 1 : 0 // only run if switch is on
  managed_instance_id        = data.azurerm_user_assigned_identity.umi_sqmi_server.id
  storage_container_path     = var.vulnerability_assessment_container_path
  storage_account_access_key = null # Required to be null when using managed identity
}

/*
 * Create the SQL Managed instance Private Endpoint
 */
resource "azurerm_private_endpoint" "sqlmi_server_pep" {
  count               = var.enable_private_endpoint ? 1 : 0
  name                = local.endpoint_name
  resource_group_name = var.resource_group_name
  location            = var.location
  subnet_id           = var.application_subnet_id

  private_service_connection {
    name                           = local.service_name
    private_connection_resource_id = azurerm_mssql_managed_instance.sqlmi_server.id
    subresource_names              = ["managedInstance"]
    is_manual_connection           = false
  }

  lifecycle { // ignore zone changes to prevent unnecessary updates
    ignore_changes = [
      private_dns_zone_group
    ]
  }

  tags = var.tags
  depends_on = [
    azurerm_mssql_managed_instance.sqlmi_server
  ]
}

/*
 * Create the audit configuration to the log analytics workspace
 */
resource "azurerm_monitor_diagnostic_setting" "sqlmi_audit_logs" {
  count                      = var.enable_diagnostic_settings ? 1 : 0
  name                       = local.audit_log_name
  target_resource_id         = azurerm_mssql_managed_instance.sqlmi_server.id
  log_analytics_workspace_id = data.azurerm_log_analytics_workspace.law_sqlmi_server.id

  enabled_log {
    category = "SQLSecurityAuditEvents"
  }
}

/*
 * Set up the administrator role group for the database. The SQL MI System Managed Identity MUST have
 * permissions granted to read users from graph for this to work. These grants and conset must be done
 * outside thepipeline due to securty concerns.
 */
resource "azurerm_mssql_managed_instance_active_directory_administrator" "sqlmi_server_admin_group" {
  count               = var.do_admin_aad_group_registration ? 1 : 0 // only run id switch is on (needs IPS to consent the SMI with correct roles)
  managed_instance_id = azurerm_mssql_managed_instance.sqlmi_server.id
  login_username      = var.admin_aad_group_login_name
  object_id           = var.admin_aad_group_login_object_id
  tenant_id           = data.azurerm_client_config.current.tenant_id

  depends_on = [
    azurerm_mssql_managed_instance.sqlmi_server
  ]
}
