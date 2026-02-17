# Migration Cutover with Automatic Status Detection

The migration cutover workflow intelligently detects VM migration status and automatically determines whether cutover is needed or if VMs are already migrated.

## 🎯 Key Features

### Intelligent Migration Detection
The workflow **automatically** checks each VM's migration status and:
- ✅ **Skips cutover** for VMs already migrated (status: `AlreadyCompleted`)
- ✅ **Performs cutover** for VMs ready to migrate (status: `Ready to migrate`)
- ✅ **Reports status** for VMs not ready (status: `NotReady`)
- ✅ **Configures patching** for all successfully migrated VMs

**You don't need to specify if cutover should run** - the workflow figures it out automatically!

## Usage

### GitHub Actions Workflow

#### Standard Migration (First Time or Mixed Status)
```yaml
Inputs:
  manifest: "Testing"
  confirmation: "CONFIRM"
  shutdown_source_vm: true
  patching_schedules_file: "patching_schedules/testing_vm_patching_schedules.json"
  dry_run: false
```

**What happens:**
1. 🔍 Checks migration status for each VM
2. ✅ Performs cutover ONLY for VMs that need it
3. ⏭️ Automatically skips VMs already migrated
4. ✅ Configures patching for all migrated VMs
5. 📊 Reports detailed status for each VM

#### Dry Run (Safe Testing)
```yaml
Inputs:
  manifest: "Testing"
  confirmation: "CONFIRM"
  patching_schedules_file: "patching_schedules/testing_vm_patching_schedules.json"
  dry_run: true  # ← Shows what would happen
```

**What happens:**
1. 🔍 Simulates all operations
2. 📋 Shows what would be done for each VM
3. ⛔ Makes NO actual changes
4. 📊 Validates configuration

### Command Line

#### Migration with Automatic Detection
```bash
ansible-playbook ansible/playbooks/migration-cutover.yml \
  -e "manifest=Testing" \
  -e "patching_schedules_file=$PWD/patching_schedules/testing_vm_patching_schedules.json"
```

The playbook automatically:
- Checks each VM's migration status
- Skips cutover for already-migrated VMs
- Performs cutover only where needed
- Configures patching for all migrated VMs

#### Patching Only (Alternative Approach)
If you want to ONLY configure patching without any cutover logic:

```bash
ansible-playbook ansible/playbooks/enable-patching-post-migration.yml \
  -e "manifest=Testing" \
  -e "patching_schedules_file=$PWD/patching_schedules/testing_vm_patching_schedules.json"
```

## Workflow Inputs

| Input | Required | Default | Description |
|-------|----------|---------|-------------|
| `manifest` | Yes | - | Manifest directory name in `ansible/vars/` |
| `confirmation` | Yes | - | Type "CONFIRM" to proceed (safety measure) |
| `shutdown_source_vm` | No | false | Shutdown source VM after successful cutover |
| `patching_schedules_file` | No | "" | Path to JSON file with patching schedules |
| `dry_run` | No | false | Simulate operations without making changes |

**Note:** `skip_cutover` input has been **removed** - the workflow now automatically determines what to do based on VM status!

## Workflow Outputs

| Output | Description | Example Value |
|--------|-------------|---------------|
| `migration_status` | Overall status check | `"checking"` |
| `cutover_needed` | Whether cutover was needed | `true` / `false` |
| `cutover_performed` | Whether cutover executed | `true` / `false` |
| `patching_configured` | Patching configuration status | `true` / `false` / `partial` |
| `vms_migrated` | Count of migrated VMs | `"2"` |
| `vms_pending` | Count of pending VMs | `"1"` |

## Execution Flow

```
GitHub Actions Triggered
    ↓
Validate Inputs
    ↓
For Each VM:
    ↓
    Check Migration Status
    ↓
    ┌─────────────────┴─────────────────┐
    ↓                                   ↓
Already Migrated               Ready to Migrate
(AlreadyCompleted)            (Ready to migrate)
    ↓                                   ↓
Skip Cutover                    Perform Cutover
    ↓                                   ↓
    └─────────────────┬─────────────────┘
                      ↓
            Configure Patching
            (for all migrated VMs)
                      ↓
            Generate Summary & Logs
```

## VM Status Handling

The workflow handles different VM states automatically:

| Migration State | Description | Action Taken |
|----------------|-------------|--------------|
| `Ready to migrate` | VM is replicated and ready | ✅ Perform cutover |
| `MigrationSucceeded` / `Migrated` | VM already migrated | ⏭️ Skip cutover, configure patching |
| `Not Found` | VM not in replication list | ⚠️ Skip and report |
| `NotReady` | VM not ready for migration | ⚠️ Skip and report |
| `Failed` | Migration failed previously | ❌ Report error |

