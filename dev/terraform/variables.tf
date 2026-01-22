variable "primary_region" {
  type        = string
  description = "Primary Azure location or region"
}

variable "secondary_region" {
  type        = string
  description = "Secondary Azure location or region"
}

variable "vm_password" {
  type        = string
  sensitive   = true
  description = "password to connect to vm for vmware migration testing"
}

variable "environment" {
  type        = string
  description = "Environment"
  validation {
    condition     = contains(["Development", "Test", "Base", "Prod", "Sandbox"], var.environment)
    error_message = "Environment must be one of: [ Development, Test, Base, Prod, Sandbox]. Actual: ${var.environment}"
  }
}

variable "primary_network_container_cidr" {
  type        = string
  description = "Primary network container CIDR"
}

variable "secondary_network_container_cidr" {
  type        = string
  description = "Secondary network container CIDR"
}

variable "application" {
  type        = string
  description = "Application name"
}

variable "infoblox_server" {
  type        = string
  description = "Infoblox server hostname"
}

variable "infoblox_username" {
  type        = string
  description = "Infoblox username"
}

variable "infoblox_password" {
  type        = string
  description = "Infoblox password"
  sensitive   = true
}

variable "github_token" {
  description = "GitHub token for authentication"
  type        = string
  sensitive   = true
}

variable "github_organization" {
  description = "GitHub organization"
  type        = string
}

variable "sqldb_password" {
  description = "SQL Database Password"
  type        = string
  sensitive   = true
}

variable "sqlmi_password" {
  description = "SQL Managed Instance password for the 'sqladminuser' account"
  type        = string
  sensitive   = true
}
