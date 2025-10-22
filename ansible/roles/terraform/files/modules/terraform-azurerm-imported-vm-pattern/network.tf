# Network resources for the imported VM pattern module

# Network Interface
resource "azurerm_network_interface" "main" {
  name                = var.network.nic_name
  location            = var.location
  resource_group_name = var.resource_group_name

  # IP Configuration (minimal for import)
  ip_configuration {
    name                          = "internal"
    subnet_id                     = var.network.subnet_id
    private_ip_address_allocation = "Dynamic"
  }

  # Tags
  tags = var.tags

  lifecycle {
    ignore_changes = [
      accelerated_networking_enabled,
      ip_configuration,
      internal_dns_name_label,
      tags
    ]
  }
}

# Optional NSG create
resource "azurerm_network_security_group" "this" {
  count               = var.network.enable_nsg && (var.network.network_security_group_id == null || var.network.network_security_group_id == "") ? 1 : 0
  name                = "nsg-${var.vm_name}"
  location            = var.location
  resource_group_name = var.resource_group_name
  tags                = var.tags
}

resource "azurerm_network_security_rule" "rules" {
  for_each                    = var.network.enable_nsg && (var.network.network_security_group_id == null || var.network.network_security_group_id == "") ? var.network.nsg_rules : {}
  name                        = each.key
  priority                    = each.value.priority
  direction                   = each.value.direction
  access                      = each.value.access
  protocol                    = each.value.protocol
  source_port_range           = lookup(each.value, "source_port_range", "*")
  destination_port_range      = lookup(each.value, "destination_port_range", "*")
  source_address_prefixes     = lookup(each.value, "source_address_prefixes", null)
  destination_address_prefix  = lookup(each.value, "destination_address_prefix", "*")
  resource_group_name         = var.resource_group_name
  network_security_group_name = azurerm_network_security_group.this[0].name
}

# Associate created NSG to NIC when created
resource "azurerm_network_interface_security_group_association" "nic_nsg" {
  count                     = var.network.enable_nsg && (var.network.network_security_group_id == null || var.network.network_security_group_id == "") ? 1 : 0
  network_interface_id      = azurerm_network_interface.main.id
  network_security_group_id = azurerm_network_security_group.this[0].id
}

# Associate existing NSG to NIC when provided
resource "azurerm_network_interface_security_group_association" "nic_nsg_existing" {
  count                     = (var.network.network_security_group_id != null && var.network.network_security_group_id != "") ? 1 : 0
  network_interface_id      = azurerm_network_interface.main.id
  network_security_group_id = var.network.network_security_group_id
}
