# Spec Requirements: Make-to-n8n Migration Environment

## Initial Description

**Source:** KICKOFF.md and user clarifications
**Date:** 2025-10-31

### Project Objective

Build a complete n8n workflow automation environment that enables:
1. **Local Development**: Docker-based n8n instance with PostgreSQL
2. **Make.com Migration**: Tools to convert Make.com blueprints to n8n workflows
3. **Version Control**: Git-based workflow management with JSON files
4. **Production Deployment**: Render.com containerized deployment with persistent storage
5. **Claude Code Management**: Full programmatic workflow maintenance via CLI

### First Step Goal

The goal is ultimately to go get one Make scenario as our first step and get it running in a container that is able to do whatever n8n does.

## Requirements Discussion

### First Round Questions

**Q1:** Make.com API Access - Do we have API key ready? Which scenarios to migrate first?
**Answer:** I actually don't want to use API access to make.com. I will provide a blueprint and we'll go from there. But each scenario/workflow we build we will build a spec for so no need to worry about that now. This is more about getting n8n set up in a new container so we can have an environment in which to do this.

**Q2:** Database Choice - Should we use PostgreSQL from the start (matching production best practices), or SQLite for initial simplicity?
**Answer:** I would love to create our own postgres instance/container that we can use not only for n8n stuff but also for other projects. So let's do postgres for this but in a separate container.

**Q3:** Authentication Method - Should we use n8n's basic auth (username/password)?
**Answer:** Sure let's use n8n's auth.

**Q4:** Docker Compose Structure - Should we include n8n service, postgres service, persistent volumes?
**Answer:** I think that makes sense.

**Q5:** Observability Integration - Should the n8n container integrate with `/Users/burke/obs/` Loki/Promtail logging stack from the start?
**Answer:** Sure but not essential.

**Q6:** Environment Variables Management - Should we use a `.env` file (not committed) with `.env.example` template (committed)?
**Answer:** Yes that's the right pattern for .env.

**Q7:** Workflow Storage Strategy - Should workflows just live inside n8n instance, or git-based export/import from day one?
**Answer:** Yes the workflows live in n8n. But we will also store a text-representation of it in git for backup. Scripts that accomplish the import/export as helpers will be key.

**Q8:** Production Deployment Scope - Should this spec include Render.com deployment?
**Answer:** Since deployment of docker to render.com is pretty easy, I think we can focus on local now and worry about integration and deployment later.

### Existing Code to Reference

**Similar Features Identified:**
- Docker Compose Patterns: `../linkedin-workspace/docker-compose.yml`
- Observability Stack: `../logs/` (likely `/Users/burke/obs/`)
- Authentication Patterns: `../authentik-expert/` (or wherever authentik project is)

**Docker Patterns from linkedin-workspace:**
- Named Docker Compose projects (`name: linkedin-workspace`)
- Custom networks (`linkedin-workspace-network`)
- Environment variables passed from `.env`
- Healthchecks for services
- Volume mounting with delegated consistency for performance
- Service dependencies with condition checks

### Follow-up Questions

**Follow-up 1:** Shared PostgreSQL Container - Should this be standalone in shared location or part of n8n compose?
**Answer:** You know, that probably isn't necessary. I don't want to create dependencies that we'll have to break up later. Let's use a dedicated postgres instance per purpose. In this case it's for n8n.

**Follow-up 2:** PostgreSQL Database Organization - One database per project or one container per project?
**Answer:** Just one for n8n for now.

**Follow-up 3:** Workflow Backup Scripts - Do we need "export all" or "import bunch" scripts?
**Answer:** We do need that, yes. But I'm intending to use claude code just like we're doing now to build, test, change, maintain, document, etc. the n8n workflows. I assume that means that we have local directories where the text representation of the workflow exists, claude uploads or syncs it to n8n, and tests/runs it and git is simply used to commit the local work. So I'm not sure we need "export all" or "import a bunch" as much as we need only to fill any gaps that might exist based on n8n's limitations for claude having free reign over the process. We want claude agentic n8n development... completely hands off for the human except doing what we're doing right now for specs, etc.

**Follow-up 4:** n8n Version - Pin to specific version or use latest?
**Answer:** Latest and greatest.

