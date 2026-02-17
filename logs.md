Error: issuing creating request for Scoped Configuration Assignment (Scope: "/subscriptions/6796a2fb-2928-4ec6-96da-962d3b0001b7/resourceGroups/rg-cu-CorpApps-MigrationTest-Dev/providers/Microsoft.Compute/virtualMachines/vmcuwinwebd01" Configuration Assignment Name: "weekly-sunday-2am"): unexpected status 400 (400 Bad Request) with response: {"Error":{"Code":"UnsupportedResourceOperation","Message":"\"Patch orchestration mode is not set to AutomaticByPlatform\",The prerequisites to patch your machine were not met. Please set the patchMode to AutomaticByPlatform and bypassPlatformChecksOnUserSchedule as true. Resource: /subscriptions/6796a2fb-2928-4ec6-96da-962d3b0001b7/resourcegroups/rg-cu-corpapps-migrationtest-dev/providers/microsoft.compute/virtualmachines/vmcuwinwebd01"}}
with azurerm_maintenance_assignment_virtual_machine.vm_patching["vmcuwinwebd01"]
on test-app-vm.tf line 417, in resource "azurerm_maintenance_assignment_virtual_machine" "vm_patching":
resource "azurerm_maintenance_assignment_virtual_machine" "vm_patching" {


Error: Conflicting configuration arguments
with module.test_app_vms["vmcuwinwebd01"].azurerm_windows_virtual_machine.main[0]
on .terraform/modules/test_app_vms/vm.tf line 48, in resource "azurerm_windows_virtual_machine" "main":
  bypass_platform_safety_checks_on_user_schedule_enabled = true
"bypass_platform_safety_checks_on_user_schedule_enabled": conflicts with os_managed_disk_id
Error: Conflicting configuration arguments
with module.test_app_vms["vmcuwinwebd01"].azurerm_windows_virtual_machine.main[0]
on .terraform/modules/test_app_vms/vm.tf line 49, in resource "azurerm_windows_virtual_machine" "main":
  automatic_updates_enabled                              = false
"automatic_updates_enabled": conflicts with os_managed_disk_id
Error: Conflicting configuration arguments
with module.test_app_vms["vmcuwinwebd01"].azurerm_windows_virtual_machine.main[0]
on .terraform/modules/test_app_vms/vm.tf line 47, in resource "azurerm_windows_virtual_machine" "main":
  patch_assessment_mode                                  = "AutomaticByPlatform"
"patch_assessment_mode": conflicts with os_managed_disk_id
Error: Conflicting configuration arguments
with module.test_app_vms["vmcuwinwebd01"].azurerm_windows_virtual_machine.main[0]
on .terraform/modules/test_app_vms/vm.tf line 46, in resource "azurerm_windows_virtual_machine" "main":
  patch_mode                                             = "AutomaticByPlatform"