# ============================================================================
# GENERAL VARIABLES
# ============================================================================

variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
}

variable "location" {
  description = "Azure region for resources"
  type        = string
  default     = "eastus"
}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default     = {}
}

# ============================================================================
# NETWORKING VARIABLES
# ============================================================================

variable "vnet_address_space" {
  description = "Address space for the virtual network"
  type        = string
  default     = "10.0.0.0/16"
}

variable "subnet_address_prefix" {
  description = "Address prefix for SQL MI subnet (minimum /28, recommended /27 or larger)"
  type        = string
  default     = "10.0.1.0/24"
}

# ============================================================================
# SQL MANAGED INSTANCE VARIABLES
# ============================================================================

variable "managed_instance_name" {
  description = "Name of the SQL Managed Instance"
  type        = string
}

variable "administrator_login" {
  description = "Administrator username for SQL Managed Instance"
  type        = string
  default     = "sqladmin"
}

variable "administrator_login_password" {
  description = "Administrator password (leave null to auto-generate)"
  type        = string
  sensitive   = true
  default     = null
}

# ============================================================================
# PERFORMANCE VARIABLES
# ============================================================================

variable "sku_name" {
  description = "SKU name (GP_Gen5, BC_Gen5, GP_Gen8IM, GP_Gen8IH, BC_Gen8IM, BC_Gen8IH)"
  type        = string
  default     = "GP_Gen5"
  validation {
    condition = contains([
      "GP_Gen5", "BC_Gen5", "GP_Gen8IM", "GP_Gen8IH", "BC_Gen8IM", "BC_Gen8IH"
    ], var.sku_name)
    error_message = "Invalid SKU. Must be: GP_Gen5, BC_Gen5, GP_Gen8IM, GP_Gen8IH, BC_Gen8IM, or BC_Gen8IH."
  }
}

variable "vcores" {
  description = "Number of vCores (4, 8, 16, 24, 32, 40, 64, 80, 128)"
  type        = number
  default     = 8
  validation {
    condition     = contains([4, 8, 16, 24, 32, 40, 64, 80, 128], var.vcores)
    error_message = "vCores must be: 4, 8, 16, 24, 32, 40, 64, 80, or 128."
  }
}

variable "storage_size_in_gb" {
  description = "Storage size in GB (32-16384)"
  type        = number
  default     = 256
  validation {
    condition     = var.storage_size_in_gb >= 32 && var.storage_size_in_gb <= 16384
    error_message = "Storage must be between 32 and 16384 GB."
  }
}

variable "license_type" {
  description = "License type: LicenseIncluded or BasePrice (Azure Hybrid Benefit - 55% savings)"
  type        = string
  default     = "LicenseIncluded"
  validation {
    condition     = contains(["LicenseIncluded", "BasePrice"], var.license_type)
    error_message = "License type must be LicenseIncluded or BasePrice."
  }
}

variable "storage_account_type" {
  description = "Storage account type (GRS, LRS, ZRS)"
  type        = string
  default     = "GRS"
  validation {
    condition     = contains(["GRS", "LRS", "ZRS"], var.storage_account_type)
    error_message = "Storage type must be GRS, LRS, or ZRS."
  }
}

# ============================================================================
# DATABASE CONFIGURATION VARIABLES
# ============================================================================

variable "collation" {
  description = "Default collation for the instance"
  type        = string
  default     = "SQL_Latin1_General_CP1_CI_AS"
}

variable "timezone_id" {
  description = "Timezone ID for the instance"
  type        = string
  default     = "UTC"
}

# ============================================================================
# SECURITY VARIABLES
# ============================================================================

variable "minimum_tls_version" {
  description = "Minimum TLS version (1.0, 1.1, 1.2)"
  type        = string
  default     = "1.2"
  validation {
    condition     = contains(["1.0", "1.1", "1.2"], var.minimum_tls_version)
    error_message = "TLS version must be 1.0, 1.1, or 1.2."
  }
}

variable "public_data_endpoint_enabled" {
  description = "Enable public data endpoint (not recommended for production)"
  type        = bool
  default     = false
}

variable "proxy_override" {
  description = "Connection policy (Proxy, Redirect, Default)"
  type        = string
  default     = "Proxy"
  validation {
    condition     = contains(["Proxy", "Redirect", "Default"], var.proxy_override)
    error_message = "Proxy override must be Proxy, Redirect, or Default."
  }
}

variable "identity_type" {
  description = "Type of managed identity (SystemAssigned, UserAssigned)"
  type        = string
  default     = "SystemAssigned"
  validation {
    condition     = contains(["SystemAssigned", "UserAssigned"], var.identity_type)
    error_message = "Identity type must be SystemAssigned or UserAssigned."
  }
}

# ============================================================================
# AZURE AD AUTHENTICATION VARIABLES
# ============================================================================

variable "enable_azure_ad_auth" {
  description = "Enable Azure AD authentication"
  type        = bool
  default     = false
}

variable "azure_ad_admin_login" {
  description = "Azure AD admin login name"
  type        = string
  default     = ""
}

variable "azure_ad_admin_object_id" {
  description = "Azure AD admin object ID"
  type        = string
  default     = ""
}

variable "azure_ad_admin_tenant_id" {
  description = "Azure AD tenant ID (leave null to use current)"
  type        = string
  default     = null
}

# ============================================================================
# THREAT DETECTION VARIABLES
# ============================================================================

variable "enable_threat_detection" {
  description = "Enable Advanced Threat Protection"
  type        = bool
  default     = true
}

variable "threat_detection_retention_days" {
  description = "Threat detection log retention in days"
  type        = number
  default     = 90
}

variable "threat_detection_email_admins" {
  description = "Send threat alerts to admins"
  type        = bool
  default     = true
}

variable "threat_detection_email_addresses" {
  description = "Email addresses for threat alerts"
  type        = list(string)
  default     = []
}

# ============================================================================
# AUDITING VARIABLES
# ============================================================================

variable "enable_auditing" {
  description = "Enable SQL auditing"
  type        = bool
  default     = true
}

# ============================================================================
# VULNERABILITY ASSESSMENT VARIABLES
# ============================================================================

variable "enable_vulnerability_assessment" {
  description = "Enable vulnerability assessment"
  type        = bool
  default     = false
}

# ============================================================================
# HIGH AVAILABILITY VARIABLES
# ============================================================================

variable "zone_redundant_enabled" {
  description = "Enable zone redundancy"
  type        = bool
  default     = false
}

variable "maintenance_configuration_name" {
  description = "Maintenance window configuration"
  type        = string
  default     = "SQL_Default"
}
