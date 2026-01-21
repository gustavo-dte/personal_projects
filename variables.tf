/*
 * Copyright (c) DTE Energy Corporate Services, LLC. All rights reserved.
 * Internal Use Only
 */

/*
 * Common module variables
 */
variable "server_name" {
  type        = string
  description = "Name of the resource group"
}

variable "resource_group_name" {
  type        = string
  description = "Name of the resource group"
}

variable "location" {
  description = "The location of the virtual network"
  type        = string
  validation {
    condition     = contains(["centralus", "eastus2"], var.location)
    error_message = "Location must be one of: [ centralus, eastus2]. Actual: '${var.location}'."
  }
  default = "centralus"
}

variable "environment" {
  description = "The environment name. Must be one of: [ Sandbox, Base ]"
  type        = string
  validation {
    condition     = contains(["Sandbox", "Base", "Dev", "Test", "Prod"], var.environment)
    error_message = "Environment must be one of: [ 'Sandbox', 'Base', 'Dev', 'Test', 'Prod' ]. Actual: '${var.environment}'."
  }
}

variable "application_criticality" {
  description = "The criticality of the application. Must be one of: [ Tier1, Tier2, Tier3, Tier4 ]"
  type        = string
  validation {
    condition     = contains(["Tier1", "Tier2", "Tier3", "Tier4"], var.application_criticality)
    error_message = "Application Criticality must be one of: [ Tier1, Tier2, Tier3, Tier4 ]. Actual: ${var.application_criticality}"
  }
}

variable "log_analytics_workspace_name" {
  type        = string
  description = "The name of the analytics workspace to store security events."
}

variable "log_analytics_workspace_resource_group_name" {
  type        = string
  description = "The location of the analytics workspace to store security events, defaults to the SQL Managed Instance resource group."
  default     = null
}

variable "tags" {
  type = object({
    Environment         = string
    Portfolio           = string
    Application         = string
    BillTo              = string
    ContactEmail        = string
    BusinessCriticality = string
    DataClassification  = string
  })
  description = "Tags to be applied to SQL Server, must include required tags for policy"
}

/*
 * Networking variables
 */
variable "sql_subnet_id" {
  type        = string
  description = "The subnet id of the SQL Managed Instance delegated subnet"
}

variable "application_subnet_id" {
  type        = string
  description = "The subnet id to home the private endpoint created for this SQL Managed Instance"
}

/*
 * Security.
 */
variable "admin_username" {
  type        = string
  description = "The administrator username for the SQL Managed Instance"
  sensitive   = true

  validation {
    condition = (
      length(var.admin_username) >= 3 &&
      length(var.admin_username) <= 128 &&
      can(regex(local.admin_username_regex, var.admin_username))
    )
    error_message = "The SQL Server user name must be 3 and 128 characters, start with a letter, and contain only letters, numbers, underscores (_), hyphens (-), or periods (.). Actual: '${var.admin_username}'."
  }
}

variable "admin_password" {
  type        = string
  description = "The administrator password for the SQL Managed Instance"
  sensitive   = true
  validation {
    condition     = length(var.admin_password) >= 16 && length(var.admin_password) <= 128
    error_message = "admin_password must be between 16 and 128 characters. Actual: ${length(var.admin_password)}."
  }
}

variable "user_managed_identity_name" {
  type        = string
  description = "The user managed identity to use for the SQL Managed Instance"

  validation {
    condition = (
      length(var.user_managed_identity_name) >= 1 &&
      length(var.user_managed_identity_name) <= 128 &&
      can(regex(local.umi_name_regex, var.user_managed_identity_name))
    )
    error_message = "The name must be 1 and 128 characters, start with a letter, end with a letter or number, and contain only letters, numbers, and hyphens. Actual: '${var.user_managed_identity_name}'."
  }
}

variable "user_managed_identity_resource_group_name" {
  type        = string
  description = "The user managed identity to use for the SQL Managed Instance, defaults to the SQL Managed Instance resource group."
  default     = null
}

/*
 * Managed SQL configuration
 * See: https://learn.microsoft.com/en-us/azure/azure-sql/managed-instance/sql-managed-instance-purchase-models
 * for more information on the options available for SQL Managed Instances
 *
 * Databases will inherit short/long term retention policies from the application criticality
 */
variable "databases" {
  type        = set(string)
  description = "Set of databases to create on the SQL Managed Instance"
  default     = [] // Default to empty object map, i.e. no databases to create

  validation {
    condition     = length(var.databases) <= 100
    error_message = "You can only declare a maximum of 100 databases for the SQL Managed Instance. Actual: ${length(var.databases)}."
  }
}

variable "do_admin_aad_group_registration" {
  type        = bool
  description = "If true, the module will create AAD application and user groups for SQL Managed Instance access"
  default     = false
}

variable "admin_aad_group_login_name" {
  type        = string
  description = "The AAD group to use as the admin group."
  default     = "Azure-IDSS-SQL-Server-Contributor"

  validation {
    condition     = length(var.admin_aad_group_login_name) > 0 && length(var.admin_aad_group_login_name) <= 256
    error_message = "The group name must be between 1 and 256 characters. Actual: '${var.admin_aad_group_login_name}'."
  }
}

