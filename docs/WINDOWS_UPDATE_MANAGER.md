# Windows Update Manager Integration

## Overview

This module supports integration with Azure Windows Update Manager through periodic update assessments. When enabled, the VM will be registered with Azure Update Manager to track and manage Windows updates.

## How It Works

The module uses the `azurerm_virtual_machine_extension` resource to deploy the Windows Update Extension, which enables:
- Automatic periodic assessment of available Windows updates
- Integration with Azure Update Manager
- Configurable assessment schedules

## Configuration

### Required Parameters

To enable Windows Update Manager integration, set the following in your module call:

```hcl
module "windows_vm" {
  source = "path/to/module"
  
  # ... other required parameters ...
  
  # Enable Windows Update Assessment
  enable_periodic_update_assessment = true
}
```

### Optional: Custom Assessment Schedule

By default, the module will assess updates **daily at 02:00 (2:00 AM)**. You can customize this schedule:

```hcl
module "windows_vm" {
  source = "path/to/module"
  
  # ... other required parameters ...
  
  # Enable Windows Update Assessment with custom schedule
  enable_periodic_update_assessment = true
  
  patch_assessment_schedule = {
    frequency   = "Daily"     # Options: "Daily" or "Weekly"
    time_of_day = "03:30"     # Time in HH:MM format (24-hour clock)
  }
}
```

### Schedule Configuration Options

#### Frequency
- **`Daily`**: Assessment runs every day
- **`Weekly`**: Assessment runs once per week

#### Time of Day
- Format: `"HH:MM"` (24-hour clock)
- Examples:
  - `"02:00"` - 2:00 AM
  - `"14:30"` - 2:30 PM
  - `"23:45"` - 11:45 PM

### Validation Rules

The module includes built-in validation:

1. **Frequency**: Must be either `"Daily"` or `"Weekly"`
2. **Time of Day**: Must be in valid `HH:MM` format with:
   - Hours: `00` to `23`
   - Minutes: `00` to `59`

## Examples

### Example 1: Default Schedule (Daily at 2 AM)

```hcl
module "windows_vm_default_schedule" {
  source = "app.terraform.io/your-org/imported-vm-pattern/azurerm"
  
  vm_name             = "vm-windows-prod-01"
  resource_group_name = "rg-production"
  location            = "eastus"
  vm_os_type          = "windows"
  
  # Enable with default schedule
  enable_periodic_update_assessment = true
  
  # ... other required parameters ...
}
```

This will configure:
- Assessment frequency: Daily
- Assessment time: 02:00 (2:00 AM)

### Example 2: Custom Schedule (Weekly at 3:30 AM)

```hcl
module "windows_vm_custom_schedule" {
  source = "app.terraform.io/your-org/imported-vm-pattern/azurerm"
  
  vm_name             = "vm-windows-prod-02"
  resource_group_name = "rg-production"
  location            = "eastus"
  vm_os_type          = "windows"
  
  # Enable with custom schedule
  enable_periodic_update_assessment = true
  patch_assessment_schedule = {
    frequency   = "Weekly"
    time_of_day = "03:30"
  }
  
  # ... other required parameters ...
}
```

This will configure:
- Assessment frequency: Weekly
- Assessment time: 03:30 (3:30 AM)

### Example 3: Multiple VMs with Different Schedules

```hcl
# Production VMs - Daily assessments at night
module "windows_vm_production" {
  source = "app.terraform.io/your-org/imported-vm-pattern/azurerm"
  
  for_each = toset(["vm-prod-01", "vm-prod-02", "vm-prod-03"])
  
  vm_name             = each.value
  resource_group_name = "rg-production"
  location            = "eastus"
  vm_os_type          = "windows"
  
  enable_periodic_update_assessment = true
  patch_assessment_schedule = {
    frequency   = "Daily"
    time_of_day = "02:00"
  }
  
  # ... other required parameters ...
}

# Development VMs - Weekly assessments
module "windows_vm_development" {
  source = "app.terraform.io/your-org/imported-vm-pattern/azurerm"
  
  for_each = toset(["vm-dev-01", "vm-dev-02"])
  
  vm_name             = each.value
  resource_group_name = "rg-development"
  location            = "eastus"
  vm_os_type          = "windows"
  
  enable_periodic_update_assessment = true
  patch_assessment_schedule = {
    frequency   = "Weekly"
    time_of_day = "04:00"
  }
  
  # ... other required parameters ...
}
```

## Important Notes

### Linux VMs
This feature is **only available for Windows VMs**. The extension will not be deployed for Linux VMs, even if `enable_periodic_update_assessment` is set to `true`.

The module automatically checks the OS type:
```terraform
count = var.enable_periodic_update_assessment && local.vm_os_type == "windows" ? 1 : 0
```

### Calling Repository Configuration
When calling this module from another repository, ensure you pass the patching configuration from your calling script:

```hcl
# In your calling repository
module "vm_from_shared_module" {
  source = "app.terraform.io/your-org/imported-vm-pattern/azurerm"
  
  # VM configuration
  vm_name     = var.vm_name
  vm_os_type  = "windows"
  # ... other parameters ...
  
  # Pass patching configuration from your repository's variables
  enable_periodic_update_assessment = var.enable_windows_patching
  patch_assessment_schedule         = var.patching_schedule
}
```

Then define these variables in your calling repository:
```hcl
# In your calling repository's variables.tf
variable "enable_windows_patching" {
  description = "Enable Windows Update Manager for VMs"
  type        = bool
  default     = true
}

variable "patching_schedule" {
  description = "Schedule for Windows update assessments"
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

## Technical Details

### Extension Settings
The module configures the Windows Update Extension with the following settings:

```json
{
  "assessmentMode": "AutomaticByPlatform",
  "periodicUpdateAssessment": {
    "enabled": true,
    "schedule": {
      "frequency": "Daily",
      "timeOfDay": "02:00"
    }
  }
}
```

### Extension Details
- **Publisher**: `Microsoft.Azure.Monitor`
- **Type**: `WindowsUpdateExtension`
- **Version**: `1.0`
- **Name**: `WindowsUpdateAssessment`

## Troubleshooting

### Extension Not Deploying
1. Verify `enable_periodic_update_assessment = true`
2. Verify `vm_os_type = "windows"`
3. Check if the VM agent is enabled: `provision_vm_agent = true`

### Invalid Schedule Format
If you receive validation errors:
- Ensure frequency is exactly `"Daily"` or `"Weekly"` (case-sensitive)
- Ensure time format is `"HH:MM"` with valid hours (00-23) and minutes (00-59)
- Examples of valid times: `"00:00"`, `"12:30"`, `"23:59"`
- Examples of invalid times: `"24:00"`, `"12:60"`, `"2:00"`, `"12:5"`

## References

- [Azure Update Manager Documentation](https://learn.microsoft.com/en-us/azure/update-manager/)
- [VM Extensions Overview](https://learn.microsoft.com/en-us/azure/virtual-machines/extensions/overview)
