#!/usr/bin/env node

/**
 * Test Suite: Workflow Validation
 * Tests the Make.com → GitHub Backup workflow structure
 * TDD RED Phase: These tests should FAIL until implementation is complete
 */

const fs = require('fs');
const path = require('path');

const WORKFLOW_PATH = path.join(__dirname, '../workflows/make-backup-github.json');

// Color codes for test output
const RED = '\x1b[31m';
const GREEN = '\x1b[32m';
const RESET = '\x1b[0m';

let testResults = {
  passed: 0,
  failed: 0,
  tests: []
};

function test(description, fn) {
  try {
    fn();
    testResults.passed++;
    testResults.tests.push({ description, status: 'PASS' });
    console.log(`${GREEN}✓${RESET} ${description}`);
  } catch (error) {
    testResults.failed++;
    testResults.tests.push({ description, status: 'FAIL', error: error.message });
    console.log(`${RED}✗${RESET} ${description}`);
    console.log(`  ${RED}${error.message}${RESET}`);
  }
}

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

function assertEquals(actual, expected, message) {
  if (actual !== expected) {
    throw new Error(`${message}\n  Expected: ${expected}\n  Actual: ${actual}`);
  }
}

function assertExists(value, message) {
  if (value === undefined || value === null) {
    throw new Error(message);
  }
}

// Main test execution
console.log('\n=== Workflow Validation Tests ===\n');

// Test 2.1.1: Workflow file exists and has valid JSON structure
test('2.1.1: Workflow file exists', () => {
  assert(fs.existsSync(WORKFLOW_PATH), `Workflow file not found at ${WORKFLOW_PATH}`);
});

let workflow;
test('2.1.1: Workflow file contains valid JSON', () => {
  const content = fs.readFileSync(WORKFLOW_PATH, 'utf8');
  workflow = JSON.parse(content); // Will throw if invalid JSON
  assert(workflow !== null, 'Workflow is null');
});

test('2.1.1: Workflow has required name', () => {
  assertEquals(workflow.name, 'Make.com → GitHub Backup', 'Workflow name mismatch');
});

test('2.1.1: Workflow has nodes array', () => {
  assertExists(workflow.nodes, 'Workflow missing nodes array');
  assert(Array.isArray(workflow.nodes), 'nodes must be an array');
});

test('2.1.1: Workflow has connections object', () => {
  assertExists(workflow.connections, 'Workflow missing connections object');
  assert(typeof workflow.connections === 'object', 'connections must be an object');
});

test('2.1.1: Workflow has settings object', () => {
  assertExists(workflow.settings, 'Workflow missing settings object');
  assert(typeof workflow.settings === 'object', 'settings must be an object');
});

// Test 2.1.2: Cron Trigger node exists
test('2.1.2: Cron Trigger node exists', () => {
  const cronNode = workflow.nodes.find(n => n.name === 'Daily 2AM CST Trigger');
  assertExists(cronNode, 'Cron Trigger node not found');
  assertEquals(cronNode.type, 'n8n-nodes-base.cron', 'Cron node type mismatch');
});

test('2.1.2: Cron Trigger has correct schedule', () => {
  const cronNode = workflow.nodes.find(n => n.name === 'Daily 2AM CST Trigger');
  const cronExpression = cronNode.parameters.cronExpression;
  assertEquals(cronExpression, '0 2 * * *', 'Cron schedule mismatch');
});

test('2.1.2: Cron Trigger has correct timezone', () => {
  const cronNode = workflow.nodes.find(n => n.name === 'Daily 2AM CST Trigger');
  const timezone = cronNode.parameters.timezone || 'America/Chicago';
  assertEquals(timezone, 'America/Chicago', 'Timezone mismatch');
});

// Test 2.1.3: Execution metadata node exists
test('2.1.3: Execution metadata node exists', () => {
  const metadataNode = workflow.nodes.find(n => n.name === 'Initialize Execution Context');
  assertExists(metadataNode, 'Execution metadata node not found');
  assertEquals(metadataNode.type, 'n8n-nodes-base.set', 'Metadata node type mismatch');
});

