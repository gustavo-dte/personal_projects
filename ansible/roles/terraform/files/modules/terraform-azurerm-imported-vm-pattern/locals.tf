# Local values for the imported VM pattern module

locals {
  vm_os_type = strcontains(lower(var.vm_os_type), "windows") ? "windows" : "linux"
}
