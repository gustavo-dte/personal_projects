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
  description = "The administrator login for the SQL Server"
  value       = azurerm_mssql_server.main.administrator_login
  sensitive   = true
}