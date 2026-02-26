## Azure Migrate Role

### Table of contents
- [Description](#description)
- [Requirements](#requirements)
- [Role Variables (selected)](#role-variables-selected)
- [Outputs](#outputs)
- [Example Plays](#example-plays)
- [Notes](#notes)
- [Troubleshooting](#troubleshooting)
- [Local manual testing: running the playbook](#local-manual-testing-running-the-playbook)
 - [Manifest-driven configuration](#manifest-driven-configuration)

### Description
Orchestrates common Azure Migrate actions for discovered servers:
- **list_projects**: Enumerate Azure Migrate projects in a resource group.
- **start_replication**: Initiate server replication for one or more machines into a target resource group/network using Az PowerShell `Az.Migrate`.
- **test_migration**: Start test migration for VMs with active replication to validate migration before cutover.
- **stop_replication**: Stop replication for VMs (requires vm_names or STOP_ALL)
- **cutover**: Placeholder for future implementation.

Authentication can be handled automatically via PowerShell (managed identity, service principal, or bridged Azure CLI token) or skipped if an existing context is already established.

### Requirements
- **Ansible**: >= 2.14
- **Collections**: `azure.azcollection`
- **CLI/Modules on controller/runner**:
  - PowerShell 7 (`pwsh`)
  - Azure CLI (`az`)
  - Az PowerShell modules: `Az.Accounts`, `Az.Migrate`
- Azure credentials: Managed Identity, Service Principal env vars, or an `az login` session

### Role Variables (selected)
- **Required (by action)**
  - For `start_replication`, required values are typically sourced from manifest (see Manifest-driven configuration): `azure_migrate_project_name`, `target_subscription_id`, `target_resource_group`.
  - `vm_name` (cutover; not yet implemented)

- **Behavior**
  - `migration_action`: One of `start_replication`, `stop_replication`, `test_migration`, `cutover`, `list_projects`, `get_replication_status` (default: `start_replication`)
  - `migration_actions`: Allowed values list; used for validation
  - `api_version_migrate`: API version used for `list_projects` (default: `2020-05-01`)

- **Selection and iteration**
  - Manifest-driven: the role loads `ansible/vars/{manifest}/manifest.yml` and iterates VMs from `vms`. Each VM entry can include overrides for replication parameters.

- **Azure Migrate project scoping**
  - `azure_migrate_project_resource_group`: If omitted, defaults to `target_resource_group`

- **Replication parameters**
  - `target_network_id` (required): Full Azure resource ID of the target virtual network (e.g., `/subscriptions/.../resourceGroups/.../providers/Microsoft.Network/virtualNetworks/vnet-name`)
  - `target_subnet_name` (required): Name of the subnet within the target virtual network
  - `os_disk_scsi_id` (default: `scsi0:0`)
  - `test_network_id` (required for test_migration): Full Azure resource ID of the test virtual network for test migration validation
  - `target_vm_name` (required): Target VM name must follow the pattern: `vm{region}{os}{appname}{env}{instance}` (exactly 13 characters)
    - Pattern breakdown:
      - `vm`: always "vm" (2 chars)
      - `region`: Azure region code - `cu` (Central US) or `e2` (East US 2) (2 chars)
      - `os`: Operating system - `win` (Windows) or `lnx` (Linux) (3 chars)
      - `appname`: Abbreviated app name (exactly 3 chars)
      - `env`: Environment - `p` (Production), `d` (Development), or `t` (Test) (1 char)
      - `instance`: Instance number 00-99 (2 chars)
    - Examples:
      - `vmcuwinwebp01`: CP, Central US, Windows, Web server, Production, 01
      - `vme2lnxsqlp02`: CP, East US 2, Linux, SQL Server, Production, 02
      - `vmcuwinmond03`: CP, Central US, Windows, Monitoring, Development, 03
      - `vme2lnxfilp01`: CP, East US 2, Linux, File server, Production, 01
    - See `validate_target_vm_name` function in `filter_plugins/vm_name_filters.py` for validation details
  - `target_vm_size` (default set in PowerShell script: `Standard_DS2_v2`)
  - `target_license_type` (default set in PowerShell script: `NoLicenseType`)
  - `target_disk_type` (default set in PowerShell script: `Standard_LRS`)

- **OS version validation**
  - `skip_os_version_check`: When false (default), validates that VMs meet minimum OS version requirements before starting replication. Set to true to bypass validation.
  - `min_os_versions`: Configurable minimum OS version requirements
    - `windows_server_build`: Minimum Windows Server build number (default: 17763 for Windows Server 2019)
    - `rhel_major`: Minimum RHEL major version (default: 8)

### Outputs
- `list_projects` sets and displays:
  - `migrate_projects_response` (raw)
  - `migrate_projects_list` (normalized list)
- `start_replication` registers and displays:
  - `replication_output`

### Example Plays

#### List Azure Migrate projects (manifest-driven)
```yaml
- hosts: localhost
  gather_facts: false
  roles:
    - role: azure_migrate
      vars:
        migration_action: list_projects          # action: list available projects
        manifest: "{{ manifest }}"               # pass through manifest variable (never hardcode)
        api_version_migrate: 2020-05-01          # optional; defaults to this value
```

**Command line usage:**
```bash
# User specifies which manifest to load at runtime
ansible-playbook my-playbook.yml -e "manifest=phase_1"
# or for a different phase
ansible-playbook my-playbook.yml -e "manifest=phase_2"
```

#### Start replication (manifest-driven)
```yaml
- hosts: localhost
  gather_facts: false
  roles:
    - role: azure_migrate
      vars:
        migration_action: start_replication            # action: start replication
        manifest: "{{ manifest }}"                          # pass through manifest variable (never hardcode)
```

**Command line usage:**
```bash
# User specifies which manifest to load at runtime
ansible-playbook my-playbook.yml -e "manifest=phase_1"
# or for a different phase
ansible-playbook my-playbook.yml -e "manifest=phase_2"
```

#### Start replication with OS version validation bypassed
```yaml
- hosts: localhost
  gather_facts: false
  roles:
    - role: azure_migrate
      vars:
        migration_action: start_replication            # action: start replication
        manifest: "{{ manifest }}"                          # pass through manifest variable (never hardcode)
        skip_os_version_check: true                    # bypass OS version validation
```

#### Start replication with custom minimum OS versions
```yaml
- hosts: localhost
  gather_facts: false
  roles:
    - role: azure_migrate
      vars:
        migration_action: start_replication            # action: start replication
        manifest: "{{ manifest }}"                          # pass through manifest variable (never hardcode)
        min_os_versions:
          windows_server_build: 20348                  # require Windows Server 2022 (build 20348)
          rhel_major: 9                               # require RHEL 9 or later
```

#### Start test migration (manifest-driven)
```yaml
- hosts: localhost
  gather_facts: false
  roles:
    - role: azure_migrate
      vars:
        migration_action: test_migration                # action: start test migration
        manifest: "{{ manifest }}"                      # pass through manifest variable (never hardcode)
```

**Command line usage:**
```bash
ansible-playbook ansible/playbooks/start-test-migration.yml \
  -e "manifest=phase_1"
```

**Note**: Test migration requires `test_network_id` to be configured in the manifest (global or per-VM).

### Notes
- The role performs early validation and will fail if required variables are missing for the chosen action.
- `cutover` is scaffolded but not yet implemented in tasks.
- **Authentication**: This role expects Azure authentication to be handled externally. Run `az login` before executing the playbook locally, or use GitHub Actions which handles authentication automatically.
- `start_replication` invokes the `Az.Migrate` cmdlet `New-AzMigrateServerReplication` under the hood via `files/start_replication.ps1`. Ensure required modules are installed on the runner.
- **Test Migration**: `test_migration` starts a test migration for VMs with active replication. Requires `test_network_id` in the manifest. The replication object ID is automatically extracted from the replication status check.
- **OS Version Validation**: By default, the role validates that VMs meet minimum OS version requirements before starting replication. Default requirements are Windows Server 2019+ (build 17763) and RHEL 8+. These requirements are configurable via the `min_os_versions` variable. Use `skip_os_version_check: true` to bypass this validation if needed.
- **Idempotency**: Starting replication now includes pre-checks to skip VMs that already have replication enabled, making it safe to re-run.

### Troubleshooting
- Missing modules errors (e.g., `Az.Migrate`): install with `Install-Module -Name Az.Migrate -Scope CurrentUser -Force`.
- VM not found: confirm the `vm_name` matches the Azure Migrate discovered server DisplayName in the specified project/RG.



### Local manual testing: running the playbook
The examples below show how to run the role's playbook locally. **Important**: Authenticate to Azure first using `az login` before running these commands.

#### Prerequisites
- Ansible installed (>= 2.14)
- Azure CLI (`az`) installed and authenticated (e.g., `az login`)
- Required Az modules if using PowerShell-based tasks on the controller: `Az.Accounts`, `Az.Migrate`

#### List Azure Migrate projects (manifest-driven)
```bash
# Show projects from manifest defaults
ansible-playbook ansible/playbooks/start-migration-replication.yml \   # playbook entry point
  -e "migration_action=list_projects" \                                  # action
  -e "manifest=phase_1" \                                                 # selects ansible/vars/phase_1/manifest.yml
  # (auth is skipped by default; ensure you have an Az context)
```

#### Start replication (manifest-driven)
```bash
# Start replication using manifest defaults and vms list
ansible-playbook ansible/playbooks/start-migration-replication.yml \   # playbook entry point
  -e "migration_action=start_replication" \                              # action
  -e "manifest=phase_1"                                                   # selects ansible/vars/phase_1/manifest.yml
```

### Manifest-driven configuration
The role loads manifest from `ansible/vars/{manifest}/manifest.yml` at runtime.

**Example structure (e.g., `ansible/vars/phase_1/manifest.yml`):**

```yaml
# Global defaults (used unless overridden per-VM)
azure_migrate_project_name: my-migrate-proj
azure_migrate_project_resource_group: rg-migrate
target_subscription_id: 00000000-0000-0000-0000-000000000000
target_resource_group: rg-target

target_virtual_network_name: vnet-target
target_subnet_name: subnet-apps
target_vm_size: Standard_D4s_v5
target_license_type: NoLicenseType
target_disk_type: Premium_LRS
os_disk_scsi_id: scsi0:0

# Test network for test_migration action
test_network_id: /subscriptions/.../resourceGroups/.../providers/Microsoft.Network/virtualNetworks/vnet-test

# List of VMs to replicate
vms:
  - name: app01
    target_vm_name: vmcuwinappp01  # Required: must follow pattern vm{region}{os}{appname}{env}{instance}

  - name: app02
    target_vm_name: vme2lnxappd02  # Required: must follow pattern vm{region}{os}{appname}{env}{instance}
    target_vm_size: Standard_D2s_v5
    target_license_type: Windows_Server

  - name: db01
    target_vm_name: vmcuwinsqlp01  # Required: must follow pattern vm{region}{os}{appname}{env}{instance}
    target_resource_group: rg-target-db
    target_virtual_network_name: vnet-target-db
    target_subnet_name: subnet-db
    target_disk_type: Premium_LRS
```

**Manifest Organization:**
- Create separate manifest files for different migration phases: `phase_1/manifest.yml`, `phase_2/manifest.yml`, etc.
- Each manifest can contain different VMs, target configurations, and Azure Migrate project settings
- Specify which manifest to use at runtime: `-e "manifest=phase_1"` or `-e "manifest=phase_2"`

**Configuration Notes:**
- The role prefers per-VM keys when present; otherwise it falls back to global defaults.
- VM entries use `name`, which maps to the Azure Migrate discovered server DisplayName.

Notes:
- If both `vms_selected` and `vm_name` are provided, `vms_selected` takes precedence.
- `list_projects` prints `migrate_projects_list`; `start_replication` prints `replication_output`.
