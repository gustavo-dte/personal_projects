# Resource Group
resource "azurerm_resource_group" "monitoring" {
  name     = var.resource_group_name
  location = var.location
}

# Log Analytics Workspace
resource "azurerm_log_analytics_workspace" "main" {
  name                = var.log_analytics_workspace_name
  location            = azurerm_resource_group.monitoring.location
  resource_group_name = azurerm_resource_group.monitoring.name
  sku                 = var.log_analytics_sku
  retention_in_days   = var.log_analytics_retention_days
}

# Application Insights
resource "azurerm_application_insights" "main" {
  name                = var.app_insights_name
  location            = azurerm_resource_group.monitoring.location
  resource_group_name = azurerm_resource_group.monitoring.name
  workspace_id        = azurerm_log_analytics_workspace.main.id
  application_type    = var.app_insights_kind
}

# Windows Data Collection Rule
resource "azurerm_monitor_data_collection_rule" "windows" {
  name                = "${var.dcr_name}-windows"
  resource_group_name = azurerm_resource_group.monitoring.name
  location            = azurerm_resource_group.monitoring.location

  destinations {
    log_analytics {
      workspace_resource_id = azurerm_log_analytics_workspace.main.id
      name                  = "la-destination"
    }
  }

  data_flow {
    streams      = ["Microsoft-Perf", "Microsoft-Event"]
    destinations = ["la-destination"]
  }

  data_sources {
    performance_counter {
      streams                       = ["Microsoft-Perf"]
      sampling_frequency_in_seconds = 60
      counter_specifiers = [
        for counter in var.windows_performance_counters : counter.counter_name
      ]
      name = "perfCounterDataSource"
    }

    windows_event_log {
      streams = ["Microsoft-Event"]
      x_path_queries = [
        "Application!*[System[(Level=1 or Level=2 or Level=3)]]",
        "System!*[System[(Level=1 or Level=2)]]",
        "Security!*[System[(Level=1 or Level=2)]]"
      ]
      name = "eventLogsDataSource"
    }
  }
}

# Linux Data Collection Rule
resource "azurerm_monitor_data_collection_rule" "linux" {
  name                = "${var.dcr_name}-linux"
  resource_group_name = azurerm_resource_group.monitoring.name
  location            = azurerm_resource_group.monitoring.location

  destinations {
    log_analytics {
      workspace_resource_id = azurerm_log_analytics_workspace.main.id
      name                  = "la-destination"
    }
  }

  data_flow {
    streams      = ["Microsoft-Perf", "Microsoft-Syslog"]
    destinations = ["la-destination"]
  }

  data_sources {
    performance_counter {
      streams                       = ["Microsoft-Perf"]
      sampling_frequency_in_seconds = 60
      counter_specifiers = [
        for counter in var.linux_performance_counters : counter.counter_name
      ]
      name = "perfCounterDataSource"
    }

    syslog {
      streams = ["Microsoft-Syslog"]
      facility_names = [
        for facility in var.syslog_facilities : facility.facility
      ]
      log_levels = ["Debug", "Info", "Notice", "Warning", "Error", "Critical", "Alert", "Emergency"]
      name       = "syslogDataSource"
    }
  }
}

# Action Group
resource "azurerm_monitor_action_group" "main" {
  name                = var.action_group_name
  resource_group_name = azurerm_resource_group.monitoring.name
  short_name          = "VMAlerts"

  email_receiver {
    name                    = "EmailAlert"
    email_address           = var.notification_email
    use_common_alert_schema = true
  }
}
