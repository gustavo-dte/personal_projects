# Azure Update Manager role

This role enables periodic patch assessment and optional scheduled patching for VMs using Azure Policy, Azure Automation and Azure Maintenance (InGuestPatch).

Variable structure
 - The role now reads configuration from the nested manifest section `manifest_data.update_manager` in your manifest file. Role defaults live in `roles/azure_update_manager/defaults/main.yml` and are used when manifest values are not provided.

Top-level update manager variables (under `manifest_data.update_manager`):

- `policy_assignment_name` (string)
  - Default from role: `PeriodicAssessMissingUpdates-Windows`
  - Subscription-scoped policy assignment name for Windows periodic assessment.

- `policy_assignment_name_linux` (string)
  - Default from role: `PeriodicAssessMissingUpdates-Linux`
  - Subscription-scoped policy assignment name for Linux periodic assessment.

- `remediation_name` / `remediation_name_linux` (string)
  - Remediation task names (defaults in role defaults).

- `automation_account` (string|null)
  - Automation account name to create a `software-update-configuration` (scheduled patch window). If not provided scheduling is skipped.

- `patch_start_time` (string|null)
  - ISO8601 start time to schedule the patch window (e.g. `2025-10-16T00:00:00Z`).

- `skip_assessment_in_dry_run` (bool)
  - Default: true (role default). When true the role will not call Azure for assessments during dry-run.

Maintenance configuration is nested under `manifest_data.update_manager.maintenance`:

- `resource_group` (string|null)
  - Resource group to create maintenance resources in; defaults to `manifest_data.target_resource_group`.

- `config_name` (string)
  - Maintenance configuration name (default `PatchConfig-InGuestPatch`).

- `assignment_name` (string)
  - Base name for maintenance assignment (per-VM suffix appended).

- `location`, `window_duration`, `window_recur_every`, `window_start_date_time`, `window_time_zone`
  - Window scheduling parameters. Defaults exist in role defaults.

- `windows.kb_exclude`, `windows.kb_include`, `windows.classifications`
  - KBs and classifications to include/exclude for Windows InGuestPatch.

- `reboot_setting`, `ingest_patch_mode` etc.
  - Additional options (see role defaults for names and defaults).

How the role reads values
- The role first runs `tasks/assign_policy.yml` from the controller to discover each VM's OS using the Ansible Azure collection `azure.azcollection.azure_rm_virtualmachine_info` and builds a `vm_os_map` used by per-VM tasks. This avoids duplicate `az` CLI calls.
- Per-VM tasks read the OS from `vm_os_map[vm_name]` and run either Windows or Linux specific tasks.
- All Azure-changing tasks support `dry_run: true` which will only log intended actions.

Example manifest (`ansible/vars/phase_1/manifest.yml`) additions:

```yaml
update_manager:
  policy_assignment_name: PeriodicAssessMissingUpdates-Windows
  policy_assignment_name_linux: PeriodicAssessMissingUpdates-Linux
  remediation_name: Remediate-PeriodicAssess
  remediation_name_linux: Remediate-PeriodicAssess-Linux
  automation_account: my-automation-account
  patch_start_time: "2025-10-16T00:00:00Z"
  skip_assessment_in_dry_run: true

  maintenance:
    resource_group: myMaintenanceRG
    config_name: myConfig
    assignment_name: Assign-PatchConfig
    location: eastus
    window_duration: "02:00"
    window_recur_every: "20days"
    window_start_date_time: "2025-12-30 07:00"
    window_time_zone: "Pacific Standard Time"
    windows:
      kb_exclude: "KB123456"
      kb_include: "KB123456"
      classifications: FeaturePack
    reboot_setting: IfRequired
    ingest_patch_mode: User
```

Notes and requirements
- Role defaults are defined in `roles/azure_update_manager/defaults/main.yml`. Set values in your manifest under `manifest_data.update_manager` to override.
- The role uses the Ansible Azure collection (`azure.azcollection`) for VM info and the Azure CLI (`az`) for some resource creations (policy assignment, remediation, maintenance and automation). Ensure both are available on the controller and the runner is authenticated with sufficient permissions (Policy Contributor/Owner, Automation Contributor, Maintenance Contributor as required).
- Run a dry-run first to validate behavior:

```bash
ansible-playbook ansible/playbooks/enable-update-manager.yml -e manifest=phase_1 -e dry_run=true -v
```

If you'd like, I can add a small example playbook showing how to call the role with `dry_run` or install instructions for `azure.azcollection` on CI runners.
