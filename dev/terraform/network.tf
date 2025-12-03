locals {
  primary_vnet_cidr           = module.primary_ipam.allocated_cidr
  primary_sqlmi_fbk_vnet_cidr = module.primary_sqlmi_fbk_ipam.allocated_cidr
  secondary_vnet_cidr         = module.secondary_ipam.allocated_cidr
}

module "primary_ipam" {
  source                 = "app.terraform.io/DTE-Cloud-Platform/ipam/infoblox"
  version                = "1.2.3"
  network_length         = 27
  application            = local.primary_prefix
  network_container_cidr = var.primary_network_container_cidr
  cloud_region           = var.primary_region
}

module "primary_sqlmi_fbk_ipam" {
  source                 = "app.terraform.io/DTE-Cloud-Platform/ipam/infoblox"
  version                = "1.2.3"
  network_length         = 27
  application            = local.primary_prefix
  network_container_cidr = var.primary_network_container_cidr
  cloud_region           = var.primary_region
}

module "secondary_ipam" {
  source                 = "app.terraform.io/DTE-Cloud-Platform/ipam/infoblox"
  version                = "1.2.3"
  network_length         = 27
  application            = local.secondary_prefix
  network_container_cidr = var.secondary_network_container_cidr
  cloud_region           = var.secondary_region
}

module "primary_network" {
  source  = "app.terraform.io/DTE-Cloud-Platform/virtual-network/azurerm"
  version = "0.3.0"

  vnet_name           = "${local.primary_prefix}-vnet"
  vnet_address_spaces = [local.primary_vnet_cidr]
  resource_group_name = azurerm_resource_group.primary.name
  location            = azurerm_resource_group.primary.location
  subnets = [
    {
      name           = "main"
      address_prefix = cidrsubnet(local.primary_vnet_cidr, 1, 0)
    },
    {
      name           = "secondary"
      address_prefix = cidrsubnet(local.primary_vnet_cidr, 1, 1)
    },
  ]
  environment       = "base"
  tags              = local.tags
  service_endpoints = []
}

module "primary_sqlmi_fbk_network" {
  source  = "app.terraform.io/DTE-Cloud-Platform/virtual-network/azurerm"
  version = "0.3.0"

  vnet_name           = "${local.primary_prefix}-sqlmi-fbk-vnet"
  vnet_address_spaces = [local.primary_sqlmi_fbk_vnet_cidr]
  resource_group_name = azurerm_resource_group.primary.name
  location            = azurerm_resource_group.primary.location
  subnets = [
    {
      name           = "main"
      address_prefix = cidrsubnet(local.primary_sqlmi_fbk_vnet_cidr, 0, 0)
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
}

module "secondary_network" {
  source  = "app.terraform.io/DTE-Cloud-Platform/virtual-network/azurerm"
  version = "0.3.0"

  vnet_name           = "${local.secondary_prefix}-vnet"
  vnet_address_spaces = [local.secondary_vnet_cidr]
  resource_group_name = azurerm_resource_group.secondary.name
  location            = azurerm_resource_group.secondary.location
  subnets = [
    {
      name           = "main"
      address_prefix = cidrsubnet(local.secondary_vnet_cidr, 1, 0)
    },
  ]
  environment       = "base"
  tags              = local.tags
  service_endpoints = []

}
