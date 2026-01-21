locals {
  uuid_regex                   = "^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
  umi_name_regex               = "^[a-zA-Z][a-zA-Z0-9-]*[a-zA-Z0-9]$"
  storage_container_path_regex = "^https://[a-z0-9]{3,24}\\.(privatelink\\.)?blob\\.core\\.windows\\.net/[a-z0-9-]{3,63}/?$"
  admin_username_regex         = "^[a-zA-Z][a-zA-Z0-9_.-]{2,127}$"
  locations = {
    centralus = "cu"
    eastus2   = "e2"
  }
  short_term_retention_days_defaults = {
    Tier1 = 35
    Tier2 = 14
    Tier3 = 7
    Tier4 = 5
  }
  long_term_retention_defaults = {
    Tier1 = {
      weekly_retention  = "P12W"
      monthly_retention = "P12M"
      yearly_retention  = "P7Y"
      week_of_year      = 1
    }
    Tier2 = {
      weekly_retention  = "P8W"
      monthly_retention = "P6M"
      yearly_retention  = "P5Y"
      week_of_year      = 1
    }
    Tier3 = {
      weekly_retention  = "P4W"
      monthly_retention = "P2M"
      yearly_retention  = "P1Y"
      week_of_year      = 1
    }
    Tier4 = {
      weekly_retention  = "P1W"
      monthly_retention = "P1M"
      yearly_retention  = null
      week_of_year      = null
    }
  }
  sku_defaults = {
    Tier1 = {
      allowed_skus = ["BC_Gen5", "BC_PremiumSeries", "BC_PremiumSeriesMemoryOptimized"]
    }
    Tier2 = {
      allowed_skus = ["BC_Gen5", "BC_PremiumSeries"]
    }
    Tier3 = {
      allowed_skus = ["GP_Gen5"]
    }
    Tier4 = {
      allowed_skus = ["GP_Gen5"]
    }
  }
  vcore_defaults = {
    prod = {
      BC_Gen5                         = [4, 8, 16, 24, 32, 40, 64, 80]
      BC_PremiumSeries                = [4, 8, 16, 24, 32, 40, 64, 80, 96, 128]
      BC_PremiumSeriesMemoryOptimized = [4, 8, 16, 24, 32, 40, 64, 80, 96, 128]
      GP_Gen5                         = [4, 8, 16, 24, 32, 40, 64, 80]
    }
    dev = {
      GP_Gen5 = [4, 8]
    }
  }
  storage_defaults = {
    prod = {
      BC_Gen5 = {
        min = 32
        max = 4096
      }
      BC_PremiumSeries = {
        min = 32
        max = 5632
      }
      BC_PremiumSeriesMemoryOptimized = {
        min = 32
        max = 16384
      }
      GP_Gen5 = {
        min = 32
        max = 16384
      }
    }
    dev = {
      GP_Gen5 = {
        min = 32
        max = 128
      }
    }
  }
  environment_lower = lower(var.environment) // lower-case the environemnt
  environment_config = (                     // Treat sandbox as dev the same for a sku config limits, treat base, test, and prod the same for a sku config limits
    local.environment_lower == "sandbox" ? "dev" :
    contains(["base", "test", "prod"], local.environment_lower) ? "prod" :
    local.environment_lower
  )
  short_location                              = local.locations[var.location]                                                     // get the location short-code for resource names
  resource_name                               = "dte-sqlmi-${local.short_location}-${local.environment_lower}-${var.server_name}" // dte-sqlmi-<region>-<env>-<server name>
  endpoint_name                               = "${local.resource_name}-pep"
  service_name                                = "${local.endpoint_name}sc"
  audit_log_name                              = "${local.resource_name}-audit-logs"
  criticality                                 = contains(["sandbox", "dev"], local.environment_lower) ? "Tier4" : var.application_criticality // downgrade sandbox and dev to Tier4
  zone_redundant                              = contains(["Tier1", "Tier2"], local.criticality)                                               // Default to zone redundant on Tiers 1 and 2
  umi_resource_group_name                     = var.user_managed_identity_resource_group_name != null ? var.user_managed_identity_resource_group_name : var.resource_group_name
  log_analytics_workspace_resource_group_name = var.log_analytics_workspace_resource_group_name != null ? var.log_analytics_workspace_resource_group_name : var.resource_group_name
  short_term_retention_days                   = local.short_term_retention_days_defaults[local.criticality] // set retention based on Tier
  long_term_retention                         = local.long_term_retention_defaults[local.criticality]       // set retention based on Tier
}
