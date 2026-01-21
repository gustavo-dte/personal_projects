/*
 * Copyright (c) DTE Energy Corporate Services, LLC. All rights reserved.
 * Internal Use Only
 */

/*
 * Outputs for SQL Managed Instance module
 */

output "id" {
  value       = azurerm_mssql_managed_instance.sqlmi_server.id
  description = "The resource ID of the SQL Managed Instance"
}

output "name" {
  value       = local.resource_name
  description = "The name of the SQL Managed Instance"
}

output "url" {
  value       = azurerm_mssql_managed_instance.sqlmi_server.fqdn
  description = "The FQDN of the Private Endpoint to the SQL Managed Instance Server"
}
