Downloading app.terraform.io/DTE-Cloud-Platform/imported-vm-pattern/azurerm 1.0.6 for test_app_vms...
- test_app_vms in .terraform/modules/test_app_vms
╷
│ Error: Module instance keys not allowed
│ 
│   on test-app-vm.tf line 361, in removed:
│  361:   from = module.test_app_vms["vmcuwinwebd01"].azurerm_virtual_machine_extension.windows_update_assessment[0]
│ 
│ Module address must be a module (e.g. "module.foo"), not a module instance
│ (e.g. "module.foo[1]").