variable "admin_aad_group_login_object_id" {
  type        = string
  description = "The AAD group to use as the admin group."
  default     = "6637f678-d27f-4a7e-b194-bc685c8a8e1d"

  validation {
    condition     = can(regex(local.uuid_regex, var.admin_aad_group_login_object_id))
    error_message = "The admin AAD group login object ID must be a valid GUID. Actual: '${var.admin_aad_group_login_object_id}'. Actual: '${var.admin_aad_group_login_object_id}'."
  }
}

/*
 * @Katen Patel is still researching how he wants to handle this so it defaults to false. Soltion Architecture is still evaluating
 * the impact to this being enabled as well. The Security Assessment lists this as a high issue to resolve.
 */
variable "enable_vulnerability_assessment" {
  type        = bool
  description = "If true, the module will enable vulnerability assessment for the SQL Managed Instance"
  default     = false // Default to false for now, enabling vulnerability assessment
}

variable "enable_diagnostic_settings" {
  type        = bool
  description = "If true, the module will enable diagnostic settings (audit logs) for the SQL Managed Instance"
  default     = true
}

variable "enable_private_endpoint" {
  type        = bool
  description = "If true, the module will create a private endpoint for the SQL Managed Instance"
  default     = true
}

variable "vulnerability_assessment_container_path" {
  type        = string
  description = "The fully qualified path to the storage container for vulnerability assessment results, only used if enable_vulnerability_assessment is true"
  default     = null

  validation {
    condition = (
      var.enable_vulnerability_assessment == false ||
      can(regex(local.storage_container_path_regex, var.vulnerability_assessment_container_path))
    )
    error_message = "If vulnerability assessment is enabled, the container path must be a valid Azure Blob Storage container URL (e.g., https://mystorage.blob.core.windows.net/container or https://mystorage.privatelink.blob.core.windows.net/container). Actual: '${var.vulnerability_assessment_container_path != null ? var.vulnerability_assessment_container_path : "null"}'."
  }
}

variable "sku_name" {
  type        = string
  description = "The SKU name for the SQL Managed Instance"

  validation {
    condition     = contains(local.sku_defaults[var.application_criticality].allowed_skus, var.sku_name)
    error_message = "SKU ${var.sku_name} is not allowed for '${var.application_criticality}' in '${var.environment}'."
  }
}

variable "vcores" {
  type        = number
  description = "Number of vCores for the SQL Managed Instance"

  validation {
    condition = contains(
      lookup(lookup(local.vcore_defaults, local.environment_config, {}),
      var.sku_name, []),
      var.vcores
    )
    error_message = "vCores must be within the allowed range for '${var.sku_name}' on '${var.application_criticality}' in '${var.environment}'. Actual: ${var.vcores}."
  }
}

variable "storage_size_in_gb" {
  type        = number
  description = "Storage size in GB for the SQL Managed Instance"

  validation {
    condition = (
      contains(keys(lookup(local.storage_defaults, local.environment_config, {})), var.sku_name) &&
      var.storage_size_in_gb >= lookup(lookup(local.storage_defaults, local.environment_config, {}), var.sku_name, {}).min &&
      var.storage_size_in_gb <= lookup(lookup(local.storage_defaults, local.environment_config, {}), var.sku_name, {}).max &&
      var.storage_size_in_gb % 32 == 0
    )
    error_message = "Storage size must be within the allowed range and in increments of 32GB for SKU ${var.sku_name} and environment ${var.environment}. Actual: ${var.storage_size_in_gb}."
  }
}

variable "license_type" {
  type        = string
  description = "The license type for the SQL Managed Instance"
  default     = "LicenseIncluded" // Options: 'LicenseIncluded', 'BasePrice'

  validation {
    condition     = contains(["LicenseIncluded", "BasePrice"], var.license_type)
    error_message = "Valid values are: 'LicenseIncluded', 'BasePrice'. Actual: '${var.license_type}'."
  }
}

variable "timezone" {
  description = "Timezone for the SQL Managed Instance. Options: 'UTC' or 'Eastern Standard Time' (auto-adjusts for DST)"
  type        = string
  default     = "UTC"

  validation {
    condition     = contains(["UTC", "Eastern Standard Time"], var.timezone)
    error_message = "Valid options are 'UTC' or 'Eastern Standard Time'. Actual: '${var.timezone}'."
  }
}

variable "collation" {
  type        = string
  description = "The collation for the SQL Managed Instance"
  default     = "SQL_Latin1_General_CP1_CI_AS" // Default collation, can be adjusted as needed

  validation {
    condition     = contains(["Latin1_General_100_CI_AS_SC", "Latin1_General_100_CS_AS", "SQL_Latin1_General_CP1_CI_AS"], var.collation)
    error_message = "Collation must be either 'Latin1_General_100_CI_AS_SC', 'Latin1_General_100_CS_AS', or 'SQL_Latin1_General_CP1_CI_AS'. Actual: '${var.collation}'."
  }
}
