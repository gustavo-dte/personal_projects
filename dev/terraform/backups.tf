# VCK Recovery Services Vault
resource "azurerm_recovery_services_vault" "dev_vck_backup_vault" {
  name                = "backup-vault-cu-dev-vck"
  location            = azurerm_resource_group.primary-vck.location
  resource_group_name = azurerm_resource_group.primary-vck.name
  sku                 = "Standard"
  soft_delete_enabled = true
  tags                = local.tags
}

# Backup Policy for Azure VM
resource "azurerm_backup_policy_vm" "backup_policy" {
  name                = "daily-vm-backup-policy"
  resource_group_name = azurerm_resource_group.primary-vck.name
  recovery_vault_name = azurerm_recovery_services_vault.dev_vck_backup_vault.name

  backup {
    frequency = "Daily"
    time      = "20:00"
  }

  retention_daily {
    count = 30
  }
}
