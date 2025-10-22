# Data source to get existing VMs
data "azurerm_virtual_machine" "vms" {
  for_each            = { for vm in var.vms_to_monitor : vm.name => vm }
  name                = each.value.name
  resource_group_name = each.value.resource_group
}

# Azure Monitor Infrastructure Module
module "azure_monitor" {
  source = "./modules/azure-monitor"

  # Resource Configuration
  resource_group_name          = var.resource_group_name
  location                     = var.azure_location
  log_analytics_workspace_name = var.log_analytics_workspace_name
  log_analytics_sku            = var.log_analytics_sku
  log_analytics_retention_days = var.log_analytics_retention_days
  app_insights_name            = var.app_insights_name
  app_insights_kind            = var.app_insights_kind
  dcr_name                     = var.dcr_name
  action_group_name            = var.action_group_name
  notification_email           = var.notification_email

  # Performance Counters
  windows_performance_counters = var.windows_performance_counters
  linux_performance_counters   = var.linux_performance_counters

  # Event Logs and Syslog
  windows_event_logs = var.windows_event_logs
  syslog_facilities  = var.syslog_facilities

  # Alert Rules
  alert_rules = var.alert_rules
}

# Windows VM Monitoring
module "windows_monitoring" {
  source = "./modules/windows-monitoring"

  for_each = {
    for vm in var.vms_to_monitor : vm.name => vm
    if vm.os_type == "Windows"
  }

  vm_name             = each.value.name
  vm_resource_group   = each.value.resource_group
  vm_id               = data.azurerm_virtual_machine.vms[each.key].id
  resource_group_name = var.resource_group_name

  # Dependencies from Azure Monitor module
  windows_dcr_id  = module.azure_monitor.windows_dcr_id
  action_group_id = module.azure_monitor.action_group_id

  # Configuration
  ama_enabled              = var.ama_enabled
  dependency_agent_enabled = var.dependency_agent_enabled
  vm_insights_enabled      = var.vm_insights_enabled
  alert_rules              = var.windows_alert_rules

  depends_on = [module.azure_monitor]
}

# Linux VM Monitoring
module "linux_monitoring" {
  source = "./modules/linux-monitoring"

  for_each = {
    for vm in var.vms_to_monitor : vm.name => vm
    if vm.os_type == "Linux"
  }

  vm_name             = each.value.name
  vm_resource_group   = each.value.resource_group
  vm_id               = data.azurerm_virtual_machine.vms[each.key].id
  resource_group_name = var.resource_group_name

  # Dependencies from Azure Monitor module
  linux_dcr_id    = module.azure_monitor.linux_dcr_id
  action_group_id = module.azure_monitor.action_group_id

  # Configuration
  ama_enabled              = var.ama_enabled
  dependency_agent_enabled = var.dependency_agent_enabled
  vm_insights_enabled      = var.vm_insights_enabled
  alert_rules              = var.linux_alert_rules

  depends_on = [module.azure_monitor]
}

# SQL Monitoring Module
module "sql_monitoring" {
  for_each = var.sql_monitoring_enabled ? { for server in var.sql_servers_to_monitor : server.name => server } : {}

  source = "./modules/azure-sql-monitoring"

  sql_server_id              = each.value.id
  sql_server_name            = each.value.name
  sql_databases              = each.value.databases
  resource_group_name        = each.value.resource_group_name
  log_analytics_workspace_id = module.azure_monitor.log_analytics_workspace_id
  action_group_id            = module.azure_monitor.action_group_id

  # SQL-specific settings
  sql_alert_rules                      = var.sql_alert_rules
  sql_insights_enabled                 = var.sql_insights_enabled
  sql_threat_detection_enabled         = var.sql_threat_detection_enabled
  sql_vulnerability_assessment_enabled = var.sql_vulnerability_assessment_enabled
  storage_account_id                   = var.sql_storage_account_id

  # Common settings
  diagnostic_settings_enabled  = var.diagnostic_settings_enabled
  log_analytics_retention_days = var.log_analytics_retention_days
}
