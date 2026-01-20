# Virtual Machine resources for the imported VM pattern module

# Virtual Machine Resource (Windows)
resource "azurerm_windows_virtual_machine" "main" {
  count                      = local.vm_os_type == "windows" ? 1 : 0
  name                       = var.vm_name
  resource_group_name        = var.resource_group_name
  location                   = var.location
  size                       = var.vm_size
  allow_extension_operations = var.provision_vm_agent
  zone                       = var.availability_zone

  network_interface_ids = [azurerm_network_interface.main.id]

  # Optional: attach VM to a Flexible VMSS when enabled
  virtual_machine_scale_set_id = var.enable_vmss ? azurerm_windows_virtual_machine_scale_set.vmss[0].id : null

  # Attach existing OS managed disk managed by this module
  os_managed_disk_id = azurerm_managed_disk.os_disk.id

  dynamic "identity" {
    for_each = var.identity.type != "None" ? [1] : []
    content {
      type = var.identity.type
      identity_ids = var.identity.type == "SystemAssigned" ? null : (
        length(var.identity.identity_ids) > 0 ? var.identity.identity_ids : (
          contains(["UserAssigned", "SystemAssigned, UserAssigned"], var.identity.type) ?
          [azurerm_user_assigned_identity.identity[0].id] : []
        )
      )
    }
  }

  # Required os_disk block (minimal) even when attaching existing managed disk
  os_disk {
    caching = var.disk.os.caching
  }

  # Enable security features for Trusted Launch
  secure_boot_enabled        = var.security_features.secure_boot_enabled
  vtpm_enabled               = var.security_features.vtpm_enabled
  encryption_at_host_enabled = true

  # Enable Windows Update Manager integration
  patch_mode            = "AutomaticByPlatform"
  patch_assessment_mode = "AutomaticByPlatform"

  dynamic "boot_diagnostics" {
    for_each = var.boot_diagnostics_uri != null ? [1] : []
    content {
      storage_account_uri = var.boot_diagnostics_uri
    }
  }

  custom_data = var.custom_data != "" ? var.custom_data : null
  tags        = var.tags

  lifecycle {
    prevent_destroy = true
    ignore_changes = [
      admin_username,
      admin_password,
      license_type,
      source_image_id,
      source_image_reference,
      os_managed_disk_id,
      network_interface_ids,
      zone,
      secure_boot_enabled,
      vtpm_enabled,
      encryption_at_host_enabled,
      computer_name,
      additional_capabilities,
      boot_diagnostics,
      os_disk[0].caching,
      allow_extension_operations,
      bypass_platform_safety_checks_on_user_schedule_enabled,
      patch_mode,
      patch_assessment_mode
    ]
  }
}

# Virtual Machine Resource (Linux)
resource "azurerm_linux_virtual_machine" "main" {
  count               = local.vm_os_type == "linux" ? 1 : 0
  name                = var.vm_name
  resource_group_name = var.resource_group_name
  location            = var.location
  size                = var.vm_size
  zone                = var.availability_zone

  network_interface_ids = [azurerm_network_interface.main.id]

  # Optional: attach VM to a Flexible VMSS when enabled
  virtual_machine_scale_set_id = var.enable_vmss ? azurerm_linux_virtual_machine_scale_set.vmss[0].id : null

  # Attach existing OS managed disk managed by this module
  os_managed_disk_id = azurerm_managed_disk.os_disk.id

  dynamic "identity" {
    for_each = var.identity.type != "None" ? [1] : []
    content {
      type = var.identity.type
      identity_ids = var.identity.type == "SystemAssigned" ? null : (
        length(var.identity.identity_ids) > 0 ? var.identity.identity_ids : (
          contains(["UserAssigned", "SystemAssigned, UserAssigned"], var.identity.type) ?
          [azurerm_user_assigned_identity.identity[0].id] : []
        )
      )
    }
  }

  # Required os_disk block (minimal) even when attaching existing managed disk
  os_disk {
    caching = var.disk.os.caching
  }

  dynamic "boot_diagnostics" {
    for_each = var.boot_diagnostics_uri != null ? [1] : []
    content {
      storage_account_uri = var.boot_diagnostics_uri
    }
  }

  admin_username                  = var.linux_admin_username
  disable_password_authentication = var.linux_disable_password_authentication

  dynamic "admin_ssh_key" {
    for_each = var.linux_disable_password_authentication && var.linux_admin_ssh_public_key != null ? [1] : []
    content {
      username   = var.linux_admin_username
      public_key = var.linux_admin_ssh_public_key
    }
  }

  admin_password = var.linux_disable_password_authentication ? null : var.linux_admin_password

  custom_data = var.custom_data != "" ? var.custom_data : null
  tags        = var.tags

  lifecycle {
    prevent_destroy = true
    ignore_changes = [
      source_image_id,
      source_image_reference,
      os_managed_disk_id,
      network_interface_ids,
      zone,
      computer_name,
      additional_capabilities,
      boot_diagnostics,
      os_disk[0].caching,
      allow_extension_operations,
      bypass_platform_safety_checks_on_user_schedule_enabled
    ]
  }
}

