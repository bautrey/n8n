# Product Requirements Document: Make.com Backup Migration

**Product:** Make.com Scenario Backup System Migration
**Version:** 1.0
**Date:** 2025-11-03
**Status:** Draft - Pending Approval
**Owner:** Product Management
**Stakeholders:** DevOps Engineering, Automation Engineering, IT Operations

---

## Executive Summary

### Problem Statement

**Current Situation:**
Fortium Partners currently backs up all Make.com automation scenarios (50+ workflows) to Google Drive using a Make.com scenario. This creates several critical risks:

- **Single Point of Failure**: The backup system runs on the same platform it's protecting
- **Limited Version Control**: Google Drive lacks native version control and diff capabilities
- **Poor Developer Experience**: No integration with development workflows or CI/CD pipelines
- **Vendor Lock-in**: Backup data stored in proprietary Make.com format within Google's ecosystem
- **Lack of Transparency**: No easy way to track changes, audit backups, or restore specific versions

**Business Impact:**
- Risk of catastrophic data loss if Make.com experiences outages or account issues
- Inability to quickly restore scenarios in disaster recovery situations
- No audit trail for compliance and change management requirements
- Manual restoration process requiring significant engineering time

### Solution Overview

Migrate the backup system from Google Drive to GitHub, replacing the Make.com backup scenario with an n8n workflow that provides:

- **Version Control**: Full Git history with diffs, branches, and restore points
- **Developer Integration**: Native integration with existing development tools and workflows
- **Platform Independence**: Backup system runs on separate infrastructure (n8n) from source system (Make.com)
- **Enhanced Reliability**: GitHub's 99.95% uptime SLA vs. Google Drive's consumer-grade reliability
- **Automated Tracking**: Smart incremental backups that only capture changed scenarios
- **Structured Data**: JSON-based storage enabling programmatic access and automation

### Value Proposition

**For DevOps Engineers:**
- Restore any scenario version using familiar Git workflows
- Diff scenarios across time periods to understand changes
- Integrate scenario backups into existing disaster recovery procedures

**For Automation Engineers:**
- Track scenario evolution over time with full change history
- Identify when and why scenarios were modified
- Collaborate on scenario development using pull request workflows

**For Business Stakeholders:**
- Reduce risk of automation data loss from 100% (current) to <0.01% (GitHub SLA)
- Decrease recovery time from hours (manual restoration) to minutes (Git restore)
- Ensure compliance with change management and audit requirements

---

## Phase 1: Product Analysis

### 1.1 User Analysis

#### Primary User Personas

**Persona 1: David - DevOps Engineer**

**Demographics:**
- Role: Senior DevOps Engineer
- Experience: 8+ years in infrastructure and automation
- Team: IT Operations (3-person team)
- Tools: Git, Docker, n8n, Terraform, Make.com

**Goals:**
- Ensure all automation systems have reliable disaster recovery procedures
- Minimize downtime and data loss across all platforms
- Maintain audit trails for compliance requirements
- Automate repetitive operational tasks

**Pain Points:**
- Current backup system creates single point of failure (Make.com backing up Make.com)
- Cannot easily restore specific scenario versions without manual reconstruction
- No visibility into what changed in scenarios or when
- Google Drive backups are disconnected from existing Git-based workflows
- Manual restoration process requires hours of engineering time

**User Journey (Current State - Google Drive):**
1. Scenario changes are made in Make.com
2. Backup scenario runs periodically (daily/weekly)
3. Scenario JSON saved to Google Drive folder
4. **Disaster occurs** - Scenario deleted or corrupted
5. David navigates to Google Drive folder
6. Downloads JSON file manually
7. Logs into Make.com UI
8. Imports scenario via drag-and-drop
9. Manually validates scenario configuration
10. Re-enables scenario and tests execution
**Total Time: 2-4 hours**

**User Journey (Desired State - GitHub):**
1. Scenario changes are made in Make.com
2. n8n backup workflow runs automatically
3. Changes committed to GitHub with descriptive message
4. **Disaster occurs** - Scenario deleted or corrupted
5. David uses GitHub UI or Git CLI to find scenario
6. Reviews diff to understand what was lost
7. Uses Make.com API or UI to restore from JSON
8. Validates restoration and re-enables scenario
**Total Time: 15-30 minutes**

---

**Persona 2: Sarah - Automation Engineer**

**Demographics:**
- Role: Automation Engineer
- Experience: 5 years in business process automation
- Team: Business Operations (5-person team)
- Tools: Make.com, Zapier, n8n, Airtable, APIs

**Goals:**
- Build and maintain reliable automation workflows
- Understand when and why workflows break or change
- Collaborate with team members on complex scenarios
- Document automation architecture for knowledge sharing

**Pain Points:**
- Cannot see who changed a scenario or when
- No diff capability to understand what changed between versions
- Difficult to troubleshoot issues caused by scenario modifications
- No way to rollback to previous working versions quickly
- Google Drive backups are opaque files with no metadata

**User Journey (Current State - Google Drive):**
1. Scenario stops working after unknown change
2. Sarah checks Make.com execution logs (no clear cause)
3. Contacts team members asking "Did anyone change this scenario?"
4. Manually reviews scenario configuration step-by-step
5. Compares to Google Drive backup (manual JSON comparison)
6. Identifies change but doesn't know why it was made
7. Manually reverts change in Make.com UI
**Total Time: 1-3 hours of investigation**

**User Journey (Desired State - GitHub):**
1. Scenario stops working after unknown change
2. Sarah checks Make.com execution logs
3. Navigates to GitHub repository for scenario
4. Reviews commit history to see recent changes
5. Uses GitHub diff to compare current vs. previous version
6. Identifies problematic change with commit message context
7. Restores previous working version from GitHub
8. Documents issue and resolution in Linear/Jira
**Total Time: 15-30 minutes of investigation**

---

**Persona 3: Mark - Backup Administrator**

**Demographics:**
- Role: IT Operations Manager
- Experience: 10+ years in IT operations and disaster recovery
- Team: IT Operations leadership
- Responsibilities: Backup strategy, compliance, disaster recovery planning

**Goals:**
- Ensure 100% backup coverage for all critical business systems
- Meet compliance requirements for change tracking and audit trails
- Minimize RTO (Recovery Time Objective) and RPO (Recovery Point Objective)
- Validate backup integrity through regular testing

