onprem-tools-uninstallation
=================================

This role uninstalls specified Windows packages on Azure VMs via **Azure Run Command** (no WinRM or direct network access required). It reads the list of packages from the migration manifest (`ansible/vars/<manifest>/manifest.yml`) under the key `uninstall_tools_list`.

Usage
-----
- The playbook `ansible/playbooks/uninstall-onprem-tools.yml` loads the manifest and runs this role once per VM in `manifest_data.vms`.
- Each VM is targeted by **Azure VM resource name**: the playbook uses `item.target_vm_name` when present, otherwise `item.name`.
- Set `dry_run: false` (e.g. via workflow input or extra vars) to perform real uninstalls; default is dry run in the role.

Variables
---------
- `manifest` (required): name of the manifest folder under `ansible/vars/` which contains `manifest.yml`.
- `azure_subscription_id`, `azure_resource_group`, `vm_name` (required for RunCommand path): set by the playbook from the manifest.
- `uninstall_list`: list of display names to uninstall; set from `manifest_data.uninstall_tools_list`.
- `dry_run` (optional): boolean; when true, no Run Command is invoked (default true in role).
- `fail_if_vm_not_found` (optional): when true, the play fails if the VM is not found in the resource group (default true). Set to false to skip missing VMs.

What it does (Azure RunCommand path)
------------------------------------
1. Queries the VM via Azure API; optionally fails if the VM is not found (`fail_if_vm_not_found`).
2. Builds an inline PowerShell script that looks up uninstall strings in the registry and runs them (or reports NotFound when already uninstalled).
3. Invokes `az vm run-command invoke` to run the script on the VM.
4. Parses the JSON output and prints a per-VM summary; on a second run, reports idempotency (all tools already uninstalled or not present).

Notes
-----
- The primary execution path is **Azure Run Command** (tasks in `uninstall_via_azure_runcommand.yml`). The role also includes WinRM-oriented tasks (`uninstall_tools_windows.yml`) for direct host execution if needed.
- The GitHub Actions workflow passes `manifest` and `dry_run`; trigger with dry run unchecked to perform real uninstalls. See `docs/UNINSTALL_ONPREM_REVIEW.md` for testing steps.
