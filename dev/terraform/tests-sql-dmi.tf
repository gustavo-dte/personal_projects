/*
 * Copyright (c) DTE Energy Corporate Services, LLC. All rights reserved.
 * Internal Use Only
 *
 * Test deployment for Azure SQL Managed Instance
 */

#------------------------------------------------------------------------------
# Local variables for SQL MI configuration
#------------------------------------------------------------------------------
locals {
  sqlmi_sku_name           = "GP_Gen5"
  sqlmi_vcores             = 4
  sqlmi_storage_size_in_gb = 32
}

#------------------------------------------------------------------------------
# Log Analytics Workspace for SQL MI diagnostics
#------------------------------------------------------------------------------
resource "azurerm_log_analytics_workspace" "sqlmi_law" {
  name                = "law-corpapps-sqlmi-dev-cu"
  location            = azurerm_resource_group.vm_migration_test.location
  resource_group_name = azurerm_resource_group.vm_migration_test.name
  sku                 = "PerGB2018"
  retention_in_days   = 30

  tags = local.tags
}

#------------------------------------------------------------------------------
# User Assigned Managed Identity for SQL MI
#------------------------------------------------------------------------------
resource "azurerm_user_assigned_identity" "sqlmi_umi" {
  name                = "umi-sqlmi-corpapps-dev"
  location            = azurerm_resource_group.vm_migration_test.location
  resource_group_name = azurerm_resource_group.vm_migration_test.name

  tags = local.tags
}

#------------------------------------------------------------------------------
# SQL Managed Instance Module
#------------------------------------------------------------------------------
module "mssqlmi" {
  source  = "app.terraform.io/DTE-Cloud-Platform/mssqlmi/azurerm"
  version = "0.1.0-alpha"

  # Resource Group
  resource_group_name = azurerm_resource_group.vm_migration_test.name
  location            = azurerm_resource_group.vm_migration_test.location

  # Server configuration
  server_name             = "test-corpapps"
  environment             = "Dev"
  application_criticality = "Tier4"

  # Admin credentials
  admin_username = "sqladminuser"
  admin_password = "P@ssw0rd!Secure2024#" # pragma: allowlist secret

  # User Managed Identity - referencing created resource
  user_managed_identity_name                = azurerm_user_assigned_identity.sqlmi_umi.name
  user_managed_identity_resource_group_name = azurerm_user_assigned_identity.sqlmi_umi.resource_group_name

  # SQL MI SKU configuration
  sku_name           = local.sqlmi_sku_name
  vcores             = local.sqlmi_vcores
  storage_size_in_gb = local.sqlmi_storage_size_in_gb
  license_type       = "LicenseIncluded"
  collation          = "SQL_Latin1_General_CP1_CI_AS"
  timezone           = "UTC"

  # Networking
  sql_subnet_id         = module.primary_sqlmi_fbk_network.subnet_ids["main"]
  application_subnet_id = module.primary_network.subnet_ids["main"]

  # Log Analytics Workspace - referencing created resource
  log_analytics_workspace_name                = azurerm_log_analytics_workspace.sqlmi_law.name
  log_analytics_workspace_resource_group_name = azurerm_log_analytics_workspace.sqlmi_law.resource_group_name

  # Vulnerability Assessment
  enable_vulnerability_assessment         = false
  vulnerability_assessment_container_path = null

  # Diagnostic Settings and Private Endpoint - disabled to avoid timeout issues
  enable_diagnostic_settings = false
  enable_private_endpoint    = false

  # AAD Admin Group configuration
  do_admin_aad_group_registration = false
  admin_aad_group_login_name      = "Azure-IDSS-SQL-Server-Contributor"
  admin_aad_group_login_object_id = "6637f678-d27f-4a7e-b194-bc685c8a8e1d"

  # Databases
  databases = [
    "TestDatabase01",
    "TestDatabase02"
  ]

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

  depends_on = [
    azurerm_log_analytics_workspace.sqlmi_law,
    azurerm_user_assigned_identity.sqlmi_umi
  ]
}