**Pain Points:**
- Cannot easily verify backup completeness (are all scenarios backed up?)
- No automated validation that backups are restorable
- Google Drive backups lack metadata (when backed up, who changed, why)
- No integration with existing disaster recovery procedures (Git-based)
- Cannot track backup success/failure metrics systematically

**User Journey (Current State - Google Drive):**
1. Monthly backup audit required for compliance
2. Mark logs into Make.com to count total scenarios
3. Navigates to Google Drive backup folder
4. Manually counts files to verify coverage
5. Spot-checks several backup files for validity (download and inspect JSON)
6. Documents findings in spreadsheet for audit report
**Total Time: 2-3 hours monthly**

**User Journey (Desired State - GitHub):**
1. Monthly backup audit required for compliance
2. Mark navigates to GitHub repository
3. Reviews `.backup-state.json` for complete scenario inventory
4. Checks commit history to verify daily backup execution
5. Queries GitHub API for backup metrics (total scenarios, last backup date, success rate)
6. Generates automated audit report from structured JSON data
**Total Time: 15-30 minutes monthly**

---

#### Secondary User Personas

**Compliance Officer:**
Needs audit trail of all automation changes for regulatory compliance. Requires timestamped records of who, what, when for each scenario modification.

**Business Analyst:**
Reviews automation workflows to understand business processes. Benefits from version history to track process evolution.

**New Team Members:**
Onboarding engineers need to understand existing automation landscape. GitHub provides discoverable, documented scenario repository.

---

### 1.2 Product Goals

#### Primary Objectives

**1. Platform Risk Reduction**
- **Goal:** Eliminate single point of failure where Make.com backs up itself
- **Success Metric:** Backup system runs on independent infrastructure (n8n) with 99%+ uptime
- **Business Value:** Reduce catastrophic data loss risk from 100% to <0.01%

**2. Recovery Time Improvement**
- **Goal:** Reduce scenario restoration time from hours to minutes
- **Success Metric:** Mean Time to Restore (MTTR) < 30 minutes for any scenario
- **Business Value:** Minimize business disruption during incident recovery

**3. Change Visibility**
- **Goal:** Provide complete audit trail of all scenario changes with diff capability
- **Success Metric:** 100% of scenario modifications tracked with timestamp, change diff, and metadata
- **Business Value:** Enable compliance, troubleshooting, and knowledge sharing

**4. Developer Experience**
- **Goal:** Integrate scenario backups into existing Git-based development workflows
- **Success Metric:** 80%+ of engineers use Git tools for scenario investigation/restoration
- **Business Value:** Reduce context switching and leverage familiar tooling

#### Secondary Objectives

**5. Automated Validation**
- **Goal:** Verify backup completeness and validity automatically
- **Success Metric:** 100% of scenarios backed up daily with automated validation
- **Business Value:** Ensure backup system reliability without manual verification

**6. Storage Efficiency**
- **Goal:** Minimize storage costs through incremental backups
- **Success Metric:** Only changed scenarios backed up (target: <20% of scenarios change daily)
- **Business Value:** Reduce GitHub storage consumption and API usage

**7. Migration Continuity**
- **Goal:** Maintain backup coverage during migration from Make.com to n8n
- **Success Metric:** Zero backup gaps during migration period (6-12 months)
- **Business Value:** Preserve disaster recovery capability throughout transition

---

### 1.3 Success Criteria

#### Launch Success Criteria (MVP)

| Criteria | Measurement | Target | Priority |
|----------|-------------|--------|----------|
| **Backup Coverage** | % of Make.com scenarios backed up to GitHub | 100% | P0 |
| **Backup Frequency** | Hours between backups | ≤24 hours | P0 |
| **Recovery Capability** | Successfully restore scenario from GitHub backup | 100% success rate | P0 |
| **Data Integrity** | Restored scenario matches original functionality | 100% match | P0 |
| **Incremental Backup** | Only changed scenarios backed up | >50% reduction in backup operations | P1 |
| **Version History** | Scenario changes tracked in Git history | 100% of changes | P1 |

#### Production Readiness Criteria

| Criteria | Measurement | Target | Priority |
|----------|-------------|--------|----------|
| **Uptime** | Backup workflow availability | 99%+ uptime | P0 |
| **Error Rate** | Failed backups / total backups | <1% failure rate | P0 |
| **Recovery Time** | Time to restore single scenario | <30 minutes | P0 |
| **Monitoring** | Backup failure alerts delivered | 100% of failures alerted | P0 |
| **Documentation** | Restoration procedures documented | 100% complete | P1 |
| **Audit Trail** | Backup operations logged | 100% of operations | P1 |

#### Long-Term Success Metrics (3-6 months)

| Metric | Baseline (Google Drive) | Target (GitHub) | Measurement |
|--------|-------------------------|-----------------|-------------|
| **Mean Time to Restore** | 2-4 hours | <30 minutes | Average restoration time |
| **Backup Verification Time** | 2-3 hours/month | <30 minutes/month | Monthly audit effort |
| **Restoration Success Rate** | ~80% (manual errors) | 99%+ | Successful restorations / attempts |
| **Engineer Satisfaction** | N/A (no baseline) | 8+/10 | Post-launch survey score |
| **Disaster Recovery Confidence** | 6/10 (subjective) | 9+/10 | Stakeholder confidence survey |

---

### 1.4 Non-Goals (Scope Boundaries)

#### Explicitly Out of Scope

**Will NOT Include:**
- Automatic restoration of deleted scenarios (requires manual approval)
- Real-time backup synchronization (<1 hour delay)
- Backup of Make.com connections/credentials (security risk)
- Backup of Make.com execution history/logs
- Migration of existing Google Drive backups to GitHub
- Backup of other platforms (Zapier, n8n scenarios, etc.)
- Version comparison UI (use GitHub native diff)
- Scenario validation/testing automation
- Multi-region GitHub backup redundancy
- Backup encryption beyond GitHub's native encryption

#### Future Consideration (Post-MVP)

**Potential Future Enhancements:**
- Automated restoration API with approval workflow
- Slack/email notifications on scenario changes
- Scenario changelog generation from commit history
- Backup health dashboard with metrics visualization
- Integration with incident management systems
- Cleanup policy for archived scenarios
- Multi-version comparison and diff visualization
- Scenario dependency mapping and impact analysis

---

## Phase 2: Requirements Definition

### 2.1 Functional Requirements

#### FR-1: Scenario Discovery and Inventory

