output "resource_group_name" {
  description = "Name of the resource group"
  value       = azurerm_resource_group.monitoring.name
}

output "log_analytics_workspace_id" {
  description = "ID of the Log Analytics workspace"
  value       = azurerm_log_analytics_workspace.main.id
}

output "log_analytics_workspace_key" {
  description = "Primary shared key of the Log Analytics workspace"
  value       = azurerm_log_analytics_workspace.main.primary_shared_key
  sensitive   = true
}

output "application_insights_id" {
  description = "ID of Application Insights"
  value       = azurerm_application_insights.main.id
}

output "windows_dcr_id" {
  description = "ID of the Windows Data Collection Rule"
  value       = azurerm_monitor_data_collection_rule.windows.id
}

output "linux_dcr_id" {
  description = "ID of the Linux Data Collection Rule"
  value       = azurerm_monitor_data_collection_rule.linux.id
}

output "action_group_id" {
  description = "ID of the action group"
  value       = azurerm_monitor_action_group.main.id
}
