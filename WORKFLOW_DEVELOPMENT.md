# Workflow Development with Claude Code

Complete guide for Claude Code-driven n8n workflow development.

## Overview

This project enables Claude Code to act as the primary workflow development interface. Local JSON files are the source of truth, and the n8n instance is the deployment target.

## Development Pattern

### Traditional Approach (Manual)
❌ Edit workflows in n8n UI → Export JSON manually → Commit to git

### Claude Code Approach (Automated)
✅ Claude edits workflow JSON locally → Deploys via API → Tests → Commits to git

## 🚨 CRITICAL: Programmatic Execution Requirements

**Workflows MUST use webhook triggers for programmatic execution**

### Why Webhook Triggers Are Required

n8n's REST API does not provide a reliable `/workflows/:id/execute` endpoint across all versions. The **only reliable way** to execute workflows programmatically is via webhook triggers.

### Workflow Structure Requirements

All workflows intended for programmatic execution must:

1. ✅ **Use webhook trigger node** (not manual trigger)
2. ✅ **Configure webhook path** (e.g., "hello-world")
3. ✅ **Be activated** before execution
4. ✅ **Respond to HTTP methods** (GET, POST, etc.)

### Example Webhook Trigger Node

```json
{
  "parameters": {
    "path": "hello-world",
    "responseMode": "lastNode",
    "options": {}
  },
  "name": "Webhook Trigger",
  "type": "n8n-nodes-base.webhook",
  "typeVersion": 1,
  "position": [250, 300],
  "webhookId": "unique-webhook-id"
}
```

### Execution Flow

1. **Deploy**: Create workflow via API
2. **Activate**: Enable webhook endpoint
3. **Execute**: Call `http://localhost:5678/webhook/{path}`
4. **Response**: Workflow returns result as HTTP response

## Workflow Development Lifecycle

### 1. Create Specification for New Workflow

Use Agent OS to create a spec for each new workflow:

```bash
# In n8n project directory
/shape-spec
```

Describe the workflow you want to build. Agent OS will:
- Ask clarifying questions about the workflow
- Create a detailed specification
- Generate task breakdown for implementation

### 2. Claude Builds Workflow JSON

Claude Code creates or modifies workflow JSON files in `workflows/`:

```json
{
  "name": "Customer Onboarding",
  "nodes": [
    {
      "name": "Webhook Trigger",
      "type": "n8n-nodes-base.webhook",
      "parameters": {...},
      "position": [250, 300]
    },
    {
      "name": "Create User Record",
      "type": "n8n-nodes-base.postgres",
      "parameters": {...},
      "position": [450, 300]
    }
  ],
  "connections": {...}
}
```

### 3. Deploy to n8n via API

**Option A - Direct curl:**
```bash
curl -X POST \
  -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  -H "Content-Type: application/json" \
  -d @workflows/customer-onboarding.json \
  http://localhost:5678/api/v1/workflows
```

**Option B - Python helper:**
```python
from lib.n8n_api import create_workflow

result = create_workflow('workflows/customer-onboarding.json')
print(f"Created workflow ID: {result['id']}")
```

### 4. Test Workflow

**Visual testing in UI:**
- Open http://localhost:5678
- Find workflow in list
- Click "Test workflow" button
- Verify execution

**Programmatic testing via API:**
```bash
curl -X POST \
  -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  http://localhost:5678/api/v1/workflows/{workflow_id}/execute
```

### 5. Iterate and Update

Claude makes changes to local JSON file, then updates via API:

```bash
curl -X PUT \
  -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  -H "Content-Type: application/json" \
  -d @workflows/customer-onboarding.json \
  http://localhost:5678/api/v1/workflows/{workflow_id}
```

### 6. Commit to Git

Once workflow is tested and working:

```bash
git add workflows/customer-onboarding.json
git commit -m "Add customer onboarding workflow

- Webhook trigger for new customer signups
- Creates user record in PostgreSQL
- Sends welcome email via SendGrid
- Notifies team in Slack

Tested and verified working."
```

## Claude Code Workflow Examples

### Example 1: Creating a New Workflow

```python
# Claude reads the spec and understands requirements
from lib.n8n_api import N8nAPI

# Create workflow JSON based on spec
workflow = {
    "name": "Daily Report Generator",
    "nodes": [
        # ... workflow configuration
    ]
}

# Save to file
with open('workflows/daily-report.json', 'w') as f:
    json.dump(workflow, f, indent=2)

# Deploy to n8n
api = N8nAPI()
result = api.create_workflow('workflows/daily-report.json')

# Commit to git
os.system('git add workflows/daily-report.json')
os.system('git commit -m "Add daily report generator workflow"')
```

