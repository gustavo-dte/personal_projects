Error: User Assigned Identity (Subscription: "6796a2fb-2928-4ec6-96da-962d3b0001b7" Resource Group Name: "rg-cu-CorpApps-MigrationTest-Dev" Name: "umi-sqlmi-corpapps-dev") was not found
with module.test_sql_dmi.data.azurerm_user_assigned_identity.umi_sqmi_server
on .terraform/modules/test_sql_dmi/data.tf line 20, in data "azurerm_user_assigned_identity" "umi_sqmi_server":
data "azurerm_user_assigned_identity" "umi_sqmi_server" {
Error: log analytics workspaces "law-corpapps-sqlmi-dev-cu" (Resource Group "rg-cu-CorpApps-MigrationTest-Dev") was not found
with module.test_sql_dmi.data.azurerm_log_analytics_workspace.law_sqlmi_server
on .terraform/modules/test_sql_dmi/data.tf line 12, in data "azurerm_log_analytics_workspace" "law_sqlmi_server":
data "azurerm_log_analytics_workspace" "law_sqlmi_server" {