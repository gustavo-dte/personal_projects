# Workflow Output: Console vs Artifacts

## ✅ Current Behavior: Console Output Only

All workflow output is now **displayed in the console logs** - no artifacts are saved.

### Why Console Output?

1. **Immediate Visibility** - See results in real-time
2. **No Download Required** - Everything visible in the browser
3. **Searchable** - Use browser search to find specific VMs or errors
4. **Always Available** - Part of the workflow run, no expiration

---

## 📊 Where to Find Output

### During Execution
Watch the **"Run migration cutover with automatic skip logic"** step to see:
- Each VM being processed
- Migration status for each VM
- Cutover operations (performed or skipped)
- Patching configuration for each VM
- Success/failure messages

### After Execution

#### 1. **Console Logs** (Primary)
Navigate to: **Actions → Workflow Run → Job → Expand Steps**

Look for:
```
Run migration cutover with automatic skip logic
  ↓
[Full Ansible playbook output]
  - VM status checks
  - Cutover operations  
  - Patching configuration
  - Summary messages
```

#### 2. **Workflow Summary** (Overview)
Navigate to: **Actions → Workflow Run → Summary tab**

Shows:
- Configuration used
- High-level results
- Next steps
- Link to Azure portal verification

---

## 📋 What You'll See in Console Output

### Example Output Structure

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MIGRATION CUTOVER OPERATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PLAY [Perform migration cutover] *******************************

TASK [Check replication status for vmcuwinwebd02] **************
✅ VM 'vmcuwinwebd02' is already migrated
   Status: MigrationSucceeded
   Migration Description: Migrated
   → Skipping cutover (already completed)

TASK [Configure patching for vmcuwinwebd02] ********************
✅ Patch mode set to AutomaticByPlatform
✅ Maintenance configuration 'weekly-sunday-2am' created
✅ Assigned to VM 'vmcuwinwebd02'

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Post-cutover patching configured for: vmcuwinwebd02
  Patch mode    : AutomaticByPlatform
  Schedule      : Week Sunday at 02:00
  Duration      : 03:00
  Reboot policy : IfRequired
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TASK [Check replication status for dca-dev7048] ****************
✅ VM 'dca-dev7048' is ready for migration
   → Proceeding with cutover

TASK [Perform cutover for dca-dev7048] *************************
✅ Cutover initiated for 'dca-dev7048'
   Job ID: abc-123-def-456

TASK [Configure patching for dca-dev7048] **********************
✅ Patch mode set to AutomaticByPlatform
✅ Maintenance configuration 'weekly-saturday-midnight' created
✅ Assigned to VM 'dca-dev7048'

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CUTOVER SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total VMs: 2
  Successful: 2
  Skipped: 1 (already migrated)
  Failed: 0

VM Details:
  vmcuwinwebd02: success (AlreadyCompleted)
  dca-dev7048: success (Initiated)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 🔍 How to Read the Output

### Key Indicators

| Symbol | Meaning |
|--------|---------|
| ✅ | Success - operation completed |
| ⚠️ | Warning - non-critical issue |
| ❌ | Error - operation failed |
| ⏭️ | Skipped - operation not needed |
| 🔄 | In Progress - operation running |

### Status Messages

| Message | What It Means |
|---------|---------------|
| `AlreadyCompleted` | VM already migrated, cutover skipped |
| `Initiated` | Cutover started successfully |
| `Skipped` | VM not ready, operation skipped |
| `NotReady` | VM cannot be migrated yet |
| `Failed` | Operation encountered an error |

---

## 💡 Tips for Using Console Logs

### 1. Use Browser Search
Press `Ctrl+F` (or `Cmd+F` on Mac) to search for:
- Specific VM names: `vmcuwinwebd02`
- Status indicators: `success`, `failed`, `skipped`
- Specific operations: `cutover`, `patching`

### 2. Expand/Collapse Steps
Click on step names to expand/collapse sections:
- Expand to see detailed output
- Collapse to focus on other steps

### 3. Download Raw Logs (If Needed)
While no artifacts are saved, you can still:
1. Click the "⋮" menu on the workflow run
2. Select "Download log archive"
3. Get complete console output as text files

### 4. Share Links
Share the workflow run URL with team members:
```
https://github.com/org/repo/actions/runs/12345678
```

---

## 📝 Comparison: Before vs After

### Before (Artifacts Approach)
```
Run completes
  ↓
Download artifacts
  ↓
Unzip files
  ↓
Open cutover.log in text editor
  ↓
Search for information
```

### After (Console Approach)
```
Run completes
  ↓
View console logs in browser
  ↓
Search with Ctrl+F
  ↓
Done!
```

---

## 🎯 When You Need Specific Information

### To Find VM Status
Search for: `VM Details:` or the VM name

### To Find Patching Config
Search for: `Post-cutover patching configured`

### To Find Errors
Search for: `❌` or `failed` or `ERROR`

### To Find Summary
Search for: `CUTOVER SUMMARY` or `Migration cutover summary`

---

## 🆘 Troubleshooting

### "I can't find the logs"
**Solution:** 
1. Go to Actions tab
2. Click on the workflow run
3. Click on the job name (usually "migration-cutover")
4. Expand the step: "Run migration cutover with automatic skip logic"

### "The output is too long"
**Solution:**
1. Use browser search (Ctrl+F) to find specific content
2. GitHub automatically collapses long outputs - click to expand
3. Download raw logs if you need to analyze offline

### "I need to share the logs"
**Solution:**
1. Share the workflow run URL
2. Or download raw logs and share the files
3. Or copy/paste relevant sections

---

## 📖 Related Documentation

- **Workflow Guide**: `.github/workflows/MIGRATION-CUTOVER-README.md`
- **Quick Start**: `QUICK-START.md`
- **Adjustments Summary**: `ADJUSTMENTS-SUMMARY.md`

---

## ✅ Benefits of Console-Only Approach

1. ✅ **Faster** - No artifact creation/upload time
2. ✅ **Simpler** - One place to look for all information
3. ✅ **Cleaner** - No expired artifacts to manage
4. ✅ **Searchable** - Use browser search directly
5. ✅ **Always Available** - Part of workflow run history
