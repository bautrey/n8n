# Task Breakdown: n8n Claude-Driven Workflow Environment

## Overview
Total Task Groups: 5
Estimated Tasks: ~20

## Task List

### Infrastructure Layer

#### Task Group 1: Docker Compose Setup
**Dependencies:** None

- [x] 1.0 Complete Docker infrastructure
  - [ ] 1.1 Create docker-compose.yml
    - Define `n8n` service with latest image
    - Define `postgres` service with PostgreSQL 15+
    - Create project name: `n8n-workspace`
    - Create custom network: `n8n-workspace-network`
    - Add named volumes: `n8n_data`, `postgres_data`
    - Reference pattern from: `../linkedin-workspace/docker-compose.yml`
  - [ ] 1.2 Configure PostgreSQL service
    - Set environment variables from `.env` (POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD)
    - Add healthcheck: `pg_isready` command
    - Map volume: `postgres_data:/var/lib/postgresql/data`
    - Expose port 5432 (or alternative if conflict)
  - [ ] 1.3 Configure n8n service
    - Use image: `n8nio/n8n:latest`
    - Set DB_TYPE=postgresdb
    - Set DB_POSTGRESDB_HOST=postgres (service name)
    - Set database connection environment variables from `.env`
    - Enable basic auth with credentials from `.env`
    - Map volume: `n8n_data:/home/node/.n8n`
    - Expose port 5678
    - Add healthcheck: curl to http://localhost:5678/healthz
    - Add dependency: `depends_on: postgres` with `condition: service_healthy`
  - [ ] 1.4 Test Docker Compose setup
    - Run `docker compose up -d`
    - Verify both services start successfully
    - Check PostgreSQL healthcheck passes
    - Check n8n healthcheck passes
    - Verify n8n can connect to PostgreSQL (check logs)

**Acceptance Criteria:**
- Both services start without errors
- PostgreSQL healthcheck passes
- n8n successfully connects to database
- Services communicate via custom network
- Data persists in named volumes

### Configuration Layer

#### Task Group 2: Environment Configuration
**Dependencies:** Task Group 1

- [x] 2.0 Complete environment configuration
  - [ ] 2.1 Create `.env.example` template
    - Add all required n8n environment variables with example values
    - Add PostgreSQL configuration variables
    - Add authentication credentials (with placeholder values)
    - Add N8N_ENCRYPTION_KEY (with instructions to generate)
    - Document each variable with comments
    - Commit to git
  - [ ] 2.2 Create `.env` file (gitignored)
    - Copy from `.env.example`
    - Generate secure N8N_ENCRYPTION_KEY (random 32-character string)
    - Set actual PostgreSQL credentials
    - Set actual n8n basic auth credentials
    - Verify `.env` is in `.gitignore`
  - [ ] 2.3 Create .gitignore
    - Add `.env` to gitignore
    - Add `node_modules/` if using Node.js helpers
    - Add `__pycache__/` and `*.pyc` if using Python helpers
    - Add `.venv/` if using Python virtual environment
    - Keep workflow JSON files tracked (not ignored)
  - [ ] 2.4 Test environment configuration
    - Restart containers with new .env: `docker compose down && docker compose up -d`
    - Verify n8n UI loads at http://localhost:5678
    - Verify basic auth prompts for credentials
    - Login with credentials from `.env`
    - Verify successful authentication

**Acceptance Criteria:**
- `.env.example` committed with documented variables
- `.env` created with actual credentials (not committed)
- `.gitignore` properly configured
- n8n UI accessible with authentication working
- All environment variables loaded correctly

### Workflow Management Layer

#### Task Group 3: Workflow Directory and API Access
**Dependencies:** Task Group 2

- [x] 3.0 Complete workflow management setup
  - [ ] 3.1 Create workflow directory structure
    - Create `workflows/` directory in project root
    - Create `workflows/README.md` with usage instructions
    - Document workflow JSON format and n8n API endpoints
    - Add example workflow JSON (simple test workflow)
  - [ ] 3.2 Test n8n REST API access
    - Verify API endpoint accessible: `curl http://localhost:5678/api/v1/workflows`
    - Test basic auth: include credentials in curl command
    - Document API authentication pattern
    - Test GET /api/v1/workflows (list workflows)
  - [ ] 3.3 Create optional helper functions (Python)
    - Create `lib/` directory
    - Create `lib/n8n_api.py` with helper functions:
      - `create_workflow(json_file)` - POST to /api/v1/workflows
      - `update_workflow(workflow_id, json_file)` - PUT to /api/v1/workflows/{id}
      - `get_workflow(workflow_id)` - GET from /api/v1/workflows/{id}
      - `list_workflows()` - GET from /api/v1/workflows
      - `delete_workflow(workflow_id)` - DELETE from /api/v1/workflows/{id}
    - Read credentials from `.env` file
    - Use requests library for HTTP calls
    - Add error handling and response validation
  - [ ] 3.4 Create workflow management documentation
    - Create `workflows/README.md` with:
      - How to create workflow JSON files
      - How to use n8n API directly with curl examples
      - How to use helper functions (if created)
      - Workflow development pattern for Claude Code
      - Git commit best practices for workflows

