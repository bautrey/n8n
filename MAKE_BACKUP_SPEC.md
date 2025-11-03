# Make.com Scenario Backup to GitHub - Implementation Specification

**Project:** Replace Make.com scenario backup (Google Drive → GitHub)
**Target:** n8n workflow with webhook trigger
**Duration:** Periodic execution until all scenarios migrated to n8n
**Date:** 2025-11-03

---

## Executive Summary

Replace the existing Make.com scenario that backs up all Make.com scenarios to Google Drive with an n8n workflow that backs up to a GitHub repository in the `fortiumpartners` organization instead.

---

## Current State Analysis

### Existing Make.com Workflow

The current backup workflow performs these steps:

1. **List Scenarios** - Retrieves all scenarios from Make.com (Fortium Partners org, team ID: 154819)
2. **Iterate** - Loops through each scenario ID
3. **Check Last Backup** - Queries internal Make.com datastore to find:
   - Scenario ID
   - Last Update Date (from Make.com)
   - Last Backup Date (from datastore)
4. **Conditional Filter** - Only backs up if:
   - Scenario doesn't exist in datastore, OR
   - Scenario's lastEdit > Last Backup Date
5. **Download Blueprint** - Gets scenario blueprint as JSON file via Make.com API
6. **Upload to Google Drive** - Saves to folder ID: `1P4cAp2L7X6VDnhvHbY0qjoQ8PraEXxid`
   - Filename format: `{scenarioId}-{scenarioName}-{timestamp}`
7. **Update Datastore** - Records backup timestamp

### Key Metadata

- **Organization ID:** 395687 (Fortium Partners)
- **Team ID:** 154819 (My Team)
- **Drive Folder:** 1P4cAp2L7X6VDnhvHbY0qjoQ8PraEXxid
- **Datastore:** 13553 (Scenario Backup tracking)

---

## Target State Requirements

### GitHub Repository Structure

**Repository:** `fortiumpartners/make-scenarios-backup` (to be created)

```
make-scenarios-backup/
├── README.md                           # Repository documentation
├── scenarios/                          # All scenario backups
│   ├── {scenarioId}/                   # One directory per scenario
│   │   ├── metadata.json               # Scenario metadata
│   │   └── blueprint.json              # Scenario blueprint
│   └── ...
├── .backup-state.json                  # Tracking file (replaces datastore)
└── .github/
    └── workflows/
        └── cleanup-old-versions.yml    # Optional: Clean old backups
```

### Backup State Tracking

Instead of Make.com datastore, use a `.backup-state.json` file in the repo:

```json
{
  "lastRun": "2025-11-03T13:00:00Z",
  "scenarios": {
    "{scenarioId}": {
      "name": "Scenario Name",
      "lastEdit": "2025-11-03T12:00:00Z",
      "lastBackup": "2025-11-03T13:00:00Z",
      "backupCount": 5,
      "gitSHA": "abc123..."
    }
  }
}
```

### File Naming Convention

**Scenario Metadata:** `scenarios/{scenarioId}/metadata.json`
```json
{
  "id": 12345,
  "name": "Scenario Name",
  "description": "Scenario description",
  "folderId": 999,
  "created": "2024-01-01T00:00:00Z",
  "lastEdit": "2025-11-03T12:00:00Z",
  "teamId": 154819,
  "organizationId": 395687,
  "isActive": true,
  "backupHistory": [
    {
      "timestamp": "2025-11-03T13:00:00Z",
      "gitCommit": "abc123...",
      "gitSHA": "def456..."
    }
  ]
}
```

**Scenario Blueprint:** `scenarios/{scenarioId}/blueprint.json`
- Contains the complete scenario blueprint from Make.com API

---

## API Requirements

### 1. Make.com API

**Base URL:** `https://us1.make.com/api/v2` (or appropriate region)

**Authentication:**
- Header: `Authorization: Token {MAKE_API_KEY}`
- Required: Paid Make.com account

