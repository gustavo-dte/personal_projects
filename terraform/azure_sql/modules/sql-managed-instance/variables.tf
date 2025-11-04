variable "managed_instance_name" {
  description = "Name of the SQL Managed Instance"
  type        = string
}

variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
}

variable "location" {
  description = "Azure region for the managed instance"
  type        = string
}

variable "administrator_login" {
  description = "Administrator login for SQL Managed Instance"
  type        = string
}

variable "administrator_login_password" {
  description = "Administrator password for SQL Managed Instance"
  type        = string
  sensitive   = true
}

# License and SKU Configuration
variable "license_type" {
  description = "License type - possible values: LicenseIncluded, BasePrice (Azure Hybrid Benefit)"
  type        = string
  default     = "LicenseIncluded"
  validation {
    condition     = contains(["LicenseIncluded", "BasePrice"], var.license_type)
    error_message = "License type must be either 'LicenseIncluded' or 'BasePrice'."
  }
}

variable "sku_name" {
  description = "SKU name - possible values: GP_Gen5, BC_Gen5, GP_Gen8IM, GP_Gen8IH, BC_Gen8IM, BC_Gen8IH"
  type        = string
  default     = "GP_Gen5"
  validation {
    condition = contains([
      "GP_Gen5", "BC_Gen5", "GP_Gen8IM", "GP_Gen8IH", "BC_Gen8IM", "BC_Gen8IH"
    ], var.sku_name)
    error_message = "Invalid SKU name. Must be one of: GP_Gen5, BC_Gen5, GP_Gen8IM, GP_Gen8IH, BC_Gen8IM, BC_Gen8IH."
  }
}

variable "vcores" {
  description = "Number of vCores for the managed instance (4, 8, 16, 24, 32, 40, 64, 80, or 128)"
  type        = number
  default     = 4
  validation {
    condition     = contains([4, 8, 16, 24, 32, 40, 64, 80, 128], var.vcores)
    error_message = "vCores must be one of: 4, 8, 16, 24, 32, 40, 64, 80, or 128."
  }
}

variable "storage_size_in_gb" {
  description = "Maximum storage size in GB (32 to 16384)"
  type        = number
  default     = 32
  validation {
    condition     = var.storage_size_in_gb >= 32 && var.storage_size_in_gb <= 16384
    error_message = "Storage size must be between 32 and 16384 GB."
  }
}

# Network Configuration
variable "subnet_id" {
  description = "ID of the subnet for the managed instance"
  type        = string
}

variable "dns_zone_partner_id" {
  description = "ID of the partner managed instance for DNS zone (for failover groups)"
  type        = string
  default     = null
}

# Database Configuration
variable "collation" {
  description = "Database collation"
  type        = string
  default     = "SQL_Latin1_General_CP1_CI_AS"
}

variable "timezone_id" {
  description = "Timezone ID for the managed instance"
  type        = string
  default     = "UTC"
}

# Public Endpoint
variable "public_data_endpoint_enabled" {
  description = "Enable public data endpoint"
  type        = bool
  default     = false
}

# Proxy Configuration
variable "proxy_override" {
  description = "Proxy override - possible values: Proxy, Redirect, Default"
  type        = string
  default     = "Proxy"
  validation {
    condition     = contains(["Proxy", "Redirect", "Default"], var.proxy_override)
    error_message = "Proxy override must be one of: Proxy, Redirect, or Default."
  }
}

# Security Configuration
variable "minimum_tls_version" {
  description = "Minimum TLS version - possible values: 1.0, 1.1, 1.2, 1.3"
  type        = string
  default     = "1.2"
  validation {
    condition     = contains(["1.0", "1.1", "1.2", "1.3"], var.minimum_tls_version)
    error_message = "Minimum TLS version must be one of: 1.0, 1.1, 1.2, or 1.3."
  }
}

# Storage Configuration
variable "storage_account_type" {
  description = "Storage account type - possible values: GRS, LRS, ZRS"
  type        = string
  default     = "GRS"
  validation {
    condition     = contains(["GRS", "LRS", "ZRS"], var.storage_account_type)
    error_message = "Storage account type must be one of: GRS, LRS, or ZRS."
  }
}

# Identity Configuration
variable "identity_type" {
  description = "Type of managed identity - possible values: SystemAssigned, UserAssigned, SystemAssigned, UserAssigned"
  type        = string
  default     = null
  validation {
    condition     = var.identity_type == null || contains(["SystemAssigned", "UserAssigned", "SystemAssigned, UserAssigned"], var.identity_type)
    error_message = "Identity type must be one of: SystemAssigned, UserAssigned, or 'SystemAssigned, UserAssigned'."
  }
}

variable "identity_ids" {
  description = "List of user assigned identity IDs"
  type        = list(string)
  default     = null
}

# Maintenance Configuration
variable "maintenance_configuration_name" {
  description = "Maintenance configuration name"
  type        = string
  default     = "SQL_Default"
}

# High Availability
variable "zone_redundant_enabled" {
  description = "Enable zone redundancy"
  type        = bool
  default     = false
}

# Azure AD Administrator
variable "azure_ad_admin" {
  description = "Azure AD administrator configuration"
  type = object({
    login_username              = string
    object_id                   = string
    tenant_id                   = optional(string)
    azuread_authentication_only = optional(bool, false)
  })
  default = null
}

# Transparent Data Encryption
variable "enable_tde" {
  description = "Enable Transparent Data Encryption with customer-managed key"
  type        = bool
  default     = false
}

variable "tde_key_vault_key_id" {
  description = "Key Vault Key ID for TDE (required if enable_tde is true)"
  type        = string
  default     = null
}

# Failover Group Configuration
variable "failover_group_config" {
  description = "Failover group configuration"
  type = object({
    name                        = string
    partner_managed_instance_id = string
    failover_policy_mode        = optional(string, "Automatic")
    grace_minutes               = optional(number, 60)
    readonly_endpoint_enabled   = optional(bool, false)
  })
  default = null
}

# Advanced Threat Protection
variable "enable_threat_detection" {
  description = "Enable Advanced Threat Protection"
  type        = bool
  default     = true
}

variable "threat_detection_policy" {
  description = "Threat detection policy configuration"
  type = object({
    retention_days             = optional(number, 30)
    disabled_alerts            = optional(list(string), [])
    email_account_admins       = optional(bool, true)
    email_addresses            = optional(list(string), [])
    storage_account_access_key = optional(string)
    storage_endpoint           = optional(string)
  })
  default = {
    retention_days       = 30
    email_account_admins = true
  }
}

# Vulnerability Assessment
variable "enable_vulnerability_assessment" {
  description = "Enable SQL Vulnerability Assessment"
  type        = bool
  default     = false
}

variable "vulnerability_assessment_config" {
  description = "Vulnerability assessment configuration"
  type = object({
    storage_container_path     = string
    storage_account_access_key = optional(string)
    recurring_scans = optional(object({
      enabled                   = optional(bool, true)
      email_subscription_admins = optional(bool, true)
      emails                    = optional(list(string), [])
    }))
  })
  default = null
}

# Tags
variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}
