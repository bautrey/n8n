# n8n Claude-Driven Workflow Environment

A Docker-based n8n workflow automation environment optimized for Claude Code-driven development, where AI handles workflow implementation while humans focus on strategic decisions.

## Overview

This project enables **fully programmatic workflow development** using Claude Code as the primary development interface. Local workflow JSON files are the source of truth, with n8n serving as the execution engine.

### Key Features

- 🐳 **Docker Compose** orchestration (n8n + PostgreSQL)
- 🔐 **Secure authentication** (basic auth + API keys)
- 💾 **Persistent storage** (workflows and database survive restarts)
- 🤖 **Claude Code integration** (direct API access for workflow management)
- 📁 **Git-based versioning** (all workflows tracked in version control)
- 🐍 **Python helper functions** (optional convenience wrappers for API calls)
- 📝 **Comprehensive documentation** (setup, development patterns, API reference)

### The Claude Code Approach

**Traditional Workflow Development:**
- ❌ Manually build workflows in UI
- ❌ Export JSON files manually
- ❌ Track changes manually
- ❌ Deploy manually

**Claude Code Workflow Development:**
- ✅ Claude builds workflow JSON from specs
- ✅ Claude deploys via REST API
- ✅ Claude tests execution programmatically
- ✅ Claude commits to git automatically

**Result:** Humans define WHAT workflows should do. Claude builds HOW they work.

## Quick Start

### 1. Prerequisites

- Docker Desktop (running)
- Docker Compose v2+
- Git
- Python 3.8+ (optional, for helper functions)

### 2. Setup (10 minutes)

```bash
# Navigate to project
cd /Users/burke/projects/n8n

# Create environment file
cp .env.example .env

# Generate encryption key and update .env
python3 -c "import secrets; print(secrets.token_hex(16))"
# Copy output to N8N_ENCRYPTION_KEY in .env

# Start services
docker compose up -d

# Verify services are healthy
docker compose ps
```

### 3. Access n8n UI

Open http://localhost:5678

- Username: `admin`
- Password: `n8n_admin_pass_2025` (from `.env`)

### 4. Create API Key

1. In n8n UI: Settings > n8n API > Create an API key
2. Copy the key
3. Add to `.env`: `N8N_API_KEY=your_key_here`

### 5. Test API Access

```bash
source .env
curl -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  http://localhost:5678/api/v1/workflows
```

Expected: `{"data":[],"nextCursor":null}`

### 6. Run Tests

```bash
./test_workflow_api.sh
```

All tests should pass ✅

## Documentation

| Document | Purpose |
|----------|---------|
| **[SETUP.md](SETUP.md)** | Complete setup instructions and troubleshooting |
| **[WORKFLOW_DEVELOPMENT.md](WORKFLOW_DEVELOPMENT.md)** | Claude Code development patterns and best practices |
| **[API_REFERENCE.md](API_REFERENCE.md)** | Complete n8n REST API documentation |
| **[workflows/README.md](workflows/README.md)** | Workflow management guide and API examples |
| **[API_KEY_SETUP.md](API_KEY_SETUP.md)** | Step-by-step API key creation guide |

## Project Structure

```
n8n/
├── docker-compose.yml          # Service orchestration
├── .env                        # Environment variables (gitignored)
├── .env.example                # Environment template (committed)
├── .gitignore                  # Git exclusions
│
├── workflows/                  # Workflow JSON files (source of truth)
│   ├── README.md              # Workflow management guide
│   └── example-hello-world.json
│
├── lib/                        # Helper functions
│   └── n8n_api.py             # Python API wrappers
│
├── test_workflow_api.sh        # End-to-end test suite
│
└── docs/
    ├── SETUP.md               # Setup guide
    ├── WORKFLOW_DEVELOPMENT.md # Development patterns
    ├── API_REFERENCE.md       # API documentation
    └── API_KEY_SETUP.md       # API key guide
```

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Claude Code                        │
│  (Edits workflow JSON, makes API calls, commits)   │
└────────────┬────────────────────────────────────────┘
             │
             │ REST API (X-N8N-API-KEY)
             ▼
