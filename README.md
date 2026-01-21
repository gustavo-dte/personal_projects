# terraform-azurerm-imported-vm-pattern

## Contributing

To contribute to this project, you'll need to install several development tools and configure your environment. Please see our **[Contributing Guide](docs/CONTRIBUTING.md)** for:

- Required software installation (pre-commit, Terraform, terraform-docs, tflint)
- Development environment setup for Windows and macOS
- Pre-commit hook configuration

### 💡 Need Help?

- Check the [Contributing Guide](docs/CONTRIBUTING.md) for detailed instructions
- Review existing issues and pull requests for context
- Contact the development team if you encounter setup difficulties

**Note:** All contributions must pass our automated checks including Terraform validation, linting, and security scans before being merged.

<!-- BEGIN_TF_DOCS -->
## Terraform Module for Cloud Platform Feature

This respository contains Terraform configuration for deploying a reuseable module.

### Usage

```hcl
terraform {
  required_version = ">= 1.5.0"
}

# Example usage of the terraform-azurerm-imported-vm-pattern module
# This example shows how to import Azure VMs (Windows and Linux) and their associated resources

# Example 1: Windows VM with basic configuration
module "imported_windows_vm" {
  source = "../"

  # Required VM Configuration
  vm_name             = "vm-windows-example"
  resource_group_name = "rg-example"
  location            = "eastus"
  vm_size             = "Standard_D2s_v5"
  vm_os_type          = "windows"

  # Required Network Configuration
  network = {
    nic_name  = "nic-windows-example"
    subnet_id = "/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/rg-example/providers/Microsoft.Network/virtualNetworks/vnet-example/subnets/subnet-example"
  }

  # Required Disk Configuration
  disk = {
    os = {
      name                 = "vm-windows-example_OsDisk_1"
      size_gb              = 127
      storage_account_type = "Premium_LRS"
      caching              = "ReadWrite"
      create_option        = "FromImage"
      os_type              = "Windows"
    }
    data = {
      "data-disk-1" = {
        lun                       = 0
        caching                   = "ReadWrite"
        write_accelerator_enabled = false
        resource_id               = "/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/rg-example/providers/Microsoft.Compute/disks/data-disk-1"
        disk_size_gb              = 100
        storage_account_type      = "Premium_LRS"
      }
      "data-disk-2" = {
        lun                       = 1
        caching                   = "ReadOnly"
        write_accelerator_enabled = false
        resource_id               = "/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/rg-example/providers/Microsoft.Compute/disks/data-disk-2"
        disk_size_gb              = 200
        storage_account_type      = "Standard_LRS"
      }
    }
  }

  # Optional: VM Advanced Settings
  provision_vm_agent   = true
  availability_zone    = "1"
  boot_diagnostics_uri = "https://storageaccount.blob.core.windows.net/"

  # Optional: Identity Configuration
  identity = {
    type         = "SystemAssigned"
    identity_ids = []
  }

  # Optional: Security Features (Trusted Launch)
  security_features = {
    secure_boot_enabled = true
    vtpm_enabled        = true
  }

  # Optional: Windows Update Assessment
  enable_periodic_update_assessment = true
  patch_assessment_schedule = {
    frequency   = "Daily"
    time_of_day = "02:00"
  }

  # Optional: Domain Join
  enable_domain_join       = true
  domain_name              = "contoso.com"
  domain_join_service_user = "serviceaccount@contoso.com"
  domain_join_password     = "SecurePassword123!" # pragma: allowlist secret (example only)
  target_ou                = "OU=Servers,DC=contoso,DC=com"

  # Tags (recommended)
  tags = {
    Environment = "dev"
    Project     = "migration"
    Owner       = "platform-team"
    CostCenter  = "IT"
    OS          = "Windows"
  }

  rec_svcs_vault_name    = ""
  rec_svcs_vault_res_grp = ""
  vm_backup_policy_name  = ""
}

# Example 2: Linux VM with SSH key authentication
module "imported_linux_vm" {
  source = "../"

  # Required VM Configuration
  vm_name             = "vm-linux-example"
  resource_group_name = "rg-example"
  location            = "eastus"
  vm_size             = "Standard_D2s_v5"
  vm_os_type          = "linux"

  # Required Network Configuration
  network = {
    nic_name  = "nic-linux-example"
    subnet_id = "/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/rg-example/providers/Microsoft.Network/virtualNetworks/vnet-example/subnets/subnet-example"
  }

  # Required Disk Configuration
  disk = {
    os = {
      name                 = "vm-linux-example_OsDisk_1"
      size_gb              = 64
      storage_account_type = "Premium_LRS"
      caching              = "ReadWrite"
      create_option        = "FromImage"
      os_type              = "Linux"
    }
    data = {}
  }

  # Linux-specific Configuration
  linux_admin_username                  = "azureuser"
  linux_disable_password_authentication = true
  linux_admin_ssh_public_key            = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC... user@hostname"

  # Optional: User Assigned Identity
  user_assigned_identity_resource_id = "/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/rg-example/providers/Microsoft.ManagedIdentity/userAssignedIdentities/identity-example"
  user_assigned_identity_name        = "identity-example"
  identity = {
    type         = "UserAssigned"
    identity_ids = []
  }

  # Tags (recommended)
  tags = {
    Environment = "dev"
    Project     = "migration"
    Owner       = "platform-team"
    CostCenter  = "IT"
    OS          = "Linux"
  }

  rec_svcs_vault_name    = ""
  rec_svcs_vault_res_grp = ""
  vm_backup_policy_name  = ""
}

# Example 3: Windows VM with VMSS integration (Flexible orchestration)
module "imported_windows_vm_with_vmss" {
  source = "../"

  # Required VM Configuration
  vm_name             = "vm-windows-vmss-example"
  resource_group_name = "rg-example"
  location            = "eastus"
  vm_size             = "Standard_D2s_v5"
  vm_os_type          = "windows"

  # Required Network Configuration
  network = {
    nic_name  = "nic-windows-vmss-example"
    subnet_id = "/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/rg-example/providers/Microsoft.Network/virtualNetworks/vnet-example/subnets/subnet-example"
  }

  # Required Disk Configuration
  disk = {
    os = {
      name                 = "vm-windows-vmss-example_OsDisk_1"
      size_gb              = 127
      storage_account_type = "Premium_LRS"
      caching              = "ReadWrite"
      create_option        = "FromImage"
      os_type              = "Windows"
    }
    data = {}
  }

  # VMSS Configuration (Flexible orchestration)
  enable_vmss                       = true
  vmss_name                         = "vmss-windows-example"
  vmss_sku                          = "Standard_D2s_v5"
  vmss_instances                    = 0 # Flexible mode - instances managed separately
  vmss_admin_username               = "azureuser"
  vmss_admin_password               = "SecurePassword123!" # pragma: allowlist secret (example only)
  vmss_image_publisher              = "MicrosoftWindowsServer"
  vmss_image_offer                  = "WindowsServer"
  vmss_image_sku                    = "2022-datacenter-g2"
  vmss_image_version                = "latest"
  vmss_os_disk_storage_account_type = "Premium_LRS"
  vmss_os_disk_caching              = "ReadWrite"

  # Tags (recommended)
  tags = {
    Environment = "dev"
    Project     = "migration"
    Owner       = "platform-team"
    CostCenter  = "IT"
    OS          = "Windows"
    VMSS        = "Enabled"
  }

  rec_svcs_vault_name    = ""
  rec_svcs_vault_res_grp = ""
  vm_backup_policy_name  = ""
}

# Example Outputs
# output "windows_vm_id" {
#   description = "ID of the imported Windows virtual machine"
#   value       = module.imported_windows_vm.vm_id
# }

# output "windows_vm_private_ip" {
#   description = "Private IP address of the Windows virtual machine"
#   value       = module.imported_windows_vm.private_ip_address
# }

# output "linux_vm_id" {
#   description = "ID of the imported Linux virtual machine"
#   value       = module.imported_linux_vm.vm_id
# }

# output "linux_vm_private_ip" {
#   description = "Private IP address of the Linux virtual machine"
#   value       = module.imported_linux_vm.private_ip_address
# }

# output "vmss_vm_id" {
#   description = "ID of the VM with VMSS integration"
#   value       = module.imported_windows_vm_with_vmss.vm_id
# }

# output "vmss_id" {
#   description = "ID of the Virtual Machine Scale Set"
#   value       = module.imported_windows_vm_with_vmss.vmss_id
# }

# output "all_vm_ids" {
#   description = "All VM IDs from the examples"
#   value = {
#     windows_vm = module.imported_windows_vm.vm_id
#     linux_vm   = module.imported_linux_vm.vm_id
#     vmss_vm    = module.imported_windows_vm_with_vmss.vm_id
#     minimal_vm = module.minimal_vm_example.vm_id
#   }
# }
```

## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 1.8.5 |
| <a name="requirement_azuread"></a> [azuread](#requirement\_azuread) | ~>3.0 |
| <a name="requirement_azurerm"></a> [azurerm](#requirement\_azurerm) | ~>4.0 |

## Resources

| Name | Type |
|------|------|
| [azurerm_backup_protected_vm.main](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/backup_protected_vm) | resource |
| [azurerm_linux_virtual_machine.main](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/linux_virtual_machine) | resource |
| [azurerm_linux_virtual_machine_scale_set.vmss](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/linux_virtual_machine_scale_set) | resource |
| [azurerm_managed_disk.data_disk](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/managed_disk) | resource |
| [azurerm_managed_disk.os_disk](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/managed_disk) | resource |
| [azurerm_network_interface.main](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/network_interface) | resource |
| [azurerm_network_interface_security_group_association.nic_nsg](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/network_interface_security_group_association) | resource |
| [azurerm_network_interface_security_group_association.nic_nsg_existing](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/network_interface_security_group_association) | resource |
| [azurerm_network_security_group.this](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/network_security_group) | resource |
| [azurerm_network_security_rule.rules](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/network_security_rule) | resource |
| [azurerm_user_assigned_identity.identity](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/user_assigned_identity) | resource |
| [azurerm_virtual_machine_data_disk_attachment.data_disk_attachment](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/virtual_machine_data_disk_attachment) | resource |
| [azurerm_virtual_machine_extension.domain_join](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/virtual_machine_extension) | resource |
| [azurerm_virtual_machine_extension.main](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/virtual_machine_extension) | resource |
| [azurerm_virtual_machine_extension.windows_update_assessment](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/virtual_machine_extension) | resource |
| [azurerm_windows_virtual_machine.main](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/windows_virtual_machine) | resource |
| [azurerm_windows_virtual_machine_scale_set.vmss](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/windows_virtual_machine_scale_set) | resource |
| [azurerm_backup_policy_vm.main](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/data-sources/backup_policy_vm) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_backup_vault_name"></a> [backup\_vault\_name](#input\_backup\_vault\_name) | Name of the Backup Vault | `string` | n/a | yes |
| <a name="input_backup_vault_policy_name"></a> [backup\_vault\_policy\_name](#input\_backup\_vault\_policy\_name) | Backup Vault Policy Name | `string` | n/a | yes |
| <a name="input_backup_vault_resource_group_name"></a> [backup\_vault\_resource\_group\_name](#input\_backup\_vault\_resource\_group\_name) | Resource Group Name of the Backup Vault | `string` | n/a | yes |
| <a name="input_disk"></a> [disk](#input\_disk) | Disk configuration: OS disk details and data disks map | <pre>object({<br/>    os = object({<br/>      name                 = string<br/>      size_gb              = number<br/>      storage_account_type = string<br/>      caching              = string<br/>      create_option        = string<br/>      os_type              = string<br/>    })<br/>    data = map(object({<br/>      lun                       = number<br/>      caching                   = string<br/>      write_accelerator_enabled = bool<br/>      resource_id               = string<br/>      disk_size_gb              = number<br/>      storage_account_type      = string<br/>    }))<br/>  })</pre> | n/a | yes |
| <a name="input_location"></a> [location](#input\_location) | Primary Azure location or region | `string` | n/a | yes |
| <a name="input_network"></a> [network](#input\_network) | Network configuration: NIC, subnet, optional NSG create/import and rules | <pre>object({<br/>    nic_name                  = string<br/>    subnet_id                 = string<br/>    network_security_group_id = optional(string)<br/>    enable_nsg                = optional(bool, false)<br/>    nsg_name                  = optional(string)<br/>    nsg_rules = optional(map(object({<br/>      priority                   = number<br/>      direction                  = string<br/>      access                     = string<br/>      protocol                   = string<br/>      source_port_range          = optional(string)<br/>      destination_port_range     = optional(string)<br/>      source_address_prefixes    = optional(list(string))<br/>      destination_address_prefix = optional(string)<br/>    })), {})<br/>  })</pre> | n/a | yes |
| <a name="input_resource_group_name"></a> [resource\_group\_name](#input\_resource\_group\_name) | The name of the resource group | `string` | n/a | yes |
| <a name="input_vm_name"></a> [vm\_name](#input\_vm\_name) | The name of the VM | `string` | n/a | yes |
| <a name="input_availability_zone"></a> [availability\_zone](#input\_availability\_zone) | The availability zone where the VM should be created. Must be 1, 2, or 3. Leave null for no zone placement. | `string` | `null` | no |
| <a name="input_boot_diagnostics_uri"></a> [boot\_diagnostics\_uri](#input\_boot\_diagnostics\_uri) | The storage account URI for boot diagnostics | `string` | `null` | no |
| <a name="input_custom_data"></a> [custom\_data](#input\_custom\_data) | The custom data to be used for the VM. Must be base64 encoded. | `string` | `""` | no |
| <a name="input_domain_join_password"></a> [domain\_join\_password](#input\_domain\_join\_password) | Password for the domain service account. Should be provided via Terraform Cloud global variable. | `string` | `""` | no |
| <a name="input_domain_join_service_user"></a> [domain\_join\_service\_user](#input\_domain\_join\_service\_user) | Domain service account for joining VMs (format: user@domain.com). Should be provided via Terraform Cloud global variable. | `string` | `""` | no |
| <a name="input_domain_name"></a> [domain\_name](#input\_domain\_name) | Azure AD Domain Services domain name (e.g., aaddscontoso.com). Should be provided via Terraform Cloud global variable. | `string` | `""` | no |
| <a name="input_enable_backup"></a> [enable\_backup](#input\_enable\_backup) | Enable backup for the VM | `bool` | `false` | no |
| <a name="input_enable_domain_join"></a> [enable\_domain\_join](#input\_enable\_domain\_join) | Enable Azure AD Domain Services join for the VM | `bool` | `false` | no |
| <a name="input_enable_periodic_update_assessment"></a> [enable\_periodic\_update\_assessment](#input\_enable\_periodic\_update\_assessment) | Enable periodic assessment for OS guest updates using Windows Update Extension. | `bool` | `false` | no |
| <a name="input_enable_vmss"></a> [enable\_vmss](#input\_enable\_vmss) | Enable Flexible VMSS import anchor and link VM to VMSS. | `bool` | `false` | no |
| <a name="input_identity"></a> [identity](#input\_identity) | Identity configuration for the VM | <pre>object({<br/>    type         = string<br/>    identity_ids = optional(list(string), [])<br/>  })</pre> | <pre>{<br/>  "identity_ids": [],<br/>  "type": "None"<br/>}</pre> | no |
| <a name="input_linux_admin_password"></a> [linux\_admin\_password](#input\_linux\_admin\_password) | Admin password for Linux VM when password auth is enabled. | `string` | `null` | no |
| <a name="input_linux_admin_ssh_public_key"></a> [linux\_admin\_ssh\_public\_key](#input\_linux\_admin\_ssh\_public\_key) | SSH public key for Linux VM when password auth is disabled. | `string` | `null` | no |
| <a name="input_linux_admin_username"></a> [linux\_admin\_username](#input\_linux\_admin\_username) | Admin username for Linux VM (schema requirement when not attaching by image). | `string` | `"azureuser"` | no |
| <a name="input_linux_disable_password_authentication"></a> [linux\_disable\_password\_authentication](#input\_linux\_disable\_password\_authentication) | Disable password authentication for Linux VM (use SSH keys). | `bool` | `true` | no |
| <a name="input_provision_vm_agent"></a> [provision\_vm\_agent](#input\_provision\_vm\_agent) | Specifies whether the VM Agent should be provisioned on the Virtual Machine. | `bool` | `true` | no |
| <a name="input_security_features"></a> [security\_features](#input\_security\_features) | Security features for Trusted Launch | <pre>object({<br/>    secure_boot_enabled = optional(bool, false)<br/>    vtpm_enabled        = optional(bool, false)<br/>  })</pre> | <pre>{<br/>  "secure_boot_enabled": false,<br/>  "vtpm_enabled": false<br/>}</pre> | no |
| <a name="input_tags"></a> [tags](#input\_tags) | Tags to be applied to all resources. Azure policies may require certain tags to be present. | `map(string)` | `{}` | no |
| <a name="input_target_ou"></a> [target\_ou](#input\_target\_ou) | Target OU DN for computer account. Defaults to Build OU for initial deployment. | `string` | `"OU=Build,OU=Windows,OU=CloudPlatform,OU=Servers,DC=dtenet,DC=com"` | no |
| <a name="input_user_assigned_identity_name"></a> [user\_assigned\_identity\_name](#input\_user\_assigned\_identity\_name) | Name of the user assigned identity | `string` | `null` | no |
| <a name="input_user_assigned_identity_resource_id"></a> [user\_assigned\_identity\_resource\_id](#input\_user\_assigned\_identity\_resource\_id) | Resource ID of the existing User Assigned Identity to import (optional) | `string` | `null` | no |
| <a name="input_vm_extension_auto_upgrade_minor_version"></a> [vm\_extension\_auto\_upgrade\_minor\_version](#input\_vm\_extension\_auto\_upgrade\_minor\_version) | Auto upgrade minor version for VM extension | `bool` | `true` | no |
| <a name="input_vm_extension_name"></a> [vm\_extension\_name](#input\_vm\_extension\_name) | Name of the VM extension | `string` | `null` | no |
| <a name="input_vm_extension_protected_settings"></a> [vm\_extension\_protected\_settings](#input\_vm\_extension\_protected\_settings) | Protected settings for the VM extension | `any` | `{}` | no |
| <a name="input_vm_extension_publisher"></a> [vm\_extension\_publisher](#input\_vm\_extension\_publisher) | Publisher of the VM extension | `string` | `"Microsoft.Compute"` | no |
| <a name="input_vm_extension_settings"></a> [vm\_extension\_settings](#input\_vm\_extension\_settings) | Settings for the VM extension | `any` | `{}` | no |
| <a name="input_vm_extension_type"></a> [vm\_extension\_type](#input\_vm\_extension\_type) | Type of the VM extension | `string` | `"CustomScriptExtension"` | no |
| <a name="input_vm_extension_type_handler_version"></a> [vm\_extension\_type\_handler\_version](#input\_vm\_extension\_type\_handler\_version) | Type handler version of the VM extension | `string` | `"1.10"` | no |
| <a name="input_vm_os_type"></a> [vm\_os\_type](#input\_vm\_os\_type) | Operating system type for the VM and optional VMSS. One of: windows, linux. | `string` | `"windows"` | no |
| <a name="input_vm_size"></a> [vm\_size](#input\_vm\_size) | The size of the VM | `string` | `"Standard_B2s"` | no |
| <a name="input_vmss_admin_password"></a> [vmss\_admin\_password](#input\_vmss\_admin\_password) | Admin password required by VMSS schema (placeholder; not used after import). | `string` | `"Placeholder-Password1!"` | no |
| <a name="input_vmss_admin_username"></a> [vmss\_admin\_username](#input\_vmss\_admin\_username) | Admin username required by VMSS schema (placeholder; not used after import). | `string` | `"azureuser"` | no |
| <a name="input_vmss_image_offer"></a> [vmss\_image\_offer](#input\_vmss\_image\_offer) | Offer for VMSS source\_image\_reference | `string` | `"WindowsServer"` | no |
| <a name="input_vmss_image_publisher"></a> [vmss\_image\_publisher](#input\_vmss\_image\_publisher) | Publisher for VMSS source\_image\_reference | `string` | `"MicrosoftWindowsServer"` | no |
| <a name="input_vmss_image_sku"></a> [vmss\_image\_sku](#input\_vmss\_image\_sku) | SKU for VMSS source\_image\_reference | `string` | `"2022-datacenter-g2"` | no |
| <a name="input_vmss_image_version"></a> [vmss\_image\_version](#input\_vmss\_image\_version) | Version for VMSS source\_image\_reference | `string` | `"latest"` | no |
| <a name="input_vmss_instances"></a> [vmss\_instances](#input\_vmss\_instances) | Number of instances for the VMSS (schema requirement; ignored after import). | `number` | `0` | no |
| <a name="input_vmss_name"></a> [vmss\_name](#input\_vmss\_name) | Name of the existing VMSS (must match the imported resource). | `string` | `null` | no |
| <a name="input_vmss_os_disk_caching"></a> [vmss\_os\_disk\_caching](#input\_vmss\_os\_disk\_caching) | Caching mode for VMSS OS disk | `string` | `"ReadWrite"` | no |
| <a name="input_vmss_os_disk_storage_account_type"></a> [vmss\_os\_disk\_storage\_account\_type](#input\_vmss\_os\_disk\_storage\_account\_type) | Storage account type for VMSS OS disk | `string` | `"Standard_LRS"` | no |
| <a name="input_vmss_sku"></a> [vmss\_sku](#input\_vmss\_sku) | SKU of the VMSS. Used to satisfy provider schema during import. | `string` | `"Standard_DS1_v2"` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_availability_zone"></a> [availability\_zone](#output\_availability\_zone) | The availability zone where the virtual machine is deployed. |
| <a name="output_data_disk_ids"></a> [data\_disk\_ids](#output\_data\_disk\_ids) | Map of data disk names to their IDs |
| <a name="output_data_disk_names"></a> [data\_disk\_names](#output\_data\_disk\_names) | Map of data disk names to their names |
| <a name="output_data_disk_sizes_gb"></a> [data\_disk\_sizes\_gb](#output\_data\_disk\_sizes\_gb) | Map of data disk names to their sizes in GB |
| <a name="output_location"></a> [location](#output\_location) | Azure region where resources are located |
| <a name="output_network_interface_id"></a> [network\_interface\_id](#output\_network\_interface\_id) | ID of the network interface |
| <a name="output_nic_mac_address"></a> [nic\_mac\_address](#output\_nic\_mac\_address) | MAC address of the network interface |
| <a name="output_nic_name"></a> [nic\_name](#output\_nic\_name) | Name of the network interface |
| <a name="output_nic_private_ip_address"></a> [nic\_private\_ip\_address](#output\_nic\_private\_ip\_address) | Private IP address of the network interface |
| <a name="output_os_managed_disk_id"></a> [os\_managed\_disk\_id](#output\_os\_managed\_disk\_id) | ID of the attached OS managed disk |
| <a name="output_private_ip_address"></a> [private\_ip\_address](#output\_private\_ip\_address) | Private IP address of the virtual machine |
| <a name="output_resource_group_name"></a> [resource\_group\_name](#output\_resource\_group\_name) | Name of the resource group |
| <a name="output_tags"></a> [tags](#output\_tags) | Tags applied to resources |
| <a name="output_user_assigned_identity_id"></a> [user\_assigned\_identity\_id](#output\_user\_assigned\_identity\_id) | ID of the user assigned identity |
| <a name="output_user_assigned_identity_name"></a> [user\_assigned\_identity\_name](#output\_user\_assigned\_identity\_name) | Name of the user assigned identity |
| <a name="output_vm_extension_id"></a> [vm\_extension\_id](#output\_vm\_extension\_id) | ID of the VM extension |
| <a name="output_vm_extension_name"></a> [vm\_extension\_name](#output\_vm\_extension\_name) | Name of the VM extension |
| <a name="output_vm_id"></a> [vm\_id](#output\_vm\_id) | Virtual machine id created. |
| <a name="output_vm_location"></a> [vm\_location](#output\_vm\_location) | location of Virtual machine created. |
| <a name="output_vm_name"></a> [vm\_name](#output\_vm\_name) | The name of the virtual machine. |
| <a name="output_vm_size"></a> [vm\_size](#output\_vm\_size) | Size of the virtual machine |
| <a name="output_vmss_id"></a> [vmss\_id](#output\_vmss\_id) | ID of the VM Scale Set when enabled |
| <a name="output_vmss_name"></a> [vmss\_name](#output\_vmss\_name) | Name of the VM Scale Set when enabled |
<!-- END_TF_DOCS -->
