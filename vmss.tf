# Virtual Machine Scale Set resources for the imported VM pattern module

# Optional VM Scale Set anchor for imports (Flexible VMSS) - Windows
resource "azurerm_windows_virtual_machine_scale_set" "vmss" {
  count               = var.enable_vmss && local.vm_os_type == "windows" ? 1 : 0
  name                = var.vmss_name
  location            = var.location
  resource_group_name = var.resource_group_name

  sku                    = var.vmss_sku
  instances              = var.vmss_instances
  single_placement_group = false
  overprovision          = false

  admin_username = var.vmss_admin_username
  admin_password = var.vmss_admin_password

  source_image_reference {
    publisher = var.vmss_image_publisher
    offer     = var.vmss_image_offer
    sku       = var.vmss_image_sku
    version   = var.vmss_image_version
  }

  os_disk {
    storage_account_type = var.vmss_os_disk_storage_account_type
    caching              = var.vmss_os_disk_caching
  }

  network_interface {
    name    = "primary"
    primary = true

    ip_configuration {
      name      = "internal"
      primary   = true
      subnet_id = var.network.subnet_id
    }
  }

  upgrade_mode = "Manual"

  tags = var.tags

  lifecycle {
    prevent_destroy = true
    ignore_changes = [
      admin_password,
      admin_username,
      source_image_reference,
      os_disk,
      network_interface,
      overprovision,
      instances
    ]
  }
}

# Optional VM Scale Set anchor for imports (Flexible VMSS) - Linux
resource "azurerm_linux_virtual_machine_scale_set" "vmss" {
  count               = var.enable_vmss && local.vm_os_type == "linux" ? 1 : 0
  name                = var.vmss_name
  location            = var.location
  resource_group_name = var.resource_group_name

  sku                    = var.vmss_sku
  instances              = var.vmss_instances
  single_placement_group = false
  overprovision          = false

  admin_username = var.linux_admin_username

  source_image_reference {
    publisher = var.vmss_image_publisher
    offer     = var.vmss_image_offer
    sku       = var.vmss_image_sku
    version   = var.vmss_image_version
  }

  os_disk {
    storage_account_type = var.vmss_os_disk_storage_account_type
    caching              = var.vmss_os_disk_caching
  }

  network_interface {
    name    = "primary"
    primary = true

    ip_configuration {
      name      = "internal"
      primary   = true
      subnet_id = var.network.subnet_id
    }
  }

  upgrade_mode = "Manual"

  tags = var.tags

  lifecycle {
    prevent_destroy = true
    ignore_changes = [
      source_image_reference,
      os_disk,
      network_interface,
      overprovision,
      instances
    ]
  }
}
