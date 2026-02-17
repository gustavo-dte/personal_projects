<!-- BEGIN_TF_DOCS -->
# Terraform Module for Cloud Platform Feature

This respository contains Terraform configuration for deploying resources into a subscription.

## Usage

```hcl
// tflint-ignore-file: terraform_required_version
// Show the world how to deploy resources into subscription
```

## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >=1.8.5 |
| <a name="requirement_azurerm"></a> [azurerm](#requirement\_azurerm) | ~>4.0 |
| <a name="requirement_github"></a> [github](#requirement\_github) | 6.4.0 |
| <a name="requirement_infoblox"></a> [infoblox](#requirement\_infoblox) | 2.6.0 |

## Resources

| Name | Type |
|------|------|
| [azurerm_backup_policy_vm.backup_policy](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/backup_policy_vm) | resource |
| [azurerm_backup_policy_vm.migration_test_backup_policy](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/backup_policy_vm) | resource |
| [azurerm_log_analytics_workspace.vm_law_cu](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/log_analytics_workspace) | resource |
| [azurerm_recovery_services_vault.dev_migration_test_backup_vault](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/recovery_services_vault) | resource |
| [azurerm_recovery_services_vault.dev_vck_backup_vault](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/recovery_services_vault) | resource |
| [azurerm_resource_group.primary](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/resource_group) | resource |
| [azurerm_resource_group.primary-vck](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/resource_group) | resource |
| [azurerm_resource_group.primary_law_cu_rg](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/resource_group) | resource |
| [azurerm_resource_group.rg-fbk](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/resource_group) | resource |
| [azurerm_resource_group.rg_captiva_scanning](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/resource_group) | resource |
| [azurerm_resource_group.secondary](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/resource_group) | resource |
| [azurerm_resource_group.secondary-vck](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/resource_group) | resource |
| [azurerm_resource_group.vm_migration_test](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/resource_group) | resource |
| [azurerm_role_assignment.primary_mi_contributor](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/role_assignment) | resource |
| [azurerm_user_assigned_identity.primary](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/user_assigned_identity) | resource |
| [azurerm_user_assigned_identity.sqlmi_umi](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/user_assigned_identity) | resource |
| [azurerm_client_config.current](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/data-sources/client_config) | data source |
| [azurerm_shared_image_version.windows](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/data-sources/shared_image_version) | data source |
| [azurerm_subscription.current](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/data-sources/subscription) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_application"></a> [application](#input\_application) | Application name | `string` | n/a | yes |
| <a name="input_environment"></a> [environment](#input\_environment) | Environment | `string` | n/a | yes |
| <a name="input_github_organization"></a> [github\_organization](#input\_github\_organization) | GitHub organization | `string` | n/a | yes |
| <a name="input_github_token"></a> [github\_token](#input\_github\_token) | GitHub token for authentication | `string` | n/a | yes |
| <a name="input_infoblox_password"></a> [infoblox\_password](#input\_infoblox\_password) | Infoblox password | `string` | n/a | yes |
| <a name="input_infoblox_server"></a> [infoblox\_server](#input\_infoblox\_server) | Infoblox server hostname | `string` | n/a | yes |
| <a name="input_infoblox_username"></a> [infoblox\_username](#input\_infoblox\_username) | Infoblox username | `string` | n/a | yes |
| <a name="input_primary_network_container_cidr"></a> [primary\_network\_container\_cidr](#input\_primary\_network\_container\_cidr) | Primary network container CIDR | `string` | n/a | yes |
| <a name="input_primary_region"></a> [primary\_region](#input\_primary\_region) | Primary Azure location or region | `string` | n/a | yes |
| <a name="input_secondary_network_container_cidr"></a> [secondary\_network\_container\_cidr](#input\_secondary\_network\_container\_cidr) | Secondary network container CIDR | `string` | n/a | yes |
| <a name="input_secondary_region"></a> [secondary\_region](#input\_secondary\_region) | Secondary Azure location or region | `string` | n/a | yes |
| <a name="input_sqldb_password"></a> [sqldb\_password](#input\_sqldb\_password) | SQL Database Password | `string` | n/a | yes |
| <a name="input_sqlmi_password"></a> [sqlmi\_password](#input\_sqlmi\_password) | SQL Managed Instance password for the 'sqladminuser' account | `string` | n/a | yes |
| <a name="input_vm_password"></a> [vm\_password](#input\_vm\_password) | password to connect to vm for vmware migration testing | `string` | n/a | yes |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_application_resource_groups"></a> [application\_resource\_groups](#output\_application\_resource\_groups) | Application resource groups created for CorpApps portfolio |
<!-- END_TF_DOCS -->
