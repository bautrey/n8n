# n8n Workflow Automation Project - Kickoff Instructions

**Created:** 2025-10-31
**Purpose:** Complete n8n setup for migrating Make.com workflows to self-hosted automation platform
**Status:** Ready for Agent OS specification phase

## Project Objective

Build a complete n8n workflow automation environment that enables:
1. **Local Development**: Docker-based n8n instance with PostgreSQL
2. **Make.com Migration**: Tools to convert Make.com blueprints to n8n workflows
3. **Version Control**: Git-based workflow management with JSON files
4. **Production Deployment**: Render.com containerized deployment with persistent storage
5. **Claude Code Management**: Full programmatic workflow maintenance via CLI

## Agent OS Workflow - Start Here

When you start working in this directory, use the Agent OS 2.1 workflow:

```bash
# 1. Shape the specification (gather requirements)
/shape-spec

# 2. Write detailed specification
/write-spec

# 3. Create task breakdown
/create-tasks

# 4. Implement with orchestration
/orchestrate-tasks
```

## Technical Requirements

### 1. Local Docker Environment
- **n8n UI**: Accessible at http://localhost:5678
- **Database**: PostgreSQL container for workflow persistence
- **Network**: Isolated Docker network for service communication
- **Volumes**: Persistent storage for workflows and database
- **Configuration**: docker-compose.yml with production-ready settings

### 2. Make.com to n8n Conversion Tools
- **Blueprint Parser**: Extract Make.com scenario blueprints via API
- **Schema Mapper**: Convert Make.com modules to n8n nodes
- **Connection Translator**: Map Make.com connections to n8n credentials
- **Data Transformation**: Convert Make.com data mappings to n8n expressions
- **Validation**: Verify converted workflows are executable

### 3. Workflow Management System
- **Directory Structure**:
  ```
  workflows/
  ├── from-make/          # Original Make.com blueprints (JSON)
  ├── converted/          # n8n format workflows (pre-import)
  ├── active/             # Currently deployed workflows
  └── archived/           # Deprecated workflows
  ```
- **Git Integration**: Automatic commit/push on workflow changes
- **Sync Tools**: Bidirectional sync between n8n instance and git repo
- **Metadata**: Track conversion date, source scenario ID, version history

### 4. Render.com Deployment
- **Dockerfile**: Production-optimized container image
- **render.yaml**: Infrastructure-as-code deployment config
- **Environment Variables**: Secure credential management
- **Persistent Disk**: Mounted storage for /data directory
- **PostgreSQL**: Managed Render PostgreSQL instance
- **Health Checks**: Automated restart and monitoring
- **Auto-Deploy**: Git push triggers deployment

### 5. Documentation
- **SETUP.md**: Complete local development setup guide
- **CONVERSION.md**: Step-by-step Make.com migration guide
- **DEPLOYMENT.md**: Render.com deployment procedures
- **WORKFLOW_MANAGEMENT.md**: Git-based workflow operations
- **CLAUDE.md**: Project-specific Claude Code instructions

## Key Technologies

- **n8n**: v1.x (latest stable) - workflow automation engine
- **PostgreSQL**: 15+ - workflow and credential storage
- **Docker**: Containerization for local + production
- **Docker Compose**: Multi-container orchestration
- **Render.com**: Production hosting platform
- **Make.com API**: Scenario blueprint extraction

## Success Criteria

✅ **Local Environment**:
- Run `docker compose up -d` and access n8n at http://localhost:5678
- Create test workflow and persist after container restart
- PostgreSQL connection working with proper migrations

✅ **Conversion Pipeline**:
- Successfully convert at least one Make.com scenario to n8n
- Document any manual intervention required
- Validate converted workflow executes correctly

✅ **Version Control**:
- Workflows stored as JSON in git repository
- Commit workflow changes with meaningful messages
- Can restore workflows from git history

✅ **Production Deployment**:
- Deploy to Render.com with one command
- Persistent storage survives container restarts
- Environment variables properly configured
- Accessible via public URL with HTTPS

✅ **Documentation**:
- Complete setup instructions for new developers
- Conversion process documented with examples
- Troubleshooting guide for common issues

## Integration with Burke's Environment

This project should integrate with existing Burke workspace standards:

- **Observability**: Log to `/Users/burke/obs/` stack (Loki + Promtail)
- **Agent OS**: Use `.claude/commands/agent-os/` workflow commands
- **Git Standards**: Conventional commits, feature branches
- **Docker Standards**: Use `docker compose` (no hyphen)
- **Linear**: Create tracking issue in appropriate workspace

## Environment Setup Notes

**Required Environment Variables** (will be defined in spec):
- `N8N_BASIC_AUTH_ACTIVE=true` - Enable authentication
- `N8N_BASIC_AUTH_USER=admin` - Default admin user
- `N8N_BASIC_AUTH_PASSWORD=<secure-password>` - Admin password
- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` - Database config
- `N8N_ENCRYPTION_KEY` - For credential encryption
- `WEBHOOK_URL` - Production webhook base URL

**Docker Compose Services**:
- `n8n` - Main workflow automation engine
- `postgres` - Database for persistence
- `n8n-import` - Optional: Workflow import sidecar

## Make.com API Integration

**Authentication**:
- API key stored in `.env` file (not committed)
- Access via `MAKE_API_KEY` environment variable

**Key Endpoints**:
- `GET /api/v2/scenarios` - List all scenarios
- `GET /api/v2/scenarios/{id}` - Get scenario blueprint
- `POST /api/v2/scenarios/{id}/run` - Test scenario execution

**Blueprint Structure**:
- Returned as JSON string (needs parsing)
- Contains modules, connections, mappings, scheduling
- May reference external data stores

## Next Steps for New Session

1. **Read this document completely**
2. **Check Agent OS setup**: Verify `.claude/commands/agent-os/` exists
3. **Run `/shape-spec`**: Answer questions about requirements
4. **Run `/write-spec`**: Generate detailed specification
5. **Review spec**: Ensure all requirements captured
6. **Run `/create-tasks`**: Break down into actionable tasks
7. **Run `/orchestrate-tasks`**: Execute implementation with specialized agents

## Questions to Clarify During /shape-spec

1. **Make.com API Access**: Do we have API key ready? Which scenarios to migrate first?
2. **Render.com Account**: Do we have Render account set up? GitHub repo connected?
3. **Database Preference**: PostgreSQL (recommended) or SQLite for local dev?
4. **Authentication**: Basic auth or OAuth for n8n UI?
5. **Webhook Configuration**: Need public webhook URLs for testing?
6. **Backup Strategy**: Automated backups of workflows and credentials?
7. **Monitoring**: Integrate with Burke's `/Users/burke/obs/` logging stack?

## Resources

- **n8n Documentation**: https://docs.n8n.io/
- **n8n Docker Hub**: https://hub.docker.com/r/n8nio/n8n
- **Render n8n Template**: https://render.com/deploy-docker/n8n
- **Make.com API Docs**: https://developers.make.com/api-documentation/
- **Burke's Observability Stack**: `/Users/burke/obs/OBS_LOGGING.md`

## Notes from Previous Session

- User has existing Make.com workflows that need migration
- Claude Code will be primary maintenance interface for workflows
- Need programmatic access (not just UI) for workflow management
- Cost savings motivation: Move from per-execution SaaS to fixed hosting
- Integration with Agent OS for workflow specs and documentation

---

**When you start the new session, begin with:**
```
"I see this is a new n8n project for migrating Make.com workflows. Let me start with the Agent OS specification workflow using /shape-spec to gather all requirements."
```
