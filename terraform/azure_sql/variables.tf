# Azure Authentication
variable "azure_subscription_id" {
  description = "Azure Subscription ID"
  type        = string
  sensitive   = true
}

variable "azure_tenant_id" {
  description = "Azure Tenant ID"
  type        = string
  sensitive   = true
}

variable "azure_client_id" {
  description = "Azure Client ID"
  type        = string
  sensitive   = true
}

variable "azure_client_secret" {
  description = "Azure Client Secret"
  type        = string
  sensitive   = true
}

# Environment Configuration
variable "environment" {
  description = "Environment name"
  type        = string
  default     = "Production"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "SQL-Database"
}

variable "resource_owner" {
  description = "Resource owner"
  type        = string
  default     = "Platform Team"
}

# Resource Configuration
variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
}

variable "azure_location" {
  description = "Azure region for resources"
  type        = string
  default     = "East US"
}

# SQL Server Configuration
variable "sql_server_name" {
  description = "Name of the SQL Server"
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
  default     = "sqladmin"
}

variable "administrator_login_password" {
  description = "Administrator password for SQL Server"
  type        = string
  sensitive   = true
}

# SQL Database Configuration
variable "sql_databases" {
  description = "List of SQL databases to create"
  type = list(object({
    name                        = string
    collation                   = optional(string, "SQL_Latin1_General_CP1_CI_AS")
    license_type               = optional(string, "LicenseIncluded")
    max_size_gb                = optional(number, 32)
    sku_name                   = optional(string, "S0")
    zone_redundant             = optional(bool, false)
    auto_pause_delay_in_minutes = optional(number, 60)
    min_capacity               = optional(number, 0.5)
  }))
  default = []
}

# Security Configuration
variable "firewall_rules" {
  description = "List of firewall rules"
  type = list(object({
    name             = string
    start_ip_address = string
    end_ip_address   = string
  }))
  default = [
    {
      name             = "AllowAzureServices"
      start_ip_address = "0.0.0.0"
      end_ip_address   = "0.0.0.0"
    }
  ]
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

# Backup Configuration
variable "backup_policy" {
  description = "Backup policy configuration"
  type = object({
    retention_days                = optional(number, 7)
    geo_redundant_backup_enabled  = optional(bool, true)
    geo_backup_enabled           = optional(bool, true)
  })
  default = {
    retention_days               = 7
    geo_redundant_backup_enabled = true
    geo_backup_enabled          = true
  }
}

# Monitoring Configuration
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

# Tagging
variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default = {
    Environment = "Production"
    Project     = "VM-Migration"
    Owner       = "Platform Team"
  }
}