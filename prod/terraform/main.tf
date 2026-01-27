resource "azurerm_resource_group" "primary" {
  name     = "rg-cu-CorpApps-Network-Prod"
  location = var.primary_region
}

resource "azurerm_resource_group" "secondary" {
  name     = "${local.secondary_prefix}-rg"
  location = var.secondary_region
}

resource "azurerm_resource_group" "primary-vck" {
  name     = "rg-cu-CorpApps-VCK-Prod"
  location = var.primary_region
}

resource "azurerm_resource_group" "secondary-vck" {
  name     = "rg-e2-CorpApps-VCK-Prod"
  location = var.secondary_region
}


# Existing Resource Group
resource "azurerm_resource_group" "rg-fbk" {
  name     = "rg-cu-corpapps-fermibest-prod"
  location = var.primary_region
}

import {
  to = azurerm_resource_group.rg-fbk
  id = "/subscriptions/5aa5e9cb-8361-49c3-bdb8-dd365bfc72dd/resourceGroups/rg-cu-corpapps-fermibest-prod"
}
