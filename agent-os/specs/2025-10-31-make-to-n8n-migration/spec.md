# Specification: n8n Claude-Driven Workflow Environment

## Goal

Create a local Docker-based n8n environment with PostgreSQL that enables Claude Code to programmatically build, test, and maintain workflows as the primary development interface, with humans only involved for high-level spec creation.

## User Stories

- As a developer, I want to run `docker compose up` and have a fully functional n8n instance with PostgreSQL so that I can start building workflows immediately
- As Claude Code, I want to programmatically create and update workflow JSON files locally and deploy them to n8n via REST API so that workflow development is completely code-driven
- As a developer, I want workflows versioned in git as JSON files so that I can track changes and rollback if needed
- As a developer, I want to access the n8n UI for visual inspection and debugging so that I can verify workflows are running correctly
- As a developer, I want persistent volumes for workflows and database so that my work survives container restarts

## Core Requirements

- Docker Compose environment with n8n (latest) and PostgreSQL (15+) services
- Project-specific Docker network for service isolation
- Environment variable management with `.env` (gitignored) and `.env.example` (committed template)
- Basic authentication enabled for n8n UI access
- Persistent volumes for workflow data and PostgreSQL database
- Healthchecks for service reliability
- Local `workflows/` directory containing workflow JSON files (source of truth)
- Simple helper functions enabling Claude Code to make direct n8n REST API calls (create/update/delete workflows)
- n8n REST API accessible at http://localhost:5678/api/v1/workflows with basic auth
- Port assignments avoiding conflicts (n8n: 5678, PostgreSQL: 5432 or alternative)
- Documentation for setup and workflow management

## Visual Design

No UI components - this is infrastructure setup only.

## Reusable Components

### Existing Code to Leverage

**Docker Compose Patterns** (`../linkedin-workspace/docker-compose.yml`):
- Named project pattern: `name: n8n-workspace`
- Custom network naming: `n8n-workspace-network`
- Environment variable organization from `.env` file
- Healthcheck implementations for services
- Volume mounting with delegated consistency for performance
- Service dependency management with condition checks (e.g., `depends_on` with `condition: service_healthy`)

**Observability Integration** (`/Users/burke/obs/docker-compose.yml`):
- Optional Promtail configuration for log shipping to Loki
- Docker labels for automatic log collection
- Log parsing and metadata extraction patterns

### New Components Required

**n8n-Specific Configuration:**
- n8n service definition with PostgreSQL connection
- PostgreSQL service configuration for n8n database
- n8n-specific environment variables (encryption key, auth credentials, database URL)
- Simple API helper functions (Python or Node.js) - thin wrappers around HTTP requests for Claude Code
- Workflow directory structure (`workflows/`)

**Why new code is needed:**
- n8n has specific configuration requirements not present in linkedin-workspace
- Optional helper functions simplify n8n REST API calls (create, update, delete workflows)
- Helper functions are simple HTTP wrappers - Claude can also make API calls directly via curl/requests

## Technical Approach

**Docker Compose Architecture:**
- Two services: `n8n` (workflow engine) and `postgres` (database)
- n8n connects to PostgreSQL via environment variable `DB_TYPE=postgresdb` and connection string
- Named volumes for persistence: `n8n_data` (workflows/credentials), `postgres_data` (database)
- Custom network enables service-to-service communication by name
- Healthchecks ensure PostgreSQL is ready before n8n starts

**Environment Variables (.env):**
- `N8N_BASIC_AUTH_ACTIVE=true` - Enable authentication
- `N8N_BASIC_AUTH_USER` - Admin username
- `N8N_BASIC_AUTH_PASSWORD` - Admin password
- `N8N_ENCRYPTION_KEY` - For credential encryption (generated randomly)
- `DB_TYPE=postgresdb`
- `DB_POSTGRESDB_HOST=postgres` - Service name from docker-compose
- `DB_POSTGRESDB_PORT=5432`
- `DB_POSTGRESDB_DATABASE`, `DB_POSTGRESDB_USER`, `DB_POSTGRESDB_PASSWORD`
- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` - PostgreSQL init vars

**Workflow Directory Structure:**
```
workflows/
├── my-first-workflow.json
├── data-processing.json
└── README.md
```

**n8n REST API Integration:**
- n8n exposes REST API at `http://localhost:5678/api/v1/workflows`
- API supports full CRUD operations: GET (list/read), POST (create), PUT (update), DELETE
- Authentication via basic auth using credentials from `.env`
- API returns/accepts workflow JSON in n8n's native format

**Optional Helper Functions** (`lib/n8n_api.py` or `lib/n8n_api.js`):
- `create_workflow(json_file)` - Simple wrapper: reads JSON, POSTs to API
- `update_workflow(workflow_id, json_file)` - Simple wrapper: reads JSON, PUTs to API
- `get_workflow(workflow_id)` - Simple wrapper: GETs from API, saves to file
- `delete_workflow(workflow_id)` - Simple wrapper: DELETEs via API
- **Note**: Claude can make these API calls directly via curl/requests without helper functions

**Workflow Development Pattern (Direct API Approach):**
1. Claude edits workflow JSON file locally in `workflows/my-workflow.json`
2. Claude makes HTTP POST/PUT to n8n API with JSON payload:
   - Direct: `curl -X POST http://localhost:5678/api/v1/workflows -u admin:password -d @workflows/my-workflow.json`
   - Or via helper: `python lib/n8n_api.py create workflows/my-workflow.json`
3. n8n creates/updates workflow and returns confirmation with workflow ID
4. Claude can test workflow execution via API: `POST /api/v1/workflows/{id}/execute`
5. Claude commits JSON file to git
6. Human uses UI only for visual inspection/debugging, never for editing

**Optional Observability:**
- Promtail sidecar (if implemented) ships n8n container logs to `/Users/burke/obs/` Loki instance
- Docker labels enable automatic log collection and parsing

## Out of Scope

- Make.com API integration for automated blueprint extraction
- Specific Make.com scenario conversion (handled in separate per-workflow specs)
- Render.com or production deployment configuration
- Automated workflow conversion tools
- Advanced monitoring/alerting beyond basic healthchecks
- Automated backup/restore for workflows
- Multi-environment configuration (staging, production)
- Webhook URL configuration for production use
- SSL/HTTPS setup
- n8n workflow execution monitoring dashboards

## Success Criteria

- Run `docker compose up -d` and access n8n UI at http://localhost:5678 with working authentication
- Create a test workflow in n8n UI, restart containers, and verify workflow persists
- PostgreSQL healthcheck passes and n8n successfully connects to database
- Claude Code can make direct API calls (via curl or helper functions) to create/update/delete workflows successfully
- Test workflow creation: POST workflow JSON to API, verify it appears in n8n UI
- Test workflow update: Modify local JSON, PUT to API, verify changes reflected in n8n
- Workflow JSON files are committed to git and changes are trackable
- All services start cleanly without port conflicts
- Documentation enables new developer to set up environment in under 10 minutes
