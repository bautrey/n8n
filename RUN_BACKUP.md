# Run Make.com Backup - Quick Guide

## Status: ✅ Ready to Run

### What Was Fixed
- **Bug:** Workflow was encoding GitHub API responses instead of Make.com blueprints
- **Fix:** Changed data source in "Prepare Commit Data" node
- **Result:** Workflow now correctly stores actual scenario blueprints

### Cleanup Complete
- ✅ All 292 corrupted scenario files deleted from GitHub
- ✅ backup-state.json reset to empty
- ✅ Fixed workflow uploaded to n8n
- ✅ Repository clean and ready for fresh backup

## Option 1: Manual Trigger (Recommended for First Run)

**Via n8n UI:**
1. Open n8n: http://localhost:5678
2. Find workflow: "Make.com → GitHub Backup"
3. Click "Execute Workflow" button
4. Monitor execution in real-time
5. Check execution log for any errors

**Expected duration:** ~10-15 minutes for 291 scenarios

## Option 2: Automated Trigger (Already Active)

The workflow is configured to run **every 2 minutes** (for testing).

**To change to daily schedule:**
1. Open workflow in n8n
2. Edit "Daily 2AM CST Trigger" node
3. Change `cronExpression` from:
   - Current: `*/2 * * * *` (every 2 minutes)
   - To: `0 2 * * *` (2:00 AM daily)
4. Save workflow

## Verification Steps

### After Backup Completes:

**1. Check Slack Notification**
- Should receive success message in configured Slack channel
- Should show: "Successfully backed up: 291"

**2. Verify GitHub Repository**
```bash
cd /Users/burke/projects/make-scenarios-backup
git pull
ls -la scenarios/ | wc -l  # Should show ~293 (291 scenarios + . and ..)
```

**3. Test Scenario Readability**
```bash
cd /Users/burke/projects/make-scenarios-backup
python3 search_scenarios.py --list
# Should show 291 scenarios with "✓ has flow"
```

**4. Verify Actual Blueprint Data**
```bash
# Pick a random scenario file
cat scenarios/564734.json | jq -r '.content' | base64 -d | jq '.' | head -30
# Should see keys like: name, flow, scheduling, teamId, etc.
# Should NOT see: content, encoding, _links (GitHub API keys)
```

**5. Test Git Diffs**
```bash
# Make a small change to a scenario in Make.com
# Wait for next backup run
# Then check diff:
git pull
git log --oneline scenarios/ | head -5
git diff HEAD~1 HEAD -- scenarios/[CHANGED_ID].json
# Should show actual blueprint changes, not GitHub wrapper changes
```

## Monitoring

**Watch n8n Execution Logs:**
```bash
docker logs -f n8n-app | grep "Make.com"
```

**Check Workflow Executions:**
- n8n UI → Executions
- Filter by "Make.com → GitHub Backup"
- Review success/error status

## Troubleshooting

**If backup fails:**
1. Check n8n execution logs
2. Verify environment variables:
   - `MAKE_API_KEY` - Make.com API token
   - `GITHUB_PAT` - GitHub personal access token
   - `SLACK_CHANNEL_ID` - Slack channel for notifications
3. Check Make.com API access
4. Check GitHub repository permissions

**If scenarios are still corrupted:**
1. Review workflow fix in "Prepare Commit Data" node
2. Ensure it's using: `$node['Download Blueprint'].json`
3. NOT using: `$input.all()[0].json`

## Success Criteria

- [x] Workflow fixed and uploaded
- [x] Repository cleaned (292 files deleted)
- [x] backup-state.json reset
- [ ] Backup executed successfully
- [ ] 291 scenarios backed up to GitHub
- [ ] All scenarios readable with flow data
- [ ] Git diffs show actual blueprint changes

---

**Created:** 2025-11-30
**Ready to run!** 🚀

See `BACKUP_RECOVERY_PLAN.md` for detailed recovery documentation.
