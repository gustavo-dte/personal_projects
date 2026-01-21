# Windows Update Manager Integration Guide

## Overview
This module supports Azure Windows Update Manager integration through periodic update assessments.

## Quick Start

### Enable with Default Schedule (Daily at 2 AM)
```hcl
module "windows_vm" {
  source = "path/to/module"
  
  enable_periodic_update_assessment = true
  # Uses default: Daily at 02:00
}
```

### Enable with Custom Schedule
```hcl
module "windows_vm" {
  source = "path/to/module"
  
  enable_periodic_update_assessment = true
  patch_assessment_schedule = {
    frequency   = "Weekly"    # "Daily" or "Weekly"
    time_of_day = "03:30"     # HH:MM format (24-hour)
  }
}
```

## Configuration from Calling Repository

Your calling script should pass the patching configuration:

```hcl
# In calling repository
module "vm" {
  source = "app.terraform.io/org/imported-vm-pattern/azurerm"
  
  # Pass patching config from your variables
  enable_periodic_update_assessment = var.enable_patching
  patch_assessment_schedule         = var.patch_schedule
}
```

Define in your variables.tf:
```hcl
variable "enable_patching" {
  type    = bool
  default = true
}

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

## Important Notes
- Only applies to Windows VMs (automatically skipped for Linux)
- Time format: HH:MM (00:00 to 23:59)
- Frequency options: "Daily" or "Weekly"
