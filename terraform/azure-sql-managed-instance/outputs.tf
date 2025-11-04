# ============================================================================
# SQL MANAGED INSTANCE OUTPUTS
# ============================================================================

output "managed_instance_id" {
  description = "The ID of the SQL Managed Instance"
  value       = azurerm_mssql_managed_instance.main.id
}

output "managed_instance_name" {
  description = "The name of the SQL Managed Instance"
  value       = azurerm_mssql_managed_instance.main.name
}

output "managed_instance_fqdn" {
  description = "The fully qualified domain name"
  value       = azurerm_mssql_managed_instance.main.fqdn
}

output "managed_instance_location" {
  description = "The location of the instance"
  value       = azurerm_mssql_managed_instance.main.location
}

output "administrator_login" {
  description = "The administrator username"
  value       = azurerm_mssql_managed_instance.main.administrator_login
  sensitive   = true
}

output "administrator_password" {
  description = "The administrator password (if auto-generated)"
  value       = var.administrator_login_password == null ? random_password.sqlmi_admin[0].result : "Password provided by user"
  sensitive   = true
}

output "dns_zone_id" {
  description = "The DNS zone ID"
  value       = azurerm_mssql_managed_instance.main.dns_zone_id
}

output "identity_principal_id" {
  description = "The principal ID of the managed identity"
  value       = azurerm_mssql_managed_instance.main.identity[0].principal_id
}

output "identity_tenant_id" {
  description = "The tenant ID of the managed identity"
  value       = azurerm_mssql_managed_instance.main.identity[0].tenant_id
}

# ============================================================================
# NETWORK OUTPUTS
# ============================================================================

output "vnet_id" {
  description = "The ID of the virtual network"
  value       = azurerm_virtual_network.main.id
}

output "subnet_id" {
  description = "The ID of the SQL MI subnet"
  value       = azurerm_subnet.sqlmi.id
}

output "nsg_id" {
  description = "The ID of the network security group"
  value       = azurerm_network_security_group.sqlmi.id
}

# ============================================================================
# CONFIGURATION OUTPUTS
# ============================================================================

output "sku_name" {
  description = "The SKU name"
  value       = azurerm_mssql_managed_instance.main.sku_name
}

output "vcores" {
  description = "Number of vCores"
  value       = azurerm_mssql_managed_instance.main.vcores
}

output "storage_size_in_gb" {
  description = "Storage size in GB"
  value       = azurerm_mssql_managed_instance.main.storage_size_in_gb
}

output "license_type" {
  description = "The license type"
  value       = azurerm_mssql_managed_instance.main.license_type
}

output "zone_redundant_enabled" {
  description = "Whether zone redundancy is enabled"
  value       = azurerm_mssql_managed_instance.main.zone_redundant_enabled
}

# ============================================================================
# CONNECTION INFORMATION
# ============================================================================

output "connection_string_template" {
  description = "Connection string template"
  value       = "Server=tcp:${azurerm_mssql_managed_instance.main.fqdn},1433;Initial Catalog=<DATABASE_NAME>;Persist Security Info=False;User ID=${azurerm_mssql_managed_instance.main.administrator_login};Password=<PASSWORD>;MultipleActiveResultSets=False;Encrypt=True;TrustServerCertificate=False;Connection Timeout=30;"
  sensitive   = true
}

# ============================================================================
# DEPLOYMENT STATUS
# ============================================================================

output "deployment_notes" {
  description = "Important deployment information"
  value = <<-EOT
    SQL Managed Instance deployed successfully!
    
    IMPORTANT NOTES:
    - FQDN: ${azurerm_mssql_managed_instance.main.fqdn}
    - Initial deployment takes 4-6 hours
    - Subsequent updates take 1-2 hours
    - Access is restricted to VNet by default
    - Administrator: ${azurerm_mssql_managed_instance.main.administrator_login}
    - SKU: ${azurerm_mssql_managed_instance.main.sku_name} (${azurerm_mssql_managed_instance.main.vcores} vCores)
    - Storage: ${azurerm_mssql_managed_instance.main.storage_size_in_gb} GB
    - License: ${azurerm_mssql_managed_instance.main.license_type}
    ${azurerm_mssql_managed_instance.main.license_type == "BasePrice" ? "  ✓ Azure Hybrid Benefit enabled (55% savings!)" : "  ℹ Consider Azure Hybrid Benefit for 55% savings"}
    
    To retrieve the auto-generated password:
    terraform output -raw administrator_password
  EOT
}
