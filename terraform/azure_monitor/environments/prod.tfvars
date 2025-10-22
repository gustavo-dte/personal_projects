azure_subscription_id = ""
azure_tenant_id       = ""
azure_client_id       = ""
azure_client_secret   = ""

environment                  = "Production"
resource_group_name          = "rg-prod-monitoring"
log_analytics_workspace_name = "law-prod-monitoring"
app_insights_name            = "ai-prod-monitoring"
dcr_name                     = "dcr-prod-monitoring"
action_group_name            = "ag-prod-alerts"
notification_email           = "prod-alerts@company.com"
azure_location               = "East us"

# Log Analytics
#log_analytics_workspace_name = "law-webapp-monitoring"
log_analytics_sku            = "PerGB2018"
log_analytics_retention_days = 90

# Application Insights
#app_insights_name = "ai-webapp-monitoring"
app_insights_kind = "web"

# Monitoring Features
vm_insights_enabled      = true
dependency_agent_enabled = true
ama_enabled              = true

# Data Collection
#dcr_name = "dcr-webapp-monitoring"

vms_to_monitor = [
  {
    name           = "vm-prod-web-02"
    resource_group = "rg-prod-web"
    os_type        = "Windows"
  },
  {
    name           = "vm-prod-web-01"
    resource_group = "rg-prod-web"
    os_type        = "Linux"
  }
]
