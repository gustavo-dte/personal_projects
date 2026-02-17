Azure + Dynatrace role
----------------------

Purpose: install Dynatrace OneAgent on Azure VMs and manage an alerting profile via Dynatrace Settings API.

Requirements:
- ansible >= 2.10
- collections:
  - azure.azcollection
  - community.general (optional)
- Azure auth via `az login` (interactive) or env vars:
  AZURE_SUBSCRIPTION_ID, AZURE_CLIENT_ID, AZURE_SECRET, AZURE_TENANT
- Dynatrace API token with `settings.read` and `settings.write` scopes to manage alerting profiles.

Usage:
- set dynatrace_url, dynatrace_env_id and dynatrace_token in group_vars or pass via --extra-vars
- mark target VMs with tag: "{{ vm_tag_key }}: {{ vm_tag_value }}"

Manifest-driven configuration:
- The role reads configuration from `manifest_data.dynatrace` when a `manifest` is passed through the playbook or CI workflows.

Manifest keys mirror role defaults and include:
- `resource_group`, `vm_tag_key`, `vm_tag_value`, `env_id`, `url`, `token`, `alerting_profile_name`, `alerting_profile`, `extension_version`, `install_extension_async`


Split tasks:
- Split tasks: `tasks/main.yml` is now a small orchestrator that imports two focused task files:
  - `tasks/install_extension.yml` — installs the Dynatrace OneAgent VM extension on matched VMs
  - `tasks/manage_alerting.yml` — creates/updates the Dynatrace alerting profile via the Settings API

- Manifest-driven variables: the role prefers values from `manifest_data.dynatrace.*` but will fall back to the role defaults in `defaults/main.yml`.

- Dry-run support: the role supports a `dry_run` flag passed to the playbook. When `dry_run: true` and `manifest_data.dynatrace.skip_in_dry_run` (or role default `skip_in_dry_run`) is true, the role will not perform destructive actions; instead it prints descriptive `[DRY RUN]` debug messages.

- Playbook & CI:
  - Playbook: `ansible/playbooks/enable-dynatrace-for-vm.yml` — uses the `azure_dynatrace` role and accepts `manifest` and `dry_run` as inputs.
  - Workflow: `.github/workflows/ansible-enable-dynatrace.yaml` — dispatchable GitHub Actions workflow that runs the playbook and injects secrets at runtime.

- Secrets and secure values:
  - Dynatrace credentials (token) are **not** stored in the repo. The workflow reads them from GitHub Secrets (`DYNATRACE_TOKEN`) and injects them into the Ansible extra-vars at runtime.
  - The workflow also uses Azure login secrets (e.g. `AZURE_TENANT_ID`, `VM_MIGRATE_MI_CLIENT_ID`) for authenticating the runner — this is expected for managed-identity based login.

Quick example (run locally in dry-run):

ansible-playbook ansible/playbooks/enable-dynatrace.yml -e manifest=phase_1 -e dry_run=true -e dynatrace_token=xxxx

Recommended manifest structure (minimal):
```yaml
manifest_data:
  dynatrace:
    resource_group: null
    vm_tag_key: dynatrace
    vm_tag_value: "true"
    env_id: ""
    url: ""
    alerting_profile_name: "Azure VM Monitoring - Ansible Managed"
    alerting_profile: {}
    extension_version: "1.*"
    install_extension_async: false
    skip_in_dry_run: true
```

Notes and troubleshooting
------------------------
- Ensure `azure.azcollection` is installed on the runner (ansible-galaxy collection install). The role prints an informational message if missing.
- If running outside GitHub Actions, provide Dynatrace credentials `dynatrace_token` via `--extra-vars` or `group_vars`, ideally using `ansible-vault` for the token.
- For large environments, the VM discovery uses resource tag filtering — confirm VMs have the configured tag.
