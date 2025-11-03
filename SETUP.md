# n8n Setup Guide

Complete setup instructions for the n8n Claude-driven workflow development environment.

## Prerequisites

- Docker Desktop installed and running
- Docker Compose v2+ (use `docker compose`, not `docker-compose`)
- Git for version control
- Python 3.8+ (optional, for helper functions)
- curl or similar HTTP client

## Quick Start (10 minutes)

### 1. Clone or Navigate to Project

```bash
cd /path/to/n8n
```

### 2. Create Environment File

```bash
# Copy the example environment file
cp .env.example .env
```

### 3. Generate Encryption Key

The n8n encryption key must be a secure random 32-character hex string:

**Option A - Python:**
```bash
python3 -c "import secrets; print(secrets.token_hex(16))"
```

**Option B - OpenSSL:**
```bash
openssl rand -hex 16
```

**Option C - Node.js:**
```bash
node -e "console.log(require('crypto').randomBytes(16).toString('hex'))"
```

Copy the generated key and update `.env`:
```bash
N8N_ENCRYPTION_KEY=your_generated_key_here
```

### 4. Start Services

```bash
docker compose up -d
```

This will:
- Pull n8n and PostgreSQL Docker images (first time only)
- Create Docker volumes for persistent storage
- Start both services with health checks
- Create custom network for service communication

### 5. Verify Services

```bash
# Check container status
docker compose ps

# Both should show (healthy) status
# NAME           STATUS
# n8n-app        Up X minutes (healthy)
# n8n-postgres   Up X minutes (healthy)
```

### 6. Access n8n UI

Open your browser to: **http://localhost:5678**

**First-time login:**
- Username: `admin`
- Password: `n8n_admin_pass_2025` (from `.env`)

### 7. Create API Key (REQUIRED)

The n8n REST API requires an API key for authentication:

1. In n8n UI, click **Settings** (gear icon, bottom left)
2. Select **n8n API**
3. Click **Create an API key**
4. Set label: "Claude Code Development"
5. Set expiration: "Never" (for development)
6. Click **Create**
7. **Copy the API key** (you won't see it again!)
8. Update `.env` file:
   ```bash
   N8N_API_KEY=your_actual_api_key_here
   ```

### 8. Test API Access

```bash
# Load environment variables
source .env

# Test API connection
curl -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  http://localhost:5678/api/v1/workflows
```

Expected response: `{"data":[],"nextCursor":null}`

### 9. (Optional) Install Python Dependencies

If you want to use the Python helper functions:

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install requests python-dotenv
```

## Troubleshooting

### Port Conflicts

**Problem:** Port 5678 or 5433 already in use

**Solution:** Change ports in `docker-compose.yml`:
```yaml
ports:
  - "5679:5678"  # Change 5679 to any available port
```

### PostgreSQL Connection Failed

**Problem:** n8n can't connect to PostgreSQL

**Solution:**
```bash
# Check PostgreSQL health
docker logs n8n-postgres

# Restart services
docker compose down
docker compose up -d
```

### Can't Access n8n UI

**Problem:** Browser shows connection refused

**Solution:**
```bash
# Check n8n logs
docker logs n8n-app

# Verify healthcheck
docker compose ps

# Wait for healthy status (may take 30-60 seconds on first start)
```

### API Key Not Working

**Problem:** API returns "X-N8N-API-KEY header required"

**Solution:**
1. Verify API key created in n8n UI Settings > n8n API
2. Verify key added to `.env` file
3. Reload environment: `source .env`
4. Test with explicit key: `curl -H "X-N8N-API-KEY: your_key" http://localhost:5678/api/v1/workflows`

### Database Migration Errors

**Problem:** n8n shows migration errors in logs

**Solution:**
```bash
# Stop services
docker compose down

# Remove volumes (⚠️ DELETES ALL DATA)
docker volume rm n8n_data postgres_data

# Restart fresh
docker compose up -d
```

## Environment Variables Reference

See `.env.example` for complete documentation of all environment variables.

**Critical Variables:**
- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` - Database credentials
- `N8N_BASIC_AUTH_USER`, `N8N_BASIC_AUTH_PASSWORD` - UI login credentials
- `N8N_ENCRYPTION_KEY` - Required for credential encryption (32-char hex)
- `N8N_API_KEY` - Required for REST API access (created in UI)

## Verifying Setup

Run the complete test suite:

```bash
./test_workflow_api.sh
```

This tests:
- API connection
- Workflow creation
- Workflow retrieval
- Workflow updates
- Data persistence
- Workflow deletion

All tests should pass if setup is correct.

## Next Steps

- Read `WORKFLOW_DEVELOPMENT.md` for Claude Code development patterns
- Read `workflows/README.md` for workflow management guide
- Read `API_REFERENCE.md` for complete API documentation
- Try creating your first workflow!

## Stopping Services

```bash
# Stop services (preserves data)
docker compose down

# Stop and remove volumes (⚠️ DELETES ALL DATA)
docker compose down -v
```

## Logs and Debugging

```bash
# View n8n logs
docker logs n8n-app

# View PostgreSQL logs
docker logs n8n-postgres

# Follow logs in real-time
docker logs -f n8n-app

# View all service logs
docker compose logs
```

## Success Criteria Checklist

- [ ] Services start without errors (`docker compose ps` shows healthy)
- [ ] Can access n8n UI at http://localhost:5678
- [ ] Can login with credentials from `.env`
- [ ] API key created and added to `.env`
- [ ] API test returns successful response
- [ ] Test script passes all checks: `./test_workflow_api.sh`

If all checkboxes are complete, your n8n environment is ready for Claude Code development!
