# Uninstall On-Prem Tools – Playbook Review & GH Testing

## Summary

The **uninstall-onprem-tools** playbook uses the **onprem-tools-uninstallation** role to remove specified Windows software (e.g. Puppet Agent, VMware Tools, EMC PowerPath, HP Insight Management Agents) from Azure VMs via **Azure Run Command**, with no WinRM or direct network access required.

---

## What Was Missing / What Was Fixed

### 1. **Real uninstall vs dry run**

- **Playbook** passes `dry_run` from the GitHub workflow (`ansible_extra_vars.json`). The workflow **default is `dry_run: false`** for `workflow_dispatch` (you can still set it to `true` when triggering).
- **To actually uninstall**: Run the workflow with **Dry run = false** (unchecked). With `dry_run: true`, the playbook only does lookups and prints what it would do; it does **not** call Azure Run Command or uninstall anything.

### 2. **Idempotency (running twice on the same VM)**

- The PowerShell script looks up each tool in the registry. If a tool is **not present** (e.g. already uninstalled), it returns `Result: 'NotFound'`.
- **Second run**: After a successful first run, all requested tools are gone, so the script returns `NotFound` for each. The role now:
  - Detects when **all** results are `NotFound`.
  - Prints: **"All requested tools are already uninstalled or not present on &lt;vm_name&gt;. No action taken. (Run is idempotent.)"**
  - Lists each tool with `→ NotFound` so the log clearly shows “already uninstalled / not present.”

So the automation **does** indicate that software was already uninstalled when you run it a second time.

### 3. **RunCommand output parsing**

- Azure returns `value[0].message`, which may be either a JSON **array** (PowerShell `ConvertTo-Json` output) or a JSON-**encoded string** containing that array.
- The role now parses both: if the first `from_json` is a string, it parses again to get the array; otherwise it uses the array. This avoids failures when the CLI wraps the message as a string.

### 4. **Workflow step name**

- The step that runs the playbook was renamed from **"Run playbook - enable update manager"** to **"Run playbook - uninstall onprem tools"**.

### 5. **Fail if VM not found (hardening)**

- The role now **fails the play** when the VM is not found in the resource group, unless `fail_if_vm_not_found: false` is set. Default is `true` (fail). This avoids silently skipping missing VMs and makes pipeline failures explicit. The variable is defined in `ansible/roles/onprem-tools-uninstallation/defaults/main.yml`.

### 6. **VM name: use target_vm_name when present**

- The playbook uses **`item.target_vm_name | default(item.name)`** for the Azure VM name. Manifests where `name` is the on-prem name and `target_vm_name` is the Azure resource name (e.g. test_vm_migration, migration manifests) now target the correct VM without changing manifest data.

---

## What You Need to Test on GitHub Actions

To consider the automation “done” you need at least one **real** run that uninstalls software and one **second** run that shows idempotency.

### Prerequisites

- **Manifest**: A manifest under `ansible/vars/<manifest>/manifest.yml` with:
  - `target_subscription_id`, `target_resource_group`
  - `vms` list (at least one Windows VM that exists in that subscription/RG)
  - `uninstall_tools_list` (e.g. Puppet Agent, VMware Tools, etc.)
- **Environment**: The workflow uses `environment: dev` and a self-hosted runner with Azure login (managed identity). The runner must have permission to run `az vm run-command invoke` on the target VMs.
- **VM**: At least one VM in the manifest should have **at least one** of the tools in `uninstall_tools_list` installed (so the first run has something to uninstall).

### Test 1: Dry run (no changes)

1. Trigger **Ansible-Uinstall-Onprem-Tools** via **Run workflow**.
2. Set **Manifest** to your test manifest (e.g. `uninstall_tools`).
3. Set **Dry run** to **true**.
4. Run the job.
5. **Expect**: No Azure Run Command execution; log shows “Dry Run Summary” and “Would execute uninstall…” for each VM. No software is removed.

### Test 2: Real uninstall (first run)

1. Trigger the workflow again with the **same** manifest.
2. Set **Dry run** to **false**.
3. Run the job.
4. **Expect**:
   - For each VM, “Uninstall Summary” with per-tool lines: `Name → Removed` (or `NotFound` if not installed).
   - At least one “Uninstalled &lt;name&gt;” for tools that were present and removed.
   - No playbook failure (unless VM missing or Run Command permission issue).

### Test 3: Idempotency (second run on same VM)

1. Trigger the workflow **again** with the **same** manifest and **Dry run = false** (same as Test 2).
2. **Expect**:
   - For each VM, “Uninstall Summary” with each tool showing `→ NotFound`.
   - Message: **“All requested tools are already uninstalled or not present on &lt;vm_name&gt;. No action taken. (Run is idempotent.)”**
   - Per-tool lines: `  &lt;Name&gt; → NotFound`.
   - Message: “No tools from the list were installed on &lt;vm_name&gt; (or were already uninstalled).”

If Tests 2 and 3 behave as above, the automation is **actually uninstalling** and **correctly indicating** when software is already uninstalled.

---

## Playbook / Role Layout (reference)

| Component | Purpose |
|----------|--------|
| `ansible/playbooks/uninstall-onprem-tools.yml` | Loads manifest, loops over `manifest_data.vms`, calls role per VM with `uninstall_via_azure_runcommand`. |
| `ansible/roles/onprem-tools-uninstallation/tasks/uninstall_via_azure_runcommand.yml` | Builds inline PowerShell, invokes `az vm run-command invoke`, parses JSON result, prints summary and idempotency message. |
| `ansible/vars/uninstall_tools/manifest.yml` | Example manifest with `uninstall_tools_list` and `vms`. |
| `.github/workflows/uninstall-onprem-tools.yml` | workflow_dispatch; passes `manifest` and `dry_run`; runs playbook with `-e @ansible_extra_vars.json`. |

---

## Hardening and best practices

- **Fail if VM not found**: Enabled by default. The role fails when the VM is not found (`fail_if_vm_not_found: true` in role defaults). Set `fail_if_vm_not_found: false` to skip missing VMs.
- **VM name**: The playbook uses `target_vm_name` when present, otherwise `name`.
- **Logs**: The workflow uploads `ansible/logs/UninstallTools_*.log` if present; ensure the playbook or ansible.cfg is configured to write there if you want logs in the artifact.
