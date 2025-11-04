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
# SQL SERVER VARIABLES
# ============================================================================

variable "sql_server_name" {
  description = "Name of the SQL Server (must be globally unique)"
  type        = string
}

variable "sql_server_version" {
  description = "Version of SQL Server (12.0 = SQL Server 2014, 12.0 is recommended)"
  type        = string
  default     = "12.0"
}

variable "administrator_login" {
  description = "Administrator username for SQL Server"
  type        = string
  default     = "sqladmin"
}

variable "administrator_login_password" {
  description = "Administrator password for SQL Server (leave null to auto-generate)"
  type        = string
  sensitive   = true
  default     = null
}

variable "minimum_tls_version" {
  description = "Minimum TLS version (1.0, 1.1, 1.2)"
  type        = string
  default     = "1.2"
  validation {
    condition     = contains(["1.0", "1.1", "1.2"], var.minimum_tls_version)
    error_message = "Minimum TLS version must be 1.0, 1.1, or 1.2."
  }
}

# ============================================================================
# FIREWALL VARIABLES
# ============================================================================

variable "firewall_rules" {
  description = "List of firewall rules to create"
  type = list(object({
    name             = string
    start_ip_address = string
    end_ip_address   = string
  }))
  default = []
}

variable "allow_azure_services" {
  description = "Allow Azure services to access the SQL Server"
  type        = bool
  default     = true
}

# ============================================================================
# DATABASE VARIABLES
# ============================================================================

variable "databases" {
  description = "Map of databases to create"
  type = map(object({
    name                        = string
    collation                   = optional(string, "SQL_Latin1_General_CP1_CI_AS")
    license_type                = optional(string, "LicenseIncluded")
    max_size_gb                 = optional(number, 32)
    sku_name                    = optional(string, "S0")
    zone_redundant              = optional(bool, false)
    auto_pause_delay_in_minutes = optional(number, 60)
    min_capacity                = optional(number, 0.5)
  }))
  default = {}
}

# ============================================================================
# BACKUP VARIABLES
# ============================================================================

variable "backup_retention_days" {
  description = "Point-in-time restore retention period in days (7-35)"
  type        = number
  default     = 7
  validation {
    condition     = var.backup_retention_days >= 7 && var.backup_retention_days <= 35
    error_message = "Backup retention must be between 7 and 35 days."
  }
}

variable "long_term_retention_weekly" {
  description = "Weekly long-term retention (e.g., P4W for 4 weeks)"
  type        = string
  default     = "P1W"
}

variable "long_term_retention_monthly" {
  description = "Monthly long-term retention (e.g., P12M for 12 months)"
  type        = string
  default     = "P1M"
}

variable "long_term_retention_yearly" {
  description = "Yearly long-term retention (e.g., P5Y for 5 years)"
  type        = string
  default     = "P1Y"
}

variable "long_term_retention_week_of_year" {
  description = "Week of year for yearly long-term retention backup"
  type        = number
  default     = 1
  validation {
    condition     = var.long_term_retention_week_of_year >= 1 && var.long_term_retention_week_of_year <= 52
    error_message = "Week of year must be between 1 and 52."
  }
}

# ============================================================================
# SECURITY VARIABLES
# ============================================================================

variable "enable_threat_detection" {
  description = "Enable Advanced Threat Protection"
  type        = bool
  default     = true
}

variable "threat_detection_retention_days" {
  description = "Threat detection log retention in days"
  type        = number
  default     = 30
}

variable "threat_detection_email_admins" {
  description = "Send threat detection alerts to admins"
  type        = bool
  default     = true
}

variable "threat_detection_email_addresses" {
  description = "Email addresses to receive threat detection alerts"
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

variable "audit_retention_days" {
  description = "Audit log retention in days"
  type        = number
  default     = 90
}

# ============================================================================
# MONITORING VARIABLES
# ============================================================================

variable "enable_monitoring" {
  description = "Enable monitoring with Log Analytics"
  type        = bool
  default     = true
}

variable "log_retention_days" {
  description = "Log Analytics retention period in days"
  type        = number
  default     = 90
  validation {
    condition     = var.log_retention_days >= 30 && var.log_retention_days <= 730
    error_message = "Log retention must be between 30 and 730 days."
  }
}
