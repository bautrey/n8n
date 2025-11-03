# Product Requirements Document: Make.com Backup Migration

**Product:** Make.com Scenario Backup System Migration
**Version:** 1.0 - APPROVED
**Date:** 2025-11-03
**Status:** ✅ Approved for Implementation
**Owner:** Product Management
**Stakeholders:** DevOps Engineering, Automation Engineering, IT Operations

---

## ✅ Approved Decisions

### Backup Schedule
- **Decision:** Daily at 2:00 AM US/Central
- **Rationale:** Low-traffic period, provides 24-hour backup freshness

### GitHub Account
- **Decision:** Use personal GitHub PAT (Burke Autrey)
- **Repository:** `bautrey/make-scenarios-backup` (private)
- **Future:** Migrate to `fortiumpartners` organization after validation

### Notifications
- **Decision:** Private Slack channel for n8n communications
- **Channel:** `#n8n-automation` (to be created)
- **Requirements:** All messages must include:
  - Workflow name and context
  - Success/failure status
  - Summary of actions taken
  - Links to relevant resources (GitHub commits, scenarios, etc.)

### Repository Visibility
- **Decision:** Private repository in `bautrey` org initially
- **Future:** Transfer to `fortiumpartners` org after successful validation period

---

## Required Integrations & Credentials

### 1. Make.com API Integration

**API Endpoint:** `https://us1.make.com/api/v2`

**Required Credentials:**
- **API Key:** Make.com API token with "Read" permissions
- **Scope:** Organization and team access
- **Location:** n8n credential store (encrypted)
- **Format:**
  ```json
  {
    "name": "Make.com API",
    "type": "httpHeaderAuth",
    "data": {
      "name": "Authorization",
      "value": "Token {{MAKE_API_KEY}}"
    }
  }
  ```

