output "managed_instance_id" {
  description = "The ID of the SQL Managed Instance"
  value       = azurerm_mssql_managed_instance.main.id
}

output "managed_instance_name" {
  description = "The name of the SQL Managed Instance"
  value       = azurerm_mssql_managed_instance.main.name
}

output "managed_instance_fqdn" {
  description = "The fully qualified domain name of the SQL Managed Instance"
  value       = azurerm_mssql_managed_instance.main.fqdn
}

output "managed_instance_location" {
  description = "The location of the SQL Managed Instance"
  value       = azurerm_mssql_managed_instance.main.location
}

output "administrator_login" {
  description = "The administrator login for the SQL Managed Instance"
  value       = azurerm_mssql_managed_instance.main.administrator_login
  sensitive   = true
}

output "dns_zone_id" {
  description = "The DNS zone ID of the SQL Managed Instance"
  value       = azurerm_mssql_managed_instance.main.dns_zone_id
}

output "identity" {
  description = "The managed identity configuration of the SQL Managed Instance"
  value = {
    type         = azurerm_mssql_managed_instance.main.identity[0].type
    principal_id = try(azurerm_mssql_managed_instance.main.identity[0].principal_id, null)
    tenant_id    = try(azurerm_mssql_managed_instance.main.identity[0].tenant_id, null)
  }
}

output "failover_group_id" {
  description = "The ID of the failover group (if configured)"
  value       = try(azurerm_mssql_managed_instance_failover_group.main[0].id, null)
}

output "public_endpoint_enabled" {
  description = "Whether the public data endpoint is enabled"
  value       = azurerm_mssql_managed_instance.main.public_data_endpoint_enabled
}

output "subnet_id" {
  description = "The subnet ID of the SQL Managed Instance"
  value       = azurerm_mssql_managed_instance.main.subnet_id
}

output "vcores" {
  description = "Number of vCores for the managed instance"
  value       = azurerm_mssql_managed_instance.main.vcores
}

output "storage_size_in_gb" {
  description = "Storage size in GB for the managed instance"
  value       = azurerm_mssql_managed_instance.main.storage_size_in_gb
}

output "sku_name" {
  description = "The SKU name of the SQL Managed Instance"
  value       = azurerm_mssql_managed_instance.main.sku_name
}

output "license_type" {
  description = "The license type of the SQL Managed Instance"
  value       = azurerm_mssql_managed_instance.main.license_type
}