**Follow-up 5:** Networking - Shared Docker network across projects or project-specific?
**Answer:** Make it only for this project.

**Follow-up 6:** Port Mapping - n8n UI on localhost:5678, PostgreSQL on localhost:5432?
**Answer:** Up to you. I don't care as long as they don't conflict.

**Follow-up 7:** Which existing Docker patterns should be referenced?
**Answer:** Yes use whatever you want. The stuff in linkedin-workspace has the most use/complexity.

## Visual Assets

### Files Provided:
No visual assets provided.

### Visual Insights:
No visual assets to analyze.

## Requirements Summary

### Functional Requirements

**Core Infrastructure:**
- Docker-based n8n instance running latest version
- Dedicated PostgreSQL container for n8n data persistence
- Docker Compose orchestration with project-specific network
- Environment variable management via `.env` (gitignored) and `.env.example` (committed)
- Basic authentication for n8n UI access

**Claude Code Integration (CRITICAL):**
- Local workflow directories containing JSON representations of n8n workflows
- Scripts for Claude to programmatically sync workflows to/from n8n
- Claude can build, test, change, maintain, and document workflows via code
- Human only involved for spec creation and high-level direction
- **Goal**: Completely hands-off workflow development except for strategic decisions

**Workflow Management:**
- Workflows stored as JSON in local git repository
- Bidirectional sync capability between local files and n8n instance
- Git commits track workflow changes over time
- Scripts to fill any gaps in n8n's programmatic API limitations

**Development Experience:**
- Access n8n UI for visual inspection/debugging
- Persistent volumes ensure data survives container restarts
- Healthchecks for service reliability
- No port conflicts with existing services

### Reusability Opportunities

**Docker Compose Patterns from linkedin-workspace:**
- Named Docker Compose project pattern
- Custom network naming convention
- Environment variable organization
- Healthcheck implementation patterns
- Volume mounting with delegated consistency
- Service dependency management with conditions

**Observability Integration (Optional):**
- Logging integration patterns from `/Users/burke/obs/`
- Loki/Promtail configuration if implemented

### Scope Boundaries

**In Scope:**
- Local Docker Compose environment with n8n + PostgreSQL
- Basic authentication setup for n8n UI
- Persistent storage configuration for workflows and database
- `.env` / `.env.example` pattern for configuration
- Scripts for Claude Code to programmatically manage workflows
- Local workflow JSON storage and git tracking
- Documentation for setup and workflow management
- Optional: Observability stack integration

**Out of Scope (Future Specs):**
- Make.com API integration for automated blueprint extraction
- Specific Make.com scenario conversion (handled in per-workflow specs)
- Render.com production deployment
- Automated workflow conversion tools (may not be needed with Claude approach)
- Advanced monitoring/alerting
- Backup/restore automation
- Multi-environment configuration (staging, production)
- Webhook URL configuration for production
- SSL/HTTPS setup

### Technical Considerations

**Architecture Decisions:**
- Dedicated PostgreSQL instance per purpose (n8n-specific, not shared)
- Project-specific Docker network (not shared across projects)
- Latest n8n version (not pinned) for newest features
- Port assignments to avoid conflicts (n8n: 5678, postgres: 5432 or alternative)

**Integration Points:**
- n8n REST API for programmatic workflow management
- PostgreSQL for workflow/credential persistence
- Docker volume mounts for local workflow file access
- Optional: Promtail for log shipping to Burke's observability stack

**Claude Code Development Model:**
- Local workflow files are source of truth
- Claude edits local JSON files
- Scripts sync changes to n8n instance
- n8n API used for testing/execution
- Git commits track all workflow changes
- Human never manually edits workflows in UI

**Technology Stack:**
- n8n: Latest stable version
- PostgreSQL: 15+ (modern version)
- Docker & Docker Compose: For containerization
- Node.js/Python: For sync scripts (Claude can write/maintain)
- Git: Version control for workflows

**Similar Code Patterns to Follow:**
- Docker Compose structure from `linkedin-workspace/docker-compose.yml`
- Environment variable pattern from linkedin-workspace
- Healthcheck patterns from linkedin-workspace
- Network naming conventions from linkedin-workspace
- Volume mounting patterns with delegated consistency
