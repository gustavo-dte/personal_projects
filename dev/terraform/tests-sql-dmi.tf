/*
 * Creates the SQL Server database for the SQL Migrate SPIKE
 */

locals {
  primary_sqlmi_sku_name           = "GP_Gen5"
  primary_sqlmi_vcores             = 4
  primary_sqlmi_storage_size_in_gb = 32
}

# Create the SQL server Managed Instance Database
resource "azurerm_mssql_managed_instance" "primary_sqlmi" {
  name                = "test-sqldmi"
  resource_group_name = azurerm_resource_group.vm_migration_test.name
  location            = azurerm_resource_group.vm_migration_test.location
  subnet_id           = module.primary_sqlmi_fbk_network.subnet_ids["main"]

  administrator_login          = "sqladminuser"
  administrator_login_password = var.sqlmi_password

  identity {
    type = "SystemAssigned"
  }

  sku_name                     = local.primary_sqlmi_sku_name
  vcores                       = local.primary_sqlmi_vcores
  storage_size_in_gb           = local.primary_sqlmi_storage_size_in_gb
  license_type                 = "LicenseIncluded"
  collation                    = "SQL_Latin1_General_CP1_CI_AS"
  timezone_id                  = "Eastern Standard Time"
  public_data_endpoint_enabled = false

  # Tags - matching module's expected structure
  tags = {
    Environment         = local.tags.Environment
    Portfolio           = local.tags.Portfolio
    Application         = local.tags.Application
    BillTo              = local.tags.BillTo
    ContactEmail        = local.tags.ItAppOwnerEmail
    BusinessCriticality = local.tags.BusinessCriticality
    DataClassification  = local.tags.DataClassification
  }
}

# module "primary_mssqlmi" {
#   source  = "app.terraform.io/DTE-Cloud-Platform/mssqlmi/azurerm"
#   version = "0.1.0-alpha"

#   resource_group_name = azurerm_resource_group.primary.name
#   location            = azurerm_resource_group.primary.location

#   server_name             = "modtstone"
#   environment             = "Dev"
#   application_criticality = "Tier3"

#   admin_username = var.primary_sqlsrv_admin_name
#   admin_password = var.primary_sqlsrv_admin_passwd

#   user_managed_identity_name                = azurerm_user_assigned_identity.primary_sqlmi_umi.name
#   user_managed_identity_resource_group_name = azurerm_user_assigned_identity.primary_sqlmi_umi.resource_group_name

#   sku_name           = local.primary_sqlmi_sku_name
#   vcores             = local.primary_sqlmi_vcores
#   storage_size_in_gb = local.primary_sqlmi_storage_size_in_gb
#   license_type       = var.microsoft_managed_sql_license
#   collation          = "Latin1_General_100_CI_AS_SC"
#   timezone           = "UTC"

#   application_subnet_id = azurerm_subnet.main-subnet-primary.id
#   sql_subnet_id         = azurerm_subnet.sql-subnet-primary.id

#   log_analytics_workspace_name                = azurerm_log_analytics_workspace.this.name
#   log_analytics_workspace_resource_group_name = azurerm_log_analytics_workspace.this.resource_group_name

#   tags = local.required_tags

#   depends_on = [
#     azurerm_user_assigned_identity.primary_sqlmi_umi,
#     azurerm_log_analytics_workspace.this
#   ]
# }

# module "policy_test_mssqlmi_instance" {
#   source  = "app.terraform.io/DTE-Cloud-Platform/mssqlmi/azurerm"
#   version = "0.1.0-alpha"

#   resource_group_name = azurerm_resource_group.primary.name
#   location            = azurerm_resource_group.primary.location

#   server_name             = "policytst"
#   environment             = "Dev"
#   application_criticality = "Tier4"

#   admin_username = var.primary_sqlsrv_admin_name
#   admin_password = var.primary_sqlsrv_admin_passwd

#   user_managed_identity_name                = azurerm_user_assigned_identity.primary_sqlmi_umi.name
#   user_managed_identity_resource_group_name = azurerm_user_assigned_identity.primary_sqlmi_umi.resource_group_name

#   sku_name           = local.primary_sqlmi_sku_name
#   vcores             = local.primary_sqlmi_vcores
#   storage_size_in_gb = local.primary_sqlmi_storage_size_in_gb
#   license_type       = var.microsoft_managed_sql_license
#   collation          = "Latin1_General_100_CI_AS_SC"
#   timezone           = "UTC"

#   application_subnet_id = azurerm_subnet.main-subnet-primary.id
#   sql_subnet_id         = azurerm_subnet.sql-subnet-primary.id

#   log_analytics_workspace_name                = azurerm_log_analytics_workspace.this.name
#   log_analytics_workspace_resource_group_name = azurerm_log_analytics_workspace.this.resource_group_name

#   databases = [
#     "SampleDatabase"
#   ]

#   tags = local.required_tags

#   depends_on = [
#     azurerm_user_assigned_identity.primary_sqlmi_umi,
#     azurerm_log_analytics_workspace.this
#   ]
# }

resource "azapi_resource" "sql_migration_service" {
  type      = "Microsoft.DataMigration/sqlMigrationServices@2023-07-15-preview"
  name      = "${azurerm_mssql_managed_instance.primary_sqlmi.name}-dms"
  location  = azurerm_resource_group.primary.location
  parent_id = azurerm_resource_group.primary.id

  body = {
    properties = {}
  }

  # Tags - matching module's expected structure
  tags = {
    Environment         = local.tags.Environment
    Portfolio           = local.tags.Portfolio
    Application         = local.tags.Application
    BillTo              = local.tags.BillTo
    ContactEmail        = local.tags.ItAppOwnerEmail
    BusinessCriticality = local.tags.BusinessCriticality
    DataClassification  = local.tags.DataClassification
  }
}
