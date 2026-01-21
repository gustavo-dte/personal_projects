terraform {
  required_version = ">= 1.5.0"
}

# Example usage of the terraform-azurerm-imported-vm-pattern module
# This example shows how to import Azure VMs (Windows and Linux) and their associated resources

# Example 1: Windows VM with basic configuration
module "imported_windows_vm" {
  source = "../"

  # Required VM Configuration
  vm_name             = "vm-windows-example"
  resource_group_name = "rg-example"
  location            = "eastus"
  vm_size             = "Standard_D2s_v5"
  vm_os_type          = "windows"

  # Required Network Configuration
  network = {
    nic_name  = "nic-windows-example"
    subnet_id = "/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/rg-example/providers/Microsoft.Network/virtualNetworks/vnet-example/subnets/subnet-example"
  }

  # Required Disk Configuration
  disk = {
    os = {
      name                 = "vm-windows-example_OsDisk_1"
      size_gb              = 127
      storage_account_type = "Premium_LRS"
      caching              = "ReadWrite"
      create_option        = "FromImage"
      os_type              = "Windows"
    }
    data = {
      "data-disk-1" = {
        lun                       = 0
        caching                   = "ReadWrite"
        write_accelerator_enabled = false
        resource_id               = "/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/rg-example/providers/Microsoft.Compute/disks/data-disk-1"
        disk_size_gb              = 100
        storage_account_type      = "Premium_LRS"
      }
      "data-disk-2" = {
        lun                       = 1
        caching                   = "ReadOnly"
        write_accelerator_enabled = false
        resource_id               = "/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/rg-example/providers/Microsoft.Compute/disks/data-disk-2"
        disk_size_gb              = 200
        storage_account_type      = "Standard_LRS"
      }
    }
  }

  # Optional: VM Advanced Settings
  provision_vm_agent   = true
  availability_zone    = "1"
  boot_diagnostics_uri = "https://storageaccount.blob.core.windows.net/"

  # Optional: Identity Configuration
  identity = {
    type         = "SystemAssigned"
    identity_ids = []
  }

  # Optional: Security Features (Trusted Launch)
  security_features = {
    secure_boot_enabled = true
    vtpm_enabled        = true
  }

  # Optional: Windows Update Assessment
  enable_periodic_update_assessment = true
  patch_assessment_schedule = {
    frequency   = "Daily"
    time_of_day = "02:00"
  }

  # Optional: Domain Join
  enable_domain_join       = true
  domain_name              = "contoso.com"
  domain_join_service_user = "serviceaccount@contoso.com"
  domain_join_password     = "SecurePassword123!" # pragma: allowlist secret (example only)
  target_ou                = "OU=Servers,DC=contoso,DC=com"

  # Tags (recommended)
  tags = {
    Environment = "dev"
    Project     = "migration"
    Owner       = "platform-team"
    CostCenter  = "IT"
    OS          = "Windows"
  }

  rec_svcs_vault_name    = ""
  rec_svcs_vault_res_grp = ""
  vm_backup_policy_name  = ""
}

# Example 2: Linux VM with SSH key authentication
module "imported_linux_vm" {
  source = "../"

  # Required VM Configuration
  vm_name             = "vm-linux-example"
  resource_group_name = "rg-example"
  location            = "eastus"
  vm_size             = "Standard_D2s_v5"
  vm_os_type          = "linux"

  # Required Network Configuration
  network = {
    nic_name  = "nic-linux-example"
    subnet_id = "/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/rg-example/providers/Microsoft.Network/virtualNetworks/vnet-example/subnets/subnet-example"
  }

  # Required Disk Configuration
  disk = {
    os = {
      name                 = "vm-linux-example_OsDisk_1"
      size_gb              = 64
      storage_account_type = "Premium_LRS"
      caching              = "ReadWrite"
      create_option        = "FromImage"
      os_type              = "Linux"
    }
    data = {}
  }

  # Linux-specific Configuration
  linux_admin_username                  = "azureuser"
  linux_disable_password_authentication = true
  linux_admin_ssh_public_key            = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC... user@hostname"

