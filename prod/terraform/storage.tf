module "primary_storage" {
  source  = "app.terraform.io/DTE-Cloud-Platform/storage-account/azurerm"
  version = "1.0.0"

  application_name    = "dtestcucorpapps"
  resource_group_name = azurerm_resource_group.rg-fbk.name
  location            = azurerm_resource_group.rg-fbk.location

  virtual_network_id                 = module.primary_network.vnet_id
  storage_account_endpoint_subnet_id = module.primary_network.subnet_ids["secondary"]
  shared_access_key_enabled          = false

  deployment_environment = "prod"
  environment            = "base"

  allow_blob_public_access = false
  create_endpoint = {
    "blob" : true,
    "file" : false,
    "queue" : false,
    "table" : false
  }

  tags = local.tags
}
