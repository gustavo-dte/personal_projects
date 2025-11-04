# Azure SQL Managed Instance
resource "azurerm_mssql_managed_instance" "main" {
  name                = var.managed_instance_name
  resource_group_name = var.resource_group_name
  location            = var.location

  # Authentication
  administrator_login          = var.administrator_login
  administrator_login_password = var.administrator_login_password

  # License and SKU Configuration
  license_type = var.license_type
  sku_name     = var.sku_name
  vcores       = var.vcores
  storage_size_in_gb = var.storage_size_in_gb

  # Network Configuration
  subnet_id = var.subnet_id

  # High Availability Configuration
  dns_zone_partner_id = var.dns_zone_partner_id

  # Collation
  collation = var.collation

  # Timezone
  timezone_id = var.timezone_id

  # Public Data Endpoint
  public_data_endpoint_enabled = var.public_data_endpoint_enabled

  # Proxy Override
  proxy_override = var.proxy_override

  # Minimum TLS Version
  minimum_tls_version = var.minimum_tls_version

  # Storage Account Type
  storage_account_type = var.storage_account_type

  # Identity Configuration
  dynamic "identity" {
    for_each = var.identity_type != null ? [1] : []
    content {
      type         = var.identity_type
      identity_ids = var.identity_ids
    }
  }

  # Maintenance Configuration
  maintenance_configuration_name = var.maintenance_configuration_name

  # Zone Redundancy
  zone_redundant_enabled = var.zone_redundant_enabled

  tags = var.tags

  lifecycle {
    ignore_changes = [
      administrator_login_password
    ]
  }
}

# Azure AD Administrator for Managed Instance
resource "azurerm_mssql_managed_instance_active_directory_administrator" "main" {
  count = var.azure_ad_admin != null ? 1 : 0

  managed_instance_id = azurerm_mssql_managed_instance.main.id
  login_username      = var.azure_ad_admin.login_username
  object_id           = var.azure_ad_admin.object_id
  tenant_id           = var.azure_ad_admin.tenant_id != null ? var.azure_ad_admin.tenant_id : data.azurerm_client_config.current.tenant_id

  azuread_authentication_only = var.azure_ad_admin.azuread_authentication_only
}

# Transparent Data Encryption
resource "azurerm_mssql_managed_instance_transparent_data_encryption" "main" {
  count = var.enable_tde ? 1 : 0

  managed_instance_id = azurerm_mssql_managed_instance.main.id
  key_vault_key_id    = var.tde_key_vault_key_id
}

# Failover Group (if secondary instance is configured)
resource "azurerm_mssql_managed_instance_failover_group" "main" {
  count = var.failover_group_config != null ? 1 : 0

  name                        = var.failover_group_config.name
  location                    = var.location
  managed_instance_id         = azurerm_mssql_managed_instance.main.id
  partner_managed_instance_id = var.failover_group_config.partner_managed_instance_id

  read_write_endpoint_failover_policy {
    mode          = var.failover_group_config.failover_policy_mode
    grace_minutes = var.failover_group_config.grace_minutes
  }

  dynamic "readonly_endpoint_failover_policy_enabled" {
    for_each = var.failover_group_config.readonly_endpoint_enabled != null ? [1] : []
    content {
      enabled = var.failover_group_config.readonly_endpoint_enabled
    }
  }
}

# Security Alert Policy
resource "azurerm_mssql_managed_instance_security_alert_policy" "main" {
  count = var.enable_threat_detection ? 1 : 0

  resource_group_name        = var.resource_group_name
  managed_instance_name      = azurerm_mssql_managed_instance.main.name
  enabled                    = true
  retention_days             = var.threat_detection_policy.retention_days
  disabled_alerts            = var.threat_detection_policy.disabled_alerts
  email_account_admins       = var.threat_detection_policy.email_account_admins
  email_addresses            = var.threat_detection_policy.email_addresses
  storage_endpoint           = var.threat_detection_policy.storage_endpoint
  storage_account_access_key = var.threat_detection_policy.storage_account_access_key
}

# Vulnerability Assessment
resource "azurerm_mssql_managed_instance_vulnerability_assessment" "main" {
  count = var.enable_vulnerability_assessment ? 1 : 0

  managed_instance_id = azurerm_mssql_managed_instance.main.id
  storage_container_path = var.vulnerability_assessment_config.storage_container_path
  storage_account_access_key = var.vulnerability_assessment_config.storage_account_access_key

  dynamic "recurring_scans" {
    for_each = var.vulnerability_assessment_config.recurring_scans != null ? [1] : []
    content {
      enabled                   = var.vulnerability_assessment_config.recurring_scans.enabled
      email_subscription_admins = var.vulnerability_assessment_config.recurring_scans.email_subscription_admins
      emails                    = var.vulnerability_assessment_config.recurring_scans.emails
    }
  }

  depends_on = [azurerm_mssql_managed_instance_security_alert_policy.main]
}

# Data source for current Azure client configuration
data "azurerm_client_config" "current" {}
