# Dynatrace Configuration Workflow - Implementation Summary

## Overview

Created a complete GitHub Actions workflow and Ansible automation to configure Dynatrace extension on Azure VMs with migration status verification.

## Created Files

### 1. GitHub Actions Workflow
**File**: `.github/workflows/ansible-configure-dynatrace.yaml`

**Features**:
- ✅ Single workflow for Windows, Linux, or both OS types
- ✅ User inputs: manifest name, OS type (dropdown), dry_run flag
- ✅ Conditional job execution based on OS selection
- ✅ Parallel execution when "both" is selected
- ✅ Automatic log upload with 90-day retention
- ✅ Summary job displaying overall results

### 2. Ansible Playbooks

#### Windows Playbook
**File**: `ansible/playbooks/configure-dynatrace-windows.yml`
- Configures Dynatrace on Windows VMs
- Uses dynatrace role with os_type: windows

#### Linux Playbook
**File**: `ansible/playbooks/configure-dynatrace-linux.yml`
- Configures Dynatrace on Linux VMs
- Uses dynatrace role with os_type: linux

### 3. Dynatrace Role (ansible/roles/dynatrace/)

#### PowerShell Scripts

**configure_dynatrace_windows.ps1**
- Checks VM running state
- Detects existing Dynatrace extension
- Installs `dynatrace.ruxit/oneAgentWindows` extension
- Returns JSON result with status
- Supports dry-run mode

**configure_dynatrace_linux.ps1**
- Checks VM running state
- Detects existing Dynatrace extension
- Installs `dynatrace.ruxit/oneAgentLinux` extension
- Returns JSON result with status
- Supports dry-run mode

#### Ansible Tasks

**main.yml**
- Entry point for the role
- Loads manifest and processes each VM

**process_vm.yml**
- **Step 1**: Checks migration status using `get_replication_status.ps1`
- Verifies `MigrationState == "MigrationSucceeded"`
- **Stops execution** if migration not completed with detailed error message
- **Step 2**: Calls OS-specific configuration if migration succeeded

**configure_windows.yml**
- Executes Windows PowerShell script
- Reads and displays JSON results
- Logs operation details
- Handles success/failure appropriately

**configure_linux.yml**
- Executes Linux PowerShell script
- Reads and displays JSON results
- Logs operation details
- Handles success/failure appropriately

#### Configuration Files

**defaults/main.yml**
- Default variables for Dynatrace configuration
- dry_run, os_type, extension version settings

**meta/main.yml**
- Role metadata and dependencies

**README.md**
- Comprehensive documentation
- Usage examples
- Error handling guide
- Troubleshooting tips

## Workflow Execution Flow

### User Input Phase
1. User navigates to GitHub Actions
2. Selects "Ansible-Configure-Dynatrace" workflow
3. Provides inputs:
   - Manifest name (e.g., `demo`, `phase_1`)
   - OS Type: Windows, Linux, or Both
   - Dry Run: true/false

### Execution Phase

#### For Each VM in Manifest:

**Phase 1: Migration Status Verification**
```
Check Azure Migrate replication status
↓
Read MigrationState from result
↓
Is MigrationState == "MigrationSucceeded"?
├─ YES → Continue to Phase 2
└─ NO  → STOP with error message showing current state
```

**Phase 2: Dynatrace Configuration** (only if Phase 1 passed)
```
Check VM power state
↓
Is VM running?
├─ NO  → Skip with message
└─ YES → Check existing extension
    ↓
    Extension already installed?
    ├─ YES → Report as AlreadyInstalled
    └─ NO  → Install Dynatrace extension
        ↓
        Read installation result
        ↓
        Display detailed status
        ↓
        Write logs
```

### Output Phase
- Upload logs to GitHub Actions artifacts
- Display summary for all VMs
- Show success/failure counts
- Provide next steps

## Key Features

### ✅ Migration Status Check
- **Verifies** VM completed migration before configuration
- **Reads** MigrationState from Azure Migrate
- **Requires** MigrationState = "MigrationSucceeded"
- **Stops** execution with clear message if not met

### ✅ Extension Installation
- **Detects** existing Dynatrace extensions (idempotent)
- **Validates** VM is running before installation
- **Supports** both Windows and Linux VMs
- **Returns** detailed JSON results

### ✅ Dry Run Mode
- **Tests** entire workflow without changes
- **Validates** all prerequisites
- **Shows** what would be installed
- **Confirms** migration status

### ✅ Error Handling
- **Comprehensive** error messages
- **Actionable** troubleshooting steps
- **Context-aware** failure descriptions
- **Graceful** degradation

