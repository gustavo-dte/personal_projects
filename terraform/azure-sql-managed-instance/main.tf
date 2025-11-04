# ============================================================================
# Azure SQL Managed Instance Terraform Configuration
# ============================================================================

terraform {
  required_version = ">= 1.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.4"
    }
  }
}

provider "azurerm" {
  features {}
}

# ============================================================================
# DATA SOURCES
# ============================================================================

data "azurerm_client_config" "current" {}

# ============================================================================
# RESOURCE GROUP
# ============================================================================

resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location
  tags     = var.tags
}

# ============================================================================
# NETWORKING - Virtual Network
# ============================================================================

resource "azurerm_virtual_network" "main" {
  name                = "${var.managed_instance_name}-vnet"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  address_space       = [var.vnet_address_space]
  tags                = var.tags
}

# ============================================================================
# SUBNET FOR SQL MANAGED INSTANCE
# ============================================================================

resource "azurerm_subnet" "sqlmi" {
  name                 = "${var.managed_instance_name}-subnet"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = [var.subnet_address_prefix]

  delegation {
    name = "managedinstancedelegation"
    
    service_delegation {
      name = "Microsoft.Sql/managedInstances"
      actions = [
        "Microsoft.Network/virtualNetworks/subnets/join/action",
        "Microsoft.Network/virtualNetworks/subnets/prepareNetworkPolicies/action",
        "Microsoft.Network/virtualNetworks/subnets/unprepareNetworkPolicies/action"
      ]
    }
  }
}

# ============================================================================
# NETWORK SECURITY GROUP
# ============================================================================

