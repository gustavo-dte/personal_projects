variable "sql_server_id" {
  description = "ID of the SQL Server"
  type        = string
}

variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
}

variable "location" {
  description = "Azure region for resources"
  type        = string
}

variable "database_name" {
  description = "Name of the SQL Database"
  type        = string
}

variable "collation" {
  description = "Database collation"
  type        = string
  default     = "SQL_Latin1_General_CP1_CI_AS"
}

variable "license_type" {
  description = "License type for the database"
  type        = string
  default     = "LicenseIncluded"
}

variable "max_size_gb" {
  description = "Maximum size of the database in GB"
  type        = number
  default     = 32
}

variable "sku_name" {
  description = "SKU name for the database"
  type        = string
  default     = "S0"
}

variable "zone_redundant" {
  description = "Enable zone redundancy"
  type        = bool
  default     = false
}

variable "auto_pause_delay_in_minutes" {
  description = "Auto-pause delay in minutes for serverless databases"
  type        = number
  default     = 60
}

variable "min_capacity" {
  description = "Minimum capacity for serverless databases"
  type        = number
  default     = 0.5
}

variable "backup_policy" {
  description = "Backup policy configuration"
  type = object({
    retention_days               = optional(number, 7)
    geo_redundant_backup_enabled = optional(bool, true)
    geo_backup_enabled          = optional(bool, true)
  })
  default = {
    retention_days               = 7
    geo_redundant_backup_enabled = true
    geo_backup_enabled          = true
  }
}

variable "enable_threat_detection" {
  description = "Enable Advanced Threat Protection"
  type        = bool
  default     = true
}

variable "threat_detection_policy" {
  description = "Threat detection policy configuration"
  type = object({
    retention_days             = optional(number, 30)
    disabled_alerts           = optional(list(string), [])
    email_account_admins      = optional(bool, true)
    email_addresses           = optional(list(string), [])
    storage_account_access_key = optional(string)
    storage_endpoint          = optional(string)
  })
  default = {
    retention_days       = 30
    email_account_admins = true
  }
}

variable "enable_monitoring" {
  description = "Enable database monitoring"
  type        = bool
  default     = true
}

variable "log_analytics_workspace_id" {
  description = "Log Analytics workspace ID for monitoring"
  type        = string
  default     = null
}

variable "storage_account_id" {
  description = "Storage account ID for audit logs"
  type        = string
  default     = null
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}