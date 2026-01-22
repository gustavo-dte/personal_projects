data "azurerm_shared_image_version" "windows" {
  provider            = azurerm.vmimage
  name                = "0.0.3"
  image_name          = "img_cu_prod_gold_win2022"
  gallery_name        = "sig_cu_prod_gold"
  resource_group_name = "gold-rg"
}

resource "azurerm_user_assigned_identity" "primary" {
  name                = "${local.application_name}-${local.short_env}-${local.primary_region}-vm-identity"
  resource_group_name = azurerm_resource_group.primary-vck.name
  location            = azurerm_resource_group.primary-vck.location
  tags                = local.tags
}

resource "azurerm_role_assignment" "primary_mi_contributor" {
  scope                = azurerm_resource_group.primary-vck.id
  role_definition_name = "Reader"
  principal_id         = azurerm_user_assigned_identity.primary.principal_id
}

resource "azurerm_resource_group" "primary_law_cu_rg" {
  name     = "${local.application_name}-${local.short_env}-${local.primary_region}-law-rg"
  location = var.primary_region
  tags     = local.tags
}

# Log Analytics Workspace central region
resource "azurerm_log_analytics_workspace" "vm_law_cu" {
  name                = "${local.application_name}-cu-law"
  location            = azurerm_resource_group.primary_law_cu_rg.location
  resource_group_name = azurerm_resource_group.primary_law_cu_rg.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
  tags                = local.tags
}



# Example 1: Basic Windows VM with periodic update assessment
module "example_windows_vm" {
  source  = "app.terraform.io/DTE-Cloud-Platform/windows-vm/azurerm"
  version = "1.3.1"

  vm_name             = "vmcuwinwebd02"
  resource_group_name = azurerm_resource_group.vm_migration_test.name
  location            = azurerm_resource_group.vm_migration_test.location
  vm_size             = "Standard_D2s_v5"
  admin_username      = "cpoeadmin"
  admin_password      = var.vm_password

  # Legacy parameters for compatibility
  # subnet_id       = module.primary_network.subnet_ids["main"]
  availability_zone = null
  source_image_id   = data.azurerm_shared_image_version.windows.id


  nic_configs = [{
    subnet_id                      = module.primary_network.subnet_ids["main"]
    private_ip_allocation_method   = "Dynamic"
    private_ip_address             = null
    accelerated_networking_enabled = false
  }]

  identity = {
    type         = "UserAssigned"
    identity_ids = [azurerm_user_assigned_identity.primary.id]
  }

  os_disk = {
    caching                   = "ReadWrite"
    storage_account_type      = "Premium_LRS"
    disk_size_gb              = 128 # Larger disk for Windows
    write_accelerator_enabled = false
  }

  enable_domain_join                = false
  enable_periodic_update_assessment = false

  enable_monitoring = true
  email_action_receivers = [{
    name          = "CloudPlatform"
    email_address = "cloudplatform@dteenergy.com"
  }]

  email_action_receivers_snow = [{
    name          = "servicenow"
    email_address = "dteenergyprod@service-now.com"
  }]

  suppress_alerts = false

  log_analytics_workspace_id = azurerm_log_analytics_workspace.vm_law_cu.id

  tags = local.tags

}

# # Example 2: Windows VM with Domain Join enabled
# module "example_windows_vm_domain_joined" {
#   source  = "app.terraform.io/DTE-Cloud-Platform/windows-vm/azurerm"
#   version = "1.0.0"

#   vm_name             = "cloud-platform-domain-vm"
#   resource_group_name = azurerm_resource_group.rg.name
#   location            = azurerm_resource_group.rg.location
#   vm_size             = "Standard_B2s"
#   admin_username      = local.github_runner_user
#   admin_password      = var.admin_password

#   nic_configs = [
#     {
#       subnet_id                      = azurerm_subnet.example_subnet.id
#       private_ip_allocation_method   = "Dynamic"
#       accelerated_networking_enabled = false
#       private_ip_address             = ""
#     }
#   ]

#   source_image_id = data.azurerm_shared_image_version.windows.id

#   # Domain Join Configuration
#   enable_domain_join = true
#   # Note: domain_name, domain_join_service_user, domain_join_password, target_ou
#   # are provided via Terraform Cloud global variables

#   # Optional: Enable periodic update assessment
#   enable_periodic_update_assessment = true

#   tags = {
#     # https://dev.azure.com/dteenergy/Storm%20Cloud/_wiki/wikis/Storm-Cloud.wiki/2540/Azure-Tagging-Standards
#     Environment         = "<env>"
#     Portfolio           = "<portfolio>"
#     Application         = "<application>"
#     BillTo              = "<billTo>"
#     ItAppOwnerEmail     = "<itappowneremail>"
#     BusinessCriticality = "<businessCriticality>"
#     DataClassification  = "<dataClassification>"
#   }
# }
