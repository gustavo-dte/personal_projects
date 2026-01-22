resource "azurerm_network_security_rule" "allow_sql_inbound" {
  name                        = "allow_sql_inbound"
  priority                    = 100
  direction                   = "Inbound"
  access                      = "Allow"
  protocol                    = "Tcp"
  source_port_range           = "*"
  destination_port_range      = "1433"
  source_address_prefix       = "*"
  destination_address_prefix  = "VirtualNetwork"
  network_security_group_name = module.primary_network_vmware.nsg_name
  resource_group_name         = azurerm_resource_group.primary_vmware_network_rg.name
}

resource "azurerm_network_security_rule" "allow_web_inbound" {
  name                        = "allow_web_inbound"
  priority                    = 120
  direction                   = "Inbound"
  access                      = "Allow"
  protocol                    = "Tcp"
  source_port_range           = "*"
  destination_port_range      = "443"
  source_address_prefix       = "*"
  destination_address_prefix  = "VirtualNetwork"
  network_security_group_name = module.primary_network_vmware.nsg_name
  resource_group_name         = azurerm_resource_group.primary_vmware_network_rg.name
}

resource "azurerm_network_security_rule" "block_all_inbound" {
  name                        = "block_all_inbound"
  priority                    = 1000
  direction                   = "Inbound"
  access                      = "Deny"
  protocol                    = "*"
  source_port_range           = "*"
  destination_port_range      = "*"
  source_address_prefix       = "*"
  destination_address_prefix  = "*"
  network_security_group_name = module.primary_network_vmware.nsg_name
  resource_group_name         = azurerm_resource_group.primary_vmware_network_rg.name
}

resource "azurerm_network_security_rule" "dependency_on_azure_sql" {
  name                        = "dependency_on_azure_sql"
  priority                    = 140
  direction                   = "Outbound"
  access                      = "Allow"
  protocol                    = "Tcp"
  source_port_range           = "*"
  destination_port_range      = "1433"
  source_address_prefix       = "VirtualNetwork"
  destination_address_prefix  = "SqlManagement"
  network_security_group_name = module.primary_network_vmware.nsg_name
  resource_group_name         = azurerm_resource_group.primary_vmware_network_rg.name
}
