# ============================================================================
# SQL SERVER OUTPUTS
# ============================================================================

output "sql_server_id" {
  description = "The ID of the SQL Server"
  value       = azurerm_mssql_server.main.id
}

output "sql_server_name" {
  description = "The name of the SQL Server"
  value       = azurerm_mssql_server.main.name
}

output "sql_server_fqdn" {
  description = "The fully qualified domain name of the SQL Server"
  value       = azurerm_mssql_server.main.fully_qualified_domain_name
}

output "sql_server_location" {
  description = "The location of the SQL Server"
  value       = azurerm_mssql_server.main.location
}

output "administrator_login" {
  description = "The administrator login username"
  value       = azurerm_mssql_server.main.administrator_login
  sensitive   = true
}

output "administrator_password" {
  description = "The administrator password (if auto-generated)"
  value       = var.administrator_login_password == null ? random_password.sql_admin[0].result : "Password provided by user"
  sensitive   = true
}

# ============================================================================
# DATABASE OUTPUTS
# ============================================================================

output "database_ids" {
  description = "Map of database names to their IDs"
  value = {
    for k, db in azurerm_mssql_database.main : k => db.id
  }
}

output "database_names" {
  description = "List of database names"
  value       = [for db in azurerm_mssql_database.main : db.name]
}

output "database_details" {
  description = "Detailed information about each database"
  value = {
    for k, db in azurerm_mssql_database.main : k => {
      id             = db.id
      name           = db.name
      sku_name       = db.sku_name
      max_size_gb    = db.max_size_gb
      zone_redundant = db.zone_redundant
    }
  }
}

# ============================================================================
# MONITORING OUTPUTS
# ============================================================================

output "log_analytics_workspace_id" {
  description = "The ID of the Log Analytics workspace (if enabled)"
  value       = var.enable_monitoring ? azurerm_log_analytics_workspace.main[0].id : null
}

output "storage_account_id" {
  description = "The ID of the audit storage account (if enabled)"
  value       = var.enable_auditing ? azurerm_storage_account.audit[0].id : null
}

# ============================================================================
# CONNECTION STRING TEMPLATE
# ============================================================================

output "connection_string_template" {
  description = "Connection string template for applications"
  value       = "Server=tcp:${azurerm_mssql_server.main.fully_qualified_domain_name},1433;Initial Catalog=<DATABASE_NAME>;Persist Security Info=False;User ID=${azurerm_mssql_server.main.administrator_login};Password=<PASSWORD>;MultipleActiveResultSets=False;Encrypt=True;TrustServerCertificate=False;Connection Timeout=30;"
  sensitive   = true
}

output "connection_strings" {
  description = "Connection strings for each database"
  value = {
    for k, db in azurerm_mssql_database.main : k => "Server=tcp:${azurerm_mssql_server.main.fully_qualified_domain_name},1433;Initial Catalog=${db.name};Persist Security Info=False;User ID=${azurerm_mssql_server.main.administrator_login};Password=<PASSWORD>;MultipleActiveResultSets=False;Encrypt=True;TrustServerCertificate=False;Connection Timeout=30;"
  }
  sensitive = true
}
