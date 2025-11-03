# n8n Project - Claude Code Instructions

**Project:** n8n Claude-Driven Workflow Environment
**Purpose:** Programmatic workflow automation development
**Status:** Ready for workflow development

## Project Overview

This is a Docker-based n8n environment optimized for Claude Code to act as the primary workflow development interface. Humans define WHAT workflows should do; Claude builds HOW they work.

## Critical Standards

### Docker Commands
- ✅ **ALWAYS use**: `docker compose` (space, no hyphen)
- ❌ **NEVER use**: `docker-compose` (causes "command not found")

### File Operations
- ✅ **ALWAYS**: Use `Read` tool before `Edit` operations
- ✅ **VALIDATE**: JSON syntax after editing workflow files
- ❌ **NEVER**: Skip file reading before modifications

### Environment Variables
- ✅ **ALWAYS**: Load from `.env` file (never hardcode)
- ❌ **NEVER**: Commit `.env` to git (use `.env.example` for templates)

## Workflow Development Pattern

### When Asked to Create/Modify Workflows

1. **Suggest Agent OS Workflow** (unless user explicitly wants direct implementation):
   ```
   "I should create a proper specification for this workflow using Agent OS
   rather than implementing directly. This ensures better planning and
   documentation. Would you like me to use the `/shape-spec` command to
   gather requirements, or would you prefer direct implementation?"
   ```

2. **Agent OS Workflow**:
   - `/shape-spec` - Gather requirements with clarifying questions
   - `/write-spec` - Create detailed specification document
   - `/create-tasks` - Break down into actionable tasks
   - `/implement-tasks` - Execute implementation

3. **Direct Implementation** (if user approves):
   - Create/modify workflow JSON in `workflows/`
   - Deploy to n8n via REST API
   - Test execution
   - Commit to git

### n8n REST API Access

**Authentication**: All API calls require X-N8N-API-KEY header

**API Base URL**: `http://localhost:5678/api/v1`

**Common Operations**:

```bash
# List workflows
curl -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  http://localhost:5678/api/v1/workflows

# Create workflow
curl -X POST \
  -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  -H "Content-Type: application/json" \
  -d @workflows/my-workflow.json \
  http://localhost:5678/api/v1/workflows

# Update workflow
curl -X PUT \
  -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  -H "Content-Type: application/json" \
  -d @workflows/my-workflow.json \
  http://localhost:5678/api/v1/workflows/{id}
```

**Python Helpers** (optional):
```python
from lib.n8n_api import N8nAPI

api = N8nAPI()
api.create_workflow('workflows/my-workflow.json')
api.update_workflow(workflow_id='123', json_file='workflows/my-workflow.json')
api.execute_workflow(workflow_id='123')
```

## Project-Specific Commands

### Starting/Stopping Services

```bash
# Start services
docker compose up -d

# Check status
docker compose ps

# View logs
docker logs n8n-app
docker logs n8n-postgres

# Restart
docker compose restart

# Stop (preserves data)
docker compose down

# Stop and delete data (⚠️ destructive)
docker compose down -v
```

### Testing

```bash
# Run complete test suite
./test_workflow_api.sh

# Manual API test
source .env
curl -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  http://localhost:5678/api/v1/workflows
```

## Git Workflow

### Commits
- **Format**: `<action> <workflow-name>: <description>`
- **Examples**:
  - `Add customer onboarding workflow`
  - `Update daily reports: add new metrics`
  - `Fix salesforce sync: handle rate limiting`

### Before Commits
1. Validate JSON syntax
2. Test workflow execution
3. Verify via n8n UI if needed
4. Only commit working workflows

## Integration with Burke's Environment

### Agent OS
- Commands available: `/shape-spec`, `/write-spec`, `/create-tasks`, `/implement-tasks`
- Standards: `agent-os/standards/`
- Specs: `agent-os/specs/YYYY-MM-DD-spec-name/`

