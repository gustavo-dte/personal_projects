output "database_id" {
  description = "The ID of the SQL Database"
  value       = azurerm_mssql_database.main.id
}

output "database_name" {
  description = "The name of the SQL Database"
  value       = azurerm_mssql_database.main.name
}

output "database_server_id" {
  description = "The server ID of the SQL Database"
  value       = azurerm_mssql_database.main.server_id
}

output "database_collation" {
  description = "The collation of the SQL Database"
  value       = azurerm_mssql_database.main.collation
}

output "database_max_size_gb" {
  description = "The maximum size of the SQL Database in GB"
  value       = azurerm_mssql_database.main.max_size_gb
}