**Requirement:**
The system MUST retrieve a complete list of all Make.com scenarios from the Fortium Partners organization (Org ID: 395687, Team ID: 154819).

**Acceptance Criteria:**
- System successfully authenticates with Make.com API using API key
- System retrieves all scenarios regardless of pagination (handle >100 scenarios)
- System captures scenario metadata: ID, name, description, folder ID, last edit timestamp, active status
- System handles API errors gracefully with retry logic (exponential backoff, max 3 retries)
- System logs total scenario count for monitoring purposes

**Test Scenarios:**
- **Given** Make.com API is accessible
  **When** workflow executes
  **Then** all scenarios are retrieved with complete metadata
- **Given** Make.com API returns paginated results
  **When** workflow retrieves scenarios
  **Then** all pages are processed until complete
- **Given** Make.com API is temporarily unavailable
  **When** workflow attempts to retrieve scenarios
  **Then** system retries with exponential backoff and logs failure after max retries

---

#### FR-2: Incremental Backup Detection

**Requirement:**
The system MUST determine which scenarios require backup by comparing Make.com last edit timestamp against last backup timestamp.

**Acceptance Criteria:**
- System reads current backup state from `.backup-state.json` in GitHub repository
- System compares each scenario's `lastEdit` timestamp to `lastBackup` timestamp from backup state
- System identifies scenarios needing backup:
  - Scenario never backed up (not in backup state)
  - Scenario modified since last backup (`lastEdit > lastBackup`)
- System skips unchanged scenarios to minimize GitHub API usage
- System handles missing or corrupted backup state file (treats as empty state)

**Test Scenarios:**
- **Given** scenario never backed up
  **When** backup detection runs
  **Then** scenario is flagged for backup
- **Given** scenario modified since last backup
  **When** backup detection compares timestamps
  **Then** scenario is flagged for backup
- **Given** scenario unchanged since last backup
  **When** backup detection runs
  **Then** scenario is skipped
- **Given** backup state file is corrupted
  **When** workflow reads backup state
  **Then** system treats as empty state and backs up all scenarios

---

#### FR-3: Scenario Blueprint Download

**Requirement:**
The system MUST download the complete blueprint (workflow definition) for each scenario requiring backup from the Make.com API.

**Acceptance Criteria:**
- System authenticates with Make.com API using API key
- System requests blueprint for specific scenario ID with `draft=false` parameter
- System retrieves complete JSON blueprint including flow, metadata, and configuration
- System validates blueprint is valid JSON before proceeding
- System handles API errors with retry logic and error logging

**Test Scenarios:**
- **Given** valid scenario ID
  **When** system requests blueprint
  **Then** complete JSON blueprint is retrieved
- **Given** scenario is deleted in Make.com
  **When** system requests blueprint
  **Then** system logs error and continues with next scenario
- **Given** Make.com API rate limit exceeded
  **When** system requests blueprint
  **Then** system retries with exponential backoff

---

#### FR-4: GitHub Repository Storage

**Requirement:**
The system MUST store scenario backups in structured format within the GitHub repository `fortiumpartners/make-scenarios-backup`.

**Acceptance Criteria:**
- System creates directory structure: `scenarios/{scenarioId}/`
- System stores two files per scenario:
  - `metadata.json`: Scenario metadata (ID, name, description, timestamps, backup history)
  - `blueprint.json`: Complete scenario blueprint from Make.com
- System creates files if they don't exist (first backup)
- System updates files if they exist (subsequent backups) using GitHub file SHA
- System commits with descriptive message: "Backup scenario {id}: {name}"
- System uses consistent committer identity: "Make.com Backup Bot <bot@fortiumpartners.com>"
- System handles GitHub API conflicts (409 errors) with retry logic

**Test Scenarios:**
- **Given** scenario never backed up
  **When** system stores to GitHub
  **Then** new directory and files are created
- **Given** scenario previously backed up
  **When** system stores updated backup
  **Then** existing files are updated using correct SHA
- **Given** GitHub API returns 409 conflict
  **When** system attempts to commit
  **Then** system retries with fresh file SHA
- **Given** multiple scenarios backed up in same run
  **When** system commits to GitHub
  **Then** each scenario creates separate commit with descriptive message

---

#### FR-5: Backup State Tracking

**Requirement:**
The system MUST maintain a persistent backup state file (`.backup-state.json`) in the GitHub repository to track backup history and enable incremental backups.

**Acceptance Criteria:**
- System reads existing backup state at workflow start (handle missing file gracefully)
- System updates backup state for each backed-up scenario:
  - Scenario ID, name
  - Last edit timestamp (from Make.com)
  - Last backup timestamp (current time)
  - Backup count (incremented)
  - Git commit SHA
- System updates `lastRun` timestamp for entire backup operation
- System commits updated backup state to GitHub after all scenarios processed
- System validates backup state is valid JSON before committing

**Test Scenarios:**
- **Given** backup state file doesn't exist
  **When** workflow starts
  **Then** system creates new backup state with empty scenarios object
- **Given** scenarios backed up successfully
  **When** workflow completes
  **Then** backup state is updated with all scenario metadata
- **Given** backup state update fails
  **When** workflow completes
  **Then** system logs error but doesn't fail entire workflow (next run will retry)

---

#### FR-6: Execution Summary and Reporting

**Requirement:**
The system MUST provide execution summary showing total scenarios, scenarios backed up, scenarios skipped, and any errors encountered.

**Acceptance Criteria:**
- System calculates execution metrics:
  - Total scenarios in Make.com
  - Scenarios backed up (changed or new)
  - Scenarios skipped (unchanged)
  - Scenarios with errors
- System returns summary in webhook response (JSON format)
- System logs summary to n8n execution log
- System includes execution timestamp and duration

**Test Scenarios:**
- **Given** workflow executes successfully
  **When** workflow completes
  **Then** summary includes all required metrics
- **Given** some scenarios fail to backup
  **When** workflow completes
  **Then** summary includes error count and error details

---

#### FR-7: Error Handling and Recovery

**Requirement:**
The system MUST handle errors gracefully, continue processing remaining scenarios, and provide detailed error reporting.

**Acceptance Criteria:**
- System implements retry logic with exponential backoff:
  - Make.com API failures: max 3 retries
  - GitHub API failures: max 3 retries
  - Retry delays: 1s, 2s, 4s
- System continues processing remaining scenarios if one scenario fails
- System logs all errors with:
  - Timestamp
  - Scenario ID and name
  - Error type (API failure, validation error, etc.)
  - Error message and stack trace
