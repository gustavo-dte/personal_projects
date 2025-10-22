### VM Migration Manifests (`ansible/vars/*/manifest.yml`)

Use a manifest to describe everything needed to replicate/migrate one or more source VMs into Azure. Each subfolder under `ansible/vars` contains a `manifest.yml` for a specific run/profile (for example `demo/`, `phase_1/`, `phase_2/`).

### How to use a manifest

- Run playbooks with the manifest as an Ansible extra-vars file:

```bash
ansible-playbook playbooks/<your-playbook>.yml -e @ansible/vars/demo/manifest.yml
```

- CI workflows can reference the same file path when invoking Ansible.

### File structure and fields

Below is a minimal, annotated template. Use values from the provided manifests (see `demo/manifest.yml` and `phase_1/manifest.yml`) as working examples.

```yaml
## Manifest for migration replication

# Global defaults
app_name: yourAppName
environment: dev
target_gh_repo: dteenergy/cloud-platform-isolation-zone-subscription-corpapps
azure_migrate_project_name: azure-migrate-automation
azure_migrate_project_resource_group: cloud-platform-prod-cu-azure-migrate-rg
# Optional, if required by your workflow
azure_migrate_subscription_id: "<subscription-guid>"

# Azure Backup defaults
recovery_vault_name: cloud-platform-prod-cu-backup-vault
backup_policy_name: DefaultPolicy
replication_threshold: 80

# Azure VMSS defaults
vmss_enabled: true
vmss_config:
  health_probe_settings:
    protocol: http
    port: 80
    requestPath: /health
  automatic_instance_repair:
    enabled: true
    grace_period: PT30M
    repair_action: Restart

# Network configuration (use full Azure resource IDs)
target_network_id: /subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.Network/virtualNetworks/<vnet>
target_subnet_name: /subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.Network/virtualNetworks/<vnet>/subnets/<subnet>

# VM configuration defaults
target_vm_size: Standard_D4s_v5
target_license_type: NoLicenseType
target_disk_type: Standard_LRS
os_disk_scsi_id: scsi0:0   # include if your source platform requires it

# List of VMs to replicate; per-VM values override the defaults above
vms:
  - name: my-vm-01
    description: "Example VM"
    portfolio: Example-Portfolio
    tier: 4
    env: dev
    app_name: your-app

    # Optional per-VM overrides
    target_vm_size: Standard_D2s_v5
    target_license_type: Windows_Server
    target_disk_type: Standard_LRS

    # Optional per-VM Backup override
    backup:
      recovery_vault_name: cloud-platform-prod-cu-backup-vault
      backup_policy_name: DefaultPolicy
      replication_threshold: 80

    # Optional per-VM NSG
    network_security_group_id: null  # set an existing NSG resource ID to reuse it
    enable_nsg: true                 # set true to create an NSG with rules below
    nsg_rules:
      allow-rdp:
        priority: 1000
        direction: Inbound
        access: Allow
        protocol: Tcp
        destination_port_range: "3389"
        source_address_prefixes: ["10.0.0.0/8"]

    # Optional per-VM VMSS overrides
    vmss_config:
      health_probe_settings:
        protocol: tcp
        port: 3389
      automatic_instance_repair:
        enabled: true
        grace_period: PT10M
        repair_action: Restart
```

### Conventions and tips

- Use full Azure resource IDs for `target_network_id` and `target_subnet_name`.
- `vms[*]` values override global defaults; omit a field to inherit the default.
- `vmss_enabled` controls whether VM Scale Set constructs are created; you can further override `vmss_config` per VM.
- Keep secrets out of manifests; these files are intended to be committed and passed to Ansible with `-e @manifest.yml`.
- See the real examples in `demo/manifest.yml` and `phase_1/manifest.yml` for working values and patterns.