### Observability (Optional)
- Logging stack: `/Users/burke/obs/`
- Can integrate Promtail for log shipping to Loki
- Not essential for basic operation

### Linear Integration
- Workspace: Create issues for significant workflow development
- Use Direct API (not MCP): See `@CLAUDE.md` in parent workspace
- API key in `.env` files

### Git Worktrees (Important!)
If running multiple Claude Code sessions:
```bash
# Check for concurrent sessions
ps aux | grep -i "claude" | grep -v grep

# If another session active, create worktree
git worktree add ../n8n-feature1 -b feature/your-feature-name
cd ../n8n-feature1
# Work in isolation
```

## Common Tasks

### Create New Workflow
1. Suggest spec-first approach with Agent OS
2. If approved, use `/shape-spec` to gather requirements
3. Create workflow JSON in `workflows/`
4. Deploy via API
5. Test execution
6. Commit to git

### Modify Existing Workflow
1. Read existing workflow JSON
2. Make targeted modifications
3. Update via API with workflow ID
4. Test changes
5. Commit updates

### Debug Workflow
1. Retrieve workflow from n8n: `get_workflow(id, save_to='workflows/debug.json')`
2. Read execution logs from n8n UI
3. Analyze and identify issue
4. Fix in JSON
5. Update via API
6. Verify fix works
7. Commit

### Backup All Workflows
1. List all workflows via API
2. Download each as JSON
3. Save to `workflows/` directory
4. Commit backup

## Required Manual Steps

### First-Time Setup
1. User must create API key in n8n UI (cannot be automated)
2. User must add API key to `.env` file
3. After that, Claude can manage everything programmatically

### Visual Inspection
- Humans may want to verify workflows visually in n8n UI
- Claude can deploy and test programmatically
- UI access: http://localhost:5678 (admin / n8n_admin_pass_2025)

## Documentation Resources

- **Setup Guide**: `SETUP.md` - Complete setup instructions
- **Development Guide**: `WORKFLOW_DEVELOPMENT.md` - Claude Code patterns
- **API Reference**: `API_REFERENCE.md` - Complete REST API docs
- **Workflow Guide**: `workflows/README.md` - Workflow management
- **API Key Setup**: `API_KEY_SETUP.md` - Manual API key creation

## Troubleshooting

### Services Won't Start
```bash
# Check for port conflicts
docker compose down
# Edit docker-compose.yml to change ports if needed
docker compose up -d
```

### API Key Not Working
1. Verify key created in n8n UI
2. Verify key added to `.env`
3. Reload environment: `source .env`

### Workflow JSON Invalid
```bash
# Validate JSON syntax
python -m json.tool workflows/my-workflow.json

# Check n8n logs for specific errors
docker logs n8n-app
```

## Success Indicators

✅ Services healthy: `docker compose ps` shows (healthy)
✅ API accessible: `curl -H "X-N8N-API-KEY: ${N8N_API_KEY}" http://localhost:5678/api/v1/workflows` returns JSON
✅ Can create workflows via API
✅ Can update workflows via API
✅ Workflows persist after restart
✅ Test suite passes: `./test_workflow_api.sh`

## Notes for New Sessions

When starting a new Claude Code session:

1. **Check for concurrent sessions** - Avoid mixed feature branches
2. **Read this file** - Review project-specific instructions
3. **Verify services running** - `docker compose ps`
4. **Test API access** - Quick curl test
5. **Review recent commits** - Understand current state
6. **Suggest Agent OS for new work** - Spec-first approach

## Context Preservation

This project uses:
- **CLAUDE.md** (this file) - Project-specific instructions
- **Agent OS specs** - `agent-os/specs/` for feature documentation
- **Git history** - Workflow evolution and changes
- **Linear issues** - Work item tracking (optional)

When context becomes limited, key information is preserved in these locations for session handoffs.

---

**Remember**: Humans define WHAT. Claude builds HOW. Let's automate ALL the things! 🤖
