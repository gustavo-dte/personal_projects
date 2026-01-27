resource "azurerm_resource_group" "primary" {
  name     = "rg-cu-CorpApps-Network-Dev"
  location = var.primary_region
}

resource "azurerm_resource_group" "secondary" {
  name     = "cloud-platform-dev-e2-corpapps-rg"
  location = var.secondary_region
}

resource "azurerm_resource_group" "primary-vck" {
  name     = "rg-cu-CorpApps-VCK-Dev"
  location = var.primary_region
}

resource "azurerm_resource_group" "secondary-vck" {
  name     = "rg-e2-CorpApps-VCK-Dev"
  location = var.secondary_region
}

resource "azurerm_resource_group" "vm_migration_test" {
  name     = "rg-cu-CorpApps-MigrationTest-Dev"
  location = var.primary_region
}

# Existing Resource Group
resource "azurerm_resource_group" "rg-fbk" {
  name     = "rg-cu-corpapps-fermibest-dev"
  location = var.primary_region
}

import {
  to = azurerm_resource_group.rg-fbk
  id = "/subscriptions/6796a2fb-2928-4ec6-96da-962d3b0001b7/resourceGroups/rg-cu-corpapps-fermibest-dev"
}

//vmware
resource "azurerm_resource_group" "primary_vmware_network_rg" {
  name     = "rg-${local.primary_region}-${local.migration_name}-Network-Dev"
  location = var.primary_region
}

resource "azurerm_resource_group" "secondary_vmware_network_rg" {
  name     = "rg-${local.secondary_region}-${local.migration_name}-Network-Dev"
  location = var.secondary_region
}

# This Feature is GA, but not enabled by default. This is to enable the feature for the subscription.
# https://learn.microsoft.com/en-us/azure/application-gateway/application-gateway-private-deployment?tabs=portal#onboard-to-the-feature
resource "azapi_update_resource" "enable_application_gateway_network_isolation" {
  type        = "Microsoft.Features/featureProviders/subscriptionFeatureRegistrations@2021-07-01"
  resource_id = "/subscriptions/${data.azurerm_subscription.current.subscription_id}/providers/Microsoft.Features/featureProviders/Microsoft.Network/subscriptionFeatureRegistrations/EnableApplicationGatewayNetworkisolation"
  body = {
    properties = {}
  }
}