# User Assigned Identity (if exists)
resource "azurerm_user_assigned_identity" "identity" {
  count               = var.user_assigned_identity_resource_id != null ? 1 : 0
  name                = var.user_assigned_identity_name
  resource_group_name = var.resource_group_name
  location            = var.location
  tags                = var.tags
}

# VM Extension for additional configuration (if needed)
resource "azurerm_virtual_machine_extension" "main" {
  count                      = var.vm_extension_name != null && !var.enable_vmss ? 1 : 0
  name                       = var.vm_extension_name
  virtual_machine_id         = local.vm_os_type == "linux" ? azurerm_linux_virtual_machine.main[0].id : azurerm_windows_virtual_machine.main[0].id
  publisher                  = var.vm_extension_publisher
  type                       = var.vm_extension_type
  type_handler_version       = var.vm_extension_type_handler_version
  auto_upgrade_minor_version = var.vm_extension_auto_upgrade_minor_version
  settings                   = var.vm_extension_settings
  protected_settings         = var.vm_extension_protected_settings

  # Tags
  tags = var.tags
}

# Windows Update Assessment Extension
resource "azurerm_virtual_machine_extension" "windows_update_assessment" {
  count                = var.enable_periodic_update_assessment && local.vm_os_type == "windows" ? 1 : 0
  name                 = "WindowsUpdateAssessment"
  virtual_machine_id   = azurerm_windows_virtual_machine.main[0].id
  publisher            = "Microsoft.Azure.Monitor"
  type                 = "WindowsUpdateExtension"
  type_handler_version = "1.0"

  settings = <<SETTINGS
    {
      "assessmentMode": "AutomaticByPlatform"
    }
SETTINGS

  depends_on = [azurerm_windows_virtual_machine.main]
  tags       = var.tags
}

# Domain Join Extension
resource "azurerm_virtual_machine_extension" "domain_join" {
  count                      = var.enable_domain_join && local.vm_os_type == "windows" ? 1 : 0
  name                       = "JsonADDomainExtension"
  virtual_machine_id         = azurerm_windows_virtual_machine.main[0].id
  publisher                  = "Microsoft.Compute"
  type                       = "JsonADDomainExtension"
  type_handler_version       = "1.3"
  auto_upgrade_minor_version = true

  settings = jsonencode({
    Name    = var.domain_name
    OUPath  = var.target_ou
    User    = var.domain_join_service_user
    Restart = "true"
    Options = "3" # NETSETUP_JOIN_DOMAIN + NETSETUP_ACCT_CREATE
  })

  protected_settings = jsonencode({
    Password = var.domain_join_password
  })

  timeouts {
    create = "30m"
    delete = "15m"
  }

  depends_on = [
    azurerm_windows_virtual_machine.main
  ]

  tags = var.tags
}
