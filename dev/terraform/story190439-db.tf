# ------------------------------------------------------
# Test Script Calls MSSQL Module Configuration
# ------------------------------------------------------
module "mssql" {
  source  = "app.terraform.io/DTE-Cloud-Platform/mssql/azurerm"
  version = "1.0.0-alpha.4"

  # --- Core identifiers (required) ---
  resource_group_name = "rg-cu-CorpApps-MigrationTest-Dev"
  location            = "centralus"

  # Secondary values (still required inputs even if Tier3/Tier4; DR resources won't be created unless Tier1)
  secondary_resource_group_name = "rg-cu-CorpApps-MigrationTest-Dev-dr" # <-- use your DR RG, or reuse the primary if you don't have one
  secondary_location            = "eastus2"                             # <-- pick your DR region (using mssql module)

  # --- Server configuration (required) ---
  sql_server_version           = "12.0"
  administrator_login          = "sqladmin"
  administrator_login_password = var.sqldb_password
  application_criticality      = "Tier3" # -> primary only

  # --- Naming context (required in alpha.4) ---
  environment      = "Dev"                    # Allowed: Sandbox, Base, Dev, Test, Prod
  application_name = "corpapps-migrationtest" # Used to construct server/db names internally

  # --- Database configuration ---
  db_sku_name = "GP_Gen5_2" # provisioned,  if you want to use serverless S: GP_S_Gen5_2. The root module version doesn’t expose min_capacity

  auto_pause_delay_in_minutes = null # set to null so the module's resource omits it
  collation                   = "SQL_Latin1_General_CP1_CI_AS"

  # --- Retention policies ---
  short_term_retention_days = 7
  enable_ltr                = true
  ltr_weekly_retention      = "P4W"
  ltr_monthly_retention     = "P12M"
  ltr_yearly_retention      = "P5Y"
  ltr_week_of_year          = 1

  # --- Networking ---
  # Private Endpoint networking (required)
  # Use subnet IDs from your VNet modules (no hard-coding)
  private_endpoint_subnet_id           = module.primary_network.subnet_ids["secondary"]
  private_endpoint_subnet_id_secondary = module.secondary_network.subnet_ids["main"]

  # --- Private DNS Zone attachment ---
  # Platform manages the Private DNS Zones; skip attaching within this module
  skip_dns_zone_for_pep = true
  dns_zone_ids          = {} # required by the module interface even when skipping

  # --- Tags ---
  tags = local.tags # ensure local.tags exists; otherwise replace with a literal map
}
