resource "azurerm_backup_protected_vm" "main" {
  count = var.enable_backup ? 1 : 0

  resource_group_name = var.backup_vault_resource_group_name
  recovery_vault_name = var.backup_vault_name
  source_vm_id        = local.vm_os_type == "windows" ? azurerm_windows_virtual_machine.main[0].id : azurerm_linux_virtual_machine.main[0].id
  backup_policy_id    = data.azurerm_backup_policy_vm.main[0].id
}