- System aggregates errors in execution summary
- System does not fail entire workflow due to single scenario failure

**Test Scenarios:**
- **Given** Make.com API fails for one scenario
  **When** workflow processes scenarios
  **Then** system logs error and continues with next scenario
- **Given** GitHub API rate limit exceeded
  **When** system commits to GitHub
  **Then** system waits and retries with exponential backoff
- **Given** multiple scenarios fail
  **When** workflow completes
  **Then** summary includes all errors with details

---

### 2.2 Non-Functional Requirements

#### NFR-1: Performance

**Requirement:**
The system MUST complete backup operations within acceptable time constraints to avoid API rate limits and ensure timely backups.

**Acceptance Criteria:**
- **Backup Duration**: Complete backup of 50 scenarios in <10 minutes
- **API Rate Limits**:
  - Make.com: Respect undocumented rate limits (implement backoff on 429 errors)
  - GitHub: Stay within 5,000 requests/hour limit (authenticated)
- **Processing**: Sequential processing (batch size = 1) to avoid GitHub API conflicts
- **Timeout**: Individual API requests timeout after 30 seconds

**Measurement:**
- Track workflow execution duration in n8n logs
- Monitor API request count per execution
- Track average time per scenario backup

---

#### NFR-2: Reliability

**Requirement:**
The system MUST operate reliably with minimal failures and comprehensive error recovery.

**Acceptance Criteria:**
- **Uptime**: 99%+ workflow availability (scheduled execution succeeds)
- **Error Rate**: <1% of scenarios fail to backup per execution
- **Recovery**: Automatic retry logic with exponential backoff (max 3 retries)
- **Idempotency**: Re-running workflow multiple times produces same result (no duplicate backups)
- **Data Integrity**: 100% of backed-up scenarios match source data

**Measurement:**
- Track workflow success rate (successful executions / total executions)
- Track scenario backup success rate (successful backups / total scenarios)
- Monitor error logs for recurring failures

---

#### NFR-3: Security

**Requirement:**
The system MUST protect sensitive credentials and authentication tokens following security best practices.

**Acceptance Criteria:**
- **Credential Storage**: All API keys stored as environment variables (never hardcoded)
- **Access Control**: GitHub repository set to private (not public)
- **Token Permissions**:
  - Make.com API key: Read-only permissions
  - GitHub PAT: Minimal scope (contents: write on single repository)
- **Credential Rotation**: API keys rotatable without code changes (environment variable updates only)
- **Audit Trail**: All API operations logged with timestamp and user identity

**Compliance:**
- Follows principle of least privilege
- No credentials stored in version control
- Audit trail for compliance requirements

---

#### NFR-4: Maintainability

**Requirement:**
The system MUST be easy to understand, modify, and troubleshoot by DevOps and automation engineers.

**Acceptance Criteria:**
- **Code Quality**: n8n workflow nodes include descriptive names and comments
- **Documentation**: Complete documentation for:
  - Workflow architecture and node configuration
  - API integration details
  - Error handling and troubleshooting
  - Restoration procedures
- **Modularity**: Workflow organized into logical sections (discovery, filtering, backup, state tracking)
- **Logging**: Detailed execution logs for debugging
- **Testability**: Workflow testable via webhook trigger without scheduling

**Measurement:**
- Time to onboard new engineer to workflow: <2 hours
- Time to troubleshoot failed execution: <30 minutes

---

#### NFR-5: Scalability

**Requirement:**
The system MUST handle growth in scenario count and backup frequency without degradation.

**Acceptance Criteria:**
- **Scenario Capacity**: Support 100+ scenarios without performance degradation
- **Pagination**: Handle Make.com API pagination for large scenario lists
- **Storage Efficiency**: Incremental backups minimize GitHub storage consumption
- **Execution Frequency**: Support daily execution with potential for more frequent backups
- **API Quotas**: Stay within GitHub (5,000 requests/hour) and Make.com rate limits

**Future Proofing:**
- Architecture supports migration to GitHub Actions or scheduled n8n cron if needed
- Repository structure supports thousands of scenarios without reorganization

---

#### NFR-6: Monitoring and Observability

**Requirement:**
The system MUST provide visibility into backup operations, success rates, and failures for operational monitoring.

**Acceptance Criteria:**
- **Execution Logging**: All workflow executions logged in n8n with:
  - Timestamp
  - Duration
  - Total scenarios processed
  - Success/failure status
  - Error details
- **Metrics Collection**: Backup state file tracks:
  - Last successful run timestamp
  - Per-scenario backup count and timestamps
  - Git commit SHAs for traceability
- **Failure Alerting**: (Future enhancement - documented requirement)
  - Email/Slack notification on workflow failure
  - Alert on consecutive failures (>3)
- **Health Monitoring**: (Future enhancement - documented requirement)
  - Dashboard showing backup success rate over time
  - Scenario change frequency analysis

**Initial Implementation:**
- n8n execution logs provide operational visibility
- Manual review of `.backup-state.json` for verification

---

### 2.3 Acceptance Criteria (Complete Definition)

#### Initial Release Acceptance Criteria

**Definition of "Done" for MVP Launch:**

**1. GitHub Repository Setup**
- [ ] Repository `fortiumpartners/make-scenarios-backup` created and configured as private
- [ ] Initial README.md committed with repository purpose and structure documentation
- [ ] Repository accessible to authorized team members (DevOps, Automation Engineering)
- [ ] GitHub PAT created with minimal permissions (contents: write)

**2. n8n Workflow Deployment**
- [ ] Workflow deployed to n8n instance and tested via webhook trigger
- [ ] All required environment variables configured (MAKE_API_KEY, GITHUB_PAT, etc.)
- [ ] Workflow executes successfully end-to-end with test scenarios
- [ ] Workflow nodes include descriptive names and documentation comments

**3. Initial Backup Execution**
- [ ] Complete initial backup of all Make.com scenarios (100% coverage)
- [ ] All scenario directories created in GitHub with correct structure
- [ ] All metadata.json files contain accurate scenario information
- [ ] All blueprint.json files contain complete scenario blueprints
- [ ] `.backup-state.json` created and populated with all scenarios
- [ ] Git commit history shows individual commits per scenario with descriptive messages

