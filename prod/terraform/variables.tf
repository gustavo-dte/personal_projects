variable "primary_region" {
  type        = string
  description = "Primary Azure location or region"
}

variable "secondary_region" {
  type        = string
  description = "Secondary Azure location or region"
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
