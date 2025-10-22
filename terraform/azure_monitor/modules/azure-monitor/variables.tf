variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
}

variable "location" {
  description = "Azure region"
  type        = string
}

variable "log_analytics_workspace_name" {
  description = "Name of the Log Analytics workspace"
  type        = string
}

variable "log_analytics_sku" {
  description = "SKU of the Log Analytics workspace"
  type        = string
}

variable "log_analytics_retention_days" {
  description = "Retention period in days"
  type        = number
}

variable "app_insights_name" {
  description = "Name of Application Insights"
  type        = string
}

variable "app_insights_kind" {
  description = "Kind of Application Insights"
  type        = string
}

variable "dcr_name" {
  description = "Name of the Data Collection Rule"
  type        = string
}

variable "action_group_name" {
  description = "Name of the action group"
  type        = string
}

variable "notification_email" {
  description = "Email for notifications"
  type        = string
}

variable "windows_performance_counters" {
  description = "Windows performance counters"
  type = list(object({
    counter_name = string
    sample_rate  = number
  }))
}

variable "linux_performance_counters" {
  description = "Linux performance counters"
  type = list(object({
    counter_name = string
    sample_rate  = number
  }))
}

variable "windows_event_logs" {
  description = "Windows event logs"
  type = list(object({
    log_name = string
    levels   = list(string)
  }))
}

variable "syslog_facilities" {
  description = "Syslog facilities"
  type = list(object({
    facility = string
    levels   = list(string)
  }))
}

variable "alert_rules" {
  description = "Alert rules"
  type = list(object({
    name             = string
    description      = string
    metric_name      = string
    threshold        = number
    operator         = string
    time_aggregation = string
    frequency        = string
    window_size      = string
    severity         = number
  }))
}