resource "azurerm_network_security_group" "sqlmi" {
  name                = "${var.managed_instance_name}-nsg"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  tags                = var.tags

  # Required: Management inbound
  security_rule {
    name                       = "allow_management_inbound"
    priority                   = 106
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_ranges    = ["9000", "9003", "1438", "1440", "1452"]
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  # Required: MI subnet inbound
  security_rule {
    name                       = "allow_misubnet_inbound"
    priority                   = 200
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "*"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = var.subnet_address_prefix
    destination_address_prefix = "*"
  }

  # Required: Health probe inbound
  security_rule {
    name                       = "allow_health_probe_inbound"
    priority                   = 300
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "*"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = "AzureLoadBalancer"
    destination_address_prefix = "*"
  }

  # Required: TDS inbound (for connections)
  security_rule {
    name                       = "allow_tds_inbound"
    priority                   = 1000
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "1433"
    source_address_prefix      = "VirtualNetwork"
    destination_address_prefix = "*"
  }

  # Optional: Redirect inbound (for better performance)
  security_rule {
    name                       = "allow_redirect_inbound"
    priority                   = 1100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "11000-11999"
    source_address_prefix      = "VirtualNetwork"
    destination_address_prefix = "*"
  }

  # Required: Deny all other inbound
  security_rule {
    name                       = "deny_all_inbound"
    priority                   = 4096
    direction                  = "Inbound"
    access                     = "Deny"
    protocol                   = "*"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  # Required: Management outbound
  security_rule {
    name                       = "allow_management_outbound"
    priority                   = 102
    direction                  = "Outbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_ranges    = ["80", "443", "12000"]
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  # Required: MI subnet outbound
  security_rule {
    name                       = "allow_misubnet_outbound"
    priority                   = 200
    direction                  = "Outbound"
    access                     = "Allow"
    protocol                   = "*"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = "*"
    destination_address_prefix = var.subnet_address_prefix
  }

  # Required: Allow all outbound (for dependencies)
  security_rule {
    name                       = "allow_linkedserver_outbound"
    priority                   = 4000
    direction                  = "Outbound"
    access                     = "Allow"
    protocol                   = "*"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = var.subnet_address_prefix
    destination_address_prefix = "*"
  }
}

resource "azurerm_subnet_network_security_group_association" "sqlmi" {
  subnet_id                 = azurerm_subnet.sqlmi.id
  network_security_group_id = azurerm_network_security_group.sqlmi.id
}

# ============================================================================
# ROUTE TABLE
# ============================================================================

resource "azurerm_route_table" "sqlmi" {
  name                = "${var.managed_instance_name}-rt"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  tags                = var.tags
}

resource "azurerm_subnet_route_table_association" "sqlmi" {
  subnet_id      = azurerm_subnet.sqlmi.id
  route_table_id = azurerm_route_table.sqlmi.id
}

# ============================================================================
# STORAGE ACCOUNT (for auditing and vulnerability assessment)
# ============================================================================

resource "random_string" "storage_suffix" {
  length  = 8
  special = false
  upper   = false
}

resource "azurerm_storage_account" "main" {
  count                    = var.enable_auditing || var.enable_vulnerability_assessment ? 1 : 0
  name                     = "sqlmi${random_string.storage_suffix.result}"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "GRS"
  
  blob_properties {
    versioning_enabled = true
    
    delete_retention_policy {
      days = 90
    }
  }

  tags = var.tags
}

resource "azurerm_storage_container" "vulnerability_assessment" {
  count                 = var.enable_vulnerability_assessment ? 1 : 0
  name                  = "vulnerability-assessment"
  storage_account_name  = azurerm_storage_account.main[0].name
  container_access_type = "private"
}

# ============================================================================
# GENERATE SECURE PASSWORD (if not provided)
# ============================================================================

resource "random_password" "sqlmi_admin" {
  count            = var.administrator_login_password == null ? 1 : 0
  length           = 24
  special          = true
  override_special = "!@#$%&*()-_=+[]{}:?"
  min_lower        = 1
  min_upper        = 1
  min_numeric      = 1
  min_special      = 1
}

# ============================================================================
# SQL MANAGED INSTANCE
# ============================================================================

resource "azurerm_mssql_managed_instance" "main" {
  name                = var.managed_instance_name
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location

  # Authentication
  administrator_login          = var.administrator_login
  administrator_login_password = var.administrator_login_password != null ? var.administrator_login_password : random_password.sqlmi_admin[0].result

  # License and SKU
  license_type       = var.license_type
  sku_name           = var.sku_name
  vcores             = var.vcores
  storage_size_in_gb = var.storage_size_in_gb

  # Network
  subnet_id = azurerm_subnet.sqlmi.id

  # Database settings
  collation   = var.collation
  timezone_id = var.timezone_id

  # Security
  minimum_tls_version          = var.minimum_tls_version
  public_data_endpoint_enabled = var.public_data_endpoint_enabled
  proxy_override               = var.proxy_override

  # Storage
  storage_account_type = var.storage_account_type

  # High Availability
  zone_redundant_enabled = var.zone_redundant_enabled

  # Maintenance
  maintenance_configuration_name = var.maintenance_configuration_name

  # Managed Identity
  identity {
    type = var.identity_type
  }

  tags = var.tags

  depends_on = [
    azurerm_subnet_network_security_group_association.sqlmi,
    azurerm_subnet_route_table_association.sqlmi
  ]

  lifecycle {
    ignore_changes = [
      administrator_login_password
    ]
  }

  timeouts {
    create = "24h"
    update = "24h"
    delete = "24h"
  }
}

# ============================================================================
# AZURE AD ADMINISTRATOR (Optional)
# ============================================================================

resource "azurerm_mssql_managed_instance_active_directory_administrator" "main" {
  count = var.enable_azure_ad_auth ? 1 : 0

  managed_instance_id = azurerm_mssql_managed_instance.main.id
  login_username      = var.azure_ad_admin_login
  object_id           = var.azure_ad_admin_object_id
  tenant_id           = var.azure_ad_admin_tenant_id != null ? var.azure_ad_admin_tenant_id : data.azurerm_client_config.current.tenant_id
}

# ============================================================================
# SECURITY ALERT POLICY (Advanced Threat Protection)
# ============================================================================

resource "azurerm_mssql_managed_instance_security_alert_policy" "main" {
  count = var.enable_threat_detection ? 1 : 0

  resource_group_name   = azurerm_resource_group.main.name
  managed_instance_name = azurerm_mssql_managed_instance.main.name
  enabled               = true
  retention_days        = var.threat_detection_retention_days
  email_account_admins  = var.threat_detection_email_admins
  email_addresses       = var.threat_detection_email_addresses
  
  storage_endpoint           = var.enable_auditing ? azurerm_storage_account.main[0].primary_blob_endpoint : null
  storage_account_access_key = var.enable_auditing ? azurerm_storage_account.main[0].primary_access_key : null
}

# ============================================================================
# VULNERABILITY ASSESSMENT (Optional)
# ============================================================================

resource "azurerm_mssql_managed_instance_vulnerability_assessment" "main" {
  count = var.enable_vulnerability_assessment ? 1 : 0

  managed_instance_id        = azurerm_mssql_managed_instance.main.id
  storage_container_path     = "${azurerm_storage_account.main[0].primary_blob_endpoint}${azurerm_storage_container.vulnerability_assessment[0].name}"
  storage_account_access_key = azurerm_storage_account.main[0].primary_access_key

  recurring_scans {
    enabled                   = true
    email_subscription_admins = true
    emails                    = var.threat_detection_email_addresses
  }

  depends_on = [
    azurerm_mssql_managed_instance_security_alert_policy.main
  ]
}
