# VM Patching Configuration - Complete Setup

## Overview

Patching is configured directly in the VM definition (`local.test_app_vms`). When the VM is imported, it will have patching settings already configured.

## Configuration Structure

### 1. VM Definition with Patch Settings

```terraform
local.test_app_vms = {
  vmcuwinwebd01 = {
    vm_name   = "vmcuwinwebd01"
    vm_size   = "Standard_D2s_v5"
    
    # ... network, disk, backup config ...
    
    # Patching configuration - applied during import
    patch_mode                                      = "AutomaticByPlatform"
    patch_assessment_mode                           = "AutomaticByPlatform"
    bypass_platform_safety_checks_on_user_schedule = true
    automatic_updates_enabled                       = false
  }
}
```

### 2. Module Call (Passes Patch Settings)

```terraform
module "test_app_vms" {
  source = "app.terraform.io/DTE-Cloud-Platform/imported-vm-pattern/azurerm"
  
  for_each = local.test_app_vms
  
  # Patching configuration (from VM definition)
  patch_mode                                      = try(each.value.patch_mode, null)
  patch_assessment_mode                           = try(each.value.patch_assessment_mode, null)
  bypass_platform_safety_checks_on_user_schedule = try(each.value.bypass_platform_safety_checks_on_user_schedule, null)
  automatic_updates_enabled                       = try(each.value.automatic_updates_enabled, null)
  
  # Module's patching is disabled
  enable_periodic_update_assessment = false
}
```

### 3. Maintenance Configuration (from JSON)

```terraform
resource "azurerm_maintenance_configuration" "vm_patching" {
  for_each = local.maintenance_config_settings  # From JSON
  
  name                     = each.key  # e.g., "weekly-sunday-2am"
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

### 4. Maintenance Assignment

```terraform
resource "azurerm_maintenance_assignment_virtual_machine" "vm_patching" {
  for_each = {
    for vm_key in keys(local.test_app_vms) : vm_key => vm_key
    if lower(local.test_app_vms[vm_key].disk.os.os_type) == "windows" && contains(keys(local.vm_to_maintenance_config), vm_key)
  }
  
  location                     = azurerm_resource_group.vm_migration_test.location
  maintenance_configuration_id = azurerm_maintenance_configuration.vm_patching["weekly-sunday-2am"].id
  virtual_machine_id           = module.test_app_vms[each.key].vm_id
  
  depends_on = [module.test_app_vms]
}
```

### 5. VM Import

```terraform
import {
  to = module.test_app_vms["vmcuwinwebd01"].azurerm_windows_virtual_machine.main[0]
  id = "/subscriptions/.../virtualMachines/vmcuwinwebd01"
}
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

## How It Works

### Import Flow:

```
1. terraform import
   ↓
2. VM imported with patch settings:
   - patch_mode = "AutomaticByPlatform"
   - patch_assessment_mode = "AutomaticByPlatform"  
   - bypass_platform_safety_checks_on_user_schedule = true
   - automatic_updates_enabled = false
   ↓
3. Maintenance config created from JSON
   ↓
4. VM assigned to maintenance schedule
   ↓
5. Done! VM will patch on schedule
```

### Key Points:

✅ **Patch settings in VM definition** - Part of `local.test_app_vms`  
✅ **No Azure CLI needed** - Module sets patch mode during import  
✅ **No null_resource** - Everything in Terraform  
✅ **Schedule from JSON** - Easy per-VM configuration  
✅ **Module patching disabled** - No interference  

## Deployment

```bash
cd "D:\DevOps\DTE\patching\personal_projects\dev\terraform"

# 1. Review the configuration
cat vm_patching_schedules.json

# 2. Initialize
terraform init

# 3. Plan - will show:
#    - VM import with patch settings
#    - Maintenance config creation
#    - Maintenance assignment
terraform plan

# 4. Apply - imports VM with patching configured
terraform apply
```

## What Gets Configured

### VM Patch Settings (in VM definition):
- **Patch Mode**: `AutomaticByPlatform`
- **Assessment Mode**: `AutomaticByPlatform`
- **Bypass Safety Checks**: `true`
- **Automatic Updates**: `false`

### Maintenance Schedule (from JSON):
- **Name**: `weekly-sunday-2am`
- **Schedule**: Sunday at 2:00 AM CST
- **Duration**: 3 hours
- **Reboot**: IfRequired
- **Classifications**: Critical, Security, UpdateRollup, etc.

## Adding More VMs

To add more VMs with patching:

1. **Add VM to `local.test_app_vms`**:
```terraform
vmcuwinwebd02 = {
  vm_name   = "vmcuwinwebd02"
  vm_size   = "Standard_D2s_v5"
  
  # Patching configuration
  patch_mode                                      = "AutomaticByPlatform"
  patch_assessment_mode                           = "AutomaticByPlatform"
  bypass_platform_safety_checks_on_user_schedule = true
  automatic_updates_enabled                       = false
  
  # ... other config ...
}
```

2. **Add schedule to JSON**:
```json
{
  "vmcuwinwebd02": {
    "maintenance_configuration": "weekly-sunday-2am",
    "frequency": "Weekly",
    "day_of_week": "Sunday",
    "time_of_day": "02:00",
    "duration": "03:00",
    "reboot_setting": "IfRequired",
    "description": "Web server 2"
  }
}
```

3. **Add import block**:
```terraform
import {
  to = module.test_app_vms["vmcuwinwebd02"].azurerm_windows_virtual_machine.main[0]
  id = "/subscriptions/.../virtualMachines/vmcuwinwebd02"
}
```

## Verification

After `terraform apply`, verify the configuration:

```bash
# Check VM patch settings
az vm show \
  --ids "/subscriptions/.../virtualMachines/vmcuwinwebd01" \
  --query "osProfile.windowsConfiguration.patchSettings"

# Expected output:
# {
#   "assessmentMode": "AutomaticByPlatform",
#   "automaticByPlatformSettings": {
#     "bypassPlatformSafetyChecksOnUserSchedule": true,
#     "rebootSetting": "Never"
#   },
#   "patchMode": "AutomaticByPlatform"
# }

# Check maintenance assignment
az maintenance assignment list \
  --resource-group "rg-cu-CorpApps-MigrationTest-Dev" \
  --provider-name "Microsoft.Compute" \
  --resource-type "virtualMachines" \
  --resource-name "vmcuwinwebd01"
```

## Result

✅ **Patch settings in VM definition** - Clean configuration  
✅ **Imported with patching enabled** - No post-import steps  
✅ **Schedule from JSON** - Easy to manage  
✅ **Maintenance config created** - From JSON  
✅ **VM assigned to schedule** - Automatic assignment  

**VM will be patched every Sunday at 2:00 AM CST!** 🎉
