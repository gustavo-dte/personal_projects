# Terraform Role

This role generates Terraform configuration files for imported Azure VMs from Azure Migrate.

## Jinja Template and Reusable Modules

The role uses a single **Jinja2 template**, `templates/app_main.tf.j2`, to produce the Terraform root module file. The template is the single place where **reusable Terraform Cloud modules** are wired in: it renders locals, module blocks, and import blocks from the loaded manifest. All module calls (VMs, load balancers, app gateways) are defined in this template so that adding or changing a shared module is done in one place.

The template currently uses these Terraform Cloud modules (see `app_main.tf.j2` for current versions):

| Module | Registry path | Purpose |
|--------|----------------|---------|
| **imported-vm-pattern** | `app.terraform.io/DTE-Cloud-Platform/imported-vm-pattern/azurerm` | Import and manage Azure Migrate–migrated VMs; reduces repeated VM/import code. |
| **load-balancer** | `app.terraform.io/DTE-Cloud-Platform/load-balancer/azurerm` | Create and manage Azure load balancers when `load_balancers` is defined in the manifest. |
| **app-gateway** | `app.terraform.io/DTE-Cloud-Platform/app-gateway/azurerm` | Create and manage Application Gateways when `app_gateways` is defined in the manifest. |

## VMSS (VM Scale Set)

The **VMSS is not created or managed by this template**. It is created and configured via **Ansible** in `tasks/vmss.yml` (Azure API calls), then **imported** into Terraform. This is required so the VMSS can use **Flexible** orchestration mode and the migrated VM can be onboarded with Instance Auto Repair; Terraform's orchestrated VMSS resource does not support importing Flexible VMSS that contain Azure Migrate–migrated VMs. The VMSS is created ahead of time, the VM is added to it with Auto Repair, and the VMSS is later brought under Terraform via import.

**The only capability we use from the VMSS is [Automatic instance repairs](https://learn.microsoft.com/en-us/azure/virtual-machine-scale-sets/virtual-machine-scale-sets-automatic-instance-repairs?tabs=portal-1%2Cportal-2%2Crest-api-4%2Crest-api-5)** (e.g. Restart or Reimage on unhealthy instance). We do not use the VMSS for scaling or for high availability across zones.

**The VMSS cannot be scaled up or down** in this design. Scaling out would require the VMSS to create new instances from a **model/image**; we attached an **imported** Azure Migrate–migrated VM instead of creating the VMSS from an image, so there is no image/model for the scale set to use to create additional instances. High availability across zones would likewise require a shared image/model to deploy instances into multiple zones. To stop or release compute for the VM in the scale set, use **deallocate** (e.g. [Virtual Machine Scale Set VMs - Deallocate](https://learn.microsoft.com/en-us/rest/api/compute/virtual-machine-scale-set-vms/deallocate?view=rest-compute-2025-04-01&tabs=HTTP)) instead of changing the instance count.

> **Warning:** Do not scale the VMSS up or down. Changing the instance count (scale down or scale up) will result in **deletion of the VM and its data**. Use deallocate to stop or release compute without removing the instance.

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
└── {app_name}_vm.tf                 # Root module file with locals, module calls, and import blocks
```

The generated file contains:
- **Locals block**: Defines VM configurations (and optional load balancer/app gateway config) using a structured data format
- **Module calls**: Uses `for_each` where applicable and conditional blocks to call the Terraform Cloud modules (imported-vm-pattern, load-balancer, app-gateway)
- **Import blocks**: Groups import statements per VM (and VMSS where used) for importing existing Azure resources

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

- **Import Blocks**: Import blocks are generated in the root `{app_name}_vm.tf` (required by Terraform) and grouped per VM for readability.
- **Modular Design**: Uses Terraform Cloud modules—**imported-vm-pattern** (VMs), **load-balancer**, and **app-gateway**—as defined in `templates/app_main.tf.j2` (see table above for registry paths and versions).
- **Locals Pattern**: Uses a structured locals block with `resource_prefix` and `vms` collection for clean organization.
- **For_each Pattern**: Leverages `for_each` to iterate over VM configurations, enabling scalable multi-VM management.
- **Flexible Configuration**: Supports optional features like data disks, managed identity, domain join, VMSS integration, load balancers, and app gateways.
- **Comprehensive Tagging**: Applies consistent tagging following DTE standards.
- **Resource ID Handling**: Accepts resource IDs as variables for import operations.

#### Notes

- **Terraform Cloud Authentication**: The generated Terraform files reference a module from Terraform Cloud. Ensure you have authenticated with Terraform Cloud before running `terraform init`:
  ```bash
  terraform login
  ```
  Or configure credentials via environment variables or credentials file.

- **Module Sources**: All modules are sourced from Terraform Cloud (`app.terraform.io/DTE-Cloud-Platform/...`). Versions are pinned in `templates/app_main.tf.j2`. This is a private module registry; appropriate access permissions are required.

- **Resource IDs**: The role requires Azure resource IDs for import operations (VM, NIC, OS disk, data disks, etc.). These resource IDs are obtained through Azure collection calls in the generate task.

- **Ready to Use**: The generated Terraform files are ready to be used with `terraform init` and `terraform plan` after Terraform Cloud authentication is configured.
