# Application Resource Groups for CorpApps Portfolio
# These resource groups host the specific applications for the CorpApps portfolio

resource "azurerm_resource_group" "rg_captiva_scanning" {
  name     = "rg-cu-corpapps-captivascanning-dev"
  location = var.primary_region

  tags = merge(local.tags, {
    Purpose              = "Server Migration"
    Application          = "CAPTIVA SCANNING SYSTEM"
    ApplicationShortName = "captivascanning"
    Tier                 = "Tier4"
  })
}
