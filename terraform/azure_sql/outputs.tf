# SQL Server Outputs
output "sql_server_id" {
  description = "The ID of the SQL Server"
  value       = module.sql_server.sql_server_id
}

output "sql_server_name" {
  description = "The name of the SQL Server"
  value       = module.sql_server.sql_server_name
}

output "sql_server_fqdn" {
  description = "The fully qualified domain name of the SQL Server"
  value       = module.sql_server.sql_server_fqdn
}

output "sql_server_location" {
  description = "The location of the SQL Server"
  value       = module.sql_server.sql_server_location
}

output "administrator_login" {
  description = "The administrator login for the SQL Server"
  value       = module.sql_server.administrator_login
  sensitive   = true
}

# SQL Database Outputs
output "database_ids" {
  description = "The IDs of the SQL Databases"
  value       = [for db in module.sql_databases : db.database_id]
}

output "database_names" {
  description = "The names of the SQL Databases"
  value       = [for db in module.sql_databases : db.database_name]
}

# Generated Password Output (if applicable)
output "generated_admin_password" {
  description = "The generated administrator password (if applicable)"
  value       = var.administrator_login_password == null ? random_password.sql_admin_password[0].result : null
  sensitive   = true
}

# Connection String Template
output "connection_string_template" {
  description = "Template for connection string"
  value       = "Server=tcp:${module.sql_server.sql_server_fqdn},1433;Initial Catalog=<DATABASE_NAME>;Persist Security Info=False;User ID=${module.sql_server.administrator_login};Password=<PASSWORD>;MultipleActiveResultSets=False;Encrypt=True;TrustServerCertificate=False;Connection Timeout=30;"
  sensitive   = true
}