**4. Incremental Backup Validation**
- [ ] Second execution skips unchanged scenarios (validates incremental logic)
- [ ] Modified scenario triggers backup (validates change detection)
- [ ] Backup state updated correctly after incremental backup
- [ ] Execution summary shows correct counts (total, backed up, skipped)

**5. Error Handling Verification**
- [ ] Workflow continues processing if single scenario fails
- [ ] Retry logic demonstrated on temporary API failure
- [ ] Error logs include sufficient detail for troubleshooting
- [ ] Execution summary includes error count and details

**6. Documentation Completion**
- [ ] Technical specification complete and reviewed
- [ ] Product Requirements Document (this document) complete
- [ ] Restoration procedure documented with step-by-step instructions
- [ ] Troubleshooting guide created for common issues
- [ ] API authentication testing procedures documented

**7. Operational Readiness**
- [ ] Scheduled execution configured (daily at 2 AM or via external cron)
- [ ] Workflow success validated over 3+ consecutive executions
- [ ] Team training completed (DevOps and Automation Engineering)
- [ ] Escalation procedures defined for backup failures

---

#### Production Readiness Acceptance Criteria

**Definition of "Done" for Production:**

**1. Reliability Validation**
- [ ] 7 days of consecutive successful executions (99%+ success rate)
- [ ] Zero scenarios consistently failing to backup
- [ ] Error rate <1% across all executions
- [ ] Backup state consistency verified (no drift between Make.com and GitHub)

**2. Recovery Testing**
- [ ] Successfully restored 5+ scenarios from GitHub backups
- [ ] Restoration time <30 minutes per scenario (average)
- [ ] Restored scenarios match original functionality (100% validation)
- [ ] Recovery procedure documented and tested by 2+ engineers

**3. Performance Validation**
- [ ] Backup completion time <10 minutes for 50 scenarios
- [ ] No GitHub API rate limit errors
- [ ] Incremental backup efficiency >50% (majority of scenarios skipped when unchanged)

**4. Monitoring and Alerting**
- [ ] Execution logs reviewed and validated for completeness
- [ ] Backup state metrics tracked over time (manual review acceptable for MVP)
- [ ] Failure alert mechanism defined (email/Slack) - implementation optional for MVP

**5. Documentation Quality**
- [ ] All documentation reviewed by at least 2 stakeholders
- [ ] New team member successfully completes restoration using documentation only
- [ ] Runbook created for common operational tasks

**6. Stakeholder Sign-Off**
- [ ] DevOps team approves production readiness
- [ ] IT Operations Manager approves disaster recovery coverage
- [ ] Automation Engineering validates workflow functionality
- [ ] Compliance requirements satisfied (audit trail, change tracking)

---

#### Test Scenarios (Comprehensive)

**Scenario 1: Initial Backup of All Scenarios**

| Step | Action | Expected Result | Success Criteria |
|------|--------|-----------------|------------------|
| 1 | Trigger workflow via webhook | Workflow executes | HTTP 200 response |
| 2 | Workflow retrieves scenarios from Make.com | All scenarios returned | Count matches Make.com UI |
| 3 | Workflow checks backup state | Empty state (first run) | All scenarios flagged for backup |
| 4 | Workflow downloads blueprints | All blueprints retrieved | No API errors |
| 5 | Workflow commits to GitHub | All scenarios backed up | One commit per scenario |
| 6 | Workflow updates backup state | State file committed | All scenarios in state file |
| 7 | Execution summary returned | Summary shows metrics | Total scenarios = backed up |

**Validation:**
- GitHub repository contains `scenarios/{id}/metadata.json` and `blueprint.json` for all scenarios
- `.backup-state.json` contains all scenario IDs with correct timestamps
- Git commit history shows individual commits with descriptive messages

---

**Scenario 2: Incremental Backup (No Changes)**

| Step | Action | Expected Result | Success Criteria |
|------|--------|-----------------|------------------|
| 1 | Trigger workflow (no scenario changes) | Workflow executes | HTTP 200 response |
| 2 | Workflow retrieves scenarios | All scenarios returned | Count matches previous run |
| 3 | Workflow checks backup state | State contains all scenarios | Timestamps comparison performed |
| 4 | Workflow filters scenarios | All scenarios skipped | needsBackup = false for all |
| 5 | Workflow completes | No GitHub commits | Execution summary shows 0 backed up |

**Validation:**
- No new commits in GitHub repository
- `.backup-state.json` unchanged
- Execution summary shows: total = 50, backed up = 0, skipped = 50

---

**Scenario 3: Incremental Backup (Single Scenario Changed)**

| Step | Action | Expected Result | Success Criteria |
|------|--------|-----------------|------------------|
| 1 | Modify scenario in Make.com | Scenario lastEdit updated | Timestamp increased |
| 2 | Trigger workflow | Workflow executes | HTTP 200 response |
| 3 | Workflow retrieves scenarios | All scenarios returned | Changed scenario included |
| 4 | Workflow checks backup state | Changed scenario flagged | needsBackup = true for 1 scenario |
| 5 | Workflow backs up changed scenario | Scenario committed to GitHub | 1 new commit created |
| 6 | Workflow updates backup state | State updated | lastBackup updated for changed scenario |

**Validation:**
- 1 new commit in GitHub repository for changed scenario
- `.backup-state.json` updated with new backup timestamp for changed scenario
- Other scenarios unchanged in backup state
- Execution summary shows: total = 50, backed up = 1, skipped = 49

---

**Scenario 4: Scenario Restoration (Disaster Recovery)**

| Step | Action | Expected Result | Success Criteria |
|------|--------|-----------------|------------------|
| 1 | Scenario deleted from Make.com | Scenario no longer accessible | Make.com UI confirms deletion |
| 2 | Navigate to GitHub repository | Scenario backup found | Directory `scenarios/{id}/` exists |
| 3 | Download blueprint.json | File downloaded | Valid JSON file |
| 4 | Import to Make.com via UI or API | Scenario recreated | Scenario appears in Make.com |
| 5 | Validate scenario functionality | Scenario executes correctly | Test execution succeeds |

**Validation:**
- Restored scenario matches original functionality
- Restoration completed in <30 minutes
- Process documented in runbook

---

**Scenario 5: Error Handling (Make.com API Failure)**

| Step | Action | Expected Result | Success Criteria |
|------|--------|-----------------|------------------|
| 1 | Simulate Make.com API failure (invalid API key) | Workflow executes | Workflow starts |
| 2 | Workflow attempts to retrieve scenarios | API returns 401 Unauthorized | Error logged |
| 3 | Workflow retries with exponential backoff | 3 retry attempts | Delays: 1s, 2s, 4s |
| 4 | Workflow fails gracefully | Execution summary shows error | Error details included |

