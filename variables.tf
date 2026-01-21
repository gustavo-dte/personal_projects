# Variables for imported VM module (Windows/Linux)

variable "user_assigned_identity_resource_id" {
  description = "Resource ID of the existing User Assigned Identity to import (optional)"
  type        = string
  default     = null
}

variable "vm_name" {
  description = "The name of the VM"
  type        = string
}

variable "resource_group_name" {
  description = "The name of the resource group"
  type        = string
}

variable "location" {
  description = "Primary Azure location or region"
  type        = string
  validation {
    condition     = can(regex("^[a-z0-9]+$", var.location))
    error_message = "Location must be a valid Azure region name (lowercase, no spaces)."
  }
}

variable "vm_size" {
  description = "The size of the VM"
  type        = string
  default     = "Standard_B2s"
  validation {
    condition     = can(regex("^Standard_[A-Za-z0-9_]+$", var.vm_size))
    error_message = "VM size must be a valid Azure VM SKU (e.g., Standard_B2s, Standard_D2s_v5)."
  }
}

## Network configuration (nested)
variable "network" {
  description = "Network configuration: NIC, subnet, optional NSG create/import and rules"
  type = object({
    nic_name                  = string
    subnet_id                 = string
    network_security_group_id = optional(string)
    enable_nsg                = optional(bool, false)
    nsg_name                  = optional(string)
    nsg_rules = optional(map(object({
      priority                   = number
      direction                  = string
      access                     = string
      protocol                   = string
      source_port_range          = optional(string)
      destination_port_range     = optional(string)
      source_address_prefixes    = optional(list(string))
      destination_address_prefix = optional(string)
    })), {})
  })
}

## Disk configuration (nested)
variable "disk" {
  description = "Disk configuration: OS disk details and data disks map"
  type = object({
    os = object({
      name                 = string
      size_gb              = number
      storage_account_type = string
      caching              = string
      create_option        = string
      os_type              = string
    })
    data = map(object({
      lun                       = number
      caching                   = string
      write_accelerator_enabled = bool
      resource_id               = string
      disk_size_gb              = number
      storage_account_type      = string
    }))
  })
}

# Identity Configuration
variable "identity" {
  description = "Identity configuration for the VM"
  type = object({
    type         = string
    identity_ids = optional(list(string), [])
  })
  default = {
    type         = "None"
    identity_ids = []
  }
  validation {
    condition     = contains(["None", "SystemAssigned", "UserAssigned", "SystemAssigned, UserAssigned"], var.identity.type)
    error_message = "Identity type must be one of: None, SystemAssigned, UserAssigned, or 'SystemAssigned, UserAssigned'"
  }
}

variable "user_assigned_identity_name" {
  description = "Name of the user assigned identity"
  type        = string
  default     = null
}

# Security Features
variable "security_features" {
  description = "Security features for Trusted Launch"
  type = object({
    secure_boot_enabled = optional(bool, false)
    vtpm_enabled        = optional(bool, false)
  })
  default = {
    secure_boot_enabled = false
    vtpm_enabled        = false
  }
}

# VM Configuration
variable "provision_vm_agent" {
  description = "Specifies whether the VM Agent should be provisioned on the Virtual Machine."
  type        = bool
  default     = true
}

variable "custom_data" {
  description = "The custom data to be used for the VM. Must be base64 encoded."
  type        = string
  default     = ""
}

variable "boot_diagnostics_uri" {
  description = "The storage account URI for boot diagnostics"
  type        = string
  default     = null
}

variable "availability_zone" {
  description = "The availability zone where the VM should be created. Must be 1, 2, or 3. Leave null for no zone placement."
  type        = string
  default     = null
  validation {
    condition     = var.availability_zone == null ? true : contains(["1", "2", "3"], tostring(var.availability_zone))
    error_message = "Availability zone must be null, '1', '2', or '3'."
  }
}

# VM Extensions
variable "vm_extension_name" {
  description = "Name of the VM extension"
  type        = string
  default     = null
}

variable "vm_extension_publisher" {
  description = "Publisher of the VM extension"
  type        = string
  default     = "Microsoft.Compute"
}

variable "vm_extension_type" {
  description = "Type of the VM extension"
  type        = string
  default     = "CustomScriptExtension"
}

variable "vm_extension_type_handler_version" {
  description = "Type handler version of the VM extension"
  type        = string
  default     = "1.10"
}

variable "vm_extension_auto_upgrade_minor_version" {
  description = "Auto upgrade minor version for VM extension"
  type        = bool
  default     = true
}

variable "vm_extension_settings" {
  description = "Settings for the VM extension"
  type        = any
  default     = {}
}

variable "vm_extension_protected_settings" {
  description = "Protected settings for the VM extension"
  type        = any
  default     = {}
  sensitive   = true
}

