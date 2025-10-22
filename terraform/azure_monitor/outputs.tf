output "resource_group_name" {
  description = "Name of the monitoring resource group"
  value       = module.azure_monitor.resource_group_name
}

output "log_analytics_workspace_id" {
  description = "ID of the Log Analytics workspace"
  value       = module.azure_monitor.log_analytics_workspace_id
}

output "application_insights_id" {
  description = "ID of Application Insights"
  value       = module.azure_monitor.application_insights_id
}

output "windows_dcr_id" {
  description = "ID of the Windows Data Collection Rule"
  value       = module.azure_monitor.windows_dcr_id
}

output "linux_dcr_id" {
  description = "ID of the Linux Data Collection Rule"
  value       = module.azure_monitor.linux_dcr_id
}

output "action_group_id" {
  description = "ID of the action group"
  value       = module.azure_monitor.action_group_id
}

output "monitored_windows_vms" {
  description = "Details of Windows VMs being monitored"
  value = {
    for vm_name, vm_module in module.windows_monitoring : vm_name => vm_module.monitoring_status
  }
}

output "monitored_linux_vms" {
  description = "Details of Linux VMs being monitored"
  value = {
    for vm_name, vm_module in module.linux_monitoring : vm_name => vm_module.monitoring_status
  }
}

output "windows_vm_extensions" {
  description = "Extensions installed on Windows VMs"
  value = {
    for vm_name, vm_module in module.windows_monitoring : vm_name => vm_module.extensions_installed
  }
}

output "linux_vm_extensions" {
  description = "Extensions installed on Linux VMs"
  value = {
    for vm_name, vm_module in module.linux_monitoring : vm_name => vm_module.extensions_installed
  }
}

output "windows_vm_alerts" {
  description = "Alert rules created for Windows VMs"
  value = {
    for vm_name, vm_module in module.windows_monitoring : vm_name => vm_module.metric_alert_ids
  }
}

output "linux_vm_alerts" {
  description = "Alert rules created for Linux VMs"
  value = {
    for vm_name, vm_module in module.linux_monitoring : vm_name => vm_module.metric_alert_ids
  }
}

output "monitoring_summary" {
  description = "Complete monitoring configuration summary"
  value = {
    infrastructure = {
      resource_group          = module.azure_monitor.resource_group_name
      log_analytics_workspace = module.azure_monitor.log_analytics_workspace_id
      application_insights    = module.azure_monitor.application_insights_id
      action_group            = module.azure_monitor.action_group_id
    }
    data_collection_rules = {
      windows = module.azure_monitor.windows_dcr_id
      linux   = module.azure_monitor.linux_dcr_id
    }
    monitored_vms = {
      windows = {
        count = length([for vm in var.vms_to_monitor : vm if vm.os_type == "Windows"])
        vms   = [for vm in var.vms_to_monitor : vm.name if vm.os_type == "Windows"]
      }
      linux = {
        count = length([for vm in var.vms_to_monitor : vm if vm.os_type == "Linux"])
        vms   = [for vm in var.vms_to_monitor : vm.name if vm.os_type == "Linux"]
      }
    }
    features_enabled = {
      vm_insights         = var.vm_insights_enabled
      dependency_agent    = var.dependency_agent_enabled
      azure_monitor_agent = var.ama_enabled
    }
    alerting = {
      total_alert_rules  = length(var.alert_rules)
      alert_rule_names   = [for rule in var.alert_rules : rule.name]
      notification_email = var.notification_email
    }
  }
}

output "dcr_associations" {
  description = "Data Collection Rule associations"
  value = merge(
    {
      for vm_name, vm_module in module.windows_monitoring :
      "${vm_name}-windows" => vm_module.dcr_association_name
    },
    {
      for vm_name, vm_module in module.linux_monitoring :
      "${vm_name}-linux" => vm_module.dcr_association_name
    }
  )
}

output "deployment_status" {
  description = "Overall deployment status"
  value = {
    timestamp = timestamp()
    status    = "completed"
    components = {
      azure_monitor_infrastructure = "deployed"
      windows_vm_monitoring        = length(module.windows_monitoring) > 0 ? "deployed" : "not_applicable"
      linux_vm_monitoring          = length(module.linux_monitoring) > 0 ? "deployed" : "not_applicable"
    }
    total_vms_monitored = length(var.vms_to_monitor)
    windows_vms_count   = length([for vm in var.vms_to_monitor : vm if vm.os_type == "Windows"])
    linux_vms_count     = length([for vm in var.vms_to_monitor : vm if vm.os_type == "Linux"])
  }
}

# SQL Server

output "monitored_sql_servers" {
  description = "Details of SQL servers being monitored"
  value = var.sql_monitoring_enabled ? {
    for server_name, server_module in module.sql_monitoring : server_name => server_module.monitoring_summary
  } : {}
}

output "sql_server_alerts" {
  description = "Alert rules created for SQL servers"
  value = var.sql_monitoring_enabled ? {
    for server_name, server_module in module.sql_monitoring : server_name => {
      server_alerts   = server_module.server_alert_ids
      database_alerts = server_module.database_alert_ids
    }
  } : {}
}

output "sql_monitoring_workbooks" {
  description = "SQL monitoring workbook IDs"
  value = var.sql_monitoring_enabled ? {
    for server_name, server_module in module.sql_monitoring : server_name => server_module.workbook_id
  } : {}
}

output "sql_security_features" {
  description = "SQL security features status"
  value = var.sql_monitoring_enabled ? {
    for server_name, server_module in module.sql_monitoring : server_name => {
      threat_detection         = server_module.threat_detection_enabled
      vulnerability_assessment = server_module.vulnerability_assessment_enabled
    }
  } : {}
}