**Validation:**
- Error logged with timestamp, error type, and message
- Workflow does not hang or timeout
- Execution summary indicates failure with clear error description

---

**Scenario 6: Error Handling (Single Scenario Failure)**

| Step | Action | Expected Result | Success Criteria |
|------|--------|-----------------|------------------|
| 1 | Simulate single scenario API failure | Workflow executes | Workflow starts |
| 2 | Workflow processes scenarios | 49 succeed, 1 fails | Error logged for failing scenario |
| 3 | Workflow continues processing | Remaining scenarios processed | All other scenarios backed up |
| 4 | Execution summary returned | Summary shows error count | backedUp = 49, errors = 1 |

**Validation:**
- 49 scenarios backed up successfully
- 1 scenario error logged with details
- Backup state updated for successful scenarios only
- Workflow completes without failing entirely

---

**Scenario 7: GitHub Conflict Resolution**

| Step | Action | Expected Result | Success Criteria |
|------|--------|-----------------|------------------|
| 1 | Trigger workflow twice simultaneously | Both workflows execute | Concurrent execution |
| 2 | First workflow commits to GitHub | Commit succeeds | File SHA updated |
| 3 | Second workflow attempts commit | 409 Conflict error | Error detected |
| 4 | Second workflow retries with fresh SHA | Retrieves updated file SHA | Fresh SHA obtained |
| 5 | Second workflow commits successfully | Commit succeeds | No data loss |

**Validation:**
- Both workflows complete successfully
- No commits lost or duplicated
- Backup state remains consistent

---

## Phase 3: Implementation Roadmap

### 3.1 Implementation Phases

#### Phase 1: Repository Setup and Configuration (Week 1, Days 1-2)

**Objectives:**
- Create GitHub repository infrastructure
- Configure access controls and permissions
- Document repository purpose and structure

**Tasks:**
1. Create private GitHub repository `fortiumpartners/make-scenarios-backup`
2. Add initial README.md with repository documentation
3. Configure repository settings (branch protection, permissions)
4. Create GitHub Personal Access Token with minimal permissions
5. Configure repository access for DevOps and Automation Engineering teams

**Deliverables:**
- Functional GitHub repository
- Initial documentation committed
- Access tokens generated and secured

**Success Criteria:**
- Repository accessible to authorized users
- Token permissions validated (can create/update files)

---

#### Phase 2: API Authentication and Testing (Week 1, Days 3-4)

**Objectives:**
- Validate Make.com and GitHub API access
- Test authentication mechanisms
- Document API integration procedures

**Tasks:**
1. Obtain Make.com API key with read permissions
2. Test Make.com API authentication (list scenarios, get blueprint)
3. Test GitHub API authentication (create/update files)
4. Document API authentication procedures
5. Add API keys to n8n environment variables

**Deliverables:**
- Working API credentials for both platforms
- API authentication test scripts
- Environment variable documentation

**Success Criteria:**
- Successfully retrieve scenarios from Make.com API
- Successfully create test file in GitHub repository
- All credentials secured in environment variables

---

#### Phase 3: n8n Workflow Development (Week 1-2, Days 5-9)

**Objectives:**
- Build complete n8n workflow
- Implement all functional requirements
- Test error handling and edge cases

**Tasks:**
1. Create workflow skeleton with webhook trigger
2. Implement scenario retrieval from Make.com
3. Implement backup state loading from GitHub
4. Implement incremental backup logic (change detection)
5. Implement blueprint download from Make.com
6. Implement GitHub file creation/update (metadata and blueprint)
7. Implement backup state tracking and update
8. Implement execution summary and reporting
9. Add error handling with retry logic
10. Test workflow end-to-end with test scenarios

**Deliverables:**
- Complete n8n workflow JSON file
- Workflow deployed to n8n instance
- Workflow tested via webhook trigger

**Success Criteria:**
- Workflow executes successfully end-to-end
- All functional requirements implemented
- Error handling validated

---

#### Phase 4: Initial Backup Execution (Week 2, Days 10-11)

**Objectives:**
- Execute first complete backup of all Make.com scenarios
- Validate data integrity and repository structure
- Verify backup state accuracy

**Tasks:**
1. Trigger workflow for initial backup
2. Monitor execution and troubleshoot any issues
3. Validate repository structure matches specification
4. Verify all scenarios backed up (100% coverage)
5. Validate metadata.json and blueprint.json contents
6. Verify backup state file accuracy
7. Review Git commit history for completeness

**Deliverables:**
- Complete backup of all Make.com scenarios in GitHub
- Validated repository structure
- Initial backup state file

**Success Criteria:**
- All scenarios backed up successfully
- Repository structure matches specification
- Backup state accurate and complete

---

#### Phase 5: Incremental Backup Validation (Week 2, Days 12-13)

**Objectives:**
- Validate incremental backup logic
- Test change detection and filtering
- Verify efficiency improvements

**Tasks:**
1. Execute workflow without changes (validate skipping logic)
2. Modify test scenario in Make.com
3. Execute workflow with single scenario change
4. Verify only changed scenario backed up
5. Validate backup state updated correctly
6. Measure backup efficiency (scenarios skipped vs. backed up)

**Deliverables:**
- Validated incremental backup functionality
- Efficiency metrics documented

**Success Criteria:**
- Unchanged scenarios skipped (no unnecessary backups)
- Changed scenarios detected and backed up
- Backup state updated correctly

---

#### Phase 6: Error Handling and Recovery Testing (Week 2, Days 14-15)

**Objectives:**
- Validate error handling mechanisms
- Test retry logic and failure scenarios
- Ensure graceful degradation

**Tasks:**
1. Simulate Make.com API failure (invalid credentials)
2. Simulate GitHub API failure (rate limiting)
3. Simulate single scenario failure
4. Test concurrent execution (conflict resolution)
5. Validate error logging and reporting
6. Test workflow recovery after failure

**Deliverables:**
- Validated error handling for all failure modes
- Error logs reviewed for completeness
- Recovery procedures documented

**Success Criteria:**
- Workflow handles errors gracefully without crashing
- Retry logic functions correctly
- Errors logged with sufficient detail for troubleshooting

---

#### Phase 7: Restoration Procedure Development (Week 3, Days 16-17)

