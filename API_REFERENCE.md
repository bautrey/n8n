# n8n REST API Reference

Complete reference for the n8n REST API used in this project.

## Base URL

```
http://localhost:5678/api/v1
```

## Authentication

All API requests require the `X-N8N-API-KEY` header:

```bash
-H "X-N8N-API-KEY: your_api_key_here"
```

Get your API key from n8n UI: Settings > n8n API > Create an API key

## Common Response Formats

### Success Response
```json
{
  "id": "123",
  "name": "My Workflow",
  "active": false,
  "nodes": [...],
  "connections": {...},
  "createdAt": "2025-10-31T12:00:00.000Z",
  "updatedAt": "2025-10-31T12:00:00.000Z"
}
```

### Error Response
```json
{
  "message": "Error description",
  "httpStatusCode": 400
}
```

## Endpoints

### List Workflows

**GET** `/workflows`

List all workflows.

**Query Parameters:**
- `active` (boolean, optional) - Filter by active status
- `tags` (string, optional) - Filter by tags (comma-separated)

**Example:**
```bash
curl -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  "http://localhost:5678/api/v1/workflows?active=true"
```

**Response:**
```json
{
  "data": [
    {
      "id": "123",
      "name": "My Workflow",
      "active": true,
      "createdAt": "2025-10-31T12:00:00.000Z",
      "updatedAt": "2025-10-31T12:00:00.000Z"
    }
  ],
  "nextCursor": null
}
```

---

### Get Workflow

**GET** `/workflows/:id`

Get a specific workflow by ID.

**Path Parameters:**
- `id` (string, required) - Workflow ID

**Example:**
```bash
curl -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  http://localhost:5678/api/v1/workflows/123
```

**Response:**
```json
{
  "id": "123",
  "name": "My Workflow",
  "active": false,
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
  "settings": {},
  "tags": []
}
```

---

### Create Workflow

**POST** `/workflows`

Create a new workflow.

**Request Body:**
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

**Example:**
```bash
curl -X POST \
  -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  -H "Content-Type: application/json" \
  -d @workflows/my-workflow.json \
  http://localhost:5678/api/v1/workflows
```

**Response:**
```json
{
  "id": "456",
  "name": "My Workflow",
  "active": false,
  "nodes": [...],
  "connections": {},
  "createdAt": "2025-10-31T12:00:00.000Z",
  "updatedAt": "2025-10-31T12:00:00.000Z"
}
```

---

### Update Workflow

**PUT** `/workflows/:id`

Update an existing workflow.

**Path Parameters:**
- `id` (string, required) - Workflow ID

**Request Body:**
```json
{
  "name": "Updated Workflow Name",
  "nodes": [...],
  "connections": {...},
  "active": true,
  "settings": {},
  "tags": ["production"]
}
```

**Example:**
```bash
curl -X PUT \
  -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  -H "Content-Type: application/json" \
  -d @workflows/my-workflow.json \
  http://localhost:5678/api/v1/workflows/123
```

**Response:**
```json
{
  "id": "123",
  "name": "Updated Workflow Name",
  "active": true,
  "updatedAt": "2025-10-31T13:00:00.000Z"
}
```

---

### Delete Workflow

**DELETE** `/workflows/:id`

Delete a workflow by ID.

**Path Parameters:**
- `id` (string, required) - Workflow ID

**Example:**
```bash
curl -X DELETE \
  -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  http://localhost:5678/api/v1/workflows/123
```

**Response:**
```json
{
  "message": "Workflow deleted successfully"
}
```

---

### Execute Workflow

**POST** `/workflows/:id/execute`

Manually execute a workflow.

**Path Parameters:**
- `id` (string, required) - Workflow ID

**Request Body (optional):**
```json
{
  "data": {
    "customField": "value"
  }
}
```

**Example:**
```bash
curl -X POST \
  -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  -H "Content-Type: application/json" \
  http://localhost:5678/api/v1/workflows/123/execute
```

**Response:**
```json
{
  "data": {
    "resultData": {
      "runData": {...}
    }
  },
  "finished": true,
  "mode": "manual",
  "startedAt": "2025-10-31T12:00:00.000Z",
  "stoppedAt": "2025-10-31T12:00:05.000Z"
}
```

---

### Activate Workflow

**POST** `/workflows/:id/activate`

Activate a workflow to run automatically.

**Path Parameters:**
- `id` (string, required) - Workflow ID

**Example:**
```bash
curl -X POST \
  -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  http://localhost:5678/api/v1/workflows/123/activate
```

---

### Deactivate Workflow

**POST** `/workflows/:id/deactivate`

Deactivate a workflow to stop automatic execution.

**Path Parameters:**
- `id` (string, required) - Workflow ID

**Example:**
```bash
curl -X POST \
  -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  http://localhost:5678/api/v1/workflows/123/deactivate
```

---

## Error Codes

| HTTP Status | Description |
|------------|-------------|
| 200 | Success |
| 201 | Created successfully |
| 400 | Bad request (invalid JSON, missing required fields) |
| 401 | Unauthorized (invalid or missing API key) |
| 404 | Not found (workflow doesn't exist) |
| 500 | Internal server error |

## Rate Limiting

n8n does not enforce rate limits on the REST API for self-hosted instances.

For production use, consider implementing rate limiting at the reverse proxy level.

## Python Helper Functions

All these API calls are wrapped in `lib/n8n_api.py`:

```python
from lib.n8n_api import N8nAPI

api = N8nAPI()

# Create
workflow = api.create_workflow('workflows/my-workflow.json')

# Read
workflow = api.get_workflow(workflow_id='123')
workflows = api.list_workflows(active_only=True)

# Update
api.update_workflow(workflow_id='123', json_file='workflows/updated.json')

# Delete
api.delete_workflow(workflow_id='123')

# Execute
result = api.execute_workflow(workflow_id='123')
```

See `lib/n8n_api.py` for complete documentation and error handling.

## Workflow JSON Structure

### Minimal Workflow
```json
{
  "name": "Minimal Workflow",
  "nodes": [
    {
      "name": "Start",
      "type": "n8n-nodes-base.manualTrigger",
      "typeVersion": 1,
      "position": [250, 300],
      "parameters": {}
    }
  ],
  "connections": {},
  "active": false
}
```

### Complete Workflow Example
```json
{
  "name": "Complete Example",
  "nodes": [
    {
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 1,
      "position": [250, 300],
      "parameters": {
        "path": "customer-signup",
        "responseMode": "responseNode",
        "responseData": "firstEntryJson"
      }
    },
    {
      "name": "Set Customer Data",
      "type": "n8n-nodes-base.set",
      "typeVersion": 1,
      "position": [450, 300],
      "parameters": {
        "values": {
          "string": [
            {
              "name": "email",
              "value": "={{$json.email}}"
            },
            {
              "name": "name",
              "value": "={{$json.name}}"
            }
          ]
        }
      }
    }
  ],
  "connections": {
    "Webhook": {
      "main": [
        [
          {
            "node": "Set Customer Data",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  },
  "active": false,
  "settings": {
    "executionOrder": "v1"
  },
  "tags": ["webhook", "customer"]
}
```

## Additional Resources

- Official n8n API Docs: https://docs.n8n.io/api/
- n8n Node Types: https://docs.n8n.io/integrations/builtin/
- n8n Expressions: https://docs.n8n.io/code-examples/expressions/

## Testing API Calls

Use the provided test script:

```bash
./test_workflow_api.sh
```

This validates all major API operations are working correctly.
