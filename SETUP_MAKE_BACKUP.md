# Make.com Backup Setup Checklist

Quick setup guide for implementing the Make.com → GitHub backup system.

---

## 🎯 Prerequisites Setup

### 1. GitHub Repository

```bash
# Create private repository
gh repo create bautrey/make-scenarios-backup \
  --private \
  --description "Automated backups of Make.com scenarios" \
  --clone=false

# Initialize with README
cat > /tmp/README.md << 'EOF'
# Make.com Scenarios Backup

Automated backup repository for all Make.com scenarios from Fortium Partners.

## Structure

- `scenarios/{id}/metadata.json` - Scenario metadata and configuration
- `scenarios/{id}/blueprint.json` - Complete scenario blueprint
- `.backup-state.json` - Backup tracking state (managed automatically)

## Backup Schedule

Backups run daily at 2:00 AM US/Central via n8n workflow.

## Restoration

To restore a scenario:
1. Navigate to desired scenario directory
2. Download `blueprint.json`
3. Import into Make.com via UI or API
EOF

# Push README
cd /tmp
git clone https://github.com/bautrey/make-scenarios-backup.git
cd make-scenarios-backup
cp /tmp/README.md .
git add README.md
git commit -m "Initial commit: Repository setup"
git push origin main
```

✅ **Verify:** https://github.com/bautrey/make-scenarios-backup

---

### 2. Make.com API Key

**Steps:**
1. Login: https://www.make.com
2. Navigate: Settings → API
3. Click: "Create an API Token"
4. Name: `n8n Backup System`
5. Permissions: ✅ Read (scenarios, blueprints)
6. **Save the token** (shown only once!)

**Test the key:**
```bash
# Replace YOUR_API_KEY with actual token
export MAKE_API_KEY="YOUR_API_KEY"

curl -X GET "https://us1.make.com/api/v2/scenarios?teamId=154819&organizationId=395687&pg[limit]=1" \
  -H "Authorization: Token ${MAKE_API_KEY}" \
  -H "Accept: application/json"

# Expected: JSON response with scenarios array
```

✅ **Store in:** `/Users/burke/projects/n8n/.env` → `MAKE_API_KEY=...`

---

### 3. GitHub Personal Access Token

**Steps:**
1. Login: https://github.com
2. Navigate: Settings → Developer settings → Personal access tokens → Tokens (classic)
3. Click: "Generate new token (classic)"
4. Name: `n8n Make.com Backup`
5. Expiration: No expiration (or 1 year with reminder)
6. Scopes: ✅ `repo` (Full control of private repositories)
7. Generate token
8. **Save the token** (shown only once!)

**Test the token:**
```bash
# Replace YOUR_GITHUB_PAT with actual token
export GITHUB_PAT="YOUR_GITHUB_PAT"

curl -X GET "https://api.github.com/repos/bautrey/make-scenarios-backup" \
  -H "Authorization: Bearer ${GITHUB_PAT}" \
  -H "Accept: application/vnd.github+json"

# Expected: JSON response with repository details
```

✅ **Store in:** `/Users/burke/projects/n8n/.env` → `GITHUB_PAT=...`

---

### 4. Slack Bot Setup

**Create Slack App:**
1. Go to: https://api.slack.com/apps
2. Click: "Create New App" → "From scratch"
3. App Name: `n8n Automation Bot`
4. Workspace: Fortium Partners

**Add Permissions:**
1. Navigate: OAuth & Permissions
2. Add Bot Token Scopes:
   - `chat:write` - Send messages
   - `chat:write.public` - Send to channels without joining
3. Click: "Install to Workspace"
4. Authorize the app
5. **Copy "Bot User OAuth Token"** (starts with `xoxb-`)

**Create Slack Channel:**
1. Create private channel: `#n8n-automation`
2. Invite bot: `/invite @n8n Automation Bot`
3. Get channel ID:
   - Click channel name
   - Click "About" tab
   - Copy Channel ID (at bottom)

