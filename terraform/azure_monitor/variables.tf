# Azure Authentication
variable "azure_subscription_id" {
  description = "Azure Subscription ID"
  type        = string
  sensitive   = true
}

variable "azure_tenant_id" {
  description = "Azure Tenant ID"
  type        = string
  sensitive   = true
}

variable "azure_client_id" {
  description = "Azure Client ID"
  type        = string
  sensitive   = true
}

variable "azure_client_secret" {
  description = "Azure Client Secret"
  type        = string
  sensitive   = true
}

# Environment Configuration
variable "environment" {
  description = "Environment name"
  type        = string
  default     = "Production"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "WebApp-Monitoring"
}

variable "resource_owner" {
  description = "Resource owner"
  type        = string
  default     = "DevOps Team"
}

variable "cost_center" {
  description = "Cost center"
  type        = string
  default     = "IT-002"
}

# Azure Resources
variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
  default     = "rg-webapp-monitoring"
}

variable "azure_location" {
  description = "Azure region"
  type        = string
  default     = "East US 2"
}

# Log Analytics Workspace
variable "log_analytics_workspace_name" {
  description = "Name of the Log Analytics workspace"
  type        = string
  default     = "law-webapp-monitoring"
}

variable "log_analytics_sku" {
  description = "SKU of the Log Analytics workspace"
  type        = string
  default     = "PerGB2018"
}

variable "log_analytics_retention_days" {
  description = "Retention period in days for Log Analytics workspace"
  type        = number
  default     = 90
}

# Application Insights
variable "app_insights_name" {
  description = "Name of the Application Insights"
  type        = string
  default     = "ai-webapp-monitoring"
}

variable "app_insights_kind" {
  description = "Kind of Application Insights"
  type        = string
  default     = "web"
}

# Data Collection Rule
variable "dcr_name" {
  description = "Name of the Data Collection Rule"
  type        = string
  default     = "dcr-webapp-monitoring"
}

# Monitoring Features
variable "vm_insights_enabled" {
  description = "Enable VM Insights"
  type        = bool
  default     = true
}

variable "dependency_agent_enabled" {
  description = "Enable Dependency Agent"
  type        = bool
  default     = true
}

variable "ama_enabled" {
  description = "Enable Azure Monitor Agent"
  type        = bool
  default     = true
}

# Alert Configuration
variable "action_group_name" {
  description = "Name of the action group"
  type        = string
  default     = "ag-webapp-alerts"
}

variable "notification_email" {
  description = "Email for notifications"
  type        = string
  default     = "devops@company.com"
}

# VMs to Monitor
variable "vms_to_monitor" {
  description = "A list of virtual machines to monitor, with their name, resource group, and OS type."
  type = list(object({
    name           = string
    resource_group = string
    os_type        = string
  }))
  default = [
    {
      name           = "vm-webapp-01"
      resource_group = "rg-webapp-vms"
      os_type        = "Windows"
    },
    {
      name           = "vm-webapp-02"
      resource_group = "rg-webapp-vms"
      os_type        = "Linux"
    }
  ]
}

# Performance Counters
variable "windows_performance_counters" {
  description = "Windows performance counters"
  type = list(object({
    counter_name = string
    sample_rate  = number
  }))
  default = [
    {
      counter_name = "\\Processor(_Total)\\% Processor Time"
      sample_rate  = 60
    },
    {
      counter_name = "\\Memory\\Available MBytes"
      sample_rate  = 60
    },
    {
      counter_name = "\\LogicalDisk(_Total)\\% Free Space"
      sample_rate  = 60
    },
    {
      counter_name = "\\LogicalDisk(_Total)\\Disk Reads/sec"
      sample_rate  = 60
    },
    {
      counter_name = "\\LogicalDisk(_Total)\\Disk Writes/sec"
      sample_rate  = 60
    },
    {
      counter_name = "\\Network Interface(*)\\Bytes Total/sec"
      sample_rate  = 60
    }
  ]
}

