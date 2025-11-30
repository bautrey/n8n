# Make.com Backup Recovery Plan

## Problem Identified

The Make.com → GitHub backup workflow had a critical bug that caused it to store GitHub API response wrappers instead of actual Make.com scenario blueprints.

### Root Cause
**File:** `workflows/make-backup-github.json`
**Node:** "Prepare Commit Data" (line 154)
**Bug:**
```javascript
// WRONG - Gets GitHub API response from "Check Existing File"
const blueprint = $input.all()[0].json.response || $input.all()[0].json;
```

**Fix:**
```javascript
// CORRECT - Gets actual Make.com blueprint from "Download Blueprint" node
const blueprint = $node['Download Blueprint'].json.response || $node['Download Blueprint'].json;
```

### Impact
- All 291 scenario files in the backup repo contain corrupted/nested GitHub API responses
- Files cannot be read, diffed, or used for restoration
- Backup has been non-functional since first run on Nov 7, 2025

## Recovery Steps

### ✅ Step 1: Fix Workflow (COMPLETED)
- [x] Identified bug in "Prepare Commit Data" node
- [x] Updated workflow to use correct data source
- [x] Uploaded fixed workflow to n8n

### Step 2: Clean GitHub Repository
**Script:** `/Users/burke/projects/make-scenarios-backup/cleanup_repo.py`

**Actions:**
1. Delete all 292 corrupted scenario JSON files from GitHub
2. Reset `backup-state.json` to empty state

**Command:**
```bash
cd /Users/burke/projects/make-scenarios-backup
source /Users/burke/projects/n8n/.env  # Load GITHUB_PAT
python3 cleanup_repo.py
```

**WARNING:** This will delete all current scenario files. Proceed only after confirming the workflow fix is correct.

### Step 3: Reset Backup State

Create fresh `backup-state.json`:
```json
{
  "lastBackup": {},
  "metadata": {
    "firstBackup": "2025-11-30T00:00:00.000Z",
    "totalBackups": 0,
    "totalScenarios": 0,
    "backedUpScenarios": 0
  }
}
```

### Step 4: Test with Single Scenario

**Manual Test:**
1. Temporarily modify "Filter Changed Scenarios" to return only 1 scenario
2. Manually trigger workflow in n8n UI
3. Check GitHub for scenario file
4. Decode and verify it contains actual Make.com blueprint (not GitHub API wrapper)
5. Verify blueprint has keys like: `name`, `flow`, `scheduling`, etc.

**Verification:**
```bash
cd /Users/burke/projects/make-scenarios-backup
python3 search_scenarios.py --list
# Should show 1 scenario with "✓ has flow"

# Manually decode and inspect
python3 -c "
import json, base64
with open('scenarios/[ID].json') as f:
    data = json.load(f)
decoded = base64.b64decode(data['content']).decode('utf-8')
scenario = json.loads(decoded)
print('Keys:', list(scenario.keys()))
print('Has flow:', 'flow' in scenario)
"
```

### Step 5: Full Backup Run

**Once test passes:**
1. Revert "Filter Changed Scenarios" to normal logic
2. Manually trigger full backup
3. Monitor execution in n8n
4. Verify all 291 scenarios backed up successfully

**Expected Duration:** ~10-15 minutes for 291 scenarios

### Step 6: Verification

**Verify backup quality:**
```bash
cd /Users/burke/projects/make-scenarios-backup
python3 search_scenarios.py --list | grep "has flow"
# Should show 291 scenarios with "✓ has flow"

# Spot check a few scenarios
python3 search_scenarios.py "LinkedIn"  # Search for LinkedIn-related scenarios
python3 search_scenarios.py "HubSpot"   # Search for HubSpot-related scenarios
```

**Verify diffs work:**
```bash
git log --oneline scenarios/ | head -20
git diff HEAD~1 HEAD -- scenarios/[ID].json
# Should show actual blueprint changes, not GitHub wrapper changes
```

## Post-Recovery

### Enable Scheduled Backups
The workflow is currently set to run every 2 minutes (for testing). Change to daily:

**Update trigger:** "Daily 2AM CST Trigger"
```json
"cronExpression": "0 2 * * *"  // 2:00 AM daily
```

### Monitor First Week
- Check Slack notifications for backup status
- Spot check scenario files weekly
- Verify diffs show actual Make.com changes

## Rollback Plan

If anything goes wrong during recovery:

1. **Workflow is broken:** Deactivate in n8n UI immediately
2. **GitHub cleanup failed:** Manually delete scenarios directory via GitHub UI
3. **Test scenario corrupted:** Delete and retry with different scenario
4. **Full backup failed:** Check n8n execution logs, fix errors, retry

## Success Criteria

- [x] Workflow fixed and uploaded to n8n
- [ ] All corrupted scenario files deleted from GitHub
- [ ] backup-state.json reset to empty
- [ ] Single scenario test passes with valid blueprint
- [ ] Full backup completes successfully (291 scenarios)
- [ ] All scenarios readable with flow data
- [ ] Git diffs show actual scenario changes
- [ ] Scheduled backup running daily at 2 AM CST

---

**Created:** 2025-11-30
**Status:** In Progress (Step 2)
**Next Action:** Execute cleanup_repo.py to delete corrupted files
