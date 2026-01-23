
/* 
 * Creates the SQL Server database for the SQL Migrate SPIKE
 */

locals {
  primary_sqlmi_sku_name           = "GP_Gen5"
  primary_sqlmi_vcores             = 4
  primary_sqlmi_storage_size_in_gb = 32

  short_term_retention_days_defaults = {
    Tier1 = 35
    Tier2 = 14
    Tier3 = 7
    Tier4 = 5
  }
  databases = [
    "TestDatabase01",
    "TestDatabase02"
  ]

}

# Create the SQL server Managed Instance Database
resource "azurerm_mssql_managed_instance" "primary_sqlmi" {
  name                         = "test-corpapps-test"
  resource_group_name = azurerm_resource_group.vm_migration_test.name
  location            = azurerm_resource_group.vm_migration_test.location
  subnet_id                    = azurerm_subnet.sql-subnet-primary.id

  administrator_login          = "sqladminuser"
  administrator_login_password = var.sqlmi_password

  identity {
    type = "SystemAssigned"
  }

  sku_name                     = local.primary_sqlmi_sku_name
  vcores                       = local.primary_sqlmi_vcores
  storage_size_in_gb           = local.primary_sqlmi_storage_size_in_gb
  license_type                 = "LicenseIncluded"
  collation                    = "SQL_Latin1_General_CP1_CI_AS"
  timezone_id                  = "UTC"
  public_data_endpoint_enabled = false

  # Tags - matching module's expected structure
  tags = {
    Environment         = local.tags.Environment
    Portfolio           = local.tags.Portfolio
    Application         = local.tags.Application
    BillTo              = "100000069697"
    ContactEmail        = local.tags.ItAppOwnerEmail
    BusinessCriticality = local.tags.BusinessCriticality
    DataClassification  = local.tags.DataClassification
  }
}

resource "azurerm_mssql_managed_database" "sqlmi_server_databases" {
  for_each = toset(local.databases)

  name                = each.key
  managed_instance_id = azurerm_mssql_managed_instance.sqlmi_server.id

  short_term_retention_days = local.short_term_retention_days_defaults["Tier4"] // based on application criticality

  long_term_retention_policy { // based on application criticality
    weekly_retention  = local.long_term_retention.weekly_retention
    monthly_retention = local.long_term_retention.monthly_retention
    yearly_retention  = local.long_term_retention.yearly_retention
    week_of_year      = local.long_term_retention.week_of_year
  }

  lifecycle {
    prevent_destroy = true // Prevent data loss
  }

  depends_on = [
    azurerm_mssql_managed_instance.sqlmi_server
  ]
}