## Patching Configuration

### Patching Schedules File

Located in `patching_schedules/` directory. Example:

```json
{
  "vmcuwinwebd02": {
    "maintenance_configuration": "weekly-sunday-2am",
    "frequency": "Weekly",
    "day_of_week": "Sunday",
    "time_of_day": "02:00",
    "duration": "03:00",
    "reboot_setting": "IfRequired",
    "description": "Web server - patched weekly on Sunday at 2 AM"
  }
}
```

### What Gets Configured

For each successfully migrated VM:
1. **Patch Mode**: Set to `AutomaticByPlatform`
2. **Maintenance Configuration**: Created with schedule from JSON
3. **Assignment**: VM linked to maintenance configuration
4. **Reboot Policy**: Per-VM setting from JSON

## Workflow Summary Page

After execution, the workflow summary shows:

- ✅ **Configuration used**
- 🔍 **Intelligent processing details**
  - Which VMs were already migrated (skipped)
  - Which VMs had cutover performed
  - Which VMs were not ready
- ✅ **Patching status** for each VM
- 📋 **Next steps** guidance
- 🔗 **Links** to Azure portal resources

## Example Scenarios

### Scenario 1: All VMs Need Migration
**Situation:** Running cutover for the first time

**Result:**
```
VM Status:
  vmcuwinwebd02: Ready to migrate → Cutover performed → Patching configured
  dca-dev7048: Ready to migrate → Cutover performed → Patching configured

Summary: 2 cutover operations, 2 patching configurations
```

### Scenario 2: Mixed Status
**Situation:** Some VMs already migrated, some need migration

**Result:**
```
VM Status:
  vmcuwinwebd02: Already migrated → Cutover skipped → Patching configured
  dca-dev7048: Ready to migrate → Cutover performed → Patching configured

Summary: 1 cutover operation, 2 patching configurations
```

### Scenario 3: All VMs Already Migrated
**Situation:** Re-running workflow on migrated VMs (e.g., to add patching)

**Result:**
```
VM Status:
  vmcuwinwebd02: Already migrated → Cutover skipped → Patching configured
  dca-dev7048: Already migrated → Cutover skipped → Patching configured

Summary: 0 cutover operations, 2 patching configurations
```

## Logs and Artifacts

Each run produces:
- `cutover.log` - Full execution log with per-VM status
- `ansible_extra_vars.json` - Variables used

**Retention:** 30 days

## Validation Before Running

1. **Manifest exists**: `ansible/vars/<manifest>/manifest.yml`
2. **Patching JSON created**: `patching_schedules/<file>.json`
3. **VM names match**: Lowercase in JSON, matches manifest
4. **Schedules validated**: No conflicts, appropriate times
5. **Dry-run executed**: Test first with `dry_run: true`

## Troubleshooting

### All VMs Skipped
**Symptom:** All VMs show "AlreadyCompleted" or "Skipped"

**Resolution:**
- This is expected if VMs are already migrated
- Check Azure portal to verify VM status
- If patching needed, this will still be configured

### Some VMs Skipped, Some Migrated
**Symptom:** Mixed results

**Resolution:**
- This is normal for partial migrations
- Check `cutover.log` for detailed status per VM
- Already-migrated VMs will get patching configured

### Patching Not Configured
**Symptom:** Cutover succeeded but no patching

**Resolution:**
- Verify `patching_schedules_file` was provided
- Check file exists and is valid JSON
- Ensure VM names in JSON match manifest (case-sensitive)

## Azure Portal Verification

After workflow completion, verify:

1. **Azure Migrate** → Projects → Check migration status
2. **Virtual Machines** → Verify VMs exist and are running
3. **Virtual Machines** → Select VM → **Updates** → Verify patch mode = `AutomaticByPlatform`
4. **Update Manager** → **Maintenance Configurations** → Verify schedules exist
5. **Update Manager** → **Machines** → Verify VM assignments

## Best Practices

1. ✅ **Always run dry-run first** in new environments
2. ✅ **Use descriptive maintenance config names** in JSON
3. ✅ **Stagger patching windows** for high-availability setups
4. ✅ **Monitor first patch window** after configuration
5. ✅ **Keep source VMs** until target VMs are fully validated

## Support

For issues or questions:
1. Check workflow summary and logs (download artifacts)
2. Review `cutover.log` for per-VM details
3. Verify VM status in Azure portal
4. Check `patching_schedules/README.md` for JSON format help
5. Contact DevOps team with workflow run URL