variable "linux_performance_counters" {
  description = "Linux performance counters"
  type = list(object({
    counter_name = string
    sample_rate  = number
  }))
  default = [
    {
      counter_name = "\\Processor\\PercentProcessorTime"
      sample_rate  = 60
    },
    {
      counter_name = "\\Memory\\PercentAvailableMemory"
      sample_rate  = 60
    },
    {
      counter_name = "\\LogicalDisk\\PercentFreeSpace"
      sample_rate  = 60
    },
    {
      counter_name = "\\LogicalDisk\\DiskReadsPerSecond"
      sample_rate  = 60
    },
    {
      counter_name = "\\LogicalDisk\\DiskWritesPerSecond"
      sample_rate  = 60
    },
    {
      counter_name = "\\Network\\TotalBytesPerSecond"
      sample_rate  = 60
    }
  ]
}

# Windows Event Logs
variable "windows_event_logs" {
  description = "Windows event logs configuration"
  type = list(object({
    log_name = string
    levels   = list(string)
  }))
  default = [
    {
      log_name = "Application"
      levels   = ["Error", "Warning", "Information"]
    },
    {
      log_name = "System"
      levels   = ["Error", "Warning"]
    },
    {
      log_name = "Security"
      levels   = ["Error", "Warning"]
    }
  ]
}

# Syslog Configuration
variable "syslog_facilities" {
  description = "Syslog facilities configuration"
  type = list(object({
    facility = string
    levels   = list(string)
  }))
  default = [
    {
      facility = "auth"
      levels   = ["debug", "info", "notice", "warning", "err", "crit", "alert", "emerg"]
    },
    {
      facility = "authpriv"
      levels   = ["debug", "info", "notice", "warning", "err", "crit", "alert", "emerg"]
    },
    {
      facility = "cron"
      levels   = ["debug", "info", "notice", "warning", "err", "crit", "alert", "emerg"]
    },
    {
      facility = "daemon"
      levels   = ["debug", "info", "notice", "warning", "err", "crit", "alert", "emerg"]
    },
    {
      facility = "kern"
      levels   = ["debug", "info", "notice", "warning", "err", "crit", "alert", "emerg"]
    },
    {
      facility = "local0"
      levels   = ["debug", "info", "notice", "warning", "err", "crit", "alert", "emerg"]
    },
    {
      facility = "mail"
      levels   = ["debug", "info", "notice", "warning", "err", "crit", "alert", "emerg"]
    },
    {
      facility = "news"
      levels   = ["debug", "info", "notice", "warning", "err", "crit", "alert", "emerg"]
    },
    {
      facility = "syslog"
      levels   = ["debug", "info", "notice", "warning", "err", "crit", "alert", "emerg"]
    },
    {
      facility = "user"
      levels   = ["debug", "info", "notice", "warning", "err", "crit", "alert", "emerg"]
    }
  ]
}

# Alert Rules
variable "windows_alert_rules" {
  description = "Alert rules for Windows VMs"
  type = list(object({
    name             = string
    description      = string
    metric_namespace = string
    metric_name      = string
    dimensions = list(object({
      name     = string
      operator = string
      values   = list(string)
    }))
    threshold        = number
    operator         = string
    time_aggregation = string
    frequency        = string
    window_size      = string
    severity         = number
  }))
  default = [
    {
      name             = "High CPU Usage"
      description      = "Alert when CPU usage is above 80%"
      metric_namespace = "Microsoft.Compute/virtualMachines"
      metric_name      = "Percentage CPU"
      dimensions       = []
      threshold        = 80
      operator         = "GreaterThan"
      time_aggregation = "Average"
      frequency        = "PT5M"
      window_size      = "PT15M"
      severity         = 2
    },
    {
      name             = "Low Available Memory"
      description      = "Alert when available memory is below 1GB"
      metric_namespace = "Microsoft.Compute/virtualMachines"
      metric_name      = "Available Memory Bytes"
      dimensions       = []
      threshold        = 1073741824
      operator         = "LessThan"
      time_aggregation = "Average"
      frequency        = "PT5M"
      window_size      = "PT15M"
      severity         = 2
    },
    {
      name             = "High Disk Usage"
      description      = "Alert when disk usage is above 90%"
      metric_namespace = "InsightsMetrics"
      metric_name      = "usedPercentage"
      dimensions = [{
        name     = "device"
        operator = "Include"
        values   = ["_total"]
      }]
      threshold        = 90
      operator         = "GreaterThan"
      time_aggregation = "Average"
      frequency        = "PT5M"
      window_size      = "PT15M"
      severity         = 1
    }
  ]
}

