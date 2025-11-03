# n8n Workflows

This directory contains n8n workflow JSON files managed via the n8n REST API.

## Workflow Development Pattern

Local workflow JSON files are the **source of truth**. The n8n instance is the deployment target.

### Development Flow

1. **Create/Edit** workflow JSON file locally in this directory
2. **Deploy** to n8n via REST API (direct curl or helper functions)
3. **Test** workflow execution via n8n API or UI
4. **Commit** changes to git

### Using the n8n REST API Directly

#### Authentication
All API calls require an API key via the `X-N8N-API-KEY` header.

**First-time setup:**
1. Access n8n UI at http://localhost:5678
2. Go to Settings > n8n API
3. Click "Create an API key"
4. Copy the API key
5. Add it to your `.env` file as `N8N_API_KEY=your_key_here`

#### List All Workflows
```bash
curl -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  http://localhost:5678/api/v1/workflows
```

#### Get Specific Workflow
```bash
curl -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  http://localhost:5678/api/v1/workflows/{workflow_id}
```

#### Create Workflow
```bash
curl -X POST \
  -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  -H "Content-Type: application/json" \
  -d @workflows/my-workflow.json \
  http://localhost:5678/api/v1/workflows
```

#### Update Workflow
```bash
curl -X PUT \
  -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  -H "Content-Type: application/json" \
  -d @workflows/my-workflow.json \
  http://localhost:5678/api/v1/workflows/{workflow_id}
```

#### Delete Workflow
```bash
curl -X DELETE \
  -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  http://localhost:5678/api/v1/workflows/{workflow_id}
```

#### Execute Workflow
```bash
curl -X POST \
  -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  http://localhost:5678/api/v1/workflows/{workflow_id}/execute
```

### Using Helper Functions (Optional)

Python helper functions are available in `lib/n8n_api.py`:

```python
from lib.n8n_api import N8nAPI

api = N8nAPI()

# Create workflow
response = api.create_workflow('workflows/my-workflow.json')
print(f"Created workflow ID: {response['id']}")

# Update workflow
api.update_workflow(workflow_id='123', json_file='workflows/my-workflow.json')

# Get workflow
workflow = api.get_workflow(workflow_id='123')

# List all workflows
workflows = api.list_workflows()

# Delete workflow
api.delete_workflow(workflow_id='123')
```

## Workflow JSON Format

n8n workflows are JSON objects with the following structure:

```json
{
  "name": "My Workflow",
  "nodes": [
    {
      "name": "Start",
      "type": "n8n-nodes-base.start",
      "position": [250, 300],
      "parameters": {},
      "typeVersion": 1
    }
  ],
  "connections": {},
  "active": false,
  "settings": {},
  "tags": []
}
```

## Claude Code Workflow Development

Claude Code can:
- Edit workflow JSON files directly
- Make API calls via curl to deploy workflows
- Use Python helper functions for cleaner code
- Test workflows via API
- Commit changes to git

## Git Best Practices

- Commit workflow JSON files after testing
- Use descriptive commit messages: "Add customer onboarding workflow"
- Tag major workflow versions
- Review workflow changes in pull requests

## Example Workflows

See `example-hello-world.json` for a minimal working example.
