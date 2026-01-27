locals {
  primary_vnet_cidr_vmware1 = module.primary_ipam_vmware1.allocated_cidr
  primary_vnet_cidr_vmware2 = module.primary_ipam_vmware2.allocated_cidr

}

module "primary_ipam_vmware1" {
  source                 = "app.terraform.io/DTE-Cloud-Platform/ipam/infoblox"
  version                = "1.2.3"
  network_length         = 23
  application            = local.primary_prefix_vmware
  network_container_cidr = var.primary_network_container_cidr
  cloud_region           = var.primary_region
}

module "primary_ipam_vmware2" {
  source                 = "app.terraform.io/DTE-Cloud-Platform/ipam/infoblox"
  version                = "1.2.3"
  network_length         = 23
  application            = local.primary_prefix_vmware
  network_container_cidr = var.primary_network_container_cidr
  cloud_region           = var.primary_region
}

module "primary_network_vmware" {
  source  = "app.terraform.io/DTE-Cloud-Platform/virtual-network/azurerm"
  version = "0.3.0"

  vnet_name           = "${local.primary_prefix_vmware}-vnet"
  vnet_address_spaces = [local.primary_vnet_cidr_vmware1, local.primary_vnet_cidr_vmware2]
  resource_group_name = azurerm_resource_group.primary_vmware_network_rg.name
  location            = azurerm_resource_group.primary_vmware_network_rg.location
  subnets = [
    {
      name                                      = "bos-db"
      address_prefix                            = cidrsubnet(local.primary_vnet_cidr_vmware1, 4, 0)
      private_endpoint_network_policies         = "Enabled"
      private_endpoint_network_policies_enabled = true
    },
    {
      name                                      = "right-fax-app"
      address_prefix                            = cidrsubnet(local.primary_vnet_cidr_vmware1, 5, 4)
      private_endpoint_network_policies         = "Enabled"
      private_endpoint_network_policies_enabled = true
    },
    {
      name                                      = "right-fax-db"
      address_prefix                            = cidrsubnet(local.primary_vnet_cidr_vmware1, 4, 1)
      private_endpoint_network_policies         = "Enabled"
      private_endpoint_network_policies_enabled = true
    },
    {
      name                                      = "powerbi-app"
      address_prefix                            = cidrsubnet(local.primary_vnet_cidr_vmware1, 5, 5)
      private_endpoint_network_policies         = "Enabled"
      private_endpoint_network_policies_enabled = true
    }
  ]
  environment       = "dev"
  tags              = local.tags
  service_endpoints = []
}
