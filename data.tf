data "azurerm_client_config" "current" {}
// tflint-ignore: terraform_unused_declarations
data "azurerm_subscription" "current" {}

/*
 * Look-up the log analytics workspace
 */
data "azurerm_log_analytics_workspace" "law_sqlmi_server" {
  name                = var.log_analytics_workspace_name
  resource_group_name = local.log_analytics_workspace_resource_group_name
}

/*
 * Look-up the UMI to use for the SQL MI
 */
data "azurerm_user_assigned_identity" "umi_sqmi_server" {
  name                = var.user_managed_identity_name
  resource_group_name = local.umi_resource_group_name
}
