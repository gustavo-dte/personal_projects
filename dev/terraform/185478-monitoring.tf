# ------------------------------------------------------
# Test Script Azure Monitoring
# ------------------------------------------------------

module "monitor" {
  source  = "app.terraform.io/DTE-Cloud-Platform/azure-monitor/azurerm"
  version = "0.0.1-alpha.2"

  # ------------------------------------------------------
  # Test values (tfvars-style) for module inputs
  # ------------------------------------------------------

  resource_group_name = azurerm_resource_group.vm_migration_test.name
  location            = "centralus"

  log_analytics_workspace_name = "lawvmcuwinwebd01"
  log_analytics_sku            = "PerGB2018"
  log_analytics_retention_days = 30

  app_insights_name = "aivmcuwinwebd01"
  app_insights_kind = "web"

  dcr_name           = "dcrvmcuwinwebd01"
  action_group_name  = "agvmcuwinwebd01"
  notification_email = "vmcuwinwebd01@example.com"

  windows_performance_counters = [
    {
      counter_name = "\\Processor(_Total)\\% Processor Time"
      sample_rate  = 60
    },
    {
      counter_name = "\\Memory\\% Committed Bytes In Use"
      sample_rate  = 60
    }
  ]

  vm_name           = "vmcuwinwebd01"
  vm_resource_group = "rg-cu-CorpApps-MigrationTest-Dev"
  vm_id             = "/subscriptions/6796a2fb-2928-4ec6-96da-962d3b0001b7/resourceGroups/rg-cu-CorpApps-MigrationTest-Dev/providers/Microsoft.Compute/virtualMachines/vmcuwinwebd01"

  # Monitoring agents
  ama_enabled              = true
  dependency_agent_enabled = true
  vm_insights_enabled      = true

  # VM alert rules (unchanged)
  vm_alert_rules = [
    {
      name             = "CPU Usage Alert"
      description      = "Alert when CPU usage exceeds 80%"
      metric_namespace = "Microsoft.Compute/virtualMachines"
      metric_name      = "Percentage CPU"
      dimensions       = []
      threshold        = 80
      operator         = "GreaterThan"
      time_aggregation = "Average"
      frequency        = "PT1M"
      window_size      = "PT5M"
      severity         = 2
    },
    {
      name             = "Memory Usage Alert"
      description      = "Alert when memory usage exceeds 90%"
      metric_namespace = "Microsoft.Compute/virtualMachines"
      metric_name      = "Available Memory Bytes"
      dimensions       = []
      threshold        = 90
      operator         = "LessThan"
      time_aggregation = "Average"
      frequency        = "PT1M"
      window_size      = "PT5M"
      severity         = 2
    }
  ]

  # Pass mandatory tags
  tags = local.tags
}