# Windows Update Assessment
variable "enable_periodic_update_assessment" {
  description = "Enable periodic assessment for OS guest updates using Windows Update Extension."
  type        = bool
  default     = false
}

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

# Domain Join Configuration
variable "enable_domain_join" {
  description = "Enable Azure AD Domain Services join for the VM"
  type        = bool
  default     = false
}

variable "domain_name" {
  description = "Azure AD Domain Services domain name (e.g., aaddscontoso.com). Should be provided via Terraform Cloud global variable."
  type        = string
  default     = ""
}

variable "domain_join_service_user" {
  description = "Domain service account for joining VMs (format: user@domain.com). Should be provided via Terraform Cloud global variable."
  type        = string
  sensitive   = true
  default     = ""
}

variable "domain_join_password" {
  description = "Password for the domain service account. Should be provided via Terraform Cloud global variable."
  type        = string
  sensitive   = true
  default     = ""
}

variable "target_ou" {
  description = "Target OU DN for computer account. Defaults to Build OU for initial deployment."
  type        = string
  default     = "OU=Build,OU=Windows,OU=CloudPlatform,OU=Servers,DC=dtenet,DC=com"
}

variable "tags" {
  description = "Tags to be applied to all resources. Azure policies may require certain tags to be present."
  type        = map(string)
  default     = {}

  validation {
    condition = alltrue([
      for k, v in var.tags : can(regex("^[^<>%&\\?/]*$", k)) && can(regex("^[^<>%&\\?/]*$", v))
    ])
    error_message = "Tag keys and values cannot contain characters: < > % & \\ ? /"
  }
}

# Optional VMSS (Flexible) Import Anchor
variable "vm_os_type" {
  description = "Operating system type for the VM and optional VMSS. One of: windows, linux."
  type        = string
  default     = "windows"
  validation {
    condition     = contains(["windows", "linux"], lower(var.vm_os_type))
    error_message = "vm_os_type must be either 'windows' or 'linux'"
  }
}

variable "enable_vmss" {
  description = "Enable Flexible VMSS import anchor and link VM to VMSS."
  type        = bool
  default     = false
}

variable "vmss_name" {
  description = "Name of the existing VMSS (must match the imported resource)."
  type        = string
  default     = null
}

variable "vmss_sku" {
  description = "SKU of the VMSS. Used to satisfy provider schema during import."
  type        = string
  default     = "Standard_DS1_v2"
}

variable "vmss_instances" {
  description = "Number of instances for the VMSS (schema requirement; ignored after import)."
  type        = number
  default     = 0
}

variable "vmss_admin_username" {
  description = "Admin username required by VMSS schema (placeholder; not used after import)."
  type        = string
  default     = "azureuser"
}

variable "vmss_admin_password" {
  description = "Admin password required by VMSS schema (placeholder; not used after import)."
  type        = string
  sensitive   = true
  default     = "Placeholder-Password1!"
}

# Linux VM configuration
variable "linux_admin_username" {
  description = "Admin username for Linux VM (schema requirement when not attaching by image)."
  type        = string
  default     = "azureuser"
}

variable "linux_disable_password_authentication" {
  description = "Disable password authentication for Linux VM (use SSH keys)."
  type        = bool
  default     = true
}

variable "linux_admin_ssh_public_key" {
  description = "SSH public key for Linux VM when password auth is disabled."
  type        = string
  default     = null
}

variable "linux_admin_password" {
  description = "Admin password for Linux VM when password auth is enabled."
  type        = string
  sensitive   = true
  default     = null
}

# VMSS Image configuration (schema requirements for import)
variable "vmss_image_publisher" {
  description = "Publisher for VMSS source_image_reference"
  type        = string
  default     = "MicrosoftWindowsServer"
}

variable "vmss_image_offer" {
  description = "Offer for VMSS source_image_reference"
  type        = string
  default     = "WindowsServer"
}

variable "vmss_image_sku" {
  description = "SKU for VMSS source_image_reference"
  type        = string
  default     = "2022-datacenter-g2"
}

variable "vmss_image_version" {
  description = "Version for VMSS source_image_reference"
  type        = string
  default     = "latest"
}

# VMSS OS disk configuration (schema requirements for import)
variable "vmss_os_disk_storage_account_type" {
  description = "Storage account type for VMSS OS disk"
  type        = string
  default     = "Standard_LRS"
}

variable "vmss_os_disk_caching" {
  description = "Caching mode for VMSS OS disk"
  type        = string
  default     = "ReadWrite"
}

# Backup configuration
variable "enable_backup" {
  description = "Enable backup for the VM"
  type        = bool
  default     = false
}

variable "backup_vault_resource_group_name" {
  description = "Resource Group Name of the Backup Vault"
  type        = string
}

variable "backup_vault_name" {
  description = "Name of the Backup Vault"
  type        = string
}

variable "backup_vault_policy_name" {
  description = "Backup Vault Policy Name"
  type        = string
}