┌─────────────────────────────────────────────────────┐
│              n8n Container (localhost:5678)         │
│  - Workflow execution engine                        │
│  - UI for visual inspection                         │
│  - REST API for programmatic control                │
└────────────┬────────────────────────────────────────┘
             │
             │ PostgreSQL connection
             ▼
┌─────────────────────────────────────────────────────┐
│         PostgreSQL Container (localhost:5433)       │
│  - Workflow storage                                 │
│  - Execution logs                                   │
│  - Credential storage (encrypted)                   │
└─────────────────────────────────────────────────────┘
```

## Usage Examples

### Create Workflow

```bash
# Direct API call
curl -X POST \
  -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  -H "Content-Type: application/json" \
  -d @workflows/my-workflow.json \
  http://localhost:5678/api/v1/workflows
```

Or using Python helper:

```python
from lib.n8n_api import create_workflow

result = create_workflow('workflows/my-workflow.json')
print(f"Created workflow ID: {result['id']}")
```

### Update Workflow

```bash
# Direct API call
curl -X PUT \
  -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  -H "Content-Type: application/json" \
  -d @workflows/my-workflow.json \
  http://localhost:5678/api/v1/workflows/123
```

Or using Python helper:

```python
from lib.n8n_api import update_workflow

update_workflow(workflow_id='123', json_file='workflows/my-workflow.json')
```

### List All Workflows

```bash
curl -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  http://localhost:5678/api/v1/workflows
```

See [API_REFERENCE.md](API_REFERENCE.md) for complete API documentation.

## Development Workflow

1. **Create Spec** - Use Agent OS to define what workflow should do
2. **Build JSON** - Claude creates/modifies workflow JSON locally
3. **Deploy** - Claude posts JSON to n8n API
4. **Test** - Claude executes workflow and verifies results
5. **Commit** - Claude commits working workflow to git
6. **Iterate** - Repeat for changes and improvements

See [WORKFLOW_DEVELOPMENT.md](WORKFLOW_DEVELOPMENT.md) for detailed patterns.

## Success Criteria

✅ Services start without errors (`docker compose ps` shows healthy)
✅ n8n UI accessible at http://localhost:5678
✅ Can login with credentials from `.env`
✅ API key created and added to `.env`
✅ API test returns successful response
✅ Can create workflows via API
✅ Can update workflows via API
✅ Workflows persist after container restarts
✅ Test suite passes: `./test_workflow_api.sh`

## Troubleshooting

See [SETUP.md](SETUP.md#troubleshooting) for common issues and solutions.

**Quick Checks:**

```bash
# Check container status
docker compose ps

# View logs
docker logs n8n-app
docker logs n8n-postgres

# Restart services
docker compose restart

# Complete reset (⚠️ deletes all data)
docker compose down -v
docker compose up -d
```

## Integration with Burke's Environment

This project follows Burke's workspace standards:

- **Docker Standards**: Uses `docker compose` (space, not hyphen)
- **Agent OS**: Spec-first development with `/shape-spec` workflow
- **Git Standards**: Conventional commits, feature branches
- **Observability**: Can integrate with `/Users/burke/obs/` logging stack
- **Environment Variables**: `.env` pattern with `.env.example` template

See [CLAUDE.md](CLAUDE.md) for project-specific Claude Code instructions.

## Contributing

When adding new workflows:

1. Create spec first using Agent OS
2. Build workflow JSON following established patterns
3. Test thoroughly via API and UI
4. Document any special requirements
5. Commit with descriptive message
6. Tag stable versions

## License

This is a personal development environment for Burke's workflow automation needs.

## Resources

- **n8n Documentation**: https://docs.n8n.io/
- **n8n Community**: https://community.n8n.io/
- **n8n Workflow Templates**: https://n8n.io/workflows
- **Agent OS**: `~/agent-os/` (installed per-project)

## Support

For issues or questions:
- Check [SETUP.md](SETUP.md#troubleshooting) for common problems
- Review [API_REFERENCE.md](API_REFERENCE.md) for API details
- Consult n8n documentation
- Ask Claude Code for help!

---

**Built with ❤️ for automated workflow development**