### ✅ Logging
- **Timestamped** operation logs
- **Detailed** PowerShell output
- **90-day** retention in GitHub
- **Per-VM** result tracking

## Result Structure

Each VM returns a structured result:

```json
{
  "VMName": "app-server-01",
  "ResourceGroup": "rg-production",
  "Success": true,
  "ExtensionStatus": "Installed",
  "ExtensionName": "DynatraceOneAgent",
  "ExtensionVersion": "2.0",
  "Message": "Dynatrace extension installed successfully",
  "StartTime": "2024-01-01 10:00:00",
  "EndTime": "2024-01-01 10:05:00",
  "Error": null
}
```

### Extension Status Values
- `Installed` - Successfully installed
- `AlreadyInstalled` - Already present, skipped
- `DryRun` - Dry run mode, no changes
- `Failed` - Installation failed
- `Skipped` - VM not running or other condition

## Usage Examples

### Example 1: Configure Windows VMs Only
```
Workflow Inputs:
- manifest: demo
- os_type: windows
- dry_run: false
```

### Example 2: Test Linux VMs (Dry Run)
```
Workflow Inputs:
- manifest: phase_1
- os_type: linux
- dry_run: true
```

### Example 3: Configure All VMs
```
Workflow Inputs:
- manifest: phase_1
- os_type: both
- dry_run: false
```

## Error Scenarios

### Scenario 1: Migration Not Completed
```
❌ Cannot configure Dynatrace extension for VM 'app-server-01'

Migration Status: MigrationInProgress
Migration Description: Migration in progress

Dynatrace extension can only be configured on VMs that have 
completed migration. Current migration state must be 
'MigrationSucceeded' to proceed.

Required: MigrationState = MigrationSucceeded
Current:  MigrationState = MigrationInProgress

Please complete the migration for this VM before attempting 
to configure Dynatrace.

Next steps:
1. Complete the VM migration using the migration-cutover workflow
2. Verify the VM is in 'MigrationSucceeded' state
3. Re-run this Dynatrace configuration workflow
```

### Scenario 2: VM Not Running
```
⚠️  VM is not running (current state: stopped)

Extension can only be installed on running VMs.
Please start the VM and re-run this workflow.
```

### Scenario 3: Extension Already Installed
```
ℹ️  Dynatrace extension is already installed (version: 2.0)

No action needed. Extension is already configured.
```

## Next Steps for Users

1. **Complete VM Migration**
   - Ensure all VMs have MigrationState = MigrationSucceeded
   - Use migration-cutover workflow if needed

2. **Run Dry Run First**
   - Test with dry_run: true
   - Verify all VMs pass migration status check
   - Review what would be installed

3. **Execute Real Configuration**
   - Run with dry_run: false
   - Monitor job progress in GitHub Actions
   - Review uploaded logs

4. **Verify in Azure**
   - Check VMs in Azure Portal
   - Confirm Dynatrace extension is listed
   - Verify Dynatrace console shows monitoring data

## Files Structure

```
.github/workflows/
└── ansible-configure-dynatrace.yaml

ansible/
├── playbooks/
│   ├── configure-dynatrace-windows.yml
│   └── configure-dynatrace-linux.yml
└── roles/
    └── dynatrace/
        ├── README.md
        ├── defaults/
        │   └── main.yml
        ├── files/
        │   ├── configure_dynatrace_windows.ps1
        │   └── configure_dynatrace_linux.ps1
        ├── meta/
        │   └── main.yml
        └── tasks/
            ├── main.yml
            ├── process_vm.yml
            ├── configure_windows.yml
            └── configure_linux.yml
```

## Testing Checklist

- [ ] Test with dry_run: true (Windows)
- [ ] Test with dry_run: true (Linux)
- [ ] Test with dry_run: true (Both)
- [ ] Verify migration status check works
- [ ] Test with VM not yet migrated (should fail gracefully)
- [ ] Test with VM already migrated (should proceed)
- [ ] Test with VM stopped (should skip)
- [ ] Test with extension already installed (should detect)
- [ ] Test actual installation (dry_run: false)
- [ ] Verify logs are uploaded
- [ ] Confirm Dynatrace console receives data

## Maintenance Notes

- Dynatrace extension versions may need updates
- PowerShell scripts use Az.Compute module
- Requires access to Azure Migrate for status checks
- Logs retained for 90 days in GitHub Actions

---

**Created**: November 2024
**Author**: Cloud Platform Migration Team
**Status**: Ready for Testing
