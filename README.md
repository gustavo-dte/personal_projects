# terraform-azurerm-mssqlmi

A module for creating Microsoft SQL Managed Instances. This module creates secure, reliable, and appropriately SQL Managed instance based on the deployment environment and
application criticality.

This module does support zone redundancy, but do to the nature of how failover groups work, both a primary and alternate SQL MI must exists. You must create a failover
group using [azurerm_mssql_managed_instance_failover_group](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/mssql_managed_instance_failover_group) outside this module to provide full region redundancy for a SQL managed instance.

To use this module, the cloud enginer must consider of the following:

## Environment

Depending on the [environment](#input\_environment), certain aspects of the SQL Managed configuration will change.

1. Regarless of the variable [application\_criticality](#input\_application\_criticality), if the [environment](#input\_environment) is 'Sandbox', 'Development', or 'Dev', the criticality will be lowered to 'Tier4'. This
    restricts the short-term and long-term retention values of databases in development to lower, more cost effective values.
2. When [environment](#input\_environment) is 'Sandbox', 'Development', or 'Dev', then:
    * [sku\_name](#input\_sku\_name) is restricted 'GP_Gen5'
    * [vcores](#input\_vcores) is restricted 4 or 8
    * [storage\_size\_in\_gb](#input\_storage\_size\_in\_gb) is restricted to a rage of 32GB - 128GB, in increments of 32GB.

## Application Criticality

This module will configure short-term and long-term retention, allowable SKU, virtual cores, and storage size based on criticality tiers. The allowable tiers are 'Tier1', 'Tier2', 'Tier3',
and 'Tier4'. Depending on the [application\_criticality](#input\_application\_criticality), certain aspects of the SQL Managed configuration will change.

### Tier1

1. Short-term retention is configured for 35 days
2. Long term retention is configures for:
    * weekly_retention 'P12W', or 12 weeks.
    * monthly_retention 'P12M', or 12 months.
    * yearly_retention 'P7Y', or 7 years.
    * week_of_year is 1
3. Allowable SKU are restricted to Business Critical (BC):
    * BC_Gen5
    * BC_PremiumSeries
    * BC_PremiumSeriesMemoryOptimized
4. Core counts are restricted for each SKU:
    * BC_Gen5 to 4, 8, 16, 24, 32, 40, 64 and 80.
    * BC_PremiumSeries to 4, 8, 16, 24, 32, 40, 64, 80, 96, and 128.
    * BC_PremiumSeriesMemoryOptimized to 4, 8, 16, 24, 32, 40, 64, 80, 96, and 128.
5. Storage Size is restricted for each SKU:
    * BC_Gen5 to between 32GB and 4096GB in increments of 32GB.
    * BC_PremiumSeries to between 32GB and 5632GB in increments of 32GB.
    * BC_PremiumSeriesMemoryOptimized to between 32GB and 16384GB in increments of 32GB.
6. Zone redundancy is set to true.

### Tier2

1. Short-term retention is configured for 14 days
2. Long term retention is configures for:
    * weekly_retention 'P8W', or 8 weeks.
    * monthly_retention 'P6M', or 6 months.
    * yearly_retention 'P5Y', or 5 years.
    * week_of_year is 1
3. Allowable SKU are restricted to Business Critical (BC):
    * BC_Gen5
    * BC_PremiumSeries
4. Core counts are restricted for each SKU:
    * BC_Gen5 to 4, 8, 16, 24, 32, 40, 64 and 80.
    * BC_PremiumSeries to 4, 8, 16, 24, 32, 40, 64, 80, 96, and 128.
5. Storage Size is restricted for each SKU:
    * BC_Gen5 to between 32GB and 4096GB in increments of 32GB.
    * BC_PremiumSeries to between 32GB and 5632GB in increments of 32GB.
6. Zone redundancy is set to true.

### Tier3

1. Short-term retention is configured for 7 days
2. Long term retention is configures for:
    * weekly_retention 'P4W', or 4 weeks.
    * monthly_retention 'P2M', or 2 months.
    * yearly_retention 'P1Y', or 1 years.
    * week_of_year is 1
3. Allowable SKU are restricted to Business Critical (BC):
    * GP_Gen5
4. Core counts are restricted for each SKU:
    * 4, 8, 16, 24, 32, 40, 64 and 80.
5. Storage Size is restricted for each SKU:
    * Between 32GB and 4096GB in increments of 32GB.
6. Zone redundancy is set to false.

### Tier4

  1. Short-term retention is configured for 5 days
  2. Long term retention is configures for:
     * weekly_retention 'P1W', or 1 weeks.
     * monthly_retention 'P1M', or 1 months.
     * yearly_retention is null
     * week_of_year is null
  3. Allowable SKU are restricted to Business Critical (BC):
     * GP_Gen5
  4. Core counts are restricted for each SKU:
     * 4, 8, 16, 24, 32, 40, 64 and 80.
  5. Storage Size is restricted for each SKU:
     * Between 32GB and 4096GB in increments of 32GB.
  6. Zone redundancy is set to false.

  See above, its important to note that these values will be changed depending on the [environment](#input\_environment).

## Prerequisits

To use this module, the following must be pre-configured in order for it to deploy successfully:

### Delegated Subnet

To use SQL Managed Instances a subnet that complies with [Configure an existing virtual network for Azure SQL Managed Instance](https://learn.microsoft.com/en-us/azure/azure-sql/managed-instance/vnet-existing-add-subnet?view=azuresql) and delagated to 'Microsoft.Sql/managedInstances' is required. This subnet must also include a compatable
NSG and route table. The subnet can ONLY be used for SQL Managed Instances and should be sized accordingly. When using private endpoint, be sure to set [application\_subnet\_id](#input\_application\_subnet\_id)
to a subnet that isn't used for the SQL Managed Instance, preferable the applications subnet.

### User Managed Identity

This module uses a UMI for two scenarios:

1. **AAD (Entra) Admin Group Authorization**: When performing AAD (Entra) Admin Group Authorization, the UMI must be granted the following permissions on its service principle:
    * User.Read.All
    * GroupMember.Read.All

    This action can only be done by IPS and must be completed before applying this module or [do\_admin\_aad\_group\_registration](#input\_do\_admin\_aad\_group\_registration) is false. Once
    IPS completes these grants and consetnts, set [do\_admin\_aad\_group\_registration](#input\_do\_admin\_aad\_group\_registration) to true.
2. **Vulnerability Assessments**: This module will only use a UMI for vulnerability sssessments if [enable\_vulnerability\_assessment](#input\_enable\_vulnerability\_assessment) is set to true. If enabled, the UMI specified must has
'Storage Blob Data Contributor' (ba92f5b4-2d11-453d-a403-e96b0029c9fe) access to the storage account specified by [vulnerability\_assessment\_container\_path](#input\_vulnerability\_assessment\_container\_path).

### Log Analytics Workspace

This module sends security and application logs to a log analytics workspace. This workspace must exist and be accessable. See [log\_analytics\_workspace\_name](#input\_log\_analytics\_workspace\_name) and
[log\_analytics\_workspace\_resource\_group\_name](#input\_log\_analytics\_workspace\_resource\_group\_name) for more information.

### Storage Account

When performing vulnerability assessments you must have a storage account available. see above User Managed Identity, and [vulnerability\_assessment\_container\_path](#input\_vulnerability\_assessment\_container\_path)
for more information.

## Potential Pitfalls

SQL Managed Instances will create resources to managing network access to your VNET. Any policies in place, including tagging, that attempt to limit or control how resources are
created may impact how a SQL Managed Instace works durint deployment or runtime. Most deployment failures are caused by improper configuration of the subnet or policies. For more information
on SQL Managed Instances, please see [Azure SQL Managed Instance documentation](https://learn.microsoft.com/en-us/azure/azure-sql/managed-instance/?view=azuresql).

## Contributing

To contribute to this project, you'll need to install several development tools and configure your environment. Please see our **[Contributing Guide](docs/CONTRIBUTING.md)** for:

* Required software installation (pre-commit, Terraform, terraform-docs, tflint)
* Development environment setup for Windows and macOS
* Pre-commit hook configuration

### 💡 Need Help?

* Check the [Contributing Guide](docs/CONTRIBUTING.md) for detailed instructions
* Review existing issues and pull requests for context
* Contact the development team if you encounter setup difficulties

**Note:** All contributions must pass our automated checks including Terraform validation, linting, and security scans before being merged.

<!-- BEGIN_TF_DOCS -->
## Terraform AzureRM MSSQL Managed Instance Module

### Usage

```hcl
// tflint-ignore-file: terraform_required_version
module "my_mssqlmi_instance" {
  source = "C:/Users/u68537/projects/terraform-azurerm-mssqlmi"

  resource_group_name = "dte_cu_myapplication_rg"
  location            = "centralus"

  server_name             = "mysqlinstance"
  environment             = "Dev"
  application_criticality = "Tier4"

  // break-glass local password
  admin_username = "<dbadmin>"
  admin_password = "<secret, secret - I got a secret>"

  user_managed_identity_name                = azurerm_user_assigned_identity.this.name
  user_managed_identity_resource_group_name = azurerm_user_assigned_identity.this.resource_group_name

  sku_name           = "GP_Gen5"
  vcores             = 4
  storage_size_in_gb = 32
  license_type       = "LicenseIncluded"
  collation          = "Latin1_General_100_CI_AS_SC"
  timezone           = "UTC"

  application_subnet_id = azurerm_subnet.application.id
  sql_subnet_id         = azurerm_subnet.sqlmi.id

  // Log Analytics Workspaces
  log_analytics_workspace_name                = azurerm_log_analytics_workspace.this.name
  log_analytics_workspace_resource_group_name = azurerm_log_analytics_workspace.this.resource_group_name

  // If doining vulnerability aseesments
  enable_vulnerability_assessment         = true // defaults to false
  vulnerability_assessment_container_path = "https://mystorageaccount.privatelink.blob.core.windows.net/va"

  // If your UMI is already set up for AAD (Entra) Admin Group Auth
  do_admin_aad_group_registration = true
  admin_aad_group_login_name      = "Azure-IDSS-SQL-Server-Contributor"    // Defaults to this
  admin_aad_group_login_object_id = "6637f678-d27f-4a7e-b194-bc685c8a8e1d" // Defaults to this

  databases = [
    "MyDatabaseOne",
    "MyDatabaseTwo",
    "MyDatabaseThree"
  ]

  tags = local.required_tags
}
```

## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 1.8.5 |
| <a name="requirement_azurerm"></a> [azurerm](#requirement\_azurerm) | ~>4.0 |
| <a name="requirement_null"></a> [null](#requirement\_null) | 3.2.3 |
| <a name="requirement_random"></a> [random](#requirement\_random) | 3.6.3 |

## Resources

| Name | Type |
|------|------|
| [azurerm_monitor_diagnostic_setting.sqlmi_audit_logs](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/monitor_diagnostic_setting) | resource |
| [azurerm_mssql_managed_database.sqlmi_server_databases](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/mssql_managed_database) | resource |
| [azurerm_mssql_managed_instance.sqlmi_server](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/mssql_managed_instance) | resource |
| [azurerm_mssql_managed_instance_active_directory_administrator.sqlmi_server_admin_group](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/mssql_managed_instance_active_directory_administrator) | resource |
| [azurerm_mssql_managed_instance_vulnerability_assessment.sqlmi_server_va](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/mssql_managed_instance_vulnerability_assessment) | resource |
| [azurerm_private_endpoint.sqlmi_server_pep](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/private_endpoint) | resource |
| [azurerm_client_config.current](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/data-sources/client_config) | data source |
| [azurerm_log_analytics_workspace.law_sqlmi_server](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/data-sources/log_analytics_workspace) | data source |
| [azurerm_subscription.current](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/data-sources/subscription) | data source |
| [azurerm_user_assigned_identity.umi_sqmi_server](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/data-sources/user_assigned_identity) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_admin_password"></a> [admin\_password](#input\_admin\_password) | The administrator password for the SQL Managed Instance | `string` | n/a | yes |
| <a name="input_admin_username"></a> [admin\_username](#input\_admin\_username) | The administrator username for the SQL Managed Instance | `string` | n/a | yes |
| <a name="input_application_criticality"></a> [application\_criticality](#input\_application\_criticality) | The criticality of the application. Must be one of: [ Tier1, Tier2, Tier3, Tier4 ] | `string` | n/a | yes |
| <a name="input_application_subnet_id"></a> [application\_subnet\_id](#input\_application\_subnet\_id) | The subnet id to home the private endpoint created for this SQL Managed Instance | `string` | n/a | yes |
| <a name="input_environment"></a> [environment](#input\_environment) | The environment name. Must be one of: [ Sandbox, Base ] | `string` | n/a | yes |
| <a name="input_log_analytics_workspace_name"></a> [log\_analytics\_workspace\_name](#input\_log\_analytics\_workspace\_name) | The name of the analytics workspace to store security events. | `string` | n/a | yes |
| <a name="input_resource_group_name"></a> [resource\_group\_name](#input\_resource\_group\_name) | Name of the resource group | `string` | n/a | yes |
| <a name="input_server_name"></a> [server\_name](#input\_server\_name) | Name of the resource group | `string` | n/a | yes |
| <a name="input_sku_name"></a> [sku\_name](#input\_sku\_name) | The SKU name for the SQL Managed Instance | `string` | n/a | yes |
| <a name="input_sql_subnet_id"></a> [sql\_subnet\_id](#input\_sql\_subnet\_id) | The subnet id of the SQL Managed Instance delegated subnet | `string` | n/a | yes |
| <a name="input_storage_size_in_gb"></a> [storage\_size\_in\_gb](#input\_storage\_size\_in\_gb) | Storage size in GB for the SQL Managed Instance | `number` | n/a | yes |
| <a name="input_tags"></a> [tags](#input\_tags) | Tags to be applied to SQL Server, must include required tags for policy | <pre>object({<br/>    Environment         = string<br/>    Portfolio           = string<br/>    Application         = string<br/>    BillTo              = string<br/>    ContactEmail        = string<br/>    BusinessCriticality = string<br/>    DataClassification  = string<br/>  })</pre> | n/a | yes |
| <a name="input_user_managed_identity_name"></a> [user\_managed\_identity\_name](#input\_user\_managed\_identity\_name) | The user managed identity to use for the SQL Managed Instance | `string` | n/a | yes |
| <a name="input_vcores"></a> [vcores](#input\_vcores) | Number of vCores for the SQL Managed Instance | `number` | n/a | yes |
| <a name="input_admin_aad_group_login_name"></a> [admin\_aad\_group\_login\_name](#input\_admin\_aad\_group\_login\_name) | The AAD group to use as the admin group. | `string` | `"Azure-IDSS-SQL-Server-Contributor"` | no |
| <a name="input_admin_aad_group_login_object_id"></a> [admin\_aad\_group\_login\_object\_id](#input\_admin\_aad\_group\_login\_object\_id) | The AAD group to use as the admin group. | `string` | `"6637f678-d27f-4a7e-b194-bc685c8a8e1d"` | no |
| <a name="input_collation"></a> [collation](#input\_collation) | The collation for the SQL Managed Instance | `string` | `"SQL_Latin1_General_CP1_CI_AS"` | no |
| <a name="input_databases"></a> [databases](#input\_databases) | Set of databases to create on the SQL Managed Instance | `set(string)` | `[]` | no |
| <a name="input_do_admin_aad_group_registration"></a> [do\_admin\_aad\_group\_registration](#input\_do\_admin\_aad\_group\_registration) | If true, the module will create AAD application and user groups for SQL Managed Instance access | `bool` | `false` | no |
| <a name="input_enable_vulnerability_assessment"></a> [enable\_vulnerability\_assessment](#input\_enable\_vulnerability\_assessment) | If true, the module will enable vulnerability assessment for the SQL Managed Instance | `bool` | `false` | no |
| <a name="input_license_type"></a> [license\_type](#input\_license\_type) | The license type for the SQL Managed Instance | `string` | `"LicenseIncluded"` | no |
| <a name="input_location"></a> [location](#input\_location) | The location of the virtual network | `string` | `"centralus"` | no |
| <a name="input_log_analytics_workspace_resource_group_name"></a> [log\_analytics\_workspace\_resource\_group\_name](#input\_log\_analytics\_workspace\_resource\_group\_name) | The location of the analytics workspace to store security events, defaults to the SQL Managed Instance resource group. | `string` | `null` | no |
| <a name="input_timezone"></a> [timezone](#input\_timezone) | Timezone for the SQL Managed Instance. Options: 'UTC' or 'Eastern Standard Time' (auto-adjusts for DST) | `string` | `"UTC"` | no |
| <a name="input_user_managed_identity_resource_group_name"></a> [user\_managed\_identity\_resource\_group\_name](#input\_user\_managed\_identity\_resource\_group\_name) | The user managed identity to use for the SQL Managed Instance, defaults to the SQL Managed Instance resource group. | `string` | `null` | no |
| <a name="input_vulnerability_assessment_container_path"></a> [vulnerability\_assessment\_container\_path](#input\_vulnerability\_assessment\_container\_path) | The fully qualified path to the storage container for vulnerability assessment results, only used if enable\_vulnerability\_assessment is true | `string` | `null` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_id"></a> [id](#output\_id) | The resource ID of the SQL Managed Instance |
| <a name="output_name"></a> [name](#output\_name) | The name of the SQL Managed Instance |
| <a name="output_url"></a> [url](#output\_url) | The FQDN of the Private Endpoint to the SQL Managed Instance Server |
<!-- END_TF_DOCS -->