**Endpoints:**

**List Scenarios:**
```
GET /scenarios?teamId={teamId}&organizationId={organizationId}&pg[limit]=100
```

Response:
```json
{
  "scenarios": [
    {
      "id": 12345,
      "name": "Scenario Name",
      "teamId": 154819,
      "description": "...",
      "folderId": 999,
      "lastEdit": "2025-11-03T12:00:00Z",
      "islinked": true,
      "isPaused": false
    }
  ],
  "pg": {
    "offset": 0,
    "limit": 100
  }
}
```

**Get Scenario Blueprint:**
```
GET /scenarios/{scenarioId}/blueprint?draft=false
```

Response:
```json
{
  "name": "Scenario Name",
  "flow": [...],
  "metadata": {...}
}
```

### 2. GitHub API

**Base URL:** `https://api.github.com`

**Authentication:**
- Header: `Authorization: Bearer {GITHUB_PAT}`
- Required Scopes: `repo` (or `Contents` write for fine-grained PAT)

**Endpoints:**

**Create/Update File:**
```
PUT /repos/{owner}/{repo}/contents/{path}
```

Body:
```json
{
  "message": "Backup scenario {scenarioId}: {scenarioName}",
  "content": "{base64_encoded_content}",
  "sha": "{current_file_sha}",  // Required for updates only
  "branch": "main",
  "committer": {
    "name": "Make.com Backup Bot",
    "email": "bot@fortiumpartners.com"
  }
}
```

Response (201 Created / 200 OK):
```json
{
  "content": {
    "name": "blueprint.json",
    "path": "scenarios/12345/blueprint.json",
    "sha": "abc123...",
    "size": 5432,
    "url": "https://api.github.com/repos/...",
    "html_url": "https://github.com/...",
    "download_url": "https://raw.githubusercontent.com/..."
  },
  "commit": {
    "sha": "def456...",
    "message": "Backup scenario 12345: Scenario Name",
    "author": {...},
    "committer": {...}
  }
}
```

**Get File Contents (for SHA):**
```
GET /repos/{owner}/{repo}/contents/{path}
```

Response:
```json
{
  "name": "blueprint.json",
  "path": "scenarios/12345/blueprint.json",
  "sha": "abc123...",
  "size": 5432,
  "content": "{base64_encoded_content}",
  "encoding": "base64"
}
```

---

## Workflow Design

### n8n Workflow Structure

```
[Webhook Trigger]
    ↓
[Get Backup State from GitHub]  // Read .backup-state.json
    ↓
[List Make.com Scenarios]  // Get all scenarios
    ↓
[Loop Through Scenarios]  // Iterator
    ↓
[Check If Backup Needed]  // Compare lastEdit vs lastBackup
    ↓ (if needs backup)
[Get Scenario Blueprint]  // Download from Make.com
    ↓
[Create/Update Metadata File]  // scenarios/{id}/metadata.json
    ↓
[Create/Update Blueprint File]  // scenarios/{id}/blueprint.json
    ↓
[Update Backup State]  // Update .backup-state.json
    ↓
[Return Summary]  // Count of scenarios backed up
```

### Detailed Node Configuration

#### 1. Webhook Trigger
- **Type:** `n8n-nodes-base.webhook`
- **Path:** `make-backup`
- **Method:** GET or POST
- **Response Mode:** `lastNode`
- **Purpose:** Allow manual triggering or scheduled external trigger

#### 2. Get Backup State
- **Type:** `n8n-nodes-base.httpRequest`
- **Method:** GET
- **URL:** `https://api.github.com/repos/fortiumpartners/make-scenarios-backup/contents/.backup-state.json`
- **Headers:**
  - `Authorization: Bearer {{$env.GITHUB_PAT}}`
  - `Accept: application/vnd.github+json`
