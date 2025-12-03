# Output definitions for CorpApps application resource groups

output "application_resource_groups" {
  description = "Application resource groups created for CorpApps portfolio"
  value = {
    captiva_scanning_system = {
      name         = azurerm_resource_group.rg_captiva_scanning.name
      location     = azurerm_resource_group.rg_captiva_scanning.location
      service      = "captivascanning"
      display_name = "CAPTIVA SCANNING SYSTEM"
    }
    financial_management_system = {
      name         = azurerm_resource_group.rg_financial_management.name
      location     = azurerm_resource_group.rg_financial_management.location
      service      = "fms"
      display_name = "FINANCIAL MANAGEMENT SYSTEM"
    }
    mywizard_ata = {
      name         = azurerm_resource_group.rg_mywizard_ata.name
      location     = azurerm_resource_group.rg_mywizard_ata.location
      service      = "mywizata"
      display_name = "myWizard Auto Ticket Assignment (ATA)"
    }
  }
}