variable "linux_alert_rules" {
  description = "Alert rules for Linux VMs"
  type = list(object({
    name             = string
    description      = string
    metric_namespace = string
    metric_name      = string
    dimensions = list(object({
      name     = string
      operator = string
      values   = list(string)
    }))
    threshold        = number
    operator         = string
    time_aggregation = string
    frequency        = string
    window_size      = string
    severity         = number
  }))
  default = [
    {
      name             = "High CPU Usage"
      description      = "Alert when CPU usage is above 80%"
      metric_namespace = "Microsoft.Compute/virtualMachines"
      metric_name      = "Percentage CPU"
      dimensions       = []
      threshold        = 80
      operator         = "GreaterThan"
      time_aggregation = "Average"
      frequency        = "PT5M"
      window_size      = "PT15M"
      severity         = 2
    },
    {
      name             = "Low Available Memory"
      description      = "Alert when available memory is below 500MB"
      metric_namespace = "InsightsMetrics"
      metric_name      = "availableMemoryMB"
      dimensions       = []
      threshold        = 500
      operator         = "LessThan"
      time_aggregation = "Average"
      frequency        = "PT5M"
      window_size      = "PT15M"
      severity         = 2
    },
    {
      name             = "High Disk Usage"
      description      = "Alert when disk usage is above 90%"
      metric_namespace = "InsightsMetrics"
      metric_name      = "usedPercentage"
      dimensions = [{
        name     = "device"
        operator = "Include"
        values   = ["_total"]
      }]
      threshold        = 90
      operator         = "GreaterThan"
      time_aggregation = "Average"
      frequency        = "PT5M"
      window_size      = "PT15M"
      severity         = 1
    }
  ]
}

variable "alert_rules" {
  description = "Generic alert rules configuration"
  type = list(object({
    name             = string
    description      = string
    metric_namespace = string
    metric_name      = string
    dimensions = list(object({
      name     = string
      operator = string
      values   = list(string)
    }))
    threshold        = number
    operator         = string
    time_aggregation = string
    frequency        = string
    window_size      = string
    severity         = number
  }))
  default = []
}

# SQL-Servers Variable

variable "sql_servers_to_monitor" {
  description = "List of SQL servers to monitor"
  type = list(object({
    name                = string
    id                  = string
    resource_group_name = string
    databases = list(object({
      name = string
      id   = string
    }))
  }))
  default = []
}

variable "diagnostic_settings_enabled" {
  description = "Enable diagnostic settings for resources"
  type        = bool
  default     = true
}

variable "sql_monitoring_enabled" {
  description = "Enable SQL monitoring"
  type        = bool
  default     = false
}

variable "sql_insights_enabled" {
  description = "Enable SQL Insights"
  type        = bool
  default     = true
}

variable "sql_threat_detection_enabled" {
  description = "Enable SQL Threat Detection"
  type        = bool
  default     = true
}

variable "sql_vulnerability_assessment_enabled" {
  description = "Enable SQL Vulnerability Assessment"
  type        = bool
  default     = true
}

variable "sql_storage_account_id" {
  description = "Storage account ID for SQL security features"
  type        = string
  default     = null
}

variable "sql_alert_rules" {
  description = "Custom SQL alert rules"
  type = list(object({
    name             = string
    description      = string
    metric_name      = string
    metric_namespace = string
    aggregation      = string
    operator         = string
    threshold        = number
    severity         = number
    frequency        = string
    window_size      = string
    resource_type    = string
  }))
  default = []
}
