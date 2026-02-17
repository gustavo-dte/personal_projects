# Output definitions for CorpApps application resource groups - Test Environment

output "application_resource_groups" {
  description = "Application resource groups created for CorpApps portfolio test environment"
  value = {
    captiva_scanning = {
      name         = azurerm_resource_group.rg_captiva_scanning.name
      location     = azurerm_resource_group.rg_captiva_scanning.location
      service      = "captivascanning"
      display_name = "CAPTIVA SCANNING SYSTEM"
    }
  }
}