- **Error Handling:** If 404 (file doesn't exist), use empty state
- **Output:** Decode base64 content to JSON

#### 3. List Make.com Scenarios
- **Type:** `n8n-nodes-base.httpRequest`
- **Method:** GET
- **URL:** `https://us1.make.com/api/v2/scenarios`
- **Query Parameters:**
  - `teamId: 154819`
  - `organizationId: 395687`
  - `pg[limit]: 100`
- **Headers:**
  - `Authorization: Token {{$env.MAKE_API_KEY}}`
- **Output:** Array of scenario objects

#### 4. Loop Through Scenarios
- **Type:** `n8n-nodes-base.splitInBatches`
- **Batch Size:** 1 (process one at a time to avoid GitHub API conflicts)
- **Input:** scenarios array from step 3

#### 5. Check If Backup Needed
- **Type:** `n8n-nodes-base.function`
- **Logic:**
```javascript
const scenario = $input.item.json;
const scenarioId = scenario.id;
const lastEdit = new Date(scenario.lastEdit);

// Get backup state
const backupState = $node["Get Backup State"].json.scenarios || {};
const lastBackup = backupState[scenarioId]?.lastBackup
  ? new Date(backupState[scenarioId].lastBackup)
  : new Date(0);

// Needs backup if scenario is new or updated since last backup
const needsBackup = lastEdit > lastBackup;

return {
  json: {
    ...scenario,
    needsBackup,
    lastBackup: lastBackup.toISOString()
  }
};
```
- **Filter:** Only continue if `needsBackup === true`

#### 6. Get Scenario Blueprint
- **Type:** `n8n-nodes-base.httpRequest`
- **Method:** GET
- **URL:** `https://us1.make.com/api/v2/scenarios/{{$json.id}}/blueprint`
- **Query Parameters:**
  - `draft: false`
- **Headers:**
  - `Authorization: Token {{$env.MAKE_API_KEY}}`
- **Output:** Blueprint JSON object

#### 7. Create/Update Metadata File
- **Type:** `n8n-nodes-base.httpRequest`
- **Method:** PUT
- **URL:** `https://api.github.com/repos/fortiumpartners/make-scenarios-backup/contents/scenarios/{{$json.id}}/metadata.json`
- **Headers:**
  - `Authorization: Bearer {{$env.GITHUB_PAT}}`
  - `Content-Type: application/json`
- **Body:**
```javascript
{
  message: `Update metadata for scenario ${$json.id}: ${$json.name}`,
  content: Buffer.from(JSON.stringify({
    id: $json.id,
    name: $json.name,
    description: $json.description,
    folderId: $json.folderId,
    lastEdit: $json.lastEdit,
    teamId: $json.teamId,
    organizationId: $json.organizationId,
    isActive: $json.islinked,
    backupTimestamp: new Date().toISOString()
  }, null, 2)).toString('base64'),
  sha: $json.metadataSHA,  // If updating existing file
  branch: 'main',
  committer: {
    name: 'Make.com Backup Bot',
    email: 'bot@fortiumpartners.com'
  }
}
```

#### 8. Create/Update Blueprint File
- **Type:** `n8n-nodes-base.httpRequest`
- **Method:** PUT
- **URL:** `https://api.github.com/repos/fortiumpartners/make-scenarios-backup/contents/scenarios/{{$json.id}}/blueprint.json`
- **Headers:**
  - `Authorization: Bearer {{$env.GITHUB_PAT}}`
  - `Content-Type: application/json`
- **Body:**
```javascript
{
  message: `Backup scenario ${$json.id}: ${$json.name}`,
  content: Buffer.from(JSON.stringify($node["Get Scenario Blueprint"].json, null, 2)).toString('base64'),
  sha: $json.blueprintSHA,  // If updating existing file
  branch: 'main',
  committer: {
    name: 'Make.com Backup Bot',
    email: 'bot@fortiumpartners.com'
  }
}
```

#### 9. Update Backup State
- **Type:** `n8n-nodes-base.function`
- **Purpose:** Aggregate all backed-up scenarios
- **Execute Once:** After all iterations complete
- **Logic:**
```javascript
// Load current backup state
const backupState = $node["Get Backup State"].json || { scenarios: {} };

// Update with all backed-up scenarios
for (const item of $input.all()) {
  const scenarioId = item.json.id;
  backupState.scenarios[scenarioId] = {
    name: item.json.name,
    lastEdit: item.json.lastEdit,
    lastBackup: new Date().toISOString(),
    backupCount: (backupState.scenarios[scenarioId]?.backupCount || 0) + 1,
    gitSHA: item.json.blueprintCommitSHA
  };
}

backupState.lastRun = new Date().toISOString();

return { json: backupState };
```

#### 10. Commit Backup State
- **Type:** `n8n-nodes-base.httpRequest`
- **Method:** PUT
- **URL:** `https://api.github.com/repos/fortiumpartners/make-scenarios-backup/contents/.backup-state.json`
- **Headers:**
  - `Authorization: Bearer {{$env.GITHUB_PAT}}`
  - `Content-Type: application/json`
- **Body:**
```javascript
{
  message: `Update backup state: ${Object.keys($json.scenarios).length} scenarios tracked`,
  content: Buffer.from(JSON.stringify($json, null, 2)).toString('base64'),
  sha: $node["Get Backup State"].json.sha,  // Current file SHA
  branch: 'main',
  committer: {
    name: 'Make.com Backup Bot',
    email: 'bot@fortiumpartners.com'
  }
}
```

#### 11. Return Summary
- **Type:** `n8n-nodes-base.set`
- **Values:**
```javascript
{
  success: true,
  timestamp: new Date().toISOString(),
  totalScenarios: $node["List Make.com Scenarios"].json.scenarios.length,
  backedUp: Object.keys($node["Update Backup State"].json.scenarios).length,
  skipped: $node["List Make.com Scenarios"].json.scenarios.length - Object.keys($node["Update Backup State"].json.scenarios).length
}
```

---

## Environment Variables

Add to `.env` file:

```bash
# Make.com API
MAKE_API_KEY=your_make_api_key_here
MAKE_TEAM_ID=154819
MAKE_ORG_ID=395687

# GitHub API
GITHUB_PAT=your_github_personal_access_token_here
GITHUB_OWNER=fortiumpartners
GITHUB_REPO=make-scenarios-backup
GITHUB_BOT_NAME="Make.com Backup Bot"
GITHUB_BOT_EMAIL="bot@fortiumpartners.com"
```

---

## Prerequisites

### 1. Create GitHub Repository

```bash
gh repo create fortiumpartners/make-scenarios-backup \
  --private \
  --description "Automated backups of Make.com scenarios" \
  --clone=false
```

**Initial Files:**

**README.md:**
```markdown
# Make.com Scenarios Backup

Automated backup repository for all Make.com scenarios from Fortium Partners.

## Structure

- `scenarios/{id}/metadata.json` - Scenario metadata and configuration
- `scenarios/{id}/blueprint.json` - Complete scenario blueprint
- `.backup-state.json` - Backup tracking state (managed automatically)

## Backup Schedule

Backups run periodically via n8n workflow until all scenarios are migrated.

## Restoration

To restore a scenario:
1. Navigate to desired scenario directory
2. Download `blueprint.json`
3. Import into Make.com via UI or API
```

### 2. Obtain API Keys

**Make.com API Key:**
1. Login to Make.com
2. Navigate to Settings > API
3. Create new API token with "Read" permissions
4. Save to `.env` as `MAKE_API_KEY`

**GitHub Personal Access Token:**
1. GitHub Settings > Developer settings > Personal access tokens > Tokens (classic)
2. Generate new token
3. Required scopes: `repo` (full control of private repositories)
4. Save to `.env` as `GITHUB_PAT`

---

## Error Handling

### API Rate Limits

**Make.com:**
- No specific rate limits documented
- Implement exponential backoff on 429 responses

**GitHub:**
- Authenticated requests: 5,000/hour
- Secondary rate limit: Avoid rapid file commits
- Batch size: 1 (sequential processing to avoid conflicts)

### Conflict Resolution

**Scenario:**
- Multiple workflows running simultaneously
- GitHub API returns 409 Conflict

**Solution:**
- Process scenarios sequentially (batch size = 1)
- Retry with exponential backoff (max 3 retries)
- Log conflicts and continue with next scenario

### Missing Scenarios

**Scenario:**
- Scenario deleted from Make.com
- Still exists in backup state

**Solution:**
- Mark as "archived" in backup state
- Do not delete from GitHub (preserve history)
- Add `archived: true` flag to metadata

---

## Testing Plan

### Unit Tests

1. **Test Backup State Loading**
   - Empty state (new repo)
   - Existing state
   - Corrupted state (fallback to empty)

2. **Test Scenario Filtering**
   - New scenario (never backed up)
   - Updated scenario (lastEdit > lastBackup)
   - Unchanged scenario (skip backup)

3. **Test GitHub File Operations**
   - Create new file (no SHA required)
   - Update existing file (SHA required)
   - Handle 409 conflicts

### Integration Tests

1. **End-to-End Backup**
   - Trigger workflow via webhook
   - Verify all scenarios backed up
   - Check `.backup-state.json` updated
   - Validate file structure in GitHub

2. **Incremental Backup**
   - Run backup twice
   - Second run should skip unchanged scenarios
   - Verify only updated scenarios backed up

### Manual Verification

1. Clone GitHub repository
2. Verify directory structure matches spec
3. Validate JSON file contents
4. Check backup state accuracy

---

## Deployment

### Workflow Deployment

```bash
cd /Users/burke/projects/n8n

# Create workflow JSON
# (Will be generated during implementation)

# Deploy to n8n
python3 -c "
from lib.n8n_api import N8nAPI
api = N8nAPI()
result = api.deploy_and_execute('workflows/make-backup-to-github.json')
print(f'Deployed: {result[\"workflow_id\"]}')
print(f'Webhook: {result[\"webhook_url\"]}')
"
```

### Scheduled Execution

**Option 1: External Cron (Recommended)**

```bash
# Add to crontab
# Run daily at 2 AM
0 2 * * * curl -X POST http://localhost:5678/webhook/make-backup
```

**Option 2: n8n Schedule Trigger**

Replace webhook trigger with schedule trigger:
- Interval: Daily at 2:00 AM
- Timezone: US/Central

---

## Monitoring

### Success Metrics

- Total scenarios in Make.com
- Scenarios backed up per run
- Scenarios skipped (unchanged)
- GitHub commits created
- Backup state consistency

### Logging

```json
{
  "timestamp": "2025-11-03T13:00:00Z",
  "workflow": "make-backup-to-github",
  "status": "success",
  "totalScenarios": 50,
  "backedUp": 5,
  "skipped": 45,
  "errors": [],
  "duration": "45s"
}
```

### Alerts

**Failure Conditions:**
- Make.com API authentication failure
- GitHub API authentication failure
- No scenarios returned from Make.com
- All scenarios fail to backup
- Backup state update fails

**Notification:**
- n8n error webhook
- Email notification
- Slack message (optional)

---

## Migration Timeline

**Phase 1: Initial Setup (Week 1)**
- Create GitHub repository
- Obtain API keys
- Deploy n8n workflow
- Run initial backup

**Phase 2: Validation (Week 2)**
- Verify all scenarios backed up
- Test incremental backups
- Validate file contents
- Review backup state accuracy

**Phase 3: Production (Ongoing)**
- Schedule periodic backups (daily)
- Monitor backup success rate
- Continue until all scenarios migrated to n8n

**Phase 4: Decommission**
- Final backup before shutdown
- Archive Google Drive backups
- Disable Make.com backup scenario
- Document GitHub repository location

---

## Future Enhancements

### Optional Features

1. **Backup History**
   - Keep last N versions of each scenario
   - Use Git tags for major versions
   - Automatic cleanup of old versions

2. **Scenario Comparison**
   - Diff view between versions
   - Notification on significant changes
   - Auto-generate changelog

3. **Restoration API**
   - Webhook endpoint to restore scenarios
   - Select specific version to restore
   - Validation before restoration

4. **Metrics Dashboard**
   - Backup success rate
   - Scenario change frequency
   - Storage usage trends

---

## Success Criteria

✅ **Workflow Implemented**
- All nodes configured correctly
- Webhook trigger working
- Error handling in place

✅ **GitHub Repository Created**
- Repository structure matches spec
- Initial README committed
- Access permissions configured

✅ **Initial Backup Complete**
- All Make.com scenarios backed up
- File structure validated
- Backup state accurate

✅ **Incremental Backups Working**
- Only updated scenarios backed up
- Unchanged scenarios skipped
- Backup state updated correctly

✅ **Production Ready**
- Scheduled execution configured
- Monitoring in place
- Documentation complete

---

## Appendix A: File Examples

### Example .backup-state.json

```json
{
  "lastRun": "2025-11-03T13:00:00Z",
  "scenarios": {
    "12345": {
      "name": "Customer Onboarding",
      "lastEdit": "2025-11-03T12:00:00Z",
      "lastBackup": "2025-11-03T13:00:00Z",
      "backupCount": 5,
      "gitSHA": "abc123def456"
    },
    "67890": {
      "name": "Invoice Processing",
      "lastEdit": "2025-11-02T10:00:00Z",
      "lastBackup": "2025-11-03T13:00:00Z",
      "backupCount": 3,
      "gitSHA": "ghi789jkl012"
    }
  }
}
```

### Example metadata.json

```json
{
  "id": 12345,
  "name": "Customer Onboarding",
  "description": "Automated customer onboarding workflow",
  "folderId": 999,
  "created": "2024-01-01T00:00:00Z",
  "lastEdit": "2025-11-03T12:00:00Z",
  "teamId": 154819,
  "organizationId": 395687,
  "isActive": true,
  "isPaused": false,
  "backupTimestamp": "2025-11-03T13:00:00Z",
  "backupHistory": [
    {
      "timestamp": "2025-11-03T13:00:00Z",
      "gitCommit": "abc123",
      "gitSHA": "def456"
    },
    {
      "timestamp": "2025-11-02T13:00:00Z",
      "gitCommit": "xyz789",
      "gitSHA": "uvw012"
    }
  ]
}
```

---

## Appendix B: API Authentication Testing

### Test Make.com API

```bash
curl -X GET "https://us1.make.com/api/v2/scenarios?teamId=154819&organizationId=395687&pg[limit]=1" \
  -H "Authorization: Token ${MAKE_API_KEY}" \
  -H "Accept: application/json"
```

Expected: 200 OK with scenarios array

### Test GitHub API

```bash
curl -X GET "https://api.github.com/repos/fortiumpartners/make-scenarios-backup/contents/README.md" \
  -H "Authorization: Bearer ${GITHUB_PAT}" \
  -H "Accept: application/vnd.github+json"
```

Expected: 200 OK with file contents

---

## Questions for Clarification

1. **Backup Frequency:** Daily at 2 AM sufficient, or prefer different schedule?
2. **Repository Visibility:** Private repository acceptable?
3. **Bot Account:** Use personal PAT or create GitHub App/bot account?
4. **Notification:** Where should backup failure alerts go?
5. **Retention:** Keep all versions forever, or implement cleanup policy?

---

**End of Specification**
