/*
 * Copyright (c) DTE Energy Corporate Services, LLC. All rights reserved.
 * Internal Use Only
 *
 * Test module for Azure SQL Managed Instance deployment
 */

module "test_sql_dmi" {
  source = "github.com/dteenergy/terraform-azurerm-mssqlmi"

  # Resource Group - using existing resource group from main.tf
  resource_group_name = azurerm_resource_group.rg-fbk.name
  location            = azurerm_resource_group.rg-fbk.location

  # Server configuration
  server_name             = "sqlmi-test-corpapps-dev"
  environment             = "Dev"
  application_criticality = "Tier4"

  # Admin credentials (break-glass local password)
  admin_username = "sqladminuser"
  admin_password = "P@ssw0rd!Secure2024#"

  # User Managed Identity - hardcoded sample values
  user_managed_identity_name                = "umi-sqlmi-corpapps-dev"
  user_managed_identity_resource_group_name = azurerm_resource_group.rg-fbk.name

  # SQL MI SKU configuration
  sku_name           = "GP_Gen5"
  vcores             = 4
  storage_size_in_gb = 32
  license_type       = "LicenseIncluded"
  collation          = "SQL_Latin1_General_CP1_CI_AS"
  timezone           = "Eastern Standard Time"

  # Networking - using existing network from network.tf
  sql_subnet_id         = module.primary_sqlmi_fbk_network.subnet_ids["main"]
  application_subnet_id = module.primary_network.subnet_ids["main"]

  # Log Analytics Workspace - hardcoded sample values
  log_analytics_workspace_name                = "law-corpapps-dev-cu"
  log_analytics_workspace_resource_group_name = azurerm_resource_group.rg-fbk.name

  # Vulnerability Assessment - disabled for test
  enable_vulnerability_assessment         = false
  vulnerability_assessment_container_path = null

  # AAD Admin Group configuration
  do_admin_aad_group_registration = false
  admin_aad_group_login_name      = "Azure-IDSS-SQL-Server-Contributor"
  admin_aad_group_login_object_id = "6637f678-d27f-4a7e-b194-bc685c8a8e1d"

  # Databases to create
  databases = [
    "TestDatabase01",
    "TestDatabase02"
  ]

  # Tags - using existing tags from locals.tf with required structure
  tags = {
    Environment         = local.tags.Environment
    Portfolio           = local.tags.Portfolio
    Application         = local.tags.Application
    BillTo              = local.tags.BillTo
    ContactEmail        = "cloudplatform@dteenergy.com"
    BusinessCriticality = "Tier4"
    DataClassification  = local.tags.DataClassification
  }
}