**Test the bot:**
```bash
# Replace tokens with actual values
export SLACK_BOT_TOKEN="xoxb-YOUR-TOKEN"
export SLACK_CHANNEL_ID="C0123456789"

curl -X POST "https://slack.com/api/chat.postMessage" \
  -H "Authorization: Bearer ${SLACK_BOT_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"channel\": \"${SLACK_CHANNEL_ID}\",
    \"text\": \"🤖 n8n Automation Bot is online! Testing Slack integration.\"
  }"

# Expected: {"ok": true, ...}
```

✅ **Store in:** `/Users/burke/projects/n8n/.env` → `SLACK_BOT_TOKEN=...` and `SLACK_CHANNEL_ID=...`

---

### 5. Update n8n Environment

Edit `/Users/burke/projects/n8n/.env`:

```bash
# Make.com API
MAKE_API_KEY=your_actual_make_api_key_here
MAKE_API_BASE_URL=https://us1.make.com/api/v2
MAKE_TEAM_ID=154819
MAKE_ORG_ID=395687

# GitHub API
GITHUB_PAT=your_actual_github_pat_here
GITHUB_OWNER=bautrey
GITHUB_REPO=make-scenarios-backup
GITHUB_BRANCH=main
GITHUB_BOT_NAME="Make.com Backup Bot"
GITHUB_BOT_EMAIL="bot@fortiumpartners.com"

# Slack API
SLACK_BOT_TOKEN=xoxb-your-actual-slack-token-here
SLACK_CHANNEL_ID=C0123456789
SLACK_BOT_NAME="n8n Automation Bot"

# Backup Configuration
BACKUP_SCHEDULE="0 2 * * *"
BACKUP_TIMEZONE="America/Chicago"
```

**Restart n8n to load new environment:**
```bash
cd /Users/burke/projects/n8n
docker compose restart
```

---

### 6. Configure n8n Credentials

**In n8n UI (http://localhost:5678):**

**Make.com Credential:**
1. Settings → Credentials → New Credential
2. Type: "Header Auth"
3. Name: `Make.com API`
4. Credential Data:
   - Header Name: `Authorization`
   - Header Value: `Token ${MAKE_API_KEY}`
5. Save

**GitHub Credential:**
1. Settings → Credentials → New Credential
2. Type: "Header Auth"
3. Name: `GitHub API (Burke)`
4. Credential Data:
   - Header Name: `Authorization`
   - Header Value: `Bearer ${GITHUB_PAT}`
5. Save

**Slack Credential:**
1. Settings → Credentials → New Credential
2. Type: "Slack OAuth2 API"
3. Name: `Slack n8n Bot`
4. OAuth Token: `${SLACK_BOT_TOKEN}`
5. Save

---

## ✅ Verification Checklist

Before proceeding to TRD creation:

- [ ] GitHub repository created and accessible
- [ ] README.md committed to repository
- [ ] Make.com API key obtained and tested
- [ ] GitHub PAT obtained and tested
- [ ] Slack bot created and tested
- [ ] Slack channel `#n8n-automation` created
- [ ] Bot invited to Slack channel
- [ ] All environment variables added to `.env`
- [ ] n8n services restarted
- [ ] All three credentials configured in n8n UI
- [ ] Test message posted to Slack successfully

---

## 🚀 Next Step: Create TRD

Once all prerequisites are complete:

```bash
/ai-mesh:create-trd /Users/burke/projects/n8n/docs/PRD/make-backup-github-prd-approved.md
```

This will generate the Technical Requirements Document with detailed implementation specifications.

---

## 📋 Quick Reference

| Service | Test Command |
|---------|--------------|
| Make.com API | `curl -H "Authorization: Token $MAKE_API_KEY" https://us1.make.com/api/v2/scenarios?teamId=154819\&pg[limit]=1` |
| GitHub API | `curl -H "Authorization: Bearer $GITHUB_PAT" https://api.github.com/repos/bautrey/make-scenarios-backup` |
| Slack API | `curl -X POST -H "Authorization: Bearer $SLACK_BOT_TOKEN" -d '{"channel":"$SLACK_CHANNEL_ID","text":"Test"}' https://slack.com/api/chat.postMessage` |

---

**Status:** Ready for setup ✨
