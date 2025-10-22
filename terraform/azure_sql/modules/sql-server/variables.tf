variable "sql_server_name" {
  description = "Name of the SQL Server"
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

variable "sql_server_version" {
  description = "Version of SQL Server"
  type        = string
  default     = "12.0"
}

variable "administrator_login" {
  description = "Administrator login for SQL Server"
  type        = string
}

variable "administrator_login_password" {
  description = "Administrator password for SQL Server"
  type        = string
  sensitive   = true
}

variable "firewall_rules" {
  description = "List of firewall rules"
  type = list(object({
    name             = string
    start_ip_address = string
    end_ip_address   = string
  }))
  default = []
}

variable "allow_azure_services" {
  description = "Allow Azure services to access the server"
  type        = bool
  default     = true
}

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