**Acceptance Criteria:**
- `workflows/` directory exists with README
- Example workflow JSON file present
- n8n REST API accessible and authenticated
- Helper functions work correctly (if implemented)
- Documentation clear and complete

### Testing Layer

#### Task Group 4: End-to-End Workflow Testing
**Dependencies:** Task Group 3

- [x] 4.0 Complete end-to-end testing
  - [ ] 4.1 Test workflow creation via API
    - Create simple test workflow JSON in `workflows/test-workflow.json`
    - POST workflow to n8n API via curl or helper function
    - Verify workflow appears in n8n UI
    - Verify workflow ID returned by API
    - Save workflow ID for subsequent tests
  - [ ] 4.2 Test workflow update via API
    - Modify test workflow JSON locally (change name or add node)
    - PUT updated workflow to n8n API using workflow ID
    - Verify changes reflected in n8n UI
    - Verify workflow still functions correctly
  - [ ] 4.3 Test workflow execution
    - Activate test workflow via UI or API
    - Execute workflow via API: POST /api/v1/workflows/{id}/execute
    - Verify execution completes successfully
    - Check execution logs in n8n UI
  - [ ] 4.4 Test workflow retrieval
    - GET workflow from n8n API by ID
    - Save response to local file
    - Verify retrieved JSON matches local version
  - [ ] 4.5 Test persistence after container restart
    - Stop containers: `docker compose down`
    - Start containers: `docker compose up -d`
    - Verify test workflow still exists in n8n UI
    - Verify PostgreSQL data persisted
  - [ ] 4.6 Test git workflow
    - Commit test workflow JSON to git
    - Make a change and commit again
    - Verify workflow history trackable in git log
    - Test rollback: checkout previous version, update via API

**Acceptance Criteria:**
- Can create workflows via API successfully
- Can update workflows via API successfully
- Can execute workflows via API successfully
- Can retrieve workflows from API successfully
- Workflows persist after container restarts
- Workflow changes tracked in git history

### Documentation Layer

#### Task Group 5: Project Documentation
**Dependencies:** Task Groups 1-4

- [x] 5.0 Complete project documentation
  - [ ] 5.1 Create SETUP.md
    - Prerequisites (Docker, Docker Compose)
    - Clone repository instructions
    - Environment setup (copy .env.example to .env)
    - How to generate N8N_ENCRYPTION_KEY
    - How to start services: `docker compose up -d`
    - How to verify setup is working
    - How to access n8n UI
    - Troubleshooting common issues
  - [ ] 5.2 Create WORKFLOW_DEVELOPMENT.md
    - Claude Code workflow development pattern
    - How to create workflow JSON files
    - How to use n8n REST API (curl examples)
    - How to use helper functions (if implemented)
    - How to test workflows
    - How to commit workflows to git
    - Best practices for workflow development
  - [ ] 5.3 Create API_REFERENCE.md
    - n8n REST API endpoints documentation
    - Authentication examples
    - CRUD operation examples (create, read, update, delete)
    - Workflow execution examples
    - Common API response formats
    - Error handling patterns
  - [ ] 5.4 Update project README.md
    - Project overview and goals
    - Quick start guide (link to SETUP.md)
    - Architecture overview
    - Links to detailed documentation
    - Success criteria checklist
    - Contributing guidelines (for future workflows)
  - [ ] 5.5 Create CLAUDE.md project instructions
    - Integration with Burke's workspace standards
    - Docker Compose usage (use `docker compose`, not `docker-compose`)
    - Agent OS workflow for creating new workflow specs
    - Observability integration notes (optional)
    - Linear integration for tracking workflow development
    - Git worktree usage if running concurrent Claude sessions

**Acceptance Criteria:**
- All documentation files created and complete
- Setup process takes under 10 minutes for new developer
- API examples all work correctly when copy-pasted
- Claude Code workflow pattern clearly documented
- Documentation follows Burke's project standards

## Execution Order

Recommended implementation sequence:
1. **Infrastructure Layer** (Task Group 1) - Set up Docker Compose with n8n and PostgreSQL
2. **Configuration Layer** (Task Group 2) - Configure environment variables and authentication
3. **Workflow Management Layer** (Task Group 3) - Set up workflow directories and API access
4. **Testing Layer** (Task Group 4) - Validate end-to-end workflow operations
5. **Documentation Layer** (Task Group 5) - Create comprehensive documentation

## Notes

- This is infrastructure setup, not application development, so testing focuses on integration and validation rather than unit tests
- Helper functions are optional - Claude can make API calls directly via curl or requests library
- Focus is on enabling Claude Code to manage workflows programmatically via n8n REST API
- Local workflow JSON files are source of truth, n8n instance is deployment target
- Git tracks all workflow changes for version control and rollback capability