// Test 2.2.1: Read Backup State node exists
test('2.2.1: Read Backup State node exists', () => {
  const node = workflow.nodes.find(n => n.name === 'Read Backup State');
  assertExists(node, 'Read Backup State node not found');
  assertEquals(node.type, 'n8n-nodes-base.httpRequest', 'Node type should be httpRequest');
});

test('2.2.1: Read Backup State uses correct GitHub URL', () => {
  const node = workflow.nodes.find(n => n.name === 'Read Backup State');
  const url = node.parameters.url;
  assert(url.includes('api.github.com'), 'URL should use GitHub API');
  assert(url.includes('bautrey/n8n'), 'URL should reference correct repo');
  assert(url.includes('backup-state.json'), 'URL should reference backup-state.json');
});

test('2.2.1: Read Backup State uses GET method', () => {
  const node = workflow.nodes.find(n => n.name === 'Read Backup State');
  const method = node.parameters.method || 'GET';
  assertEquals(method, 'GET', 'Should use GET method');
});

// Test 2.2.2: Parse Backup State node exists
test('2.2.2: Parse Backup State node exists', () => {
  const node = workflow.nodes.find(n => n.name === 'Parse Backup State');
  assertExists(node, 'Parse Backup State node not found');
  assertEquals(node.type, 'n8n-nodes-base.function', 'Node type should be function');
});

// Test 2.2.3: Update Backup State node exists
test('2.2.3: Update Backup State node exists', () => {
  const node = workflow.nodes.find(n => n.name === 'Update Backup State');
  assertExists(node, 'Update Backup State node not found');
  assertEquals(node.type, 'n8n-nodes-base.function', 'Node type should be function');
});

// Test 2.2.4: Commit Backup State node exists
test('2.2.4: Commit Backup State node exists', () => {
  const node = workflow.nodes.find(n => n.name === 'Commit Backup State');
  assertExists(node, 'Commit Backup State node not found');
  assertEquals(node.type, 'n8n-nodes-base.httpRequest', 'Node type should be httpRequest');
});

test('2.2.4: Commit Backup State uses PUT method', () => {
  const node = workflow.nodes.find(n => n.name === 'Commit Backup State');
  assertEquals(node.parameters.method, 'PUT', 'Should use PUT method');
});

// Test 2.3.1: Fetch All Scenarios node
test('2.3.1: Fetch All Scenarios node exists', () => {
  const node = workflow.nodes.find(n => n.name === 'Fetch All Scenarios');
  assertExists(node, 'Fetch All Scenarios node not found');
  assertEquals(node.type, 'n8n-nodes-base.httpRequest', 'Node type should be httpRequest');
});

test('2.3.1: Fetch All Scenarios uses Make.com API', () => {
  const node = workflow.nodes.find(n => n.name === 'Fetch All Scenarios');
  const url = node.parameters.url;
  assert(url.includes('make.com/api/v2/scenarios'), 'URL should use Make.com API scenarios endpoint');
  assert(url.includes('teamId=154819'), 'URL should include correct team ID');
});

// Test 2.3.2: Filter Changed Scenarios node
test('2.3.2: Filter Changed Scenarios node exists', () => {
  const node = workflow.nodes.find(n => n.name === 'Filter Changed Scenarios');
  assertExists(node, 'Filter Changed Scenarios node not found');
  assertEquals(node.type, 'n8n-nodes-base.function', 'Node type should be function');
});

// Test 2.3.3: Split Scenarios node
test('2.3.3: Split Scenarios node exists', () => {
  const node = workflow.nodes.find(n => n.name === 'Split Scenarios');
  assertExists(node, 'Split Scenarios node not found');
  assertEquals(node.type, 'n8n-nodes-base.splitInBatches', 'Node type should be splitInBatches');
});

test('2.3.3: Split Scenarios uses batch size of 1', () => {
  const node = workflow.nodes.find(n => n.name === 'Split Scenarios');
  const batchSize = node.parameters.batchSize;
  assertEquals(batchSize, 1, 'Batch size should be 1 for sequential processing');
});

