resource "azurerm_resource_group" "primary" {
  name     = "${local.primary_prefix}-rg"
  location = var.primary_region
}

resource "azurerm_resource_group" "secondary" {
  name     = "${local.secondary_prefix}-rg"
  location = var.secondary_region
}
