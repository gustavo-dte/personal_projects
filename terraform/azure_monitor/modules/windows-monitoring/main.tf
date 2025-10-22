# Azure Monitor Agent Extension
resource "azurerm_virtual_machine_extension" "ama_windows" {
  count                      = var.ama_enabled ? 1 : 0
  name                       = "AzureMonitorWindowsAgent"
  virtual_machine_id         = var.vm_id
  publisher                  = "Microsoft.Azure.Monitor"
  type                       = "AzureMonitorWindowsAgent"
  type_handler_version       = "1.0"
  auto_upgrade_minor_version = true
}

# Dependency Agent Extension
resource "azurerm_virtual_machine_extension" "dependency_agent_windows" {
  count                      = var.dependency_agent_enabled ? 1 : 0
  name                       = "DependencyAgentWindows"
  virtual_machine_id         = var.vm_id
  publisher                  = "Microsoft.Azure.Monitoring.DependencyAgent"
  type                       = "DependencyAgentWindows"
  type_handler_version       = "9.10"
  auto_upgrade_minor_version = true

  depends_on = [azurerm_virtual_machine_extension.ama_windows]
}

# Data Collection Rule Association
resource "azurerm_monitor_data_collection_rule_association" "windows" {
  name                    = "dcra-${var.vm_name}-windows"
  target_resource_id      = var.vm_id
  data_collection_rule_id = var.windows_dcr_id

  depends_on = [azurerm_virtual_machine_extension.ama_windows]
}

# Metric Alert Rules
resource "azurerm_monitor_metric_alert" "vm_alerts" {
  for_each = {
    for alert in var.alert_rules : alert.name => alert
  }

  name                = "alert-${var.vm_name}-${lower(replace(each.value.name, " ", "-"))}"
  resource_group_name = var.resource_group_name
  scopes              = [var.vm_id]
  description         = "${each.value.description} for ${var.vm_name}"
  severity            = each.value.severity
  frequency           = each.value.frequency
  window_size         = each.value.window_size

  criteria {
    metric_namespace       = each.value.metric_namespace
    metric_name            = each.value.metric_name
    aggregation            = each.value.time_aggregation
    operator               = each.value.operator
    threshold              = each.value.threshold
    skip_metric_validation = each.value.metric_namespace == "InsightsMetrics"

    dynamic "dimension" {
      for_each = each.value.dimensions
      content {
        name     = dimension.value.name
        operator = dimension.value.operator
        values   = dimension.value.values
      }
    }
  }

  action {
    action_group_id = var.action_group_id
  }
}

# Get existing VM data
data "azurerm_virtual_machine" "existing" {
  name                = var.vm_name
  resource_group_name = var.vm_resource_group
}
