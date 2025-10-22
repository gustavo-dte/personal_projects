variable "vm_name" {
  description = "Name of the virtual machine"
  type        = string
}

variable "vm_resource_group" {
  description = "Resource group of the virtual machine"
  type        = string
}

variable "vm_id" {
  description = "ID of the virtual machine"
  type        = string
}

variable "resource_group_name" {
  description = "Name of the monitoring resource group"
  type        = string
}

variable "windows_dcr_id" {
  description = "ID of the Windows Data Collection Rule"
  type        = string
}

variable "action_group_id" {
  description = "ID of the action group"
  type        = string
}

variable "ama_enabled" {
  description = "Enable Azure Monitor Agent"
  type        = bool
  default     = true
}

variable "dependency_agent_enabled" {
  description = "Enable Dependency Agent"
  type        = bool
  default     = true
}

variable "vm_insights_enabled" {
  description = "Enable VM Insights"
  type        = bool
  default     = true
}

variable "alert_rules" {
  description = "A list of alert rules to create for the VM."
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
