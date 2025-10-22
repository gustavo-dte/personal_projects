# Azure Authentication (use environment variables or Azure CLI)
azure_subscription_id = ""
azure_tenant_id       = ""
azure_client_id       = ""
azure_client_secret   = ""

# Environment Configuration
environment    = "Production"
project_name   = "WebApp-Monitoring"
resource_owner = "APP Team"
cost_center    = "IT-002"

# Azure Resources
resource_group_name = "rg-webapp-monitoring"
azure_location      = "East us"

# Log Analytics
log_analytics_workspace_name = "law-webapp-monitoring"
log_analytics_sku            = "PerGB2018"
log_analytics_retention_days = 90

# Application Insights
app_insights_name = "ai-webapp-monitoring"
app_insights_kind = "web"

# Monitoring Features
vm_insights_enabled      = true
dependency_agent_enabled = true
ama_enabled              = true

# Data Collection
dcr_name = "dcr-webapp-monitoring"

# Alerting
action_group_name  = "ag-webapp-alerts"
notification_email = "devops@company.com"

# VMs to Monitor
vms_to_monitor = [
  {
    name           = "vm-webapp-01"
    resource_group = "rg-webapp-vms"
    os_type        = "Windows"
  },
  {
    name           = "vm-webapp-02"
    resource_group = "rg-webapp-vms"
    os_type        = "Linux"
  }
]

# # SQL Monitoring Configuration
# sql_monitoring_enabled = true
# sql_insights_enabled   = true
# sql_threat_detection_enabled = true
# sql_vulnerability_assessment_enabled = true

# # SQL Servers to Monitor
# sql_servers_to_monitor = [
#   {
#     name                = "my-sql-server-prod"
#     id                  = "/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/rg-sql-prod/providers/Microsoft.Sql/servers/my-sql-server-prod"
#     resource_group_name = "rg-sql-prod"
#     databases = [
#       {
#         name = "database1"
#         id   = "/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/rg-sql-prod/providers/Microsoft.Sql/servers/my-sql-server-prod/databases/database1"
#       },
#       {
#         name = "database2"
#         id   = "/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/rg-sql-prod/providers/Microsoft.Sql/servers/my-sql-server-prod/databases/database2"
#       }
#     ]
#   }
# ]

# # Storage account for SQL security features (optional)
# sql_storage_account_id = "/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/rg-storage/providers/Microsoft.Storage/storageAccounts/sqlsecuritystorage"

# # Custom SQL Alert Rules (optional - will use defaults if not specified)
# sql_alert_rules = [
#   {
#     name               = "Critical CPU Usage"
#     description        = "Database CPU usage is critically high"
#     metric_name        = "cpu_percent"
#     metric_namespace   = "Microsoft.Sql/servers/databases"
#     aggregation        = "Average"
#     operator           = "GreaterThan"
#     threshold          = 95
#     severity           = 0
#     frequency          = "PT1M"
#     window_size        = "PT5M"
#     resource_type      = "database"
#   },
#   {
#     name               = "Low Storage Space"
#     description        = "Database storage space is running low"
#     metric_name        = "storage_percent"
#     metric_namespace   = "Microsoft.Sql/servers/databases"
#     aggregation        = "Average"
#     operator           = "GreaterThan"
#     threshold          = 95
#     severity           = 1
#     frequency          = "PT5M"
#     window_size        = "PT15M"
#     resource_type      = "database"
#   }
# ]
