# Outputs for imported Windows VM module

# VM Outputs
output "vm_id" {
  description = "Virtual machine id created."
  value       = local.vm_os_type == "windows" ? azurerm_windows_virtual_machine.main[0].id : azurerm_linux_virtual_machine.main[0].id
}

output "vm_name" {
  description = "The name of the virtual machine."
  value       = local.vm_os_type == "windows" ? azurerm_windows_virtual_machine.main[0].name : azurerm_linux_virtual_machine.main[0].name
}

output "vm_location" {
  description = "location of Virtual machine created."
  value       = local.vm_os_type == "windows" ? azurerm_windows_virtual_machine.main[0].location : azurerm_linux_virtual_machine.main[0].location
}

output "vm_size" {
  description = "Size of the virtual machine"
  value       = local.vm_os_type == "windows" ? azurerm_windows_virtual_machine.main[0].size : azurerm_linux_virtual_machine.main[0].size
}

output "availability_zone" {
  description = "The availability zone where the virtual machine is deployed."
  value       = local.vm_os_type == "windows" ? azurerm_windows_virtual_machine.main[0].zone : azurerm_linux_virtual_machine.main[0].zone
}

output "private_ip_address" {
  description = "Private IP address of the virtual machine"
  value       = azurerm_network_interface.main.ip_configuration[0].private_ip_address
}


# Network Interface Outputs
output "network_interface_id" {
  description = "ID of the network interface"
  value       = azurerm_network_interface.main.id
}

output "nic_name" {
  description = "Name of the network interface"
  value       = azurerm_network_interface.main.name
}

output "nic_private_ip_address" {
  description = "Private IP address of the network interface"
  value       = azurerm_network_interface.main.ip_configuration[0].private_ip_address
}

output "nic_mac_address" {
  description = "MAC address of the network interface"
  value       = azurerm_network_interface.main.mac_address
}

# OS Disk Output (attached by ID)
output "os_managed_disk_id" {
  description = "ID of the attached OS managed disk"
  value       = local.vm_os_type == "windows" ? azurerm_windows_virtual_machine.main[0].os_managed_disk_id : azurerm_linux_virtual_machine.main[0].os_managed_disk_id
}

# Data Disk Outputs
output "data_disk_ids" {
  description = "Map of data disk names to their IDs"
  value       = { for k, v in azurerm_managed_disk.data_disk : k => v.id }
}

output "data_disk_names" {
  description = "Map of data disk names to their names"
  value       = { for k, v in azurerm_managed_disk.data_disk : k => v.name }
}

output "data_disk_sizes_gb" {
  description = "Map of data disk names to their sizes in GB"
  value       = { for k, v in azurerm_managed_disk.data_disk : k => v.disk_size_gb }
}

# Identity Outputs
output "user_assigned_identity_id" {
  description = "ID of the user assigned identity"
  value       = var.user_assigned_identity_resource_id != null ? azurerm_user_assigned_identity.identity[0].id : null
}

output "user_assigned_identity_name" {
  description = "Name of the user assigned identity"
  value       = var.user_assigned_identity_resource_id != null ? azurerm_user_assigned_identity.identity[0].name : null
}

# VM Extension Outputs
output "vm_extension_id" {
  description = "ID of the VM extension"
  value       = var.vm_extension_name != null ? azurerm_virtual_machine_extension.main[0].id : null
}

output "vm_extension_name" {
  description = "Name of the VM extension"
  value       = var.vm_extension_name != null ? azurerm_virtual_machine_extension.main[0].name : null
}

# Resource Group and Location
output "resource_group_name" {
  description = "Name of the resource group"
  value       = var.resource_group_name
}

output "location" {
  description = "Azure region where resources are located"
  value       = var.location
}

# Tags
output "tags" {
  description = "Tags applied to resources"
  value       = var.tags
}

# Optional VMSS Outputs
output "vmss_id" {
  description = "ID of the VM Scale Set when enabled"
  value       = var.enable_vmss ? azurerm_windows_virtual_machine_scale_set.vmss[0].id : null
}

output "vmss_name" {
  description = "Name of the VM Scale Set when enabled"
  value       = var.enable_vmss ? azurerm_windows_virtual_machine_scale_set.vmss[0].name : null
}
