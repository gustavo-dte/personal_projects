# Data sources for the imported VM pattern module

# Backup Policy for Azure VM
data "azurerm_backup_policy_vm" "main" {
  count = var.enable_backup ? 1 : 0

  name                = var.backup_vault_policy_name
  recovery_vault_name = var.backup_vault_name
  resource_group_name = var.backup_vault_resource_group_name
}
