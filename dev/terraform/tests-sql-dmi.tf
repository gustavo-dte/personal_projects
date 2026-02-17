locals {
  primary_sqlmi_test_vnet_cidr = module.primary_sqlmi_test_ipam.allocated_cidr
}
/*
 * Copyright (c) DTE Energy Corporate Services, LLC. All rights reserved.
 * Internal Use Only
 *
 * Test deployment for Azure SQL Managed Instance
 */
#------------------------------------------------------------------------------
# User Assigned Managed Identity for SQL MI
#------------------------------------------------------------------------------
resource "azurerm_user_assigned_identity" "sqlmi_umi" {
  name                = "umi-sqlmi-corpapps-dev"
  resource_group_name = azurerm_resource_group.vm_migration_test.name
  location            = azurerm_resource_group.vm_migration_test.location

  tags = local.tags
}

module "primary_sqlmi_test_ipam" {
  source                 = "app.terraform.io/DTE-Cloud-Platform/ipam/infoblox"
  version                = "1.2.3"
  network_length         = 25
  application            = local.primary_prefix
  network_container_cidr = var.primary_network_container_cidr
  cloud_region           = var.primary_region
}

module "primary_sqlmi_test_network" {
  source  = "app.terraform.io/DTE-Cloud-Platform/virtual-network/azurerm"
  version = "0.3.0"

  vnet_name           = "${local.primary_prefix}-sqlmi-test-vnet"
  vnet_address_spaces = [local.primary_sqlmi_test_vnet_cidr]
  resource_group_name = azurerm_resource_group.primary.name
  location            = azurerm_resource_group.vm_migration_test.location

  subnets = [
    {
      name           = "main"
      address_prefix = cidrsubnet(local.primary_sqlmi_test_vnet_cidr, 0, 0)
      delegations = [{
        name         = "Microsoft.Sql/managedInstances"
        service_name = "Microsoft.Sql/managedInstances"
        actions = ["Microsoft.Network/virtualNetworks/subnets/join/action", "Microsoft.Network/virtualNetworks/subnets/prepareNetworkPolicies/action", "Microsoft.Network/virtualNetworks/subnets/unprepareNetworkPolicies/action"
        ]
      }]
    },
  ]
  environment       = "base"
  tags              = local.tags
  service_endpoints = []

  depends_on = [
    module.primary_sqlmi_test_ipam
  ]
}

#------------------------------------------------------------------------------
# SQL Managed Instance Module
#------------------------------------------------------------------------------
module "mssqlmi_test" {
  source  = "app.terraform.io/DTE-Cloud-Platform/mssqlmi/azurerm"
  version = "0.1.0-alpha"

  # Resource Group
  resource_group_name = azurerm_resource_group.vm_migration_test.name
  location            = azurerm_resource_group.vm_migration_test.location

  # Server configuration
  server_name             = "test-corpapps-test"
  environment             = "Dev"
  application_criticality = "Tier4"

  # Admin credentials
  admin_username = "sqladminuser"
  admin_password = var.sqlmi_password

  # User Managed Identity - referencing created resource
  user_managed_identity_name                = azurerm_user_assigned_identity.sqlmi_umi.name
  user_managed_identity_resource_group_name = azurerm_user_assigned_identity.sqlmi_umi.resource_group_name

  # SQL MI SKU configuration
  sku_name           = "GP_Gen5"
  vcores             = 4
  storage_size_in_gb = 32
  license_type       = "LicenseIncluded"
  collation          = "SQL_Latin1_General_CP1_CI_AS"
  timezone           = "Eastern Standard Time"

  # Networking
  sql_subnet_id         = module.primary_sqlmi_test_network.subnet_ids["main"]
  application_subnet_id = module.primary_network.subnet_ids["main"]

  # Log Analytics Workspace - referencing created resource
  log_analytics_workspace_name                = azurerm_log_analytics_workspace.vm_law_cu.name
  log_analytics_workspace_resource_group_name = azurerm_log_analytics_workspace.vm_law_cu.resource_group_name
  # Vulnerability Assessment
  enable_vulnerability_assessment         = false
  vulnerability_assessment_container_path = null

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
    BillTo              = "100000069697"
    ContactEmail        = local.tags.ItAppOwnerEmail
    BusinessCriticality = local.tags.BusinessCriticality
    DataClassification  = local.tags.DataClassification
  }

  depends_on = [
    azurerm_user_assigned_identity.sqlmi_umi,
    module.primary_sqlmi_test_network
  ]
}
