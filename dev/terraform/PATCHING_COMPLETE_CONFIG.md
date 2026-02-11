# VM Patching Setup - Complete Configuration in test-app-vm.tf

## Overview

All patching configuration is done directly in `test-app-vm.tf`. The module's `enable_periodic_update_assessment` is **DISABLED** because we configure everything ourselves.

## Configuration Flow

```
1. Import VM (via import block)
   ↓
2. Configure VM patch mode (via null_resource + Azure CLI)
   ↓
3. Create maintenance configuration (via azurerm_maintenance_configuration)
   ↓
4. Assign VM to maintenance config (via azurerm_maintenance_assignment_virtual_machine)
```

## Components

### 1. Module Configuration (DISABLED)
```terraform
# Line 323-325
enable_periodic_update_assessment = false  # ← DISABLED!
# All patching done via resources below
```

### 2. Maintenance Configuration (from JSON)
```terraform
# Lines 373-403
resource "azurerm_maintenance_configuration" "vm_patching" {
  for_each = local.maintenance_config_settings
  
  name                     = "weekly-sunday-2am"  # From JSON
  resource_group_name      = azurerm_resource_group.vm_migration_test.name
  location                 = azurerm_resource_group.vm_migration_test.location
  scope                    = "InGuestPatch"
  in_guest_user_patch_mode = "User"
  
  window {
    start_date_time = "2026-01-01 02:00:00"
    duration        = "03:00"
    time_zone       = "Central Standard Time"
    recur_every     = "Week Sunday"
  }
  
  install_patches {
    reboot = "IfRequired"
    windows {
      classifications_to_include = ["Critical", "Security", ...]
    }
  }
}
```

### 3. VM Patch Mode Configuration (Azure CLI)
```terraform
# Lines 405-432
resource "null_resource" "configure_vm_patch_mode" {
  for_each = { ... }  # For each Windows VM with schedule
  
  provisioner "local-exec" {
    command = <<-EOT
      az vm update \
        --ids ${module.test_app_vms[each.key].vm_id} \
        --set osProfile.windowsConfiguration.patchSettings.patchMode=AutomaticByPlatform \
        --set osProfile.windowsConfiguration.patchSettings.assessmentMode=AutomaticByPlatform \
        --set osProfile.windowsConfiguration.patchSettings.automaticByPlatformSettings.bypassPlatformSafetyChecksOnUserSchedule=true \
        --set osProfile.windowsConfiguration.patchSettings.automaticByPlatformSettings.rebootSetting=Never
    EOT
  }
  
  depends_on = [module.test_app_vms]
}
```

**Why Azure CLI?**
- Module doesn't set patch mode (because `enable_periodic_update_assessment = false`)
- We need to configure it ourselves after VM import
- Azure CLI is the simplest way to update VM properties

### 4. Maintenance Assignment
```terraform
# Lines 434-448
resource "azurerm_maintenance_assignment_virtual_machine" "vm_patching" {
  for_each = { ... }  # For each Windows VM with schedule
  
  location                     = azurerm_resource_group.vm_migration_test.location
  maintenance_configuration_id = azurerm_maintenance_configuration.vm_patching["weekly-sunday-2am"].id
  virtual_machine_id           = module.test_app_vms["vmcuwinwebd01"].vm_id
  
  depends_on = [null_resource.configure_vm_patch_mode]
}
```

### 5. VM Import
```terraform
# Lines 450+
import {
  to = module.test_app_vms["vmcuwinwebd01"].azurerm_windows_virtual_machine.main[0]
  id = "/subscriptions/.../virtualMachines/vmcuwinwebd01"
}
# ... other imports (NIC, disks, etc.)
```

## Resource Dependencies

```
module.test_app_vms (imports VM)
         ↓
null_resource.configure_vm_patch_mode (sets patch mode via Azure CLI)
         ↓
azurerm_maintenance_assignment_virtual_machine (assigns to schedule)
```

## Schedule Configuration (JSON)

**File**: `vm_patching_schedules.json`
```json
{
  "vmcuwinwebd01": {
    "maintenance_configuration": "weekly-sunday-2am",
    "frequency": "Weekly",
    "day_of_week": "Sunday",
    "time_of_day": "02:00",
    "duration": "03:00",
    "reboot_setting": "IfRequired",
    "description": "Web server - patched weekly on Sunday at 2 AM"
  }
}
```

## Deployment Steps

```bash
cd "D:\DevOps\DTE\patching\personal_projects\dev\terraform"

# 1. Initialize
terraform init

# 2. Plan
terraform plan
# Shows:
# - VM import
# - Maintenance config creation
# - null_resource for patch mode (will run az vm update)
# - Maintenance assignment

# 3. Apply
terraform apply
# Executes in order:
# 1. Imports VM
# 2. Runs az vm update to set patch mode
# 3. Creates maintenance config
# 4. Assigns VM to maintenance config
```

## What Gets Configured

### VM Patch Settings (via Azure CLI)
- **Patch Mode**: `AutomaticByPlatform`
- **Assessment Mode**: `AutomaticByPlatform`
- **Bypass Safety Checks**: `true`
- **Reboot Setting**: `Never` (reboot controlled by maintenance config)

### Maintenance Schedule (from JSON)
- **Schedule**: Sunday at 2:00 AM CST
- **Duration**: 3 hours
- **Reboot**: IfRequired (from JSON config)
- **Classifications**: Critical, Security, UpdateRollup, etc.

## Key Points

✅ **Module patching DISABLED** - No interference from module  
✅ **All config in test-app-vm.tf** - Single source of truth  
✅ **Azure CLI for patch mode** - Sets VM properties after import  
✅ **JSON for schedules** - Easy to manage per-VM schedules  
✅ **Proper dependencies** - Ensures correct execution order  

## Verification

After `terraform apply`, verify:

```bash
# Check VM patch settings
az vm show \
  --ids "/subscriptions/.../virtualMachines/vmcuwinwebd01" \
  --query "osProfile.windowsConfiguration.patchSettings"

# Check maintenance assignment
az maintenance assignment list \
  --resource-group "rg-cu-CorpApps-MigrationTest-Dev" \
  --provider-name "Microsoft.Compute" \
  --resource-type "virtualMachines" \
  --resource-name "vmcuwinwebd01"
```

## Result

✅ VM imported into Terraform state  
✅ Patch mode configured via Azure CLI  
✅ Maintenance config created from JSON  
✅ VM assigned to patching schedule  
✅ VM will be patched every Sunday at 2:00 AM CST  

**Everything configured in test-app-vm.tf!** 🎉