**Objectives:**
- Document scenario restoration procedures
- Test restoration process with real scenarios
- Train team members on restoration workflows

**Tasks:**
1. Document step-by-step restoration procedure
2. Test restoration with 3+ scenarios
3. Measure restoration time (target: <30 minutes)
4. Create troubleshooting guide for common issues
5. Conduct team training session
6. Update documentation based on feedback

**Deliverables:**
- Complete restoration procedure documentation
- Restoration tested and validated
- Team trained on recovery workflows

**Success Criteria:**
- Restoration procedure documented and validated
- Average restoration time <30 minutes
- 2+ team members successfully complete restoration

---

#### Phase 8: Scheduled Execution and Monitoring (Week 3, Days 18-20)

**Objectives:**
- Configure scheduled execution (daily backups)
- Implement basic monitoring and alerting
- Validate production readiness

**Tasks:**
1. Configure scheduled execution (cron or n8n schedule trigger)
2. Monitor 3+ consecutive daily executions
3. Review execution logs for issues
4. Define failure alerting mechanism (email/Slack)
5. Create operational runbook
6. Conduct stakeholder review and sign-off

**Deliverables:**
- Scheduled execution configured and validated
- Monitoring procedures documented
- Operational runbook complete

**Success Criteria:**
- 3+ consecutive successful daily backups
- Execution logs reviewed and validated
- Stakeholder sign-off obtained

---

#### Phase 9: Production Launch (Week 3, Day 21)

**Objectives:**
- Officially launch backup system
- Transition from Google Drive to GitHub as primary backup
- Monitor initial production period

**Tasks:**
1. Final stakeholder review and approval
2. Launch announcement to team
3. Monitor first week of production backups
4. Address any issues or feedback
5. Schedule decommissioning of Google Drive backup

**Deliverables:**
- Production backup system operational
- Team notified of new backup location
- Monitoring in place

**Success Criteria:**
- 7 days of successful production backups
- No critical issues identified
- Stakeholder satisfaction achieved

---

### 3.2 Resource Requirements

#### Personnel

| Role | Responsibility | Time Commitment |
|------|----------------|-----------------|
| **DevOps Engineer** | n8n workflow development, deployment, testing | 40 hours (2 weeks) |
| **Automation Engineer** | Requirements validation, restoration testing | 8 hours (review and testing) |
| **IT Operations Manager** | Stakeholder coordination, approval, monitoring strategy | 4 hours (reviews and sign-off) |
| **Product Manager** | Requirements definition, acceptance criteria, stakeholder communication | 8 hours (PRD creation and reviews) |

#### Infrastructure

| Component | Requirement | Cost |
|-----------|-------------|------|
| **n8n Instance** | Existing infrastructure | $0 (already deployed) |
| **GitHub Repository** | Private repository in fortiumpartners org | $0 (within plan limits) |
| **Make.com API** | API access (requires paid plan) | $0 (existing subscription) |
| **GitHub API** | 5,000 requests/hour (authenticated) | $0 (free tier) |

#### API Credentials

| Service | Credential Type | Permissions | Owner |
|---------|----------------|-------------|-------|
| **Make.com** | API Token | Read (scenarios, blueprints) | DevOps team |
| **GitHub** | Personal Access Token | repo (or contents: write for fine-grained) | DevOps team |

---

### 3.3 Risk Assessment

#### High-Risk Items (P0 - Critical)

**Risk 1: Make.com API Rate Limiting**
- **Probability:** Medium
- **Impact:** High (backup failures)
- **Mitigation:**
  - Implement exponential backoff on 429 errors
  - Sequential processing to minimize request volume
  - Monitor API usage and adjust backup frequency if needed
- **Contingency:**
  - Reduce backup frequency from daily to every 2 days if rate limiting occurs
  - Contact Make.com support to increase rate limits if available

**Risk 2: GitHub API Rate Limiting**
- **Probability:** Low (within 5,000 requests/hour limit)
- **Impact:** High (backup failures)
- **Mitigation:**
  - Sequential processing (1 scenario at a time) to minimize concurrent commits
  - Incremental backups reduce total API calls
  - Monitor GitHub API usage in logs
- **Contingency:**
  - Implement request throttling if approaching limits
  - Split backups across multiple runs if scenario count exceeds limits

**Risk 3: Make.com API Authentication Failure**
- **Probability:** Low
- **Impact:** High (no backups)
- **Mitigation:**
  - Validate API key during setup phase
  - Implement clear error logging for auth failures
  - Document API key rotation procedure
- **Contingency:**
  - Monitor for auth failures in logs
  - Immediate alert to DevOps team if auth fails
  - Keep backup API key for emergency rotation

---

#### Medium-Risk Items (P1 - Important)

**Risk 4: Workflow Execution Failure**
- **Probability:** Medium
- **Impact:** Medium (delayed backups)
- **Mitigation:**
  - Comprehensive error handling with retries
  - Workflow continues processing if single scenario fails
  - n8n workflow error logging
- **Contingency:**
  - Manual workflow trigger if scheduled execution fails
  - Review logs and fix issues within 24 hours

**Risk 5: Backup State File Corruption**
- **Probability:** Low
- **Impact:** Medium (full backup required on next run)
- **Mitigation:**
  - Validate JSON before committing backup state
  - Graceful handling of corrupted state (treat as empty)
- **Contingency:**
  - Rebuild backup state from Git commit history if corrupted
  - Full backup run acceptable if state lost (one-time cost)

**Risk 6: GitHub Repository Access Loss**
- **Probability:** Low
- **Impact:** High (no backups, no restoration capability)
- **Mitigation:**
  - Multiple team members with repository access
  - Personal Access Token rotatable without code changes
  - Repository ownership assigned to organization (not individual)
- **Contingency:**
  - Emergency restoration from Google Drive backups if GitHub unavailable
  - Escalate to GitHub support for access recovery

---

#### Low-Risk Items (P2 - Monitor)

**Risk 7: n8n Instance Downtime**
- **Probability:** Low (self-hosted, high availability)
- **Impact:** Medium (delayed backups)
- **Mitigation:**
  - n8n instance monitoring and alerting
  - Docker container auto-restart configured
- **Contingency:**
  - Manual workflow trigger after n8n recovery
  - Missed backups caught by incremental logic on next run

**Risk 8: Documentation Outdated**
- **Probability:** Medium (over time)
- **Impact:** Low (training and troubleshooting delays)
- **Mitigation:**
  - Documentation review during any workflow changes
  - Quarterly documentation review scheduled