**How to Obtain:**
1. Login to Make.com (https://www.make.com)
2. Navigate to: Settings → API
3. Click "Create an API Token"
4. Name: "n8n Backup System"
5. Permissions: Read (scenarios, blueprints)
6. Copy token (only shown once!)
7. Store in n8n credentials

**Required for:**
- Listing all scenarios (GET /scenarios)
- Downloading scenario blueprints (GET /scenarios/{id}/blueprint)

**Organization Details:**
- Organization ID: 395687 (Fortium Partners)
- Team ID: 154819 (My Team)

---

### 2. GitHub API Integration

**API Endpoint:** `https://api.github.com`

**Required Credentials:**
- **Personal Access Token (Classic):** Burke Autrey's GitHub account
- **Scope:** `repo` (Full control of private repositories)
- **Location:** n8n credential store (encrypted)
- **Format:**
  ```json
  {
    "name": "GitHub API (Burke)",
    "type": "httpHeaderAuth",
    "data": {
      "name": "Authorization",
      "value": "Bearer {{GITHUB_PAT}}"
    }
  }
  ```

**How to Obtain:**
1. Login to GitHub (https://github.com)
2. Navigate to: Settings → Developer settings → Personal access tokens → Tokens (classic)
3. Click "Generate new token (classic)"
4. Name: "n8n Make.com Backup"
5. Expiration: No expiration (or 1 year with calendar reminder)
6. Scopes:
   - ✅ `repo` (Full control of private repositories)
     - ✅ repo:status
     - ✅ repo_deployment
     - ✅ public_repo
     - ✅ repo:invite
     - ✅ security_events
7. Generate token
8. Copy token (only shown once!)
9. Store in n8n credentials

**Required for:**
- Creating/updating files (PUT /repos/{owner}/{repo}/contents/{path})
- Reading file SHAs (GET /repos/{owner}/{repo}/contents/{path})
- Committing changes to repository

**Repository Details:**
- Owner: `bautrey`
- Repository: `make-scenarios-backup`
- Branch: `main`
- Visibility: Private

---

### 3. Slack API Integration

**API Endpoint:** `https://slack.com/api`

**Required Credentials:**
- **Bot OAuth Token:** Slack app with channel posting permissions
- **Scope:** `chat:write`, `chat:write.public`
- **Location:** n8n credential store (encrypted)
- **Format:**
  ```json
  {
    "name": "Slack n8n Bot",
    "type": "slackOAuth2Api",
    "data": {
      "accessToken": "{{SLACK_BOT_TOKEN}}"
    }
  }
  ```

**How to Obtain:**
1. Go to https://api.slack.com/apps
2. Click "Create New App" → "From scratch"
3. App Name: "n8n Automation Bot"
4. Workspace: Fortium Partners workspace
5. Navigate to "OAuth & Permissions"
6. Add Bot Token Scopes:
   - `chat:write` - Send messages as app
   - `chat:write.public` - Send messages to public channels without joining
7. Click "Install to Workspace"
8. Authorize the app
9. Copy "Bot User OAuth Token" (starts with `xoxb-`)
10. Store in n8n credentials

**Required for:**
- Posting workflow execution summaries
- Sending error notifications
- Reporting backup status

**Channel Setup:**
1. Create private Slack channel: `#n8n-automation`
2. Invite n8n Bot to channel: `/invite @n8n Automation Bot`
3. Note channel ID (visible in channel details)
4. Store channel ID in n8n environment variables

**Message Format Requirements:**
```
✅ [WORKFLOW: Make.com Backup] SUCCESS

**Context:** Periodic backup of Make.com scenarios to GitHub
**Timestamp:** 2025-11-03 02:00:15 AM CST
**Duration:** 2m 34s

**Summary:**
• Total scenarios: 52
• Backed up: 7 (updated since last run)
• Skipped: 45 (unchanged)
• Errors: 0

**Details:**
• Repository: https://github.com/bautrey/make-scenarios-backup
• Latest commit: abc123de
• Backup state: Updated successfully

**Changes:**
• Scenario 12345: "Customer Onboarding" (last edit: 2025-11-02)
• Scenario 67890: "Invoice Processing" (last edit: 2025-11-03)
• ... (5 more)
```

---

### 4. n8n Configuration

**Required Environment Variables:**

Add to `/Users/burke/projects/n8n/.env`:

```bash
# Make.com API
MAKE_API_KEY=your_make_api_key_here
MAKE_API_BASE_URL=https://us1.make.com/api/v2
MAKE_TEAM_ID=154819
MAKE_ORG_ID=395687

# GitHub API
GITHUB_PAT=your_github_personal_access_token_here
GITHUB_OWNER=bautrey
GITHUB_REPO=make-scenarios-backup
GITHUB_BRANCH=main
GITHUB_BOT_NAME="Make.com Backup Bot"
GITHUB_BOT_EMAIL="bot@fortiumpartners.com"

# Slack API
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token-here
SLACK_CHANNEL_ID=C0123456789  # #n8n-automation channel
SLACK_BOT_NAME="n8n Automation Bot"

# Backup Configuration
BACKUP_SCHEDULE="0 2 * * *"  # Daily at 2:00 AM
BACKUP_TIMEZONE="America/Chicago"
```

**Credential Storage in n8n:**

All credentials must be stored in n8n's credential manager:

1. **Make.com Credential:**
   - Type: "Header Auth"
   - Name: "Make.com API"
   - Header: `Authorization`
   - Value: `Token {API_KEY}`

2. **GitHub Credential:**
   - Type: "Header Auth"
   - Name: "GitHub API (Burke)"
   - Header: `Authorization`
   - Value: `Bearer {PAT}`

3. **Slack Credential:**
   - Type: "Slack OAuth2 API"
   - Name: "Slack n8n Bot"
   - OAuth Token: `{SLACK_BOT_TOKEN}`

---

## n8n Workflow Nodes Required

### Node Types Needed

1. **Webhook Trigger** (`n8n-nodes-base.webhook`)
   - Path: `make-backup`
   - Method: GET, POST
   - Response: lastNode

2. **HTTP Request** (`n8n-nodes-base.httpRequest`)
   - Make.com API calls (list scenarios, get blueprints)
   - GitHub API calls (create/update files, read SHAs)
   - Slack API calls (post messages)

3. **Function** (`n8n-nodes-base.function`)
   - Backup state comparison logic
   - Base64 encoding for GitHub
   - Message formatting for Slack

4. **Split In Batches** (`n8n-nodes-base.splitInBatches`)
   - Process scenarios sequentially
   - Batch size: 1 (avoid GitHub conflicts)

5. **IF/Filter** (`n8n-nodes-base.if`)
   - Check if backup needed (lastEdit > lastBackup)
   - Error handling branches

6. **Set** (`n8n-nodes-base.set`)
   - Format response data
   - Prepare commit messages

7. **Error Trigger** (`n8n-nodes-base.errorTrigger`)
   - Catch workflow failures
   - Send error notifications to Slack

---

## Prerequisites Checklist

### Before Implementation

- [ ] **GitHub Repository Created**
  - Repository: `bautrey/make-scenarios-backup`
  - Visibility: Private
  - Initial files: README.md, .gitignore

- [ ] **API Keys Obtained**
  - [ ] Make.com API key (stored securely)
  - [ ] GitHub Personal Access Token (stored securely)
  - [ ] Slack Bot Token (stored securely)

- [ ] **Slack Channel Setup**
  - [ ] Channel created: `#n8n-automation`
  - [ ] Bot invited to channel
  - [ ] Channel ID recorded

- [ ] **n8n Configuration**
  - [ ] Environment variables added to `.env`
  - [ ] Credentials stored in n8n credential manager
  - [ ] n8n services running (docker compose up -d)

- [ ] **Testing**
  - [ ] Make.com API accessible (test with curl)
  - [ ] GitHub API accessible (test with curl)
  - [ ] Slack API accessible (test message post)

---

## Implementation with AI-Mesh

### Recommended Workflow

```bash
# Current state: PRD approved
# Status: ✅ Ready for TRD creation

# Step 1: Create Technical Requirements Document
/ai-mesh:create-trd /Users/burke/projects/n8n/docs/PRD/make-backup-github-prd-approved.md

# This will:
# - Analyze the PRD
# - Design technical architecture
# - Create detailed task breakdown
# - Define quality requirements
# - Output TRD to docs/TRD/

# Step 2: Implement the TRD
/ai-mesh:implement-trd docs/TRD/{generated-trd-filename}.md

# This will:
# - Create git-town feature branch
# - Implement workflow nodes
# - Add error handling
# - Create tests
# - Generate documentation
# - Commit with proper messages
# - Create pull request

# Step 3: Monitor Progress
/ai-mesh:sprint-status

# Step 4: Validate Implementation
# - Run test execution
# - Verify GitHub commits
# - Check Slack notifications
# - Review backup state
```

### AI-Mesh Delegation Flow

```
User: /ai-mesh:create-trd → PRD approved
    ↓
ai-mesh-orchestrator: Analyze PRD, delegate to tech-lead
    ↓
tech-lead-orchestrator: Design architecture, create tasks
    ↓
Output: TRD document with implementation plan
    ↓
User: /ai-mesh:implement-trd → TRD path
    ↓
ai-mesh-orchestrator: Analyze tasks, coordinate specialists
    ↓
tech-lead-orchestrator: Manage implementation workflow
    ↓
backend-developer: Create n8n workflow JSON
    ↓
test-runner: Validate workflow execution
    ↓
git-workflow: Commit and create PR
    ↓
Output: Implemented feature, ready for deployment
```

---

## Security Considerations

### Credentials Management

**✅ DO:**
- Store all API keys in n8n credential manager (encrypted at rest)
- Use environment variables for non-sensitive configuration
- Rotate GitHub PAT every 12 months
- Limit Make.com API key to Read-only permissions
- Use Slack bot token (not user token)

**❌ DO NOT:**
- Commit API keys to Git
- Share credentials via Slack or email
- Use admin-level Make.com API keys
- Store credentials in plain text files
- Use same GitHub PAT for multiple purposes

### Repository Access

- Private repository prevents public exposure
- Only Burke Autrey has write access initially
- Future: Add fortiumpartners org members with appropriate roles
- Audit log via GitHub's commit history

### Backup Data

- Scenario blueprints do NOT contain actual API keys or credentials
- Make.com exports exclude connection authentication data
- Safe to store in version control
- Contains only workflow structure and configuration

---

## Success Metrics (Approved)

### Launch Criteria (MVP)

✅ **Initial Backup Complete**
- All 50+ Make.com scenarios backed up to GitHub
- Repository structure matches specification
- Backup state file created and accurate

✅ **Workflow Operational**
- n8n workflow deployed and active
- Webhook endpoint accessible
- All API integrations working
- Error handling in place

✅ **Slack Integration Live**
- Bot posted to #n8n-automation channel
- Success messages formatted correctly
- Error notifications tested

### Production Readiness

✅ **Scheduled Execution**
- Daily backups running at 2:00 AM
- Successful execution 7 consecutive days
- Zero manual interventions required

✅ **Incremental Backups Working**
- Only changed scenarios backed up
- Unchanged scenarios skipped correctly
- Backup state updated accurately

✅ **Monitoring & Alerts**
- Slack notifications for all runs
- Error alerts trigger within 5 minutes
- Backup metrics visible in Slack history

---

## Timeline

### Phase 1: Setup & Integration (Week 1)
- Create GitHub repository ✅ Ready
- Obtain all API credentials → In Progress
- Create Slack channel → To Do
- Configure n8n environment → To Do

### Phase 2: TRD Creation (Week 1)
- Run `/ai-mesh:create-trd` with approved PRD
- Review and refine technical specification
- Validate architecture decisions
- Approve TRD for implementation

### Phase 3: Implementation (Week 2)
- Run `/ai-mesh:implement-trd` with TRD
- Review generated n8n workflow
- Test API integrations
- Validate error handling
- Deploy to production

### Phase 4: Validation (Week 2-3)
- Run initial backup
- Verify GitHub commits
- Check Slack notifications
- Validate backup state accuracy
- Test incremental backup

### Phase 5: Production (Ongoing)
- Monitor daily backups
- Track success metrics
- Maintain until Make.com → n8n migration complete
- Decommission after migration

---

## Appendix: Credential Locations

### Production Credentials

| Credential | Type | Location | Rotation |
|------------|------|----------|----------|
| Make.com API Key | API Token | n8n credential store | 12 months |
| GitHub PAT | Personal Access Token | n8n credential store | 12 months |
| Slack Bot Token | OAuth Token | n8n credential store | Never expires |

### Environment Configuration

| Variable | Purpose | Source |
|----------|---------|--------|
| MAKE_TEAM_ID | Filter scenarios by team | Make.com UI |
| MAKE_ORG_ID | Filter scenarios by org | Make.com UI |
| GITHUB_OWNER | Repository owner | GitHub account |
| GITHUB_REPO | Repository name | Repository settings |
| SLACK_CHANNEL_ID | Notification channel | Slack channel details |

---

## Next Action

✅ **PRD Approved** - Ready for TRD creation

**Command:**
```bash
/ai-mesh:create-trd /Users/burke/projects/n8n/docs/PRD/make-backup-github-prd-approved.md
```

This will generate a detailed Technical Requirements Document with:
- Complete n8n workflow node configuration
- API integration specifications
- Error handling strategies
- Testing requirements
- Deployment procedures
- Task breakdown for implementation

**Expected Output:** `docs/TRD/2025-11-03-make-backup-github-migration.md`

---

**End of Approved PRD**
