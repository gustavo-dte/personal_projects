// tflint-ignore-file: terraform_required_version
module "my_mssqlmi_instance" {
  source = "C:/Users/u68537/projects/terraform-azurerm-mssqlmi"

  resource_group_name = "dte_cu_myapplication_rg"
  location            = "centralus"

  server_name             = "mysqlinstance"
  environment             = "Dev"
  application_criticality = "Tier4"

  // break-glass local password
  admin_username = "<dbadmin>"
  admin_password = "<secret, secret - I got a secret>"

  user_managed_identity_name                = azurerm_user_assigned_identity.this.name
  user_managed_identity_resource_group_name = azurerm_user_assigned_identity.this.resource_group_name

  sku_name           = "GP_Gen5"
  vcores             = 4
  storage_size_in_gb = 32
  license_type       = "LicenseIncluded"
  collation          = "Latin1_General_100_CI_AS_SC"
  timezone           = "UTC"

  application_subnet_id = azurerm_subnet.application.id
  sql_subnet_id         = azurerm_subnet.sqlmi.id

  // Log Analytics Workspaces
  log_analytics_workspace_name                = azurerm_log_analytics_workspace.this.name
  log_analytics_workspace_resource_group_name = azurerm_log_analytics_workspace.this.resource_group_name

  // If doining vulnerability aseesments
  enable_vulnerability_assessment         = true // defaults to false
  vulnerability_assessment_container_path = "https://mystorageaccount.privatelink.blob.core.windows.net/va"

  // If your UMI is already set up for AAD (Entra) Admin Group Auth
  do_admin_aad_group_registration = true
  admin_aad_group_login_name      = "Azure-IDSS-SQL-Server-Contributor"    // Defaults to this
  admin_aad_group_login_object_id = "6637f678-d27f-4a7e-b194-bc685c8a8e1d" // Defaults to this

  databases = [
    "MyDatabaseOne",
    "MyDatabaseTwo",
    "MyDatabaseThree"
  ]

  tags = local.required_tags
}
