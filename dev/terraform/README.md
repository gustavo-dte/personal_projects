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
| [azurerm_recovery_services_vault.dev_vck_backup_vault](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/recovery_services_vault) | resource |
| [azurerm_resource_group.primary](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/resource_group) | resource |
| [azurerm_resource_group.primary-vck](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/resource_group) | resource |
| [azurerm_resource_group.rg-fbk](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/resource_group) | resource |
| [azurerm_resource_group.rg_captiva_scanning](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/resource_group) | resource |
| [azurerm_resource_group.secondary](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/resource_group) | resource |
| [azurerm_resource_group.secondary-vck](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/resource_group) | resource |
| [azurerm_resource_group.vm_migration_test](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/resource_group) | resource |
| [azurerm_client_config.current](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/data-sources/client_config) | data source |
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

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_application_resource_groups"></a> [application\_resource\_groups](#output\_application\_resource\_groups) | Application resource groups created for CorpApps portfolio |
<!-- END_TF_DOCS -->
