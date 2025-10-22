output "vm_name" {
  description = "Name of the monitored Windows VM"
  value       = var.vm_name
}

output "vm_id" {
  description = "ID of the monitored Windows VM"
  value       = var.vm_id
}

output "vm_resource_group" {
  description = "Resource group of the monitored Windows VM"
  value       = var.vm_resource_group
}

output "azure_monitor_agent_extension_id" {
  description = "ID of the Azure Monitor Agent extension"
  value       = var.ama_enabled ? azurerm_virtual_machine_extension.ama_windows[0].id : null
}

output "dependency_agent_extension_id" {
  description = "ID of the Dependency Agent extension"
  value       = var.dependency_agent_enabled ? azurerm_virtual_machine_extension.dependency_agent_windows[0].id : null
}

output "data_collection_rule_association_id" {
  description = "ID of the Data Collection Rule association"
  value       = azurerm_monitor_data_collection_rule_association.windows.id
}

output "metric_alert_ids" {
  description = "IDs of the created metric alerts"
  value = {
    for alert_name, alert in azurerm_monitor_metric_alert.vm_alerts : alert_name => alert.id
  }
}

output "monitoring_status" {
  description = "Monitoring configuration status"
  value = {
    vm_name             = var.vm_name
    os_type             = "Windows"
    azure_monitor_agent = var.ama_enabled
    dependency_agent    = var.dependency_agent_enabled
    vm_insights         = var.vm_insights_enabled
    dcr_associated      = true
    alerts_configured   = length(var.alert_rules)
    monitoring_enabled  = true
  }
}

output "extensions_installed" {
  description = "List of installed monitoring extensions"
  value = compact([
    var.ama_enabled ? "AzureMonitorWindowsAgent" : null,
    var.dependency_agent_enabled ? "DependencyAgentWindows" : null
  ])
}

output "alert_rules_created" {
  description = "List of alert rules created for this VM"
  value = [
    for alert in var.alert_rules : {
      name        = alert.name
      description = alert.description
      metric_name = alert.metric_name
      threshold   = alert.threshold
      severity    = alert.severity
    }
  ]
}

output "dcr_association_name" {
  description = "Name of the Data Collection Rule association"
  value       = azurerm_monitor_data_collection_rule_association.windows.name
}

output "monitoring_configuration_summary" {
  description = "Summary of monitoring configuration"
  value = {
    vm_details = {
      name           = var.vm_name
      resource_group = var.vm_resource_group
      id             = var.vm_id
    }
    agents = {
      azure_monitor_agent = {
        enabled      = var.ama_enabled
        extension_id = var.ama_enabled ? azurerm_virtual_machine_extension.ama_windows[0].id : null
      }
      dependency_agent = {
        enabled      = var.dependency_agent_enabled
        extension_id = var.dependency_agent_enabled ? azurerm_virtual_machine_extension.dependency_agent_windows[0].id : null
      }
    }
    data_collection = {
      rule_id        = var.windows_dcr_id
      association_id = azurerm_monitor_data_collection_rule_association.windows.id
    }
    alerting = {
      action_group_id = var.action_group_id
      alert_count     = length(var.alert_rules)
      alert_names     = [for alert in var.alert_rules : alert.name]
    }
    features = {
      vm_insights_enabled = var.vm_insights_enabled
    }
  }
}
