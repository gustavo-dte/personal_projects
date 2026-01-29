# Terraform File Update - test-app-vm.tf

## Update Applied: 2025-01-29

### ✅ Copied Latest Changes from Main to Personal Projects

Latest fixes from the main branch have been copied to your personal projects directory.

### Source File:
`D:\DevOps\DTE\patching\cloud-platform-isolation-zone-subscription-corpapps\dev\terraform\test-app-vm.tf`

### Destination File:
`D:\DevOps\DTE\patching\corpapps\personal_projects\dev\terraform\test-app-vm.tf`

---

## Key Features in This File

### 1. **Patching Schedule Configuration**
- Loads patching schedules from `vm_patching_schedules.json`
- Creates unique maintenance configurations based on schedules
- Maps VMs to their respective maintenance configurations

```hcl
patching_schedules = fileexists("${path.module}/vm_patching_schedules.json") 
  ? jsondecode(file("${path.module}/vm_patching_schedules.json")) 
  : {}
```

### 2. **Maintenance Configuration Resources**
- Creates Azure Maintenance Configurations dynamically
- Properly sets `start_date_time` with time of day from JSON
- Configures patching windows with duration and frequency

```hcl
window {
  start_date_time = "2026-01-01 ${each.value.time_of_day}:00"
  duration        = each.value.duration
  time_zone       = "Central Standard Time"
  recur_every     = each.value.frequency == "Weekly" ? "Week ${each.value.day_of_week}" : "Day"
}
```

### 3. **Maintenance Assignment**
- Assigns VMs to their maintenance configurations
- Only assigns Windows VMs that have schedules defined
- Proper dependency management

```hcl
resource "azurerm_maintenance_assignment_virtual_machine" "vm_patching" {
  for_each = {
    for vm_key in keys(local.test_app_vms) : vm_key => vm_key
    if lower(local.test_app_vms[vm_key].disk.os.os_type) == "windows" 
       && contains(keys(local.vm_to_maintenance_config), vm_key)
  }
  # ...
}
```

### 4. **VM Configuration**
- Uses imported-vm-pattern module v1.0.7-alpha.2
- Enables periodic update assessment for Windows VMs
- Includes backup, monitoring, and alerting configuration

---

## What This Fixes

### ✅ Previous Issue (Now Fixed):
**Error:** `StartDateTime is not set for maintenance window`

**Root Cause:** Maintenance configurations were being created without proper start date/time

**Solution:** 
- Loads schedules from JSON file
- Sets `start_date_time` properly using the format: `"2026-01-01 ${time_of_day}:00"`
- Only creates maintenance configs when valid schedules exist

### ✅ How It Works Now:

1. **JSON Schedule File** (`vm_patching_schedules.json`):
```json
{
  "vmcuwinwebd01": {
    "maintenance_configuration": "weekly-sunday-2am",
    "time_of_day": "02:00",
    "day_of_week": "Sunday",
    "frequency": "Weekly",
    "duration": "03:00",
    "reboot_setting": "IfRequired",
    "description": "Weekly patching on Sunday at 2 AM"
  }
}
```

2. **Terraform creates maintenance config** with proper start_date_time
3. **VM is assigned** to the maintenance configuration
4. **No more errors** about missing StartDateTime

---

## Expected JSON File Structure

Create a file named `vm_patching_schedules.json` in the same directory as `test-app-vm.tf`:

```json
{
  "vm_name": {
    "maintenance_configuration": "schedule-name",
    "time_of_day": "HH:MM",
    "day_of_week": "Sunday|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday",
    "frequency": "Weekly|Daily",
    "duration": "HH:MM",
    "reboot_setting": "IfRequired|Always|Never",
    "description": "Schedule description"
  }
}
```

### Example:
```json
{
  "vmcuwinwebd01": {
    "maintenance_configuration": "weekly-sunday-2am",
    "time_of_day": "02:00",
    "day_of_week": "Sunday",
    "frequency": "Weekly",
    "duration": "03:00",
    "reboot_setting": "IfRequired",
    "description": "Weekly patching on Sunday at 2 AM"
  },
  "vmcuwinwebd02": {
    "maintenance_configuration": "weekly-sunday-3am",
    "time_of_day": "03:00",
    "day_of_week": "Sunday",
    "frequency": "Weekly",
    "duration": "03:00",
    "reboot_setting": "IfRequired",
    "description": "Weekly patching on Sunday at 3 AM"
  }
}
```

---

## Next Steps

1. ✅ File has been updated with latest fixes
2. ⚠️ **Create `vm_patching_schedules.json`** in the terraform directory
3. ⚠️ **Define patching schedules** for each VM
4. ✅ Run `terraform plan` to verify configuration
5. ✅ Run `terraform apply` to create maintenance configurations

---

## File Location

**Your Updated File:**
```
D:\DevOps\DTE\patching\corpapps\personal_projects\dev\terraform\test-app-vm.tf
```

**Create JSON Schedule File Here:**
```
D:\DevOps\DTE\patching\corpapps\personal_projects\dev\terraform\vm_patching_schedules.json
```

---

**Status:** ✅ Complete  
**Latest changes from main branch successfully copied to personal projects**
