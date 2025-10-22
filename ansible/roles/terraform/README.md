# Terraform Role

This role generates Terraform configuration files for imported Azure VMs from Azure Migrate.

## Available Actions

### generate

Generates Terraform configuration files for all VMs defined in the manifest.

#### Parameters

- `manifest` (string, **required**) - Manifest name to load. This should be passed as a variable from the command line or playbook execution.
- `terraform_action` (string, optional) - Action to perform. Default: `generate`
- `dry_run` (boolean, optional) - If true, skips Azure lookups but still generates Terraform files using computed/placeholder resource IDs. Default: `false`

#### Generated Files

The role generates the following Terraform file structure:

```
output/
├── {app_name}.tf                    # Root module call
├── {app_name}/                      # App module directory
│   ├── main.tf                      # App module main configuration
│   ├── variables.tf                 # App module variables
│   ├── outputs.tf                   # App module outputs
│   ├── modules/                     # Terraform modules directory
│   │   └── terraform-azurerm-imported-windows-vm/  # VM module
│   └── {vm_name}_main.tf           # Individual VM configurations
    ├── {vm_name}_locals.tf
    ├── {vm_name}_variables.tf
    └── {vm_name}_outputs.tf
```

#### Usage Examples

**Command line execution:**
```bash
# Generate Terraform files for phase_1 manifest
ansible-playbook terraform-playbook.yml -e "manifest=phase_1"

# Dry run: generates files, skips Azure lookups
ansible-playbook terraform-playbook.yml -e "manifest=phase_1" -e "dry_run=true"
```

**In playbook:**
```yaml
- name: Generate Terraform configuration
  ansible.builtin.include_role:
    name: terraform
  vars:
    manifest: "{{ manifest }}"
    terraform_action: generate
    dry_run: "{{ dry_run | default(false) }}"
```

#### Required Manifest Variables

The following variables must be present in the manifest:

- `app_name` - Application name
- `environment` - Environment (Development, Test, Base, Prod, Sandbox)
- `target_subscription_id` - Azure subscription ID
- `target_resource_group` - Target resource group name
- `target_network_id` - Target network ID
- `target_subnet_name` - Target subnet name
- `vms` - List of VMs to generate Terraform for

#### Generated Configuration Features

- **Import Blocks**: Import blocks are generated in the root `{app_name}.tf` (required by Terraform) and grouped per VM for readability.
- **Modular Design**: Uses the `terraform-azurerm-imported-windows-vm` module for consistent VM management
- **Flexible Configuration**: Supports optional features like data disks, managed identity, domain join, etc.
- **Comprehensive Tagging**: Applies consistent tagging following DTE standards
- **Resource ID Handling**: Accepts resource IDs as variables for import operations

#### Notes

- The role requires Azure resource IDs for import operations (VM, NIC, OS disk, data disks, etc.)
- These resource IDs will be obtained through Azure collection calls in the generate task
- The generated Terraform files are ready to be used with `terraform init` and `terraform plan`
