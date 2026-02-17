# Import Blocks Generation Guide

## Overview
This document explains how the import blocks work in the `test-app-vm.tf` file after the refactoring.

## Current Structure

The import blocks have been refactored to use `for_each` to dynamically generate imports for all VMs defined in `local.test_app_vms`.

### How It Works

1. **VM Definition**: Each VM in `local.test_app_vms` contains all necessary resource IDs
2. **Import Generation**: The `local.all_imports` map combines all import operations
3. **Dynamic Import**: A single `import` block with `for_each` handles all resources

## Adding New VMs

To add a new VM to the import process, simply add it to the `local.test_app_vms` map:

```terraform
test_app_vms = {
  # Existing VM
  vmcuwinwebd01 = { ... }
  
  # New VM
  vmcuwinwebd02 = {
    vmss_name = "vmss-vmcuwinwebd02"
    vm_name   = "vmcuwinwebd02"
    vm_size   = "Standard_D2s_v5"
    network = {
      nic_name  = "nic-vmcuwinwebd02-00"
      subnet_id = module.primary_network.subnet_ids["main"]
      # ... other network config
    }
    disk = {
      os = {
        name                 = "vmcuwinwebd02-OSdisk-00-<guid>"
        caching              = "ReadWrite"
        size_gb              = 100
        storage_account_type = "Standard_LRS"
        create_option        = "Attach"
        os_type              = "Windows"  # or "Linux"
      }
      data = {
        # Add data disks here if any
      }
    }
    # REQUIRED: Resource IDs for imports
    vm_resource_id      = "${local.test_app_resource_prefix}/providers/Microsoft.Compute/virtualMachines/vmcuwinwebd02"
    nic_resource_id     = "${local.test_app_resource_prefix}/providers/Microsoft.Network/networkInterfaces/nic-vmcuwinwebd02-00"
    os_disk_resource_id = "${local.test_app_resource_prefix}/providers/Microsoft.Compute/disks/vmcuwinwebd02-OSdisk-00-<guid>"
    
    user_assigned_identity_resource_id = null
    
    backup = {
      enable_backup                    = true
      backup_vault_name                = "backup-vault-cu-dev-migration-test"
      backup_vault_resource_group_name = "rg-cu-CorpApps-MigrationTest-Dev"
      backup_vault_policy_name         = "daily-migration-test-vm-backup-policy"
    }
  }
}
```

The import blocks will automatically be generated for:
- The VM itself (Windows or Linux based on `os_type`)
- Network interface
- OS disk
- Data disks (if any)
- Data disk attachments (if any)
- VMSS (if `vmss_name` is not null)

## What Gets Imported

For each VM, the following resources are imported:

1. **Virtual Machine**: `azurerm_windows_virtual_machine` or `azurerm_linux_virtual_machine`
2. **Network Interface**: `azurerm_network_interface`
3. **OS Disk**: `azurerm_managed_disk` (OS disk)
4. **Data Disks**: `azurerm_managed_disk` (for each data disk)
5. **Data Disk Attachments**: `azurerm_virtual_machine_data_disk_attachment` (for each data disk)
6. **VMSS** (optional): `azurerm_windows_virtual_machine_scale_set` or `azurerm_linux_virtual_machine_scale_set`

## Import Block Structure

The import block uses `for_each` to iterate through `local.all_imports`:

```terraform
import {
  for_each = local.all_imports
  
  to = each.value.resource_address
  id = each.value.resource_id
}
```

Each entry in `local.all_imports` has:
- `resource_address`: The Terraform resource address (e.g., `module.test_app_vms["vm_name"].azurerm_windows_virtual_machine.main[0]`)
- `resource_id`: The Azure resource ID

## Terraform Version Requirement

This approach requires **Terraform >= 1.5.0** which supports `for_each` in import blocks.

## Alternative: Individual Import Blocks

If you need to use Terraform < 1.5.0, you'll need to generate individual import blocks. You can use the following template for each VM:

```terraform
# VM
import {
  to = module.test_app_vms["VM_KEY"].azurerm_windows_virtual_machine.main[0]
  id = "/subscriptions/.../virtualMachines/VM_NAME"
}

# NIC
import {
  to = module.test_app_vms["VM_KEY"].azurerm_network_interface.main
  id = "/subscriptions/.../networkInterfaces/NIC_NAME"
}

# OS Disk
import {
  to = module.test_app_vms["VM_KEY"].azurerm_managed_disk.os_disk
  id = "/subscriptions/.../disks/OS_DISK_NAME"
}

# Data Disk (for each data disk)
import {
  to = module.test_app_vms["VM_KEY"].azurerm_managed_disk.data_disk["DISK_KEY"]
  id = "/subscriptions/.../disks/DATA_DISK_NAME"
}

# Data Disk Attachment (for each data disk)
import {
  to = module.test_app_vms["VM_KEY"].azurerm_virtual_machine_data_disk_attachment.data_disk_attachment["DISK_KEY"]
  id = "/subscriptions/.../virtualMachines/VM_NAME/dataDisks/DATA_DISK_NAME"
}

# VMSS (if applicable)
import {
  to = module.test_app_vms["VM_KEY"].azurerm_windows_virtual_machine_scale_set.vmss[0]
  id = "/subscriptions/.../virtualMachineScaleSets/VMSS_NAME"
}
```

## Debugging

To see what imports will be generated, you can output `local.all_imports`:

```terraform
output "debug_imports" {
  value = local.all_imports
}
```

This will show all the import operations that will be performed.