### Example 2: Updating Existing Workflow

```python
# Load existing workflow
with open('workflows/customer-onboarding.json', 'r') as f:
    workflow = json.load(f)

# Add new node
workflow['nodes'].append({
    "name": "Send Welcome SMS",
    "type": "n8n-nodes-base.twilio",
    # ... configuration
})

# Save changes
with open('workflows/customer-onboarding.json', 'w') as f:
    json.dump(workflow, f, indent=2)

# Update in n8n
api.update_workflow(workflow_id='123', json_file='workflows/customer-onboarding.json')

# Test
result = api.execute_workflow(workflow_id='123')

# If test passes, commit
os.system('git add workflows/customer-onboarding.json')
os.system('git commit -m "Add SMS notification to onboarding workflow"')
```

### Example 3: Backup Existing Workflows

```python
# Get all workflows from n8n
api = N8nAPI()
workflows = api.list_workflows()

# Save each to file
for workflow in workflows:
    filename = f"workflows/{workflow['name'].lower().replace(' ', '-')}.json"
    with open(filename, 'w') as f:
        json.dump(workflow, f, indent=2)
    print(f"Saved: {filename}")

# Commit backup
os.system('git add workflows/*.json')
os.system('git commit -m "Backup all workflows from n8n instance"')
```

## Best Practices

### File Naming
- Use kebab-case: `customer-onboarding.json`
- Be descriptive: `send-weekly-report-email.json` not `workflow-1.json`
- Include version if needed: `data-sync-v2.json`

### Workflow Organization
```
workflows/
├── README.md
├── customer-onboarding.json
├── daily-reports.json
├── data-sync.json
└── integrations/
    ├── salesforce-sync.json
    └── slack-notifications.json
```

### Git Commit Messages
- **Format:** `<action> <workflow-name>: <description>`
- **Examples:**
  - `Add customer onboarding workflow`
  - `Update daily reports: add new metrics`
  - `Fix salesforce sync: handle rate limiting`

### Testing Strategy
1. **Unit test** individual nodes in n8n UI
2. **Integration test** full workflow with test data
3. **Monitor** first few production executions
4. **Iterate** based on real-world usage

### Version Control
- Commit after each successful test
- Tag stable versions: `git tag v1.0-customer-onboarding`
- Create branches for major changes
- Use pull requests for team review

## Human Involvement

Humans are involved for:
- **Spec creation** - defining what workflows should do
- **Visual inspection** - verifying workflows in n8n UI
- **Business decisions** - approving workflow logic
- **Production deployment** - final approval before activation

Humans are NOT involved for:
- Writing workflow JSON (Claude does this)
- Deploying to n8n (Claude does this)
- Testing workflows (Claude does this)
- Committing to git (Claude does this)

## Common Workflows

### Add New Trigger
1. Claude adds webhook/schedule/email trigger node to JSON
2. Claude deploys updated workflow
3. Human tests trigger in UI
4. Claude commits if test passes

### Add Data Transformation
1. Claude adds Set/Function/Code node to JSON
2. Claude defines data mapping expressions
3. Claude deploys and tests with sample data
4. Claude commits if transformations work correctly

### Integrate External Service
1. Claude adds HTTP Request/API node
2. Claude configures authentication (references credentials)
3. Claude adds error handling nodes
4. Claude deploys and tests API calls
5. Claude commits if integration works

### Debug Failing Workflow
1. Human reports issue
2. Claude retrieves workflow from n8n: `get_workflow(id, save_to='workflows/debug.json')`
3. Claude analyzes JSON and execution logs
4. Claude identifies and fixes issue in JSON
5. Claude deploys fix
6. Human verifies fix in production
7. Claude commits fix

## Troubleshooting

### Workflow Won't Activate
- Check all required credentials are configured in n8n UI
- Verify trigger configuration (webhook URLs, cron expressions)
- Check execution logs for startup errors

### Workflow Executes But Fails
- Review execution logs in n8n UI for specific node failures
- Test individual nodes with sample data
- Check API rate limits and authentication

### JSON Syntax Errors
- Validate JSON: `python -m json.tool workflows/my-workflow.json`
- Check node connections are valid
- Ensure all required parameters are present

## Additional Resources

- n8n Node Documentation: https://docs.n8n.io/integrations/builtin/
- Workflow Templates: https://n8n.io/workflows
- Community Forum: https://community.n8n.io

## Next Steps

1. Create your first workflow spec with `/shape-spec`
2. Have Claude build the workflow JSON
3. Deploy and test via API
4. Commit to git
5. Repeat!

The goal: **Humans define WHAT, Claude builds HOW.**
