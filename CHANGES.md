# Summary of Changes - Windows Update Manager Integration

## Overview
Updated the module to accept patching configuration parameters from calling repositories, making the Windows Update Manager integration flexible and configurable.

## Files Modified

### 1. variables.tf
**Added new variable**: `patch_assessment_schedule`

```terraform
variable "patch_assessment_schedule" {
  description = "Configuration for periodic update assessment schedule. Only applies when enable_periodic_update_assessment is true."
  type = object({
    frequency  = optional(string, "Daily")
    time_of_day = optional(string, "02:00")
  })
  default = {
    frequency  = "Daily"
    time_of_day = "02:00"
  }
  validation {
    condition     = contains(["Daily", "Weekly"], var.patch_assessment_schedule.frequency)
    error_message = "Frequency must be either 'Daily' or 'Weekly'."
  }
  validation {
    condition     = can(regex("^([0-1][0-9]|2[0-3]):[0-5][0-9]$", var.patch_assessment_schedule.time_of_day))
    error_message = "Time of day must be in HH:MM format (24-hour clock), e.g., '02:00' or '14:30'."
  }
}
```

**Purpose**: Allows calling repositories to specify custom patching schedules

### 2. vm.tf
**Updated**: Windows Update Assessment Extension settings

**Before**:
```terraform
settings = <<SETTINGS
  {
    "assessmentMode": "AutomaticByPlatform"
  }
SETTINGS
```

**After**:
```terraform
settings = jsonencode({
  assessmentMode = "AutomaticByPlatform"
  periodicUpdateAssessment = {
    enabled = true
    schedule = {
      frequency = var.patch_assessment_schedule.frequency
      timeOfDay = var.patch_assessment_schedule.time_of_day
    }
  }
})
```

**Purpose**: Dynamically applies the patching schedule from the variable

### 3. README.md
**Updated**: Added patching configuration to Example 1

**Before**:
```terraform
enable_periodic_update_assessment = true
```

**After**:
```terraform
enable_periodic_update_assessment = true
patch_assessment_schedule = {
  frequency   = "Daily"
  time_of_day = "02:00"
}
```

### 4. examples/example.tf
**Updated**: Same change as README.md for consistency

### 5. docs/patching.md
**Created**: New documentation file explaining:
- How to use the patching feature
- How calling repositories should pass configuration
- Configuration examples
- Important notes

## How It Works

### Module Flexibility
The module now accepts patching configuration as input parameters instead of hardcoding values:

1. **Calling repository** defines patching requirements in their variables
2. **Calling repository** passes these values to the module
3. **Module** validates and applies the configuration
4. **Extension** is deployed with the specified schedule

### Example Flow

**Step 1**: Calling repository defines variables
```terraform
variable "patch_schedule" {
  type = object({
    frequency   = string
    time_of_day = string
  })
  default = {
    frequency   = "Daily"
    time_of_day = "02:00"
  }
}
```

**Step 2**: Calling repository calls the module
```terraform
module "imported_vm" {
  source = "app.terraform.io/org/imported-vm-pattern/azurerm"
  
  enable_periodic_update_assessment = true
  patch_assessment_schedule         = var.patch_schedule
  
  # ... other parameters ...
}
```

**Step 3**: Module applies the configuration
The module receives the values and configures the Windows Update Extension accordingly.

## Validation

The module includes validation to ensure:
1. **Frequency** must be `"Daily"` or `"Weekly"`
2. **Time** must be in valid HH:MM format (00:00 to 23:59)

Invalid configurations will fail during `terraform plan` with clear error messages.

## Default Behavior

If `patch_assessment_schedule` is not provided:
- **Frequency**: Daily
- **Time**: 02:00 (2:00 AM)

This ensures backward compatibility while allowing customization.

## Linux VMs

The extension is automatically skipped for Linux VMs through the condition:
```terraform
count = var.enable_periodic_update_assessment && local.vm_os_type == "windows" ? 1 : 0
```

## Benefits

1. **Flexibility**: Calling repositories control their own patching schedules
2. **Reusability**: One module supports multiple patching strategies
3. **Validation**: Built-in checks prevent configuration errors
4. **Documentation**: Clear examples for users
5. **Defaults**: Sensible defaults reduce configuration burden
