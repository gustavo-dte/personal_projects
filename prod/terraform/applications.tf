
# Server Migration Resource Groups for Corporate Applications
resource "azurerm_resource_group" "rg_captiva_scanning" {
  name     = "rg-cu-corpapps-captivascanning-prod"
  location = var.primary_region

  tags = merge(local.tags, {
    Purpose              = "Server Migration"
    Application          = "CAPTIVA SCANNING SYSTEM"
    ApplicationShortName = "captivascanning"
    Teir                 = "Teir4"
  })
}

resource "azurerm_resource_group" "rg_financial_management" {
  name     = "rg-cu-corpapps-fms-prod"
  location = var.primary_region

  tags = merge(local.tags, {
    Purpose              = "Server Migration"
    Application          = "FINANCIAL MANAGEMENT SYSTEM"
    ApplicationShortName = "fms"
    Tier                 = "Tier4"
  })
}

resource "azurerm_resource_group" "rg_mywizard_ata" {
  name     = "rg-cu-corpapps-mywizata-prod"
  location = var.primary_region

  tags = merge(local.tags, {
    Purpose              = "Server Migration"
    Application          = "myWizard Auto Ticket Assignment (ATA)"
    ApplicationShortName = "mywizata"
    Tier                 = "Tier4"
  })
}
