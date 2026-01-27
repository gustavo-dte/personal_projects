# Disk resources for the imported VM pattern module

# OS Disk managed as a first-class resource (import existing)
resource "azurerm_managed_disk" "os_disk" {
  name                = var.disk.os.name
  resource_group_name = var.resource_group_name
  location            = var.location
  # Match existing disk to avoid replacement; ignore changes for provider-computed fields
  create_option        = "Import" # ignore changes for existing disks
  disk_size_gb         = var.disk.os.size_gb
  storage_account_type = var.disk.os.storage_account_type
  os_type              = var.disk.os.os_type != "" ? var.disk.os.os_type : null

  tags = var.tags

  lifecycle {
    prevent_destroy = true
    ignore_changes = [
      source_resource_id,
      create_option,
      image_reference_id,
      hyper_v_generation,
      tier,
      zone,
      trusted_launch_enabled
    ]
  }
}

# Data Disks
resource "azurerm_managed_disk" "data_disk" {
  for_each             = var.disk.data
  name                 = each.key
  resource_group_name  = var.resource_group_name
  location             = var.location
  storage_account_type = each.value.storage_account_type
  create_option        = "Import" # ignore changes for existing disks
  disk_size_gb         = each.value.disk_size_gb
  tags                 = var.tags

  lifecycle {
    prevent_destroy = true
    ignore_changes = [
      source_resource_id,
      create_option,
      image_reference_id,
      hyper_v_generation,
      tier,
      trusted_launch_enabled,
      zone,
      on_demand_bursting_enabled,
      upload_size_bytes
    ]
  }
}

# Attach data disks to the VM
resource "azurerm_virtual_machine_data_disk_attachment" "data_disk_attachment" {
  for_each = var.disk.data

  managed_disk_id           = azurerm_managed_disk.data_disk[each.key].id
  virtual_machine_id        = local.vm_os_type == "linux" ? azurerm_linux_virtual_machine.main[0].id : azurerm_windows_virtual_machine.main[0].id
  lun                       = each.value.lun
  caching                   = each.value.caching
  write_accelerator_enabled = each.value.write_accelerator_enabled
}