// Test 2.3.4: Download Blueprint node
test('2.3.4: Download Blueprint node exists', () => {
  const node = workflow.nodes.find(n => n.name === 'Download Blueprint');
  assertExists(node, 'Download Blueprint node not found');
  assertEquals(node.type, 'n8n-nodes-base.httpRequest', 'Node type should be httpRequest');
});

test('2.3.4: Download Blueprint uses blueprint API endpoint', () => {
  const node = workflow.nodes.find(n => n.name === 'Download Blueprint');
  const url = node.parameters.url;
  assert(url.includes('blueprint'), 'URL should include blueprint endpoint');
});

// Test 2.4.1: Check Existing File node
test('2.4.1: Check Existing File node exists', () => {
  const node = workflow.nodes.find(n => n.name === 'Check Existing File');
  assertExists(node, 'Check Existing File node not found');
  assertEquals(node.type, 'n8n-nodes-base.httpRequest', 'Node type should be httpRequest');
});

test('2.4.1: Check Existing File uses GitHub scenarios path', () => {
  const node = workflow.nodes.find(n => n.name === 'Check Existing File');
  const url = node.parameters.url;
  assert(url.includes('api.github.com'), 'URL should use GitHub API');
  assert(url.includes('scenarios'), 'URL should reference scenarios directory');
});

test('2.4.1: Check Existing File continues on fail', () => {
  const node = workflow.nodes.find(n => n.name === 'Check Existing File');
  assert(node.continueOnFail === true, 'Should continue on fail for 404 handling');
});

// Test 2.4.2: Prepare Commit Data node
test('2.4.2: Prepare Commit Data node exists', () => {
  const node = workflow.nodes.find(n => n.name === 'Prepare Commit Data');
  assertExists(node, 'Prepare Commit Data node not found');
  assertEquals(node.type, 'n8n-nodes-base.function', 'Node type should be function');
});

// Test 2.4.3: Commit Scenario File node
test('2.4.3: Commit Scenario File node exists', () => {
  const node = workflow.nodes.find(n => n.name === 'Commit Scenario File');
  assertExists(node, 'Commit Scenario File node not found');
  assertEquals(node.type, 'n8n-nodes-base.httpRequest', 'Node type should be httpRequest');
});

test('2.4.3: Commit Scenario File uses PUT method', () => {
  const node = workflow.nodes.find(n => n.name === 'Commit Scenario File');
  assertEquals(node.parameters.method, 'PUT', 'Should use PUT method');
});

// Test 2.5.1: Aggregate Results node
test('2.5.1: Aggregate Results node exists', () => {
  const node = workflow.nodes.find(n => n.name === 'Aggregate Results');
  assertExists(node, 'Aggregate Results node not found');
  assertEquals(node.type, 'n8n-nodes-base.function', 'Node type should be function');
});

// Test 2.5.2: Format Slack Message node
test('2.5.2: Format Slack Message node exists', () => {
  const node = workflow.nodes.find(n => n.name === 'Format Slack Message');
  assertExists(node, 'Format Slack Message node not found');
  assertEquals(node.type, 'n8n-nodes-base.function', 'Node type should be function');
});

// Test 2.5.3: Send Slack Notification node
test('2.5.3: Send Slack Notification node exists', () => {
  const node = workflow.nodes.find(n => n.name === 'Send Slack Notification');
  assertExists(node, 'Send Slack Notification node not found');
  assertEquals(node.type, 'n8n-nodes-base.slack', 'Node type should be slack');
});

// Summary
console.log('\n=== Test Results ===');
console.log(`Total: ${testResults.passed + testResults.failed}`);
console.log(`${GREEN}Passed: ${testResults.passed}${RESET}`);
console.log(`${RED}Failed: ${testResults.failed}${RESET}`);

if (testResults.failed > 0) {
  console.log('\nFailed Tests:');
  testResults.tests
    .filter(t => t.status === 'FAIL')
    .forEach(t => console.log(`  - ${t.description}`));
  process.exit(1);
}

console.log(`\n${GREEN}All tests passed!${RESET}\n`);
process.exit(0);