  # Optional: User Assigned Identity
  user_assigned_identity_resource_id = "/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/rg-example/providers/Microsoft.ManagedIdentity/userAssignedIdentities/identity-example"
  user_assigned_identity_name        = "identity-example"
  identity = {
    type         = "UserAssigned"
    identity_ids = []
  }

  # Tags (recommended)
  tags = {
    Environment = "dev"
    Project     = "migration"
    Owner       = "platform-team"
    CostCenter  = "IT"
    OS          = "Linux"
  }

  rec_svcs_vault_name    = ""
  rec_svcs_vault_res_grp = ""
  vm_backup_policy_name  = ""
}

# Example 3: Windows VM with VMSS integration (Flexible orchestration)
module "imported_windows_vm_with_vmss" {
  source = "../"

  # Required VM Configuration
  vm_name             = "vm-windows-vmss-example"
  resource_group_name = "rg-example"
  location            = "eastus"
  vm_size             = "Standard_D2s_v5"
  vm_os_type          = "windows"

  # Required Network Configuration
  network = {
    nic_name  = "nic-windows-vmss-example"
    subnet_id = "/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/rg-example/providers/Microsoft.Network/virtualNetworks/vnet-example/subnets/subnet-example"
  }

  # Required Disk Configuration
  disk = {
    os = {
      name                 = "vm-windows-vmss-example_OsDisk_1"
      size_gb              = 127
      storage_account_type = "Premium_LRS"
      caching              = "ReadWrite"
      create_option        = "FromImage"
      os_type              = "Windows"
    }
    data = {}
  }

  # VMSS Configuration (Flexible orchestration)
  enable_vmss                       = true
  vmss_name                         = "vmss-windows-example"
  vmss_sku                          = "Standard_D2s_v5"
  vmss_instances                    = 0 # Flexible mode - instances managed separately
  vmss_admin_username               = "azureuser"
  vmss_admin_password               = "SecurePassword123!" # pragma: allowlist secret (example only)
  vmss_image_publisher              = "MicrosoftWindowsServer"
  vmss_image_offer                  = "WindowsServer"
  vmss_image_sku                    = "2022-datacenter-g2"
  vmss_image_version                = "latest"
  vmss_os_disk_storage_account_type = "Premium_LRS"
  vmss_os_disk_caching              = "ReadWrite"

  # Tags (recommended)
  tags = {
    Environment = "dev"
    Project     = "migration"
    Owner       = "platform-team"
    CostCenter  = "IT"
    OS          = "Windows"
    VMSS        = "Enabled"
  }

  rec_svcs_vault_name    = ""
  rec_svcs_vault_res_grp = ""
  vm_backup_policy_name  = ""
}

# Example Outputs
# output "windows_vm_id" {
#   description = "ID of the imported Windows virtual machine"
#   value       = module.imported_windows_vm.vm_id
# }

# output "windows_vm_private_ip" {
#   description = "Private IP address of the Windows virtual machine"
#   value       = module.imported_windows_vm.private_ip_address
# }

# output "linux_vm_id" {
#   description = "ID of the imported Linux virtual machine"
#   value       = module.imported_linux_vm.vm_id
# }

# output "linux_vm_private_ip" {
#   description = "Private IP address of the Linux virtual machine"
#   value       = module.imported_linux_vm.private_ip_address
# }

# output "vmss_vm_id" {
#   description = "ID of the VM with VMSS integration"
#   value       = module.imported_windows_vm_with_vmss.vm_id
# }

# output "vmss_id" {
#   description = "ID of the Virtual Machine Scale Set"
#   value       = module.imported_windows_vm_with_vmss.vmss_id
# }

# output "all_vm_ids" {
#   description = "All VM IDs from the examples"
#   value = {
#     windows_vm = module.imported_windows_vm.vm_id
#     linux_vm   = module.imported_linux_vm.vm_id
#     vmss_vm    = module.imported_windows_vm_with_vmss.vm_id
#     minimal_vm = module.minimal_vm_example.vm_id
#   }
# }