- **Contingency:**
  - Update documentation as needed when issues found

---

### 3.4 Migration Strategy

#### Google Drive to GitHub Transition

**Objective:**
Transition from Google Drive as primary backup location to GitHub while maintaining backup coverage throughout migration.

**Approach: Parallel Operation (Recommended)**

**Phase 1: GitHub Backup Activation (Week 1-2)**
- Deploy n8n GitHub backup workflow
- Run initial complete backup to GitHub
- Validate GitHub backups for completeness
- **Keep Google Drive backup running in parallel**

**Phase 2: Validation Period (Week 3-4)**
- Monitor both backup systems for consistency
- Compare GitHub vs. Google Drive backups (spot checks)
- Test restoration from GitHub backups (non-production scenarios)
- Validate incremental backup logic working correctly

**Phase 3: Primary Cutover (Week 5)**
- Declare GitHub as primary backup location
- Update disaster recovery procedures to reference GitHub
- Update team training and documentation
- **Keep Google Drive backup running as secondary for 30 days**

**Phase 4: Google Drive Decommission (Week 9-10)**
- Verify 30+ days of successful GitHub backups
- Final backup to Google Drive (archive)
- Disable Google Drive backup scenario in Make.com
- Archive Google Drive folder (read-only, preserve for 90 days)
- Remove Google Drive from disaster recovery procedures

**Rollback Strategy:**
- If GitHub backups fail consistently (>3 consecutive failures), revert to Google Drive as primary
- Google Drive backups remain functional until 30 days after GitHub proven reliable
- Restoration procedures documented for both systems during transition

---

## Appendix A: Technical Integration Details

### A.1 API Endpoints Reference

**Make.com API:**
```
Base URL: https://us1.make.com/api/v2
Authentication: Authorization: Token {MAKE_API_KEY}

Endpoints:
- GET /scenarios?teamId={teamId}&organizationId={organizationId}&pg[limit]=100
  Purpose: List all scenarios

- GET /scenarios/{scenarioId}/blueprint?draft=false
  Purpose: Download scenario blueprint
```

**GitHub API:**
```
Base URL: https://api.github.com
Authentication: Authorization: Bearer {GITHUB_PAT}

Endpoints:
- GET /repos/{owner}/{repo}/contents/{path}
  Purpose: Get file contents and SHA

- PUT /repos/{owner}/{repo}/contents/{path}
  Purpose: Create or update file
  Body: { message, content (base64), sha (for updates), branch, committer }
```

---

### A.2 Data Schemas

**Backup State Schema (`.backup-state.json`):**
```json
{
  "lastRun": "ISO 8601 timestamp",
  "scenarios": {
    "{scenarioId}": {
      "name": "string",
      "lastEdit": "ISO 8601 timestamp",
      "lastBackup": "ISO 8601 timestamp",
      "backupCount": "integer",
      "gitSHA": "string (Git commit SHA)"
    }
  }
}
```

**Scenario Metadata Schema (`metadata.json`):**
```json
{
  "id": "integer (Make.com scenario ID)",
  "name": "string",
  "description": "string",
  "folderId": "integer",
  "created": "ISO 8601 timestamp",
  "lastEdit": "ISO 8601 timestamp",
  "teamId": "integer",
  "organizationId": "integer",
  "isActive": "boolean",
  "isPaused": "boolean",
  "backupTimestamp": "ISO 8601 timestamp",
  "backupHistory": [
    {
      "timestamp": "ISO 8601 timestamp",
      "gitCommit": "string",
      "gitSHA": "string"
    }
  ]
}
```

---

### A.3 GitHub Repository Structure

```
make-scenarios-backup/
├── README.md                           # Repository documentation
├── scenarios/                          # All scenario backups
│   ├── 12345/                          # Scenario ID directory
│   │   ├── metadata.json               # Scenario metadata
│   │   └── blueprint.json              # Scenario blueprint
│   ├── 67890/
│   │   ├── metadata.json
│   │   └── blueprint.json
│   └── .../
├── .backup-state.json                  # Backup tracking state
└── .github/
    └── workflows/
        └── cleanup-old-versions.yml    # (Optional future enhancement)
```

---

## Appendix B: Success Metrics Dashboard (Future Enhancement)

### Key Performance Indicators (KPIs)

**Backup Coverage:**
- Total Make.com scenarios: [count]
- Scenarios backed up: [count] ([percentage]%)
- Last successful backup: [timestamp]

**Backup Efficiency:**
- Scenarios backed up (changed): [count]
- Scenarios skipped (unchanged): [count]
- Efficiency ratio: [percentage]%

**Reliability:**
- Successful executions (7 days): [count]/[total] ([percentage]%)
- Scenario backup success rate: [percentage]%
- Average execution duration: [minutes]

**Recovery:**
- Restoration tests performed: [count]
- Successful restorations: [count] ([percentage]%)
- Average restoration time: [minutes]

---

## Appendix C: Stakeholder Communication Plan

### Launch Communication

**Audience:** DevOps, Automation Engineering, IT Operations, Business Stakeholders

**Message:**
> Subject: New Make.com Backup System - GitHub Integration Launched
>
> We've successfully migrated our Make.com scenario backups from Google Drive to GitHub. This provides:
>
> - **Better disaster recovery**: Restore scenarios in minutes, not hours
> - **Complete version history**: Track all scenario changes with Git
> - **Improved reliability**: Independent backup infrastructure (n8n + GitHub)
>
> Key Information:
> - Repository: https://github.com/fortiumpartners/make-scenarios-backup
> - Backup schedule: Daily at 2 AM
> - Restoration procedure: [link to documentation]
>
> Questions? Contact DevOps team.

**Training:**
- 30-minute team training session (week 3)
- Documentation available in GitHub repository
- Practice restoration exercise during training

---

## Document Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-03 | Product Management | Initial PRD creation from technical specification |

---

## Approval Sign-Off

| Stakeholder | Role | Signature | Date |
|-------------|------|-----------|------|
| DevOps Lead | Technical Approval | _____________ | ______ |
| IT Operations Manager | Operational Approval | _____________ | ______ |
| Automation Engineering Lead | User Acceptance | _____________ | ______ |
| Product Manager | Requirements Owner | _____________ | ______ |

---

**END OF PRODUCT REQUIREMENTS DOCUMENT**
