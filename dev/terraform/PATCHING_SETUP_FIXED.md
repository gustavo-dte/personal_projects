# VM Patching Setup - Fixed

## Changes Made

### 1. ✅ Removed ARM Template Deployment
**Before** (Bad - using azurerm_resource_group_template_deployment):
```terraform
resource "azurerm_resource_group_template_deployment" "vm_patch_mode" {
  # ... ARM template JSON ...
}
```

**After** (Good - using native Terraform):
```terraform
# Patch mode is set by the module's enable_periodic_update_assessment
# No ARM template needed!
```

### 2. ✅ Fixed Resource Group and Location References
**Before** (Bad - hardcoded):
```terraform
resource_group_name = "rg-cu-CorpApps-MigrationTest-Dev"
location            = azurerm_resource_group.primary.location
```

**After** (Good - using correct resource):
```terraform
resource_group_name = azurerm_resource_group.vm_migration_test.name
location            = azurerm_resource_group.vm_migration_test.location
```

### 3. ✅ Enabled Patching in Module
**Before** (Bad - disabled):
```terraform
enable_periodic_update_assessment = false
```

**After** (Good - enabled for Windows VMs):
```terraform
enable_periodic_update_assessment = lower(each.value.disk.os.os_type) == "windows" ? true : false
```

### 4. ✅ Fixed Time Format
**Before**:
```terraform
start_date_time = "2026-01-01 ${each.value.time_of_day}"
```

**After**:
```terraform
start_date_time = "2026-01-01 ${each.value.time_of_day}:00"
```

## How It Works Now

### Phase 1: Create Maintenance Configuration
```terraform
resource "azurerm_maintenance_configuration" "vm_patching" {
  name                     = "weekly-sunday-2am"
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

### Phase 2: VM Module Sets Patch Mode
The module (`enable_periodic_update_assessment = true`) sets:
- `patch_mode = "AutomaticByPlatform"`
- `patch_assessment_mode = "AutomaticByPlatform"`
- `bypass_platform_safety_checks_on_user_schedule_enabled = true`

### Phase 3: Assign VM to Maintenance Config
```terraform
resource "azurerm_maintenance_assignment_virtual_machine" "vm_patching" {
  location                     = azurerm_resource_group.vm_migration_test.location
  maintenance_configuration_id = azurerm_maintenance_configuration.vm_patching["weekly-sunday-2am"].id
  virtual_machine_id           = module.test_app_vms["vmcuwinwebd01"].vm_id
}
```

### Phase 4: Import VM into State
```terraform
import {
  to = module.test_app_vms["vmcuwinwebd01"].azurerm_windows_virtual_machine.main[0]
  id = "/subscriptions/.../virtualMachines/vmcuwinwebd01"
}
```

## Deployment Workflow

```bash
cd "D:\DevOps\DTE\patching\personal_projects\dev\terraform"

# 1. Initialize
terraform init

# 2. Plan (will show import + patching config)
terraform plan

# 3. Apply (creates maintenance config, enables patching, assigns VM, imports VM)
terraform apply
```

## What Gets Created

1. **Maintenance Configuration**: `weekly-sunday-2am`
   - Window: Sunday 2:00 AM CST
   - Duration: 3 hours
   - Reboot: IfRequired
   - Classifications: Critical, Security, etc.

2. **VM Patch Settings** (via module):
   - Patch mode: AutomaticByPlatform
   - Assessment mode: AutomaticByPlatform
   - Bypass safety checks: true

3. **Maintenance Assignment**: Links VM to schedule

4. **VM Import**: Brings existing VM into Terraform state

## Key Files

- **test-app-vm.tf**: VM definition and patching config
- **vm_patching_schedules.json**: Schedule configuration
- **main.tf**: Resource group definition (`vm_migration_test`)

## Result

✅ No ARM templates  
✅ Correct resource group references  
✅ Patching enabled via module  
✅ Schedule from JSON  
✅ VM imported with patching configured  

The VM will now be patched every Sunday at 2 AM CST according to the schedule!
