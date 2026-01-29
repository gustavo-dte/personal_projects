Error: creating Maintenance Configuration (Subscription: "6796a2fb-2928-4ec6-96da-962d3b0001b7" Resource Group Name: "rg-cu-CorpApps-MigrationTest-Dev" Maintenance Configuration Name: "weekly-sunday-2am"): unexpected status 400 (400 Bad Request) with response: {"Error":{"Code":"InvalidMaintenanceWindow","Message":"Invalid maintenance window. Error: StartDateTime is not set for maintenance window."}}
with azurerm_maintenance_configuration.vm_patching["weekly-sunday-2am"]
on test-app-vm.tf line 374, in resource "azurerm_maintenance_configuration" "vm_patching":
resource "azurerm_maintenance_configuration" "vm_patching" {

Error: creating/updating Extension (Subscription: "6796a2fb-2928-4ec6-96da-962d3b0001b7" Resource Group Name: "rg-cu-CorpApps-MigrationTest-Dev" Virtual Machine Name: "vmcuwinwebd01" Extension Name: "WindowsUpdateAssessment"): performing CreateOrUpdate: unexpected status 404 (404 Not Found) with error: ArtifactNotFound: The VM extension with publisher 'Microsoft.Azure.Monitor' and type 'WindowsUpdateExtension' could not be found.
with module.test_app_vms["vmcuwinwebd01"].azurerm_virtual_machine_extension.windows_update_assessment[0]
on .terraform/modules/test_app_vms/vm.tf line 180, in resource "azurerm_virtual_machine_extension" "windows_update_assessment":
resource "azurerm_virtual_machine_extension" "windows_update_assessment" {