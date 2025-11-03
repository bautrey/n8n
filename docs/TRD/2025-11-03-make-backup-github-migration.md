# Technical Requirements Document: Make.com Backup Migration

**Project:** Make.com Scenario Backup System Migration
**Version:** 1.0
**Date:** 2025-11-03
**Status:** 🔴 Ready for Implementation
**TRD Owner:** Technical Lead
**Implementation Team:** Backend Developer, Test Runner, Git Workflow

---

## Document Overview

This TRD transforms the approved PRD for migrating Make.com scenario backups from Google Drive to GitHub using n8n. It provides complete technical specifications, architecture design, implementation tasks, and quality requirements.

**Related Documents:**
- **PRD:** `/Users/burke/projects/n8n/docs/PRD/make-backup-github-prd-approved.md` (APPROVED)
- **Implementation Output:** n8n workflow JSON in `workflows/make-backup-github.json`

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Technical Architecture](#technical-architecture)
3. [Master Task List](#master-task-list)
4. [API Specifications](#api-specifications)
5. [Data Schemas](#data-schemas)
6. [n8n Workflow Design](#n8n-workflow-design)
7. [Error Handling & Recovery](#error-handling--recovery)
8. [Testing Requirements](#testing-requirements)
9. [Security Requirements](#security-requirements)
10. [Performance Requirements](#performance-requirements)
11. [Monitoring & Observability](#monitoring--observability)
12. [Deployment Procedures](#deployment-procedures)
13. [Acceptance Criteria](#acceptance-criteria)

---

## Executive Summary

### Problem Statement

Fortium Partners currently backs up 289 Make.com scenarios to Google Drive, which lacks version control, change tracking, and proper automation visibility. The backup system needs migration to GitHub for better version control and integration with n8n automation platform.

### Solution Overview

Create an n8n workflow that:
1. Runs daily at 2:00 AM US/Central
2. Queries Make.com API for all scenarios (289 total)
3. Downloads scenario blueprints (JSON exports)
4. Compares against last backup state to identify changes
5. Commits only changed scenarios to GitHub
6. Maintains backup state file for incremental backups
7. Sends execution summary to Slack #n8n-automation channel

### Technical Scope

**In Scope:**
- n8n workflow implementation with all nodes
- Make.com API integration (list scenarios, download blueprints)
- GitHub API integration (commit files, update state)
- Slack API integration (execution notifications)
- Backup state management (JSON file tracking)
- Error handling and retry logic
- Comprehensive testing suite

**Out of Scope:**
- Make.com credential management (stored in Make.com, not backed up)
- Historical backup migration from Google Drive
- GitHub repository creation (prerequisite)
- API credential generation (manual setup required)
- Slack channel creation (manual setup required)

### Success Criteria

✅ All 289 Make.com scenarios backed up to GitHub
✅ Daily scheduled execution at 2:00 AM CST with 100% reliability
✅ Incremental backups (only changed scenarios committed)
✅ Slack notifications for all executions (success and failure)
✅ Zero manual interventions for 7 consecutive days
✅ Test suite with 100% critical path coverage

---

## Technical Architecture

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         n8n Workflow                            │
│                  (make-backup-github.json)                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┼─────────────┐
                │             │             │
                ▼             ▼             ▼
        ┌───────────┐  ┌───────────┐  ┌───────────┐
        │ Make.com  │  │  GitHub   │  │   Slack   │
        │    API    │  │    API    │  │    API    │
        └───────────┘  └───────────┘  └───────────┘
                │             │             │
                ▼             ▼             ▼
        ┌───────────┐  ┌───────────┐  ┌───────────┐
        │ 289       │  │ bautrey/  │  │ #n8n-     │
        │ Scenarios │  │ make-     │  │ automation│
        │           │  │ scenarios-│  │           │
        │           │  │ backup    │  │           │
        └───────────┘  └───────────┘  └───────────┘
```

### Workflow Execution Flow

```
┌──────────────────┐
│  Cron Trigger    │
│  (Daily 2:00 AM) │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Initialize State │ ← Read backup-state.json from GitHub
│ & Variables      │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Fetch All        │ ← Make.com API: GET /scenarios?teamId=154819
│ Scenarios        │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Filter Changed   │ ← Compare lastEditedDate vs backup state
│ Scenarios        │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Split In Batches │ ← Process scenarios one at a time
│ (batch size: 1)  │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Download         │ ← Make.com API: GET /scenarios/{id}/blueprint
│ Blueprint        │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Commit to GitHub │ ← GitHub API: PUT /repos/.../contents/{path}
│                  │   Base64 encode, include SHA if exists
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Update Backup    │ ← Update backup-state.json with new timestamps
│ State            │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Commit State     │ ← GitHub API: PUT /repos/.../contents/backup-state.json
│ File             │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Send Slack       │ ← Slack API: POST /chat.postMessage
│ Notification     │   Include summary, links, stats
└──────────────────┘
         │
         ▼
    [Complete]
```

### Error Handling Flow

```
┌──────────────────┐
│ Any Node Fails   │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Error Trigger    │ ← Catches workflow errors
│ Node             │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Format Error     │ ← Extract error details, stack trace
│ Details          │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Send Slack Error │ ← Post to #n8n-automation with ❌ emoji
│ Notification     │   Include failed node, error message, context
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Log to n8n       │ ← Workflow execution marked as failed
│ Execution Log    │
└──────────────────┘
```

### Technology Stack

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Workflow Engine** | n8n | 1.x | Workflow orchestration and scheduling |
| **Backend API** | Make.com API | v2 | Scenario and blueprint retrieval |
| **Version Control** | GitHub API | v3 (REST) | File storage and version control |
| **Notifications** | Slack API | Web API | Execution status notifications |
| **Data Format** | JSON | - | All data interchange and storage |
| **Authentication** | HTTP Header Auth | - | API key and token authentication |
| **Scheduling** | Cron | - | Daily execution at 2:00 AM CST |

### Data Flow Architecture

```
Make.com (Source)
    │
    │ GET /scenarios → JSON array of 289 scenarios
    │
    ▼
n8n Memory (Processing)
    │
    │ Compare lastEditedDate vs backup state
    │ Filter to changed scenarios only
    │
    ▼
Make.com (Source)
    │
    │ GET /scenarios/{id}/blueprint → JSON blueprint
    │ Loop for each changed scenario
    │
    ▼
n8n Memory (Processing)
    │
    │ Base64 encode blueprint JSON
    │ Format commit message
    │ Prepare GitHub API request
    │
    ▼
GitHub (Destination)
    │
    │ PUT /repos/.../contents/scenarios/{id}.json
    │ Commit each scenario individually
    │
    ▼
GitHub (Destination)
    │
    │ PUT /repos/.../contents/backup-state.json
    │ Update backup state with new timestamps
    │
    ▼
Slack (Notification)
    │
    │ POST /chat.postMessage
    │ Send execution summary to #n8n-automation
    │
    ▼
Complete
```

---

## Master Task List

### Sprint 1: Setup & Prerequisites (Estimated: 2 hours)

#### 1.1 Environment Configuration
- [ ] **1.1.1** Create GitHub repository `bautrey/make-scenarios-backup` (private)
  - [ ] Initialize with README.md
  - [ ] Add .gitignore for n8n files
  - [ ] Create initial directory structure: `scenarios/`, `docs/`
  - **Acceptance:** Repository exists and accessible via GitHub API

- [ ] **1.1.2** Obtain Make.com API credentials
  - [ ] Login to Make.com → Settings → API
  - [ ] Create API token named "n8n Backup System"
  - [ ] Set permissions: Read (scenarios, blueprints)
  - [ ] Store token in secure location (password manager)
  - **Acceptance:** API token generated and securely stored

- [ ] **1.1.3** Obtain GitHub Personal Access Token
  - [ ] Login to GitHub → Settings → Developer settings → Personal access tokens
  - [ ] Generate token (classic) with `repo` scope
  - [ ] Name: "n8n Make.com Backup"
  - [ ] Store token in secure location
  - **Acceptance:** GitHub PAT generated and securely stored

- [ ] **1.1.4** Create Slack bot and obtain token
  - [ ] Go to https://api.slack.com/apps → Create New App
  - [ ] Name: "n8n Automation Bot"
  - [ ] Add bot scopes: `chat:write`, `chat:write.public`
  - [ ] Install to Fortium Partners workspace
  - [ ] Copy Bot User OAuth Token
  - [ ] Store token in secure location
  - **Acceptance:** Slack bot created and token obtained

- [ ] **1.1.5** Create Slack channel for notifications
  - [ ] Create private channel `#n8n-automation`
  - [ ] Invite n8n Automation Bot to channel
  - [ ] Note channel ID from channel details
  - **Acceptance:** Channel exists, bot has access, channel ID recorded

- [ ] **1.1.6** Configure n8n environment variables
  - [ ] Edit `/Users/burke/projects/n8n/.env`
  - [ ] Add all Make.com, GitHub, Slack variables (see PRD section 4)
  - [ ] Verify syntax with `source .env && env | grep MAKE`
  - **Acceptance:** All environment variables set correctly

- [ ] **1.1.7** Add credentials to n8n credential manager
  - [ ] Create "Make.com API" credential (Header Auth)
  - [ ] Create "GitHub API (Burke)" credential (Header Auth)
  - [ ] Create "Slack n8n Bot" credential (Slack OAuth2 API)
  - **Acceptance:** All credentials stored and encrypted in n8n

#### 1.2 Validation & Testing
- [ ] **1.2.1** Test Make.com API connectivity
  - [ ] Execute curl command: `GET /scenarios?teamId=154819`
  - [ ] Verify 200 response with scenario list
  - [ ] Confirm 289 scenarios returned
  - **Acceptance:** API returns valid scenario list

- [ ] **1.2.2** Test GitHub API connectivity
  - [ ] Execute curl command: `GET /repos/bautrey/make-scenarios-backup`
  - [ ] Verify 200 response with repository details
  - [ ] Test file creation: `PUT /repos/.../contents/test.txt`
  - **Acceptance:** API accessible, file creation successful

- [ ] **1.2.3** Test Slack API connectivity
  - [ ] Execute curl command: `POST /chat.postMessage`
  - [ ] Send test message to #n8n-automation
  - [ ] Verify message appears in channel
  - **Acceptance:** Bot can post messages to channel

---

### Sprint 2: Core Workflow Implementation (Estimated: 6 hours)

#### 2.1 Workflow Structure
- [ ] **2.1.1** Create workflow JSON file
  - [ ] Create `workflows/make-backup-github.json`
  - [ ] Set workflow name: "Make.com → GitHub Backup"
  - [ ] Add workflow metadata (description, tags)
  - **Acceptance:** Workflow file created with valid JSON structure

- [ ] **2.1.2** Add Cron Trigger node
  - [ ] Node type: `n8n-nodes-base.cron`
  - [ ] Schedule: `0 2 * * *` (2:00 AM daily)
  - [ ] Timezone: `America/Chicago`
  - [ ] Name: "Daily 2AM CST Trigger"
  - **Acceptance:** Cron trigger configured correctly

- [ ] **2.1.3** Add workflow execution metadata node
  - [ ] Node type: `n8n-nodes-base.set`
  - [ ] Capture: execution start time, workflow ID
  - [ ] Name: "Initialize Execution Context"
  - **Acceptance:** Execution metadata captured

#### 2.2 Backup State Management
- [ ] **2.2.1** Create "Read Backup State" node
  - [ ] Node type: `n8n-nodes-base.httpRequest`
  - [ ] URL: `https://api.github.com/repos/bautrey/make-scenarios-backup/contents/backup-state.json`
  - [ ] Method: GET
  - [ ] Credential: GitHub API (Burke)
  - [ ] Error handling: Continue on 404 (file doesn't exist yet)
  - **Acceptance:** Node retrieves existing backup state or handles missing file

- [ ] **2.2.2** Create "Parse Backup State" node
  - [ ] Node type: `n8n-nodes-base.function`
  - [ ] Parse base64 content from GitHub response
  - [ ] Decode JSON backup state
  - [ ] If 404, create empty state: `{ "lastBackup": {}, "metadata": {} }`
  - **Acceptance:** Backup state parsed and available for comparison

- [ ] **2.2.3** Create "Update Backup State" node (end of workflow)
  - [ ] Node type: `n8n-nodes-base.function`
  - [ ] Merge new scenario timestamps into backup state
  - [ ] Add workflow execution metadata
  - [ ] Format for GitHub commit
  - **Acceptance:** Updated backup state prepared for commit

- [ ] **2.2.4** Create "Commit Backup State" node
  - [ ] Node type: `n8n-nodes-base.httpRequest`
  - [ ] URL: `https://api.github.com/repos/bautrey/make-scenarios-backup/contents/backup-state.json`
  - [ ] Method: PUT
  - [ ] Body: Base64 encoded state, commit message, SHA (if exists)
  - [ ] Credential: GitHub API (Burke)
  - **Acceptance:** Backup state committed to GitHub successfully

#### 2.3 Make.com Integration
- [ ] **2.3.1** Create "Fetch All Scenarios" node
  - [ ] Node type: `n8n-nodes-base.httpRequest`
  - [ ] URL: `https://us1.make.com/api/v2/scenarios?teamId=154819`
  - [ ] Method: GET
  - [ ] Credential: Make.com API
  - [ ] Pagination: Handle if >100 scenarios per page
  - **Acceptance:** All 289 scenarios retrieved from Make.com

- [ ] **2.3.2** Create "Filter Changed Scenarios" node
  - [ ] Node type: `n8n-nodes-base.function`
  - [ ] Compare each scenario's `lastEditedDate` vs backup state
  - [ ] Filter to scenarios where `lastEditedDate > lastBackup[scenarioId]`
  - [ ] Output array of changed scenario IDs
  - **Acceptance:** Only changed scenarios identified for backup

- [ ] **2.3.3** Create "Split Scenarios" node
  - [ ] Node type: `n8n-nodes-base.splitInBatches`
  - [ ] Batch size: 1 (process one scenario at a time)
  - [ ] Reset: After all items processed
  - **Acceptance:** Scenarios processed sequentially to avoid GitHub conflicts

- [ ] **2.3.4** Create "Download Blueprint" node
  - [ ] Node type: `n8n-nodes-base.httpRequest`
  - [ ] URL: `https://us1.make.com/api/v2/scenarios/{{$json.id}}/blueprint`
  - [ ] Method: GET
  - [ ] Credential: Make.com API
  - [ ] Output: Blueprint JSON
  - **Acceptance:** Blueprint downloaded for each changed scenario

#### 2.4 GitHub Integration
- [ ] **2.4.1** Create "Check Existing File" node
  - [ ] Node type: `n8n-nodes-base.httpRequest`
  - [ ] URL: `https://api.github.com/repos/bautrey/make-scenarios-backup/contents/scenarios/{{$json.id}}.json`
  - [ ] Method: GET
  - [ ] Credential: GitHub API (Burke)
  - [ ] Error handling: Continue on 404 (new scenario)
  - [ ] Extract SHA if file exists (required for update)
  - **Acceptance:** Existing file SHA retrieved or 404 handled

- [ ] **2.4.2** Create "Prepare Commit Data" node
  - [ ] Node type: `n8n-nodes-base.function`
  - [ ] Base64 encode blueprint JSON
  - [ ] Format commit message: "Update scenario {id}: {name}"
  - [ ] Include SHA if updating existing file
  - [ ] Set bot name and email
  - **Acceptance:** Commit data formatted correctly for GitHub API

- [ ] **2.4.3** Create "Commit Scenario File" node
  - [ ] Node type: `n8n-nodes-base.httpRequest`
  - [ ] URL: `https://api.github.com/repos/bautrey/make-scenarios-backup/contents/scenarios/{{$json.id}}.json`
  - [ ] Method: PUT
  - [ ] Body: message, content (base64), sha (if exists), branch
  - [ ] Credential: GitHub API (Burke)
  - **Acceptance:** Scenario committed to GitHub successfully

#### 2.5 Slack Notification
- [ ] **2.5.1** Create "Aggregate Results" node
  - [ ] Node type: `n8n-nodes-base.function`
  - [ ] Count total scenarios processed
  - [ ] Count successful commits
  - [ ] Count skipped (unchanged) scenarios
  - [ ] Count errors
  - [ ] Calculate execution duration
  - **Acceptance:** Execution statistics aggregated

- [ ] **2.5.2** Create "Format Slack Message" node
  - [ ] Node type: `n8n-nodes-base.function`
  - [ ] Format message per PRD specification (section 3)
  - [ ] Include: workflow name, context, timestamp, duration, summary, details, changes
  - [ ] Use ✅ emoji for success header
  - [ ] Add links to GitHub repo and latest commit
  - **Acceptance:** Slack message formatted correctly

- [ ] **2.5.3** Create "Send Slack Notification" node
  - [ ] Node type: `n8n-nodes-base.slack`
  - [ ] Channel: `#n8n-automation` (use channel ID from env)
  - [ ] Credential: Slack n8n Bot
  - [ ] Message: From previous node
  - [ ] Fallback text: "Make.com backup completed"
  - **Acceptance:** Notification posted to Slack channel

---

### Sprint 3: Error Handling & Recovery (Estimated: 3 hours)

#### 3.1 Error Detection
- [ ] **3.1.1** Add Error Trigger node
  - [ ] Node type: `n8n-nodes-base.errorTrigger`
  - [ ] Name: "Catch Workflow Errors"
  - [ ] Trigger on: Any workflow error
  - **Acceptance:** Error trigger configured and catches failures

- [ ] **3.1.2** Create "Extract Error Details" node
  - [ ] Node type: `n8n-nodes-base.function`
  - [ ] Extract: failed node name, error message, stack trace
  - [ ] Include: execution ID, timestamp, workflow context
  - [ ] Sanitize: Remove sensitive data from error output
  - **Acceptance:** Error details extracted and formatted

#### 3.2 Error Notification
- [ ] **3.2.1** Create "Format Error Message" node
  - [ ] Node type: `n8n-nodes-base.function`
  - [ ] Format message with ❌ emoji header
  - [ ] Include: workflow name, failed node, error message, timestamp
  - [ ] Add: execution link, troubleshooting steps
  - **Acceptance:** Error message formatted for Slack

- [ ] **3.2.2** Create "Send Error Notification" node
  - [ ] Node type: `n8n-nodes-base.slack`
  - [ ] Channel: `#n8n-automation`
  - [ ] Credential: Slack n8n Bot
  - [ ] Message: From previous node
  - [ ] Priority: High (mention @channel if critical)
  - **Acceptance:** Error notification sent to Slack

#### 3.3 Retry Logic
- [ ] **3.3.1** Add retry configuration to API nodes
  - [ ] Make.com API calls: 3 retries, exponential backoff
  - [ ] GitHub API calls: 3 retries, exponential backoff
  - [ ] Slack API calls: 2 retries, linear backoff
  - [ ] Wait time: 2s, 5s, 10s for attempts
  - **Acceptance:** Retry logic configured on all API nodes

- [ ] **3.3.2** Add rate limit handling
  - [ ] Detect 429 (Too Many Requests) responses
  - [ ] Extract `Retry-After` header
  - [ ] Wait specified time before retry
  - [ ] Log rate limit events
  - **Acceptance:** Rate limits handled gracefully

#### 3.4 Partial Failure Recovery
- [ ] **3.4.1** Add "Continue On Fail" to batch processing
  - [ ] Enable on "Download Blueprint" node
  - [ ] Enable on "Commit Scenario File" node
  - [ ] Log failed scenario IDs
  - [ ] Include in final summary
  - **Acceptance:** Workflow continues even if individual scenarios fail

- [ ] **3.4.2** Create "Partial Failure Summary" node
  - [ ] Node type: `n8n-nodes-base.function`
  - [ ] List failed scenarios with error reasons
  - [ ] Suggest remediation actions
  - [ ] Include in Slack notification
  - **Acceptance:** Partial failures reported clearly

---

### Sprint 4: Testing & Validation (Estimated: 4 hours)

#### 4.1 Unit Testing
- [ ] **4.1.1** Test backup state parsing logic
  - [ ] Test empty state (404 from GitHub)
  - [ ] Test existing state with scenarios
  - [ ] Test corrupted JSON handling
  - [ ] Test base64 decode edge cases
  - **Acceptance:** All state parsing scenarios handled correctly

- [ ] **4.1.2** Test scenario filtering logic
  - [ ] Test all scenarios changed (no backup state)
  - [ ] Test no scenarios changed
  - [ ] Test partial scenario changes
  - [ ] Test date comparison edge cases
  - **Acceptance:** Filtering logic works for all cases

- [ ] **4.1.3** Test message formatting
  - [ ] Test success message format
  - [ ] Test error message format
  - [ ] Test partial failure message format
  - [ ] Verify markdown rendering in Slack
  - **Acceptance:** All message formats render correctly

#### 4.2 Integration Testing
- [ ] **4.2.1** Test Make.com API integration
  - [ ] Fetch all scenarios successfully
  - [ ] Handle API rate limits
  - [ ] Download blueprints successfully
  - [ ] Handle invalid scenario IDs
  - **Acceptance:** Make.com integration fully functional

- [ ] **4.2.2** Test GitHub API integration
  - [ ] Create new file successfully
  - [ ] Update existing file with SHA
  - [ ] Handle file conflicts
  - [ ] Commit backup state file
  - **Acceptance:** GitHub integration fully functional

- [ ] **4.2.3** Test Slack API integration
  - [ ] Post success notification
  - [ ] Post error notification
  - [ ] Handle rate limits
  - [ ] Verify message formatting
  - **Acceptance:** Slack integration fully functional

#### 4.3 End-to-End Testing
- [ ] **4.3.1** Test initial backup (no existing state)
  - [ ] Execute workflow manually
  - [ ] Verify all 289 scenarios backed up
  - [ ] Check GitHub commits (289 scenario files + 1 state file)
  - [ ] Verify Slack notification
  - **Acceptance:** Initial backup completes successfully

- [ ] **4.3.2** Test incremental backup (no changes)
  - [ ] Execute workflow again immediately
  - [ ] Verify no scenarios backed up (all unchanged)
  - [ ] Check no new GitHub commits
  - [ ] Verify Slack notification shows 0 backed up
  - **Acceptance:** Incremental backup skips unchanged scenarios

- [ ] **4.3.3** Test incremental backup (with changes)
  - [ ] Manually update a scenario in Make.com
  - [ ] Execute workflow
  - [ ] Verify only changed scenario backed up
  - [ ] Check GitHub commit (1 scenario file + 1 state file)
  - [ ] Verify Slack notification shows 1 backed up
  - **Acceptance:** Incremental backup detects and backs up changes

- [ ] **4.3.4** Test error handling
  - [ ] Simulate Make.com API failure
  - [ ] Verify error notification sent to Slack
  - [ ] Verify workflow marked as failed
  - [ ] Check error details in execution log
  - **Acceptance:** Errors detected and reported correctly

#### 4.4 Performance Testing
- [ ] **4.4.1** Measure execution time
  - [ ] Record time for 289 scenarios (initial backup)
  - [ ] Record time for 0 scenarios (no changes)
  - [ ] Record time for 10 scenarios (partial changes)
  - [ ] Target: <15 minutes for full backup
  - **Acceptance:** Execution time within acceptable range

- [ ] **4.4.2** Test concurrent execution prevention
  - [ ] Attempt to trigger workflow while running
  - [ ] Verify n8n prevents concurrent execution
  - [ ] Check no data corruption occurs
  - **Acceptance:** Workflow cannot run concurrently

---

### Sprint 5: Deployment & Documentation (Estimated: 2 hours)

#### 5.1 Workflow Deployment
- [ ] **5.1.1** Deploy workflow to n8n
  - [ ] Import workflow JSON via n8n UI
  - [ ] Or use REST API: `POST /api/v1/workflows`
  - [ ] Activate workflow
  - [ ] Verify cron trigger enabled
  - **Acceptance:** Workflow active and scheduled

- [ ] **5.1.2** Verify webhook accessibility
  - [ ] Test manual trigger via webhook
  - [ ] Verify workflow executes successfully
  - [ ] Check execution logs
  - **Acceptance:** Manual trigger works correctly

- [ ] **5.1.3** Schedule production execution
  - [ ] Confirm cron schedule: 2:00 AM CST daily
  - [ ] Wait for first scheduled execution
  - [ ] Verify automatic execution
  - [ ] Check Slack notification received
  - **Acceptance:** Workflow runs on schedule automatically

#### 5.2 Documentation
- [ ] **5.2.1** Create workflow documentation
  - [ ] Document workflow purpose and design
  - [ ] List all nodes with descriptions
  - [ ] Explain error handling strategy
  - [ ] Add troubleshooting guide
  - [ ] Save to: `docs/workflows/make-backup-github.md`
  - **Acceptance:** Comprehensive workflow documentation complete

- [ ] **5.2.2** Create runbook
  - [ ] Document manual execution procedure
  - [ ] List common issues and resolutions
  - [ ] Explain backup state recovery
  - [ ] Add credential rotation procedure
  - [ ] Save to: `docs/runbooks/make-backup-runbook.md`
  - **Acceptance:** Operational runbook available

- [ ] **5.2.3** Update main README
  - [ ] Add workflow description
  - [ ] Link to workflow documentation
  - [ ] List prerequisites
  - [ ] Add quick start guide
  - [ ] Save to: `README.md`
  - **Acceptance:** README updated with new workflow

- [ ] **5.2.4** Create API reference document
  - [ ] Document all API endpoints used
  - [ ] Include request/response examples
  - [ ] List authentication requirements
  - [ ] Add rate limit information
  - [ ] Save to: `docs/API_REFERENCE.md`
  - **Acceptance:** API reference complete

#### 5.3 Monitoring Setup
- [ ] **5.3.1** Configure execution logging
  - [ ] Enable n8n execution retention: 30 days
  - [ ] Enable binary data retention: 7 days
  - [ ] Configure log level: info
  - **Acceptance:** Execution history retained properly

- [ ] **5.3.2** Document monitoring procedures
  - [ ] How to check execution history in n8n UI
  - [ ] How to search Slack notifications
  - [ ] How to verify GitHub commits
  - [ ] How to validate backup state
  - [ ] Save to: `docs/MONITORING.md`
  - **Acceptance:** Monitoring procedures documented

---

### Sprint 6: Production Validation (Estimated: Ongoing - 7 days)

#### 6.1 Production Monitoring
- [ ] **6.1.1** Day 1: Monitor first scheduled execution
  - [ ] Verify execution at 2:00 AM CST
  - [ ] Check Slack notification received
  - [ ] Review GitHub commits
  - [ ] Validate backup state updated
  - **Acceptance:** First execution successful

- [ ] **6.1.2** Day 2-7: Daily health checks
  - [ ] Review Slack notifications daily
  - [ ] Check for any errors or warnings
  - [ ] Verify GitHub commit history
  - [ ] Monitor execution duration trends
  - **Acceptance:** 7 consecutive successful executions

- [ ] **6.1.3** Validate incremental backup behavior
  - [ ] Observe scenarios backed up vs skipped
  - [ ] Verify only changed scenarios committed
  - [ ] Check backup state accuracy
  - [ ] Confirm no duplicate commits
  - **Acceptance:** Incremental backup working correctly

#### 6.2 Production Adjustments
- [ ] **6.2.1** Performance optimization (if needed)
  - [ ] Adjust batch processing if too slow
  - [ ] Optimize API request parallelization
  - [ ] Reduce unnecessary data in state file
  - **Acceptance:** Execution time optimized

- [ ] **6.2.2** Alert tuning (if needed)
  - [ ] Adjust Slack notification verbosity
  - [ ] Add error severity levels
  - [ ] Configure alert escalation
  - **Acceptance:** Alerts provide appropriate detail

---

## API Specifications

### Make.com API

**Base URL:** `https://us1.make.com/api/v2`

**Authentication:**
- Type: API Key
- Header: `Authorization: Token {API_KEY}`
- Credential Name: "Make.com API"

#### Endpoint 1: List Scenarios

**Request:**
```http
GET /scenarios?teamId=154819&limit=100&pg[from]=0
Authorization: Token {MAKE_API_KEY}
```

**Response:** (200 OK)
```json
{
  "scenarios": [
    {
      "id": 123456,
      "name": "Customer Onboarding Workflow",
      "teamId": 154819,
      "folderId": null,
      "scheduling": {
        "type": "interval",
        "interval": 15
      },
      "lastEdit": "2025-11-02T14:23:10.000Z",
      "lastRun": "2025-11-03T01:45:00.000Z",
      "status": "active"
    }
  ],
  "pg": {
    "from": 0,
    "to": 99,
    "total": 289
  }
}
```

**Pagination:**
- Use `pg[from]` parameter for offset
- Max 100 scenarios per page
- Loop until `pg.to >= pg.total - 1`

**Error Handling:**
- 401: Invalid API key → Send error notification
- 429: Rate limit → Retry after `Retry-After` header
- 500: Server error → Retry with exponential backoff

#### Endpoint 2: Download Blueprint

**Request:**
```http
GET /scenarios/{scenarioId}/blueprint
Authorization: Token {MAKE_API_KEY}
```

**Response:** (200 OK)
```json
{
  "response": {
    "name": "Customer Onboarding Workflow",
    "flow": [
      {
        "id": 1,
        "module": "webhook",
        "version": 1,
        "parameters": { ... },
        "mapper": { ... }
      }
    ],
    "metadata": {
      "version": 1,
      "scenario": {
        "roundtrips": 1,
        "maxErrors": 10,
        "autoCommit": true
      }
    }
  }
}
```

**Error Handling:**
- 404: Scenario not found → Skip scenario, log warning
- 401: Invalid API key → Send error notification
- 500: Server error → Retry, then skip if persistent

---

### GitHub API

**Base URL:** `https://api.github.com`

**Authentication:**
- Type: Personal Access Token
- Header: `Authorization: Bearer {GITHUB_PAT}`
- Scope: `repo` (full control of private repositories)
- Credential Name: "GitHub API (Burke)"

#### Endpoint 1: Get File Contents

**Request:**
```http
GET /repos/bautrey/make-scenarios-backup/contents/{path}
Authorization: Bearer {GITHUB_PAT}
Accept: application/vnd.github.v3+json
```

**Response:** (200 OK)
```json
{
  "name": "backup-state.json",
  "path": "backup-state.json",
  "sha": "abc123def456...",
  "size": 12345,
  "content": "ewogICJsYXN0QmFja3VwIjoge30KfQ==",
  "encoding": "base64"
}
```

**Response:** (404 Not Found)
```json
{
  "message": "Not Found",
  "documentation_url": "https://docs.github.com/rest/reference/repos#get-repository-content"
}
```

**Usage:**
- Check if file exists before update
- Extract `sha` for file update (required)
- Decode `content` from base64

#### Endpoint 2: Create or Update File

**Request:**
```http
PUT /repos/bautrey/make-scenarios-backup/contents/{path}
Authorization: Bearer {GITHUB_PAT}
Accept: application/vnd.github.v3+json
Content-Type: application/json

{
  "message": "Update scenario 123456: Customer Onboarding",
  "content": "ewogICJuYW1lIjogIkN1c3RvbWVyIE9uYm9hcmRpbmciCn0=",
  "sha": "abc123def456...",
  "branch": "main",
  "committer": {
    "name": "Make.com Backup Bot",
    "email": "bot@fortiumpartners.com"
  }
}
```

**Notes:**
- `content` must be base64 encoded
- `sha` required for updates, omit for new files
- `sha` mismatch returns 409 conflict

**Response:** (200 OK or 201 Created)
```json
{
  "content": {
    "name": "123456.json",
    "path": "scenarios/123456.json",
    "sha": "new_sha_here...",
    "size": 5678
  },
  "commit": {
    "sha": "commit_sha_here...",
    "message": "Update scenario 123456: Customer Onboarding",
    "author": { ... },
    "committer": { ... }
  }
}
```

**Error Handling:**
- 409: File SHA mismatch → Fetch latest SHA, retry
- 422: Invalid base64 → Log error, skip scenario
- 429: Rate limit → Wait per `Retry-After` header

---

### Slack API

**Base URL:** `https://slack.com/api`

**Authentication:**
- Type: Bot OAuth Token
- Header: `Authorization: Bearer {SLACK_BOT_TOKEN}`
- Token Format: `xoxb-...`
- Credential Name: "Slack n8n Bot"

#### Endpoint: Post Message

**Request:**
```http
POST /chat.postMessage
Authorization: Bearer {SLACK_BOT_TOKEN}
Content-Type: application/json

{
  "channel": "C0123456789",
  "text": "Make.com backup completed",
  "blocks": [
    {
      "type": "header",
      "text": {
        "type": "plain_text",
        "text": "✅ [WORKFLOW: Make.com Backup] SUCCESS"
      }
    },
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "*Context:* Periodic backup of Make.com scenarios to GitHub\n*Timestamp:* 2025-11-03 02:00:15 AM CST\n*Duration:* 2m 34s"
      }
    },
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "*Summary:*\n• Total scenarios: 289\n• Backed up: 7 (updated since last run)\n• Skipped: 282 (unchanged)\n• Errors: 0"
      }
    },
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "*Details:*\n• Repository: https://github.com/bautrey/make-scenarios-backup\n• Latest commit: abc123de\n• Backup state: Updated successfully"
      }
    }
  ]
}
```

**Response:** (200 OK)
```json
{
  "ok": true,
  "channel": "C0123456789",
  "ts": "1699012345.123456",
  "message": {
    "text": "Make.com backup completed",
    "blocks": [ ... ]
  }
}
```

**Error Handling:**
- 429: Rate limit → Retry after delay
- 403: Bot not in channel → Alert user to invite bot
- 500: Server error → Retry once, log if fails

---

## Data Schemas

### Backup State Schema

**File:** `backup-state.json` (stored in GitHub root)

**Purpose:** Track last backup timestamp for each scenario to enable incremental backups

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "metadata": {
      "type": "object",
      "properties": {
        "version": { "type": "string", "const": "1.0" },
        "lastUpdated": { "type": "string", "format": "date-time" },
        "totalScenarios": { "type": "integer" },
        "workflowExecutionId": { "type": "string" }
      },
      "required": ["version", "lastUpdated", "totalScenarios"]
    },
    "lastBackup": {
      "type": "object",
      "patternProperties": {
        "^[0-9]+$": {
          "type": "object",
          "properties": {
            "scenarioId": { "type": "integer" },
            "scenarioName": { "type": "string" },
            "lastEditedDate": { "type": "string", "format": "date-time" },
            "backedUpAt": { "type": "string", "format": "date-time" },
            "githubSha": { "type": "string" }
          },
          "required": ["scenarioId", "lastEditedDate", "backedUpAt"]
        }
      }
    }
  },
  "required": ["metadata", "lastBackup"]
}
```

**Example:**
```json
{
  "metadata": {
    "version": "1.0",
    "lastUpdated": "2025-11-03T02:05:45.123Z",
    "totalScenarios": 289,
    "workflowExecutionId": "12345"
  },
  "lastBackup": {
    "123456": {
      "scenarioId": 123456,
      "scenarioName": "Customer Onboarding Workflow",
      "lastEditedDate": "2025-11-02T14:23:10.000Z",
      "backedUpAt": "2025-11-03T02:01:15.456Z",
      "githubSha": "abc123def456..."
    },
    "789012": {
      "scenarioId": 789012,
      "scenarioName": "Invoice Processing",
      "lastEditedDate": "2025-10-15T09:12:00.000Z",
      "backedUpAt": "2025-10-16T02:00:30.789Z",
      "githubSha": "def456abc123..."
    }
  }
}
```

---

### Scenario Blueprint Schema

**File:** `scenarios/{scenarioId}.json` (stored in GitHub)

**Purpose:** Complete Make.com scenario export for backup and potential restore

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "name": { "type": "string" },
    "flow": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": { "type": "integer" },
          "module": { "type": "string" },
          "version": { "type": "integer" },
          "parameters": { "type": "object" },
          "mapper": { "type": "object" },
          "metadata": { "type": "object" }
        },
        "required": ["id", "module"]
      }
    },
    "metadata": {
      "type": "object",
      "properties": {
        "version": { "type": "integer" },
        "scenario": {
          "type": "object",
          "properties": {
            "roundtrips": { "type": "integer" },
            "maxErrors": { "type": "integer" },
            "autoCommit": { "type": "boolean" },
            "sequential": { "type": "boolean" }
          }
        },
        "designer": { "type": "object" },
        "zone": { "type": "string" }
      }
    }
  },
  "required": ["name", "flow"]
}
```

**Note:** This schema comes directly from Make.com API. We store it as-is without modification.

---

### Slack Notification Payload

**Structure:** Slack Block Kit format

```json
{
  "channel": "C0123456789",
  "text": "Make.com backup completed",
  "blocks": [
    {
      "type": "header",
      "text": {
        "type": "plain_text",
        "text": "✅ [WORKFLOW: Make.com Backup] SUCCESS"
      }
    },
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "*Context:* Periodic backup of Make.com scenarios to GitHub\n*Timestamp:* {{timestamp}}\n*Duration:* {{duration}}"
      }
    },
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "*Summary:*\n• Total scenarios: {{total}}\n• Backed up: {{backed_up}} (updated since last run)\n• Skipped: {{skipped}} (unchanged)\n• Errors: {{errors}}"
      }
    },
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "*Details:*\n• Repository: {{repo_url}}\n• Latest commit: {{commit_sha}}\n• Backup state: {{state_status}}"
      }
    },
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "*Changes:*\n{{changed_scenarios_list}}"
      }
    }
  ]
}
```

**Error Notification:**
```json
{
  "channel": "C0123456789",
  "text": "Make.com backup FAILED",
  "blocks": [
    {
      "type": "header",
      "text": {
        "type": "plain_text",
        "text": "❌ [WORKFLOW: Make.com Backup] FAILED"
      }
    },
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "*Error Details:*\n• Failed Node: {{node_name}}\n• Error Message: {{error_message}}\n• Timestamp: {{timestamp}}"
      }
    },
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "*Troubleshooting:*\n• Execution ID: {{execution_id}}\n• Check logs: {{n8n_execution_url}}\n• Contact: DevOps team"
      }
    }
  ]
}
```

---

## n8n Workflow Design

### Node Diagram

```
[Cron Trigger: Daily 2AM CST]
    │
    ▼
[Set: Initialize Execution Context]
    │
    ▼
[HTTP: Read Backup State from GitHub] (GET backup-state.json)
    │ (Continue on 404)
    ▼
[Function: Parse Backup State] (Decode base64, parse JSON, handle missing)
    │
    ▼
[HTTP: Fetch All Scenarios from Make.com] (GET /scenarios with pagination)
    │
    ▼
[Function: Filter Changed Scenarios] (Compare lastEditedDate vs backup state)
    │
    ▼
[IF: Any Changed Scenarios?]
    │
    ├─ NO ─> [Function: Prepare Summary (No Changes)]
    │            │
    │            └─> [Jump to Slack Notification]
    │
    └─ YES ─> [Split In Batches: Process Scenarios] (batch size: 1)
                  │
                  ▼
              [HTTP: Download Blueprint] (GET /scenarios/{id}/blueprint)
                  │ (Continue on fail)
                  ▼
              [HTTP: Check Existing File in GitHub] (GET /contents/scenarios/{id}.json)
                  │ (Continue on 404)
                  ▼
              [Function: Prepare Commit Data] (Base64 encode, format message, extract SHA)
                  │
                  ▼
              [HTTP: Commit Scenario to GitHub] (PUT /contents/scenarios/{id}.json)
                  │ (Continue on fail)
                  ▼
              [Loop back to Split In Batches until complete]
                  │
                  ▼
              [Function: Update Backup State] (Merge new timestamps)
                  │
                  ▼
              [Function: Prepare State Commit] (Base64 encode state)
                  │
                  ▼
              [HTTP: Get Current State SHA] (GET /contents/backup-state.json)
                  │
                  ▼
              [HTTP: Commit Backup State] (PUT /contents/backup-state.json)
                  │
                  ▼
              [Function: Aggregate Results] (Count successes, failures, skipped)
                  │
                  ▼
              [Function: Format Slack Message] (Success format per spec)
                  │
                  ▼
              [Slack: Send Notification] (POST /chat.postMessage to #n8n-automation)
                  │
                  ▼
              [Complete]

[Error Trigger: Catch All Errors]
    │
    ▼
[Function: Extract Error Details]
    │
    ▼
[Function: Format Error Message]
    │
    ▼
[Slack: Send Error Notification] (POST /chat.postMessage with ❌)
    │
    ▼
[Mark Execution as Failed]
```

---

### Node Configuration Details

#### Node 1: Cron Trigger
```json
{
  "id": "cron-trigger",
  "type": "n8n-nodes-base.cron",
  "name": "Daily 2AM CST Trigger",
  "parameters": {
    "rule": {
      "interval": [
        {
          "field": "cronExpression",
          "expression": "0 2 * * *"
        }
      ],
      "timezone": "America/Chicago"
    }
  },
  "position": [250, 300]
}
```

#### Node 2: Initialize Execution Context
```json
{
  "id": "init-context",
  "type": "n8n-nodes-base.set",
  "name": "Initialize Execution Context",
  "parameters": {
    "values": {
      "string": [
        {
          "name": "executionStartTime",
          "value": "={{ $now }}"
        },
        {
          "name": "workflowId",
          "value": "={{ $workflow.id }}"
        }
      ]
    }
  },
  "position": [450, 300]
}
```

#### Node 3: Read Backup State
```json
{
  "id": "read-state",
  "type": "n8n-nodes-base.httpRequest",
  "name": "Read Backup State from GitHub",
  "parameters": {
    "url": "https://api.github.com/repos/bautrey/make-scenarios-backup/contents/backup-state.json",
    "method": "GET",
    "authentication": "predefinedCredentialType",
    "nodeCredentialType": "githubApi",
    "options": {
      "response": {
        "response": {
          "fullResponse": false,
          "neverError": false
        }
      }
    }
  },
  "credentials": {
    "githubApi": {
      "id": "github-burke-cred-id",
      "name": "GitHub API (Burke)"
    }
  },
  "continueOnFail": true,
  "position": [650, 300]
}
```

#### Node 4: Parse Backup State
```json
{
  "id": "parse-state",
  "type": "n8n-nodes-base.function",
  "name": "Parse Backup State",
  "parameters": {
    "functionCode": "// Check if file exists (200 OK) or missing (404)\nconst statusCode = $input.all()[0]?.json?.statusCode || 200;\n\nlet backupState;\n\nif (statusCode === 404 || !$input.all()[0]?.json?.content) {\n  // No backup state exists yet - create empty state\n  backupState = {\n    metadata: {\n      version: '1.0',\n      lastUpdated: new Date().toISOString(),\n      totalScenarios: 0\n    },\n    lastBackup: {}\n  };\n} else {\n  // Decode base64 content and parse JSON\n  const base64Content = $input.all()[0].json.content;\n  const decodedContent = Buffer.from(base64Content, 'base64').toString('utf-8');\n  backupState = JSON.parse(decodedContent);\n}\n\nreturn {\n  json: {\n    backupState: backupState,\n    stateExists: statusCode !== 404\n  }\n};"
  },
  "position": [850, 300]
}
```

#### Node 5: Fetch All Scenarios
```json
{
  "id": "fetch-scenarios",
  "type": "n8n-nodes-base.httpRequest",
  "name": "Fetch All Scenarios from Make.com",
  "parameters": {
    "url": "https://us1.make.com/api/v2/scenarios?teamId=154819&limit=100",
    "method": "GET",
    "authentication": "predefinedCredentialType",
    "nodeCredentialType": "makeApi",
    "options": {
      "response": {
        "response": {
          "fullResponse": false,
          "neverError": false
        }
      },
      "retry": {
        "retry": {
          "maxRetries": 3,
          "waitBetweenRetries": 2000
        }
      }
    }
  },
  "credentials": {
    "makeApi": {
      "id": "make-api-cred-id",
      "name": "Make.com API"
    }
  },
  "position": [1050, 300]
}
```

**Note:** Handle pagination in Function node if total > 100

#### Node 6: Filter Changed Scenarios
```json
{
  "id": "filter-changed",
  "type": "n8n-nodes-base.function",
  "name": "Filter Changed Scenarios",
  "parameters": {
    "functionCode": "const scenarios = $input.all()[0].json.scenarios;\nconst backupState = $input.all()[1].json.backupState;\n\nconst changedScenarios = scenarios.filter(scenario => {\n  const scenarioId = scenario.id.toString();\n  const lastBackup = backupState.lastBackup[scenarioId];\n  \n  if (!lastBackup) {\n    // Scenario never backed up\n    return true;\n  }\n  \n  // Compare lastEditedDate\n  const scenarioEditDate = new Date(scenario.lastEdit);\n  const backupDate = new Date(lastBackup.lastEditedDate);\n  \n  return scenarioEditDate > backupDate;\n});\n\nreturn {\n  json: {\n    totalScenarios: scenarios.length,\n    changedScenarios: changedScenarios,\n    changedCount: changedScenarios.length,\n    skippedCount: scenarios.length - changedScenarios.length\n  }\n};"
  },
  "position": [1250, 300]
}
```

#### Node 7: Check If Any Changes
```json
{
  "id": "check-changes",
  "type": "n8n-nodes-base.if",
  "name": "Any Changed Scenarios?",
  "parameters": {
    "conditions": {
      "number": [
        {
          "value1": "={{ $json.changedCount }}",
          "operation": "larger",
          "value2": 0
        }
      ]
    }
  },
  "position": [1450, 300]
}
```

#### Node 8: Split In Batches
```json
{
  "id": "split-batches",
  "type": "n8n-nodes-base.splitInBatches",
  "name": "Process Scenarios Sequentially",
  "parameters": {
    "batchSize": 1,
    "options": {}
  },
  "position": [1650, 250]
}
```

#### Node 9: Download Blueprint
```json
{
  "id": "download-blueprint",
  "type": "n8n-nodes-base.httpRequest",
  "name": "Download Blueprint",
  "parameters": {
    "url": "=https://us1.make.com/api/v2/scenarios/{{ $json.id }}/blueprint",
    "method": "GET",
    "authentication": "predefinedCredentialType",
    "nodeCredentialType": "makeApi",
    "options": {
      "retry": {
        "retry": {
          "maxRetries": 3,
          "waitBetweenRetries": 2000
        }
      }
    }
  },
  "credentials": {
    "makeApi": {
      "id": "make-api-cred-id",
      "name": "Make.com API"
    }
  },
  "continueOnFail": true,
  "position": [1850, 250]
}
```

#### Node 10: Check Existing File
```json
{
  "id": "check-file",
  "type": "n8n-nodes-base.httpRequest",
  "name": "Check Existing File in GitHub",
  "parameters": {
    "url": "=https://api.github.com/repos/bautrey/make-scenarios-backup/contents/scenarios/{{ $json.id }}.json",
    "method": "GET",
    "authentication": "predefinedCredentialType",
    "nodeCredentialType": "githubApi"
  },
  "credentials": {
    "githubApi": {
      "id": "github-burke-cred-id",
      "name": "GitHub API (Burke)"
    }
  },
  "continueOnFail": true,
  "position": [2050, 250]
}
```

#### Node 11: Prepare Commit Data
```json
{
  "id": "prepare-commit",
  "type": "n8n-nodes-base.function",
  "name": "Prepare Commit Data",
  "parameters": {
    "functionCode": "const blueprint = $input.all()[0].json.response;\nconst existingFile = $input.all()[1].json;\nconst scenarioId = $json.id;\nconst scenarioName = $json.name;\n\n// Base64 encode blueprint\nconst blueprintJson = JSON.stringify(blueprint, null, 2);\nconst base64Content = Buffer.from(blueprintJson, 'utf-8').toString('base64');\n\n// Extract SHA if file exists\nconst sha = existingFile.statusCode !== 404 ? existingFile.sha : null;\n\n// Format commit message\nconst commitMessage = `Update scenario ${scenarioId}: ${scenarioName}`;\n\nreturn {\n  json: {\n    scenarioId: scenarioId,\n    scenarioName: scenarioName,\n    content: base64Content,\n    message: commitMessage,\n    sha: sha,\n    branch: 'main',\n    committer: {\n      name: 'Make.com Backup Bot',\n      email: 'bot@fortiumpartners.com'\n    }\n  }\n};"
  },
  "position": [2250, 250]
}
```

#### Node 12: Commit Scenario File
```json
{
  "id": "commit-scenario",
  "type": "n8n-nodes-base.httpRequest",
  "name": "Commit Scenario to GitHub",
  "parameters": {
    "url": "=https://api.github.com/repos/bautrey/make-scenarios-backup/contents/scenarios/{{ $json.scenarioId }}.json",
    "method": "PUT",
    "authentication": "predefinedCredentialType",
    "nodeCredentialType": "githubApi",
    "sendBody": true,
    "bodyParameters": {
      "parameters": [
        {
          "name": "message",
          "value": "={{ $json.message }}"
        },
        {
          "name": "content",
          "value": "={{ $json.content }}"
        },
        {
          "name": "sha",
          "value": "={{ $json.sha }}"
        },
        {
          "name": "branch",
          "value": "main"
        },
        {
          "name": "committer",
          "value": "={{ $json.committer }}"
        }
      ]
    },
    "options": {
      "retry": {
        "retry": {
          "maxRetries": 3,
          "waitBetweenRetries": 2000
        }
      }
    }
  },
  "credentials": {
    "githubApi": {
      "id": "github-burke-cred-id",
      "name": "GitHub API (Burke)"
    }
  },
  "continueOnFail": true,
  "position": [2450, 250]
}
```

**Note:** Loop back to "Split In Batches" node until all scenarios processed

#### Node 13: Update Backup State
```json
{
  "id": "update-state",
  "type": "n8n-nodes-base.function",
  "name": "Update Backup State",
  "parameters": {
    "functionCode": "const backupState = $input.all()[0].json.backupState;\nconst processedScenarios = $input.all().slice(1); // All processed scenarios\n\nconst now = new Date().toISOString();\n\n// Update backup state for each successfully committed scenario\nprocessedScenarios.forEach(item => {\n  const scenarioId = item.json.scenarioId.toString();\n  const githubResponse = item.json.commit || {};\n  \n  backupState.lastBackup[scenarioId] = {\n    scenarioId: item.json.scenarioId,\n    scenarioName: item.json.scenarioName,\n    lastEditedDate: item.json.lastEdit,\n    backedUpAt: now,\n    githubSha: githubResponse.sha || null\n  };\n});\n\n// Update metadata\nbackupState.metadata.lastUpdated = now;\nbackupState.metadata.totalScenarios = Object.keys(backupState.lastBackup).length;\nbackupState.metadata.workflowExecutionId = $execution.id;\n\nreturn {\n  json: {\n    backupState: backupState\n  }\n};"
  },
  "position": [2650, 250]
}
```

#### Node 14: Prepare State Commit
```json
{
  "id": "prepare-state-commit",
  "type": "n8n-nodes-base.function",
  "name": "Prepare State Commit",
  "parameters": {
    "functionCode": "const backupState = $json.backupState;\n\n// Base64 encode state\nconst stateJson = JSON.stringify(backupState, null, 2);\nconst base64Content = Buffer.from(stateJson, 'utf-8').toString('base64');\n\nreturn {\n  json: {\n    content: base64Content,\n    message: 'Update backup state',\n    branch: 'main',\n    committer: {\n      name: 'Make.com Backup Bot',\n      email: 'bot@fortiumpartners.com'\n    }\n  }\n};"
  },
  "position": [2850, 250]
}
```

#### Node 15: Get Current State SHA
```json
{
  "id": "get-state-sha",
  "type": "n8n-nodes-base.httpRequest",
  "name": "Get Current State SHA",
  "parameters": {
    "url": "https://api.github.com/repos/bautrey/make-scenarios-backup/contents/backup-state.json",
    "method": "GET",
    "authentication": "predefinedCredentialType",
    "nodeCredentialType": "githubApi"
  },
  "credentials": {
    "githubApi": {
      "id": "github-burke-cred-id",
      "name": "GitHub API (Burke)"
    }
  },
  "continueOnFail": true,
  "position": [3050, 250]
}
```

#### Node 16: Commit Backup State
```json
{
  "id": "commit-state",
  "type": "n8n-nodes-base.httpRequest",
  "name": "Commit Backup State",
  "parameters": {
    "url": "https://api.github.com/repos/bautrey/make-scenarios-backup/contents/backup-state.json",
    "method": "PUT",
    "authentication": "predefinedCredentialType",
    "nodeCredentialType": "githubApi",
    "sendBody": true,
    "bodyParameters": {
      "parameters": [
        {
          "name": "message",
          "value": "={{ $json.message }}"
        },
        {
          "name": "content",
          "value": "={{ $json.content }}"
        },
        {
          "name": "sha",
          "value": "={{ $input.all()[1].json.sha }}"
        },
        {
          "name": "branch",
          "value": "main"
        }
      ]
    }
  },
  "credentials": {
    "githubApi": {
      "id": "github-burke-cred-id",
      "name": "GitHub API (Burke)"
    }
  },
  "position": [3250, 250]
}
```

#### Node 17: Aggregate Results
```json
{
  "id": "aggregate-results",
  "type": "n8n-nodes-base.function",
  "name": "Aggregate Results",
  "parameters": {
    "functionCode": "const totalScenarios = $input.all()[0].json.totalScenarios;\nconst changedCount = $input.all()[0].json.changedCount;\nconst skippedCount = $input.all()[0].json.skippedCount;\nconst processedScenarios = $input.all().slice(1);\n\nlet successCount = 0;\nlet errorCount = 0;\nconst errors = [];\n\nprocessedScenarios.forEach(item => {\n  if (item.json.commit && item.json.commit.sha) {\n    successCount++;\n  } else {\n    errorCount++;\n    errors.push({\n      scenarioId: item.json.scenarioId,\n      scenarioName: item.json.scenarioName,\n      error: item.json.error || 'Unknown error'\n    });\n  }\n});\n\nconst executionStart = new Date($node['Initialize Execution Context'].json.executionStartTime);\nconst executionEnd = new Date();\nconst durationMs = executionEnd - executionStart;\nconst durationMin = Math.floor(durationMs / 60000);\nconst durationSec = Math.floor((durationMs % 60000) / 1000);\n\nreturn {\n  json: {\n    summary: {\n      total: totalScenarios,\n      changed: changedCount,\n      skipped: skippedCount,\n      backedUp: successCount,\n      errors: errorCount\n    },\n    execution: {\n      startTime: executionStart.toISOString(),\n      endTime: executionEnd.toISOString(),\n      duration: `${durationMin}m ${durationSec}s`\n    },\n    errors: errors,\n    processedScenarios: processedScenarios.map(s => ({\n      id: s.json.scenarioId,\n      name: s.json.scenarioName\n    }))\n  }\n};"
  },
  "position": [3450, 250]
}
```

#### Node 18: Format Slack Message
```json
{
  "id": "format-slack",
  "type": "n8n-nodes-base.function",
  "name": "Format Slack Message",
  "parameters": {
    "functionCode": "const summary = $json.summary;\nconst execution = $json.execution;\nconst errors = $json.errors;\nconst scenarios = $json.processedScenarios;\n\n// Format changed scenarios list\nconst scenariosList = scenarios.slice(0, 5).map(s => \n  `• Scenario ${s.id}: \"${s.name}\"`\n).join('\\n');\nconst moreCount = scenarios.length > 5 ? `\\n• ... (${scenarios.length - 5} more)` : '';\n\n// Success or warning emoji\nconst statusEmoji = errors.length > 0 ? '⚠️' : '✅';\nconst statusText = errors.length > 0 ? 'PARTIAL SUCCESS' : 'SUCCESS';\n\nconst message = {\n  channel: process.env.SLACK_CHANNEL_ID,\n  text: `Make.com backup ${statusText.toLowerCase()}`,\n  blocks: [\n    {\n      type: 'header',\n      text: {\n        type: 'plain_text',\n        text: `${statusEmoji} [WORKFLOW: Make.com Backup] ${statusText}`\n      }\n    },\n    {\n      type: 'section',\n      text: {\n        type: 'mrkdwn',\n        text: `*Context:* Periodic backup of Make.com scenarios to GitHub\\n*Timestamp:* ${execution.endTime}\\n*Duration:* ${execution.duration}`\n      }\n    },\n    {\n      type: 'section',\n      text: {\n        type: 'mrkdwn',\n        text: `*Summary:*\\n• Total scenarios: ${summary.total}\\n• Backed up: ${summary.backedUp} (updated since last run)\\n• Skipped: ${summary.skipped} (unchanged)\\n• Errors: ${summary.errors}`\n      }\n    },\n    {\n      type: 'section',\n      text: {\n        type: 'mrkdwn',\n        text: `*Details:*\\n• Repository: https://github.com/bautrey/make-scenarios-backup\\n• Backup state: Updated successfully`\n      }\n    }\n  ]\n};\n\nif (scenarios.length > 0) {\n  message.blocks.push({\n    type: 'section',\n    text: {\n      type: 'mrkdwn',\n      text: `*Changes:*\\n${scenariosList}${moreCount}`\n    }\n  });\n}\n\nif (errors.length > 0) {\n  const errorList = errors.map(e => \n    `• Scenario ${e.scenarioId}: ${e.error}`\n  ).join('\\n');\n  message.blocks.push({\n    type: 'section',\n    text: {\n      type: 'mrkdwn',\n      text: `*Errors:*\\n${errorList}`\n    }\n  });\n}\n\nreturn { json: message };"
  },
  "position": [3650, 250]
}
```

#### Node 19: Send Slack Notification
```json
{
  "id": "send-slack",
  "type": "n8n-nodes-base.slack",
  "name": "Send Slack Notification",
  "parameters": {
    "resource": "message",
    "operation": "post",
    "channel": "={{ $json.channel }}",
    "text": "={{ $json.text }}",
    "blocksUi": {
      "blocksValues": "={{ JSON.stringify($json.blocks) }}"
    }
  },
  "credentials": {
    "slackApi": {
      "id": "slack-bot-cred-id",
      "name": "Slack n8n Bot"
    }
  },
  "position": [3850, 250]
}
```

#### Node 20: Error Trigger
```json
{
  "id": "error-trigger",
  "type": "n8n-nodes-base.errorTrigger",
  "name": "Catch Workflow Errors",
  "parameters": {},
  "position": [2050, 500]
}
```

#### Node 21: Extract Error Details
```json
{
  "id": "extract-error",
  "type": "n8n-nodes-base.function",
  "name": "Extract Error Details",
  "parameters": {
    "functionCode": "const error = $input.all()[0].json;\n\nconst errorDetails = {\n  workflowName: 'Make.com → GitHub Backup',\n  executionId: $execution.id,\n  failedNode: error.node?.name || 'Unknown',\n  errorMessage: error.error?.message || 'Unknown error',\n  timestamp: new Date().toISOString(),\n  stackTrace: error.error?.stack || null\n};\n\nreturn { json: errorDetails };"
  },
  "position": [2250, 500]
}
```

#### Node 22: Format Error Message
```json
{
  "id": "format-error",
  "type": "n8n-nodes-base.function",
  "name": "Format Error Message",
  "parameters": {
    "functionCode": "const details = $json;\n\nconst message = {\n  channel: process.env.SLACK_CHANNEL_ID,\n  text: 'Make.com backup FAILED',\n  blocks: [\n    {\n      type: 'header',\n      text: {\n        type: 'plain_text',\n        text: '❌ [WORKFLOW: Make.com Backup] FAILED'\n      }\n    },\n    {\n      type: 'section',\n      text: {\n        type: 'mrkdwn',\n        text: `*Error Details:*\\n• Failed Node: ${details.failedNode}\\n• Error Message: ${details.errorMessage}\\n• Timestamp: ${details.timestamp}`\n      }\n    },\n    {\n      type: 'section',\n      text: {\n        type: 'mrkdwn',\n        text: `*Troubleshooting:*\\n• Execution ID: ${details.executionId}\\n• Check n8n execution logs\\n• Contact: DevOps team`\n      }\n    }\n  ]\n};\n\nreturn { json: message };"
  },
  "position": [2450, 500]
}
```

#### Node 23: Send Error Notification
```json
{
  "id": "send-error-slack",
  "type": "n8n-nodes-base.slack",
  "name": "Send Error Notification",
  "parameters": {
    "resource": "message",
    "operation": "post",
    "channel": "={{ $json.channel }}",
    "text": "={{ $json.text }}",
    "blocksUi": {
      "blocksValues": "={{ JSON.stringify($json.blocks) }}"
    }
  },
  "credentials": {
    "slackApi": {
      "id": "slack-bot-cred-id",
      "name": "Slack n8n Bot"
    }
  },
  "position": [2650, 500]
}
```

---

## Error Handling & Recovery

### Error Categories

#### 1. API Errors (Make.com, GitHub, Slack)

**Types:**
- 401 Unauthorized: Invalid credentials
- 403 Forbidden: Insufficient permissions
- 404 Not Found: Resource doesn't exist
- 409 Conflict: File SHA mismatch (GitHub)
- 422 Unprocessable Entity: Invalid data
- 429 Too Many Requests: Rate limit
- 500/502/503: Server errors

**Handling Strategy:**
```javascript
// Retry logic for API calls
{
  "retry": {
    "maxRetries": 3,
    "waitBetweenRetries": 2000, // 2 seconds
    "exponentialBackoff": true
  }
}

// Rate limit handling
if (response.statusCode === 429) {
  const retryAfter = response.headers['retry-after'];
  await sleep(retryAfter * 1000);
  retry();
}

// Credential errors (no retry)
if (response.statusCode === 401 || response.statusCode === 403) {
  sendErrorNotification('API credential issue - requires manual intervention');
  throw error; // Stop workflow
}
```

#### 2. Data Errors

**Types:**
- Invalid JSON in backup state
- Missing required fields in API responses
- Base64 encoding/decoding failures
- Date parsing errors

**Handling Strategy:**
```javascript
try {
  const backupState = JSON.parse(decodedContent);
} catch (error) {
  // Create new backup state
  backupState = {
    metadata: { version: '1.0', lastUpdated: new Date().toISOString(), totalScenarios: 0 },
    lastBackup: {}
  };
  logWarning('Backup state corrupted, created new state');
}
```

#### 3. Partial Failures

**Scenario:** Some scenarios fail to back up while others succeed

**Handling Strategy:**
```javascript
// Enable continueOnFail on batch processing nodes
{
  "continueOnFail": true
}

// Track failures
const failures = [];
processedScenarios.forEach(scenario => {
  if (!scenario.json.commit) {
    failures.push({
      id: scenario.json.scenarioId,
      name: scenario.json.scenarioName,
      error: scenario.json.error
    });
  }
});

// Report in Slack notification
if (failures.length > 0) {
  notificationEmoji = '⚠️';
  notificationStatus = 'PARTIAL SUCCESS';
  includeFailuresList(failures);
}
```

#### 4. Workflow Execution Errors

**Types:**
- Node configuration errors
- Missing environment variables
- Network connectivity issues
- n8n system errors

**Handling Strategy:**
- Error Trigger node catches all workflow errors
- Extract error details (node name, message, stack trace)
- Send error notification to Slack
- Mark execution as failed
- Manual intervention required

---

### Recovery Procedures

#### Recovery 1: Missing Backup State

**Problem:** `backup-state.json` file deleted or corrupted

**Detection:** 404 response from GitHub or JSON parse error

**Recovery:**
1. Workflow automatically creates empty backup state
2. All scenarios treated as "never backed up"
3. Full backup executed (all 289 scenarios)
4. New backup state created with current timestamps

**Impact:** One full backup cycle, then back to incremental

#### Recovery 2: GitHub File Conflicts

**Problem:** SHA mismatch when updating file (409 Conflict)

**Detection:** 409 response from GitHub PUT request

**Recovery:**
```javascript
if (response.statusCode === 409) {
  // Fetch latest SHA
  const latestFile = await fetchFileFromGitHub(path);
  const latestSha = latestFile.sha;

  // Retry commit with latest SHA
  retryCommit({ ...commitData, sha: latestSha });
}
```

#### Recovery 3: Rate Limit Exceeded

**Problem:** Too many API requests to Make.com or GitHub

**Detection:** 429 response with `Retry-After` header

**Recovery:**
```javascript
if (response.statusCode === 429) {
  const retryAfterSeconds = parseInt(response.headers['retry-after']) || 60;
  logWarning(`Rate limited, waiting ${retryAfterSeconds}s`);
  await sleep(retryAfterSeconds * 1000);
  // Retry automatically via node retry configuration
}
```

#### Recovery 4: Failed Workflow Execution

**Problem:** Workflow fails midway through execution

**Detection:** Error Trigger node activated

**Recovery:**
1. Error notification sent to Slack with details
2. Execution marked as failed in n8n logs
3. Next scheduled execution (2:00 AM) will retry
4. If multiple failures, manual investigation required

**Manual Steps:**
1. Check n8n execution logs for detailed error
2. Verify API credentials still valid
3. Check GitHub repository accessibility
4. Test API connectivity manually
5. Re-run workflow once issue resolved

#### Recovery 5: Incomplete Scenario Backup

**Problem:** Some scenarios backed up, others skipped due to failures

**Detection:** Slack notification shows errors > 0

**Recovery:**
1. Failed scenarios NOT updated in backup state
2. Next scheduled run will retry failed scenarios (appear as "changed")
3. Review error list in Slack notification
4. If persistent failures, investigate specific scenario issues

**Manual Steps:**
1. Identify failing scenario IDs from Slack
2. Test Make.com API for those specific scenarios
3. Check scenario blueprint validity
4. If scenario issue, skip manually or fix in Make.com

---

### Monitoring & Alerting

#### Alert Levels

**Level 1: INFO** (Slack notification, no action required)
- Successful execution with 0 errors
- X scenarios backed up, Y skipped
- Normal incremental backup behavior

**Level 2: WARNING** (Slack notification, review recommended)
- Partial success (some scenarios failed)
- Execution took longer than expected (>15 minutes)
- Rate limit encountered but handled

**Level 3: ERROR** (Slack notification, action required)
- Workflow execution failed
- All API calls failing
- Credential authentication failure
- Backup state corruption unrecoverable

#### Alert Response Times

| Alert Level | Response Time | Action Required |
|-------------|--------------|-----------------|
| INFO | None | Review weekly |
| WARNING | Within 24 hours | Investigate partial failures |
| ERROR | Within 1 hour | Immediate investigation |

---

## Testing Requirements

### Unit Tests

#### Test 1: Backup State Parsing
```javascript
// Test cases
describe('Parse Backup State', () => {
  test('Should parse valid backup state', () => {
    const validState = { metadata: {}, lastBackup: {} };
    expect(parseBackupState(validState)).toMatchObject(validState);
  });

  test('Should handle missing backup state (404)', () => {
    const result = parseBackupState(null, 404);
    expect(result.metadata.version).toBe('1.0');
    expect(result.lastBackup).toEqual({});
  });

  test('Should handle corrupted JSON', () => {
    const corruptedState = 'invalid json {{{';
    const result = parseBackupState(corruptedState);
    expect(result.metadata.version).toBe('1.0');
  });
});
```

#### Test 2: Scenario Filtering
```javascript
describe('Filter Changed Scenarios', () => {
  test('Should identify changed scenarios', () => {
    const scenarios = [
      { id: 1, lastEdit: '2025-11-03T10:00:00Z' },
      { id: 2, lastEdit: '2025-11-01T10:00:00Z' }
    ];
    const backupState = {
      lastBackup: {
        '1': { lastEditedDate: '2025-11-02T10:00:00Z' },
        '2': { lastEditedDate: '2025-11-02T10:00:00Z' }
      }
    };
    const changed = filterChangedScenarios(scenarios, backupState);
    expect(changed).toHaveLength(1);
    expect(changed[0].id).toBe(1);
  });

  test('Should return all scenarios if no backup state', () => {
    const scenarios = [{ id: 1 }, { id: 2 }];
    const backupState = { lastBackup: {} };
    const changed = filterChangedScenarios(scenarios, backupState);
    expect(changed).toHaveLength(2);
  });
});
```

#### Test 3: Base64 Encoding
```javascript
describe('Base64 Encoding', () => {
  test('Should encode blueprint correctly', () => {
    const blueprint = { name: 'Test Scenario', flow: [] };
    const encoded = encodeBlueprint(blueprint);
    expect(encoded).toMatch(/^[A-Za-z0-9+/=]+$/); // Valid base64
  });

  test('Should decode to original blueprint', () => {
    const blueprint = { name: 'Test Scenario', flow: [] };
    const encoded = encodeBlueprint(blueprint);
    const decoded = decodeBlueprint(encoded);
    expect(decoded).toEqual(blueprint);
  });
});
```

---

### Integration Tests

#### Test 4: Make.com API Integration
```bash
# Test scenario list retrieval
curl -H "Authorization: Token ${MAKE_API_KEY}" \
  "https://us1.make.com/api/v2/scenarios?teamId=154819&limit=10"

# Expected: 200 OK with scenario array
# Validate: Response contains "scenarios" array, "pg" object

# Test blueprint download
curl -H "Authorization: Token ${MAKE_API_KEY}" \
  "https://us1.make.com/api/v2/scenarios/{SCENARIO_ID}/blueprint"

# Expected: 200 OK with blueprint JSON
# Validate: Response contains "response" object with "flow" array
```

#### Test 5: GitHub API Integration
```bash
# Test repository access
curl -H "Authorization: Bearer ${GITHUB_PAT}" \
  "https://api.github.com/repos/bautrey/make-scenarios-backup"

# Expected: 200 OK with repository details

# Test file creation
echo "test content" | base64 > /tmp/content.txt
CONTENT=$(cat /tmp/content.txt)
curl -X PUT \
  -H "Authorization: Bearer ${GITHUB_PAT}" \
  -H "Content-Type: application/json" \
  -d "{\"message\":\"Test commit\",\"content\":\"${CONTENT}\"}" \
  "https://api.github.com/repos/bautrey/make-scenarios-backup/contents/test.txt"

# Expected: 201 Created with commit details

# Test file update (requires SHA)
curl -H "Authorization: Bearer ${GITHUB_PAT}" \
  "https://api.github.com/repos/bautrey/make-scenarios-backup/contents/test.txt"
# Extract SHA from response

# Update with SHA
curl -X PUT \
  -H "Authorization: Bearer ${GITHUB_PAT}" \
  -H "Content-Type: application/json" \
  -d "{\"message\":\"Update test\",\"content\":\"${CONTENT}\",\"sha\":\"${SHA}\"}" \
  "https://api.github.com/repos/bautrey/make-scenarios-backup/contents/test.txt"

# Expected: 200 OK with updated commit details
```

#### Test 6: Slack API Integration
```bash
# Test message posting
curl -X POST https://slack.com/api/chat.postMessage \
  -H "Authorization: Bearer ${SLACK_BOT_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"channel\": \"${SLACK_CHANNEL_ID}\",
    \"text\": \"Test notification from n8n workflow\",
    \"blocks\": [
      {
        \"type\": \"header\",
        \"text\": {
          \"type\": \"plain_text\",
          \"text\": \"✅ Test Notification\"
        }
      }
    ]
  }"

# Expected: 200 OK with "ok": true
# Validate: Message appears in #n8n-automation channel
```

---

### End-to-End Tests

#### Test 7: Initial Full Backup
**Preconditions:**
- No `backup-state.json` in repository
- All API credentials configured
- n8n workflow deployed

**Steps:**
1. Trigger workflow manually via webhook
2. Wait for execution to complete (monitor in n8n UI)
3. Verify Slack notification received
4. Check GitHub repository for scenario files
5. Verify `backup-state.json` created

**Expected Results:**
- All 289 scenarios backed up to `scenarios/` directory
- `backup-state.json` contains 289 entries
- Slack notification shows "289 backed up, 0 skipped, 0 errors"
- No error logs in n8n execution

#### Test 8: Incremental Backup (No Changes)
**Preconditions:**
- Test 7 completed successfully
- No scenarios modified in Make.com

**Steps:**
1. Trigger workflow manually
2. Wait for execution to complete
3. Verify Slack notification
4. Check GitHub commit history

**Expected Results:**
- Slack notification shows "0 backed up, 289 skipped, 0 errors"
- Only 1 new commit: update to `backup-state.json` (metadata only)
- Execution time <2 minutes (no blueprint downloads)

#### Test 9: Incremental Backup (With Changes)
**Preconditions:**
- Test 7 completed successfully
- 1 scenario manually modified in Make.com

**Steps:**
1. Edit a scenario in Make.com (change name or add module)
2. Note the scenario ID
3. Trigger workflow manually
4. Wait for execution to complete
5. Verify Slack notification
6. Check GitHub commit history

**Expected Results:**
- Slack notification shows "1 backed up, 288 skipped, 0 errors"
- 2 new commits: updated scenario file + updated backup state
- Changed scenario ID listed in Slack notification
- Scenario file in GitHub reflects new changes

#### Test 10: Error Handling
**Preconditions:**
- Test 7 completed successfully

**Steps:**
1. Temporarily invalidate Make.com API key in n8n credentials
2. Trigger workflow manually
3. Wait for execution to fail
4. Verify error notification in Slack
5. Check n8n execution log

**Expected Results:**
- Workflow execution marked as failed
- Slack error notification received with ❌ emoji
- Error message indicates "401 Unauthorized" from Make.com API
- n8n execution log contains detailed error stack trace
- Restore API key and next run succeeds

#### Test 11: Scheduled Execution
**Preconditions:**
- All previous tests passed
- Cron trigger enabled

**Steps:**
1. Wait for scheduled execution at 2:00 AM CST
2. Check Slack channel at 2:05 AM for notification
3. Verify GitHub commit timestamp
4. Review n8n execution history

**Expected Results:**
- Workflow executed automatically at 2:00 AM ±1 minute
- Slack notification received within 5 minutes
- GitHub commit timestamp matches 2:00 AM CST
- n8n shows successful scheduled execution

---

### Performance Tests

#### Test 12: Full Backup Execution Time
**Objective:** Measure time to back up all 289 scenarios

**Method:**
1. Delete `backup-state.json` from GitHub
2. Trigger workflow manually
3. Measure execution time from start to completion

**Success Criteria:**
- Execution completes in <15 minutes
- No timeouts or resource exhaustion
- All scenarios backed up successfully

#### Test 13: Incremental Backup Efficiency
**Objective:** Verify incremental backup only processes changed scenarios

**Method:**
1. Run full backup (Test 12)
2. Modify 10 scenarios in Make.com
3. Trigger workflow manually
4. Measure execution time and API calls

**Success Criteria:**
- Execution completes in <3 minutes
- Only 10 blueprint downloads (not 289)
- Backup state updated for 10 scenarios only

#### Test 14: Concurrent Execution Prevention
**Objective:** Ensure workflow cannot run concurrently

**Method:**
1. Trigger workflow manually
2. While workflow running, attempt second trigger
3. Observe n8n behavior

**Success Criteria:**
- n8n prevents second execution (queues or rejects)
- No data corruption in GitHub repository
- Both executions complete successfully in sequence

---

## Security Requirements

### Credential Management

#### Requirement 1: API Key Storage
**Requirement:** All API keys stored securely in n8n credential manager

**Implementation:**
- Make.com API Key: n8n credential type "Header Auth"
- GitHub PAT: n8n credential type "Header Auth"
- Slack Bot Token: n8n credential type "Slack OAuth2 API"
- All credentials encrypted at rest
- No credentials in workflow JSON or environment variables (only IDs)

**Validation:**
```bash
# Check workflow JSON does not contain plain credentials
grep -i "api.*key\|token\|password" workflows/make-backup-github.json
# Expected: No matches (only credential IDs)
```

#### Requirement 2: Credential Rotation
**Requirement:** Credentials rotated every 12 months

**Implementation:**
1. Set calendar reminder for credential expiration
2. Generate new API keys 1 week before expiration
3. Update n8n credentials (test in staging first)
4. Revoke old credentials after validation
5. Document rotation in changelog

**Rotation Procedure:**
```markdown
1. Generate new Make.com API key
2. Add new credential in n8n: "Make.com API (New)"
3. Update workflow to use new credential
4. Test workflow execution
5. If successful, delete old credential
6. Revoke old API key in Make.com
7. Repeat for GitHub PAT and Slack token
```

---

### Access Control

#### Requirement 3: Principle of Least Privilege
**Requirement:** API keys have minimum required permissions

**Implementation:**
- Make.com API: Read-only permissions (scenarios, blueprints)
- GitHub PAT: `repo` scope only (no org/admin permissions)
- Slack Bot: `chat:write` and `chat:write.public` only (no admin permissions)

**Validation:**
```bash
# Test Make.com API cannot create/delete scenarios
curl -X POST \
  -H "Authorization: Token ${MAKE_API_KEY}" \
  "https://us1.make.com/api/v2/scenarios"
# Expected: 403 Forbidden (insufficient permissions)

# Test GitHub PAT cannot access other repositories
curl -H "Authorization: Bearer ${GITHUB_PAT}" \
  "https://api.github.com/repos/other-user/other-repo"
# Expected: 404 Not Found (no access)
```

#### Requirement 4: Repository Visibility
**Requirement:** GitHub repository must be private

**Implementation:**
- Repository `bautrey/make-scenarios-backup` set to private
- Only Burke Autrey has access initially
- Future: Transfer to `fortiumpartners` org with team access

**Validation:**
```bash
# Check repository visibility
curl -H "Authorization: Bearer ${GITHUB_PAT}" \
  "https://api.github.com/repos/bautrey/make-scenarios-backup" | jq '.private'
# Expected: true
```

---

### Data Security

#### Requirement 5: Backup Data Sanitization
**Requirement:** Ensure scenario blueprints do not contain credentials

**Implementation:**
- Make.com API exports blueprints WITHOUT connection credentials
- Blueprints contain only workflow structure and configuration
- No manual sanitization required (Make.com handles this)

**Validation:**
1. Download sample blueprint from Make.com
2. Search for credential keywords: `password`, `api_key`, `token`, `secret`
3. Verify no sensitive data present

**Note:** If Make.com ever includes credentials in exports, add sanitization step before GitHub commit.

#### Requirement 6: Backup State Integrity
**Requirement:** Backup state file protected from unauthorized modification

**Implementation:**
- GitHub repository private (only authorized users can push)
- Backup state committed by bot with known email
- Git history provides audit trail of all changes

**Validation:**
```bash
# Check backup state commit history
git log --follow backup-state.json
# Verify all commits from "Make.com Backup Bot <bot@fortiumpartners.com>"
```

---

### Audit & Compliance

#### Requirement 7: Execution Logging
**Requirement:** All workflow executions logged with retention policy

**Implementation:**
- n8n execution retention: 30 days
- Binary data retention: 7 days
- Slack notifications archived indefinitely (Slack retention)
- GitHub commit history permanent

**Configuration:**
```javascript
// n8n settings.json
{
  "executions": {
    "saveDataOnSuccess": "all",
    "saveDataOnError": "all",
    "saveDataManualExecutions": true,
    "pruneData": true,
    "pruneDataMaxAge": 30 // days
  }
}
```

#### Requirement 8: Change Tracking
**Requirement:** All changes to workflow tracked and auditable

**Implementation:**
- Workflow JSON committed to git repository
- All changes via pull requests with review
- Commit messages follow conventional commit format
- Changelog maintained for major changes

**Git Workflow:**
```bash
# Create feature branch for workflow changes
git checkout -b feature/improve-error-handling

# Make changes to workflow JSON
# Test in n8n

# Commit with conventional commit message
git commit -m "feat(workflow): add retry logic for API failures"

# Push and create pull request
git push origin feature/improve-error-handling

# Review, approve, merge to main
```

---

## Performance Requirements

### Execution Time

#### Requirement 1: Full Backup Duration
**Target:** Complete backup of 289 scenarios in <15 minutes

**Calculation:**
```
289 scenarios × 3 API calls per scenario (list, blueprint, commit) = 867 API calls
Average API response time: 500ms
Total API time: 867 × 0.5s = 433.5s = 7.2 minutes
Processing overhead: ~2 minutes
Total: ~10 minutes (within 15-minute target)
```

**Optimization Strategies:**
- Sequential processing (batch size: 1) to avoid GitHub conflicts
- Retry logic with exponential backoff
- Skip unchanged scenarios (incremental backup)

#### Requirement 2: Incremental Backup Duration
**Target:** Incremental backup with no changes in <2 minutes

**Calculation:**
```
API calls: List scenarios (1 call) + Read backup state (1 call) + Update state (1 call) = 3 calls
Average API response time: 500ms
Total API time: 3 × 0.5s = 1.5s
Processing time: ~30s (filter scenarios, format messages)
Total: <2 minutes (well within target)
```

#### Requirement 3: Incremental Backup with Changes
**Target:** Backup 10 changed scenarios in <5 minutes

**Calculation:**
```
API calls: List scenarios (1) + 10 × (blueprint, commit) = 21 calls
Average API response time: 500ms
Total API time: 21 × 0.5s = 10.5s
Processing time: ~1 minute
Total: <2 minutes (well within 5-minute target)
```

---

### Resource Utilization

#### Requirement 4: n8n Memory Usage
**Target:** Workflow execution uses <500MB memory

**Implementation:**
- Process scenarios sequentially (batch size: 1)
- Do not load all blueprints into memory simultaneously
- Stream data through workflow nodes
- Clear large objects after processing

**Monitoring:**
```bash
# Check n8n container memory usage during execution
docker stats n8n-app --no-stream
```

#### Requirement 5: Network Bandwidth
**Target:** <100MB data transfer per full backup

**Calculation:**
```
Average blueprint size: 50KB
289 scenarios × 50KB = 14.45MB (Make.com downloads)
GitHub uploads: Similar size (~15MB)
Total: ~30MB (well within 100MB target)
```

---

### API Rate Limits

#### Make.com API Limits
- **Limit:** Unknown (not published)
- **Observed:** No rate limiting encountered in testing
- **Mitigation:** Retry logic with exponential backoff

#### GitHub API Limits
- **Limit:** 5,000 requests/hour for authenticated users
- **Usage:** Full backup = ~580 requests (289 scenarios × 2 = 578, plus state file)
- **Margin:** 5,000 - 580 = 4,420 requests remaining (89% margin)
- **Mitigation:** If rate limited, respect `Retry-After` header

#### Slack API Limits
- **Limit:** 1 message/second (Tier 1)
- **Usage:** 1 message per workflow execution
- **Margin:** No risk of rate limiting

---

### Scalability

#### Requirement 6: Support for Growing Scenario Count
**Current:** 289 scenarios
**Future:** Up to 500 scenarios

**Impact Analysis:**
```
500 scenarios × 3 API calls = 1,500 API calls
Estimated time: 500 × 0.5s × 3 = 750s = 12.5 minutes
Still within 15-minute target
```

**Mitigation:**
- If scenario count exceeds 500, implement parallel processing
- Use GitHub batch commit API for efficiency
- Consider moving to GitHub Actions for execution

---

## Monitoring & Observability

### Slack Notifications

#### Success Notification Format
```
✅ [WORKFLOW: Make.com Backup] SUCCESS

**Context:** Periodic backup of Make.com scenarios to GitHub
**Timestamp:** 2025-11-03 02:05:15 AM CST
**Duration:** 3m 42s

**Summary:**
• Total scenarios: 289
• Backed up: 12 (updated since last run)
• Skipped: 277 (unchanged)
• Errors: 0

**Details:**
• Repository: https://github.com/bautrey/make-scenarios-backup
• Latest commit: abc123de
• Backup state: Updated successfully

**Changes:**
• Scenario 123456: "Customer Onboarding"
• Scenario 789012: "Invoice Processing"
• ... (10 more)
```

#### Error Notification Format
```
❌ [WORKFLOW: Make.com Backup] FAILED

**Error Details:**
• Failed Node: Download Blueprint
• Error Message: 401 Unauthorized - Invalid API token
• Timestamp: 2025-11-03 02:01:30 AM CST

**Troubleshooting:**
• Execution ID: 12345
• Check n8n execution logs at http://localhost:5678/executions
• Verify Make.com API key is valid
• Contact: DevOps team
```

#### Warning Notification Format (Partial Success)
```
⚠️ [WORKFLOW: Make.com Backup] PARTIAL SUCCESS

**Context:** Periodic backup of Make.com scenarios to GitHub
**Timestamp:** 2025-11-03 02:07:45 AM CST
**Duration:** 4m 12s

**Summary:**
• Total scenarios: 289
• Backed up: 8 (updated since last run)
• Skipped: 277 (unchanged)
• Errors: 4

**Errors:**
• Scenario 111222: Failed to download blueprint (500 Server Error)
• Scenario 333444: Failed to commit to GitHub (409 Conflict)
• Scenario 555666: Failed to download blueprint (Timeout)
• Scenario 777888: Failed to commit to GitHub (422 Invalid Content)

**Details:**
• Repository: https://github.com/bautrey/make-scenarios-backup
• Backup state: Updated for successful scenarios only
• Failed scenarios will retry in next execution
```

---

### n8n Execution Logs

#### Log Retention
- **Successful executions:** 30 days
- **Failed executions:** 30 days
- **Binary data:** 7 days
- **Log level:** INFO (captures warnings and errors)

#### Key Metrics to Track
1. **Execution duration:** Track trend over time
2. **Scenario count:** Monitor for growth
3. **Error rate:** Alert if >5% failures
4. **API response times:** Detect degradation

#### Accessing Logs
```
n8n UI → Executions → Select workflow → View execution details
```

---

### GitHub Repository Monitoring

#### Commit History Analysis
```bash
# View recent commits
git log --oneline -20

# Count commits per day
git log --since="7 days ago" --oneline | wc -l

# View backup state changes
git log --follow -p backup-state.json | head -50
```

#### Repository Size Monitoring
```bash
# Check repository size
du -sh /path/to/make-scenarios-backup

# Expected growth: ~2MB per month
# Alert if growth >10MB per month (indicates issue)
```

---

### Observability Stack Integration (Optional)

**If integrating with `/Users/burke/obs/` logging stack:**

#### Promtail Configuration
```yaml
# Add to /Users/burke/obs/promtail-config.yml
scrape_configs:
  - job_name: n8n
    static_configs:
      - targets:
          - localhost
        labels:
          job: n8n
          container: n8n-app
          __path__: /var/log/n8n/*.log
```

#### Loki Queries
```logql
# All n8n workflow executions
{container="n8n-app"} |= "workflow" |= "execution"

# Failed executions only
{container="n8n-app"} |= "workflow" |= "failed"

# Make.com backup workflow specifically
{container="n8n-app"} |= "Make.com Backup"
```

#### Grafana Dashboard
```json
{
  "dashboard": {
    "title": "n8n Workflow Monitoring",
    "panels": [
      {
        "title": "Execution Success Rate",
        "targets": [
          {
            "expr": "rate({container=\"n8n-app\"} |= \"workflow\" |= \"success\"[5m])"
          }
        ]
      },
      {
        "title": "Execution Duration",
        "targets": [
          {
            "expr": "{container=\"n8n-app\"} |= \"Make.com Backup\" |= \"duration\" | json | line_format \"{{.duration}}\""
          }
        ]
      }
    ]
  }
}
```

**Note:** Observability stack integration is optional. Slack notifications provide sufficient monitoring for initial deployment.

---

## Deployment Procedures

### Pre-Deployment Checklist

#### Environment Setup
- [ ] n8n services running (`docker compose ps` shows healthy)
- [ ] GitHub repository created (`bautrey/make-scenarios-backup`)
- [ ] Slack channel created (`#n8n-automation`)
- [ ] Slack bot invited to channel
- [ ] All environment variables set in `.env`
- [ ] All API credentials obtained and tested

#### Credential Verification
```bash
# Test Make.com API
source .env
curl -H "Authorization: Token ${MAKE_API_KEY}" \
  "https://us1.make.com/api/v2/scenarios?teamId=154819&limit=1"
# Expected: 200 OK with scenario data

# Test GitHub API
curl -H "Authorization: Bearer ${GITHUB_PAT}" \
  "https://api.github.com/repos/bautrey/make-scenarios-backup"
# Expected: 200 OK with repository details

# Test Slack API
curl -X POST https://slack.com/api/chat.postMessage \
  -H "Authorization: Bearer ${SLACK_BOT_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{\"channel\":\"${SLACK_CHANNEL_ID}\",\"text\":\"Test message\"}"
# Expected: 200 OK with "ok": true
```

---

### Deployment Steps

#### Step 1: Create Workflow in n8n

**Option A: Via n8n UI**
1. Open n8n: `http://localhost:5678`
2. Navigate to "Workflows" → "Create New Workflow"
3. Import workflow JSON: `workflows/make-backup-github.json`
4. Configure credentials for each node
5. Save workflow (do not activate yet)

**Option B: Via n8n API**
```bash
# Deploy workflow via API
curl -X POST http://localhost:5678/api/v1/workflows \
  -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  -H "Content-Type: application/json" \
  -d @workflows/make-backup-github.json

# Response includes workflow ID
```

#### Step 2: Configure Credentials in n8n

1. **Make.com API Credential**
   - Type: "Header Auth"
   - Name: "Make.com API"
   - Header Name: `Authorization`
   - Header Value: `Token ${MAKE_API_KEY}`

2. **GitHub API Credential**
   - Type: "Header Auth"
   - Name: "GitHub API (Burke)"
   - Header Name: `Authorization`
   - Header Value: `Bearer ${GITHUB_PAT}`

3. **Slack API Credential**
   - Type: "Slack OAuth2 API"
   - Name: "Slack n8n Bot"
   - OAuth Token: `${SLACK_BOT_TOKEN}`

#### Step 3: Test Workflow Manually

```bash
# Trigger workflow manually via webhook
curl http://localhost:5678/webhook/make-backup

# Or via n8n UI: Click "Execute Workflow" button
```

**Validation:**
1. Check n8n execution log (should show "Success")
2. Verify Slack notification received
3. Check GitHub repository for scenario files
4. Verify `backup-state.json` created

#### Step 4: Activate Workflow

```bash
# Activate workflow via n8n UI
# Settings → Active: Toggle ON

# Or via API
curl -X PATCH http://localhost:5678/api/v1/workflows/{workflowId} \
  -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"active": true}'
```

**Validation:**
- Workflow status shows "Active" in n8n UI
- Cron trigger enabled (visible in workflow nodes)

#### Step 5: Monitor First Scheduled Execution

**Timeline:**
- **Day 0 (Deployment):** Workflow activated, manual test successful
- **Day 1 (2:00 AM):** First scheduled execution
- **Day 1 (2:05 AM):** Check Slack for notification
- **Day 1 (Morning):** Review execution log and GitHub commits

**Validation:**
```bash
# Check last execution time
curl http://localhost:5678/api/v1/executions?workflowId={id}&limit=1 \
  -H "X-N8N-API-KEY: ${N8N_API_KEY}" | jq '.[0].startedAt'

# Expected: Timestamp around 2:00 AM CST

# Check GitHub commit timestamp
git log -1 --format="%ai" -- backup-state.json

# Expected: Timestamp around 2:00 AM CST
```

---

### Rollback Procedures

#### Scenario 1: Workflow Errors in Production

**Steps:**
1. Deactivate workflow immediately
   ```bash
   curl -X PATCH http://localhost:5678/api/v1/workflows/{workflowId} \
     -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
     -d '{"active": false}'
   ```
2. Review error logs in n8n execution history
3. Identify root cause (API failure, logic error, credential issue)
4. Fix issue in workflow JSON
5. Test manually before reactivating
6. Reactivate workflow after validation

#### Scenario 2: Data Corruption in GitHub

**Steps:**
1. Identify corrupted files via GitHub UI or git log
2. Revert to previous commit
   ```bash
   git revert {commit_sha}
   git push origin main
   ```
3. Update backup state manually if needed
4. Continue monitoring next scheduled execution

#### Scenario 3: Complete Workflow Replacement

**Steps:**
1. Export current workflow JSON from n8n
2. Deactivate current workflow
3. Import new workflow JSON
4. Configure credentials
5. Test manually
6. Activate new workflow
7. Archive old workflow (do not delete immediately)

---

### Post-Deployment Monitoring

#### Week 1: Daily Monitoring
- [ ] Check Slack notifications daily
- [ ] Review n8n execution logs
- [ ] Verify GitHub commits
- [ ] Monitor execution duration trends

#### Week 2-4: Periodic Monitoring
- [ ] Review Slack notifications 3x per week
- [ ] Check for any errors or warnings
- [ ] Validate backup state accuracy
- [ ] Monitor GitHub repository size

#### Ongoing: Monthly Review
- [ ] Review execution success rate (target: >99%)
- [ ] Check average execution duration (alert if >2x normal)
- [ ] Validate incremental backup behavior
- [ ] Review and update documentation if needed

---

## Acceptance Criteria

### Launch Criteria (MVP)

✅ **All Prerequisites Complete**
- [ ] GitHub repository created and accessible
- [ ] All API credentials obtained and tested
- [ ] Slack channel created and bot invited
- [ ] n8n environment configured with credentials

✅ **Workflow Deployed**
- [ ] Workflow JSON created and validated
- [ ] All nodes configured correctly
- [ ] Credentials linked to workflow nodes
- [ ] Workflow imported into n8n

✅ **Initial Backup Successful**
- [ ] Manual workflow execution succeeds
- [ ] All 289 scenarios backed up to GitHub
- [ ] `backup-state.json` created with all entries
- [ ] Slack notification received with correct format

✅ **Error Handling Validated**
- [ ] Error trigger node catches failures
- [ ] Error notifications sent to Slack
- [ ] Workflow execution marked as failed in n8n
- [ ] Manual recovery procedures documented

---

### Production Readiness

✅ **Scheduled Execution Working**
- [ ] Workflow runs automatically at 2:00 AM CST
- [ ] First scheduled execution successful
- [ ] Slack notification received after scheduled run
- [ ] GitHub commit timestamp matches schedule

✅ **Incremental Backup Functional**
- [ ] Unchanged scenarios skipped correctly
- [ ] Changed scenarios detected and backed up
- [ ] Backup state updated accurately
- [ ] No unnecessary GitHub commits

✅ **Monitoring & Alerting**
- [ ] Success notifications include all required fields
- [ ] Error notifications provide actionable details
- [ ] Slack message format matches PRD specification
- [ ] Execution logs retained for 30 days

✅ **Documentation Complete**
- [ ] Workflow documentation created
- [ ] Runbook with troubleshooting guide
- [ ] API reference document
- [ ] README updated with workflow details

✅ **Performance Requirements Met**
- [ ] Full backup completes in <15 minutes
- [ ] Incremental backup (no changes) completes in <2 minutes
- [ ] Memory usage stays <500MB during execution
- [ ] No resource exhaustion or timeouts

✅ **Security Requirements Met**
- [ ] All credentials stored in n8n credential manager
- [ ] No credentials in workflow JSON or git repository
- [ ] GitHub repository is private
- [ ] API keys have minimum required permissions

✅ **7-Day Validation Period**
- [ ] 7 consecutive successful scheduled executions
- [ ] Zero manual interventions required
- [ ] All notifications received correctly
- [ ] No data integrity issues in GitHub

---

### Quality Gates

#### Quality Gate 1: Code Review
- [ ] Workflow JSON reviewed by peer
- [ ] All Function node code follows best practices
- [ ] Error handling implemented comprehensively
- [ ] No hardcoded values (all use environment variables)

#### Quality Gate 2: Testing
- [ ] All unit tests passing (backup state parsing, filtering, encoding)
- [ ] All integration tests passing (Make.com, GitHub, Slack APIs)
- [ ] All E2E tests passing (initial backup, incremental backup, error handling)
- [ ] Performance tests meet targets

#### Quality Gate 3: Security Review
- [ ] Credentials managed securely
- [ ] Principle of least privilege enforced
- [ ] No sensitive data in git repository
- [ ] Audit logging enabled

#### Quality Gate 4: Documentation
- [ ] Workflow documentation complete
- [ ] Runbook with troubleshooting procedures
- [ ] API reference with examples
- [ ] README updated

#### Quality Gate 5: Production Validation
- [ ] 7 consecutive successful executions
- [ ] Success rate >99%
- [ ] Average execution time within targets
- [ ] No escalated incidents

---

## Appendix

### Glossary

| Term | Definition |
|------|------------|
| **Blueprint** | Make.com scenario export in JSON format, contains workflow structure and configuration |
| **Backup State** | JSON file tracking last backup timestamp for each scenario to enable incremental backups |
| **Incremental Backup** | Backup strategy that only backs up changed scenarios, skipping unchanged ones |
| **Scenario** | A workflow/automation in Make.com (equivalent to n8n workflow) |
| **SHA** | Git commit hash or file hash, required by GitHub API to update existing files |
| **Cron Trigger** | n8n node that triggers workflow on a schedule (e.g., daily at 2:00 AM) |
| **Split In Batches** | n8n node that processes array items sequentially in configurable batch sizes |
| **Continue On Fail** | n8n node setting that allows workflow to continue even if node fails |

---

### Reference Links

**PRD:**
- Approved PRD: `/Users/burke/projects/n8n/docs/PRD/make-backup-github-prd-approved.md`

**API Documentation:**
- Make.com API: https://www.make.com/en/api-documentation
- GitHub REST API: https://docs.github.com/en/rest
- Slack API: https://api.slack.com/web

**n8n Documentation:**
- n8n Nodes: https://docs.n8n.io/integrations/builtin/
- n8n Workflow: https://docs.n8n.io/workflows/
- n8n Credentials: https://docs.n8n.io/credentials/

**Project Files:**
- Workflow JSON: `workflows/make-backup-github.json`
- Environment Config: `.env`
- Docker Compose: `docker-compose.yml`

---

### Contact Information

| Role | Contact | Responsibility |
|------|---------|----------------|
| **Product Owner** | Burke Autrey | PRD approval, requirements clarification |
| **Technical Lead** | AI-Mesh Tech Lead | TRD creation, architecture design |
| **Backend Developer** | AI-Mesh Backend Dev | Workflow implementation |
| **Test Runner** | AI-Mesh Test Runner | Test execution, validation |
| **DevOps** | Burke Autrey | Deployment, monitoring, incident response |

---

### Change Log

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-03 | Tech Lead | Initial TRD creation from approved PRD |

---

**End of Technical Requirements Document**

**Status:** 🔴 Ready for Implementation

**Next Steps:**
1. Review TRD with stakeholders
2. Approve TRD for implementation
3. Execute task list (Sprints 1-6)
4. Validate acceptance criteria
5. Deploy to production

**Estimated Implementation Time:** 17 hours across 6 sprints + 7-day validation period
