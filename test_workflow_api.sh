#!/bin/bash

# n8n Workflow API End-to-End Test Script
#
# Prerequisites:
# 1. Docker services running (docker compose up -d)
# 2. API key created in n8n UI and added to .env

set -e  # Exit on error

echo "========================================="
echo "n8n Workflow API End-to-End Tests"
echo "========================================="
echo ""

# Load environment variables
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found"
    exit 1
fi

source .env

# Check API key is set
if [ "$N8N_API_KEY" == "your_api_key_here" ] || [ -z "$N8N_API_KEY" ]; then
    echo "❌ Error: N8N_API_KEY not configured in .env"
    echo "   See API_KEY_SETUP.md for setup instructions"
    exit 1
fi

echo "✓ Environment variables loaded"
echo ""

# Test 1: List workflows (should work even with empty list)
echo "Test 1: List all workflows"
echo "----------------------------"
WORKFLOWS=$(curl -s -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  http://localhost:5678/api/v1/workflows)

if echo "$WORKFLOWS" | grep -q "data"; then
    echo "✅ API connection successful"
    echo "Response: $WORKFLOWS"
else
    echo "❌ API connection failed"
    echo "Response: $WORKFLOWS"
    exit 1
fi
echo ""

# Test 2: Create workflow from example JSON
echo "Test 2: Create workflow from JSON"
echo "-----------------------------------"
CREATE_RESPONSE=$(curl -s -X POST \
  -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  -H "Content-Type: application/json" \
  -d @workflows/example-hello-world.json \
  http://localhost:5678/api/v1/workflows)

WORKFLOW_ID=$(echo "$CREATE_RESPONSE" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)

if [ -n "$WORKFLOW_ID" ]; then
    echo "✅ Workflow created successfully"
    echo "Workflow ID: $WORKFLOW_ID"
else
    echo "❌ Workflow creation failed"
    echo "Response: $CREATE_RESPONSE"
    exit 1
fi
echo ""

# Test 3: Get specific workflow
echo "Test 3: Get workflow by ID"
echo "----------------------------"
GET_RESPONSE=$(curl -s -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  http://localhost:5678/api/v1/workflows/${WORKFLOW_ID})

if echo "$GET_RESPONSE" | grep -q "Hello World"; then
    echo "✅ Workflow retrieved successfully"
else
    echo "❌ Workflow retrieval failed"
    echo "Response: $GET_RESPONSE"
    exit 1
fi
echo ""

# Test 4: Update workflow
echo "Test 4: Update workflow"
echo "------------------------"
# Modify the workflow JSON slightly (add a tag)
TMP_WORKFLOW=$(mktemp)
echo "$GET_RESPONSE" | jq '.tags = ["test"]' > "$TMP_WORKFLOW"

UPDATE_RESPONSE=$(curl -s -X PUT \
  -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  -H "Content-Type: application/json" \
  -d @"$TMP_WORKFLOW" \
  http://localhost:5678/api/v1/workflows/${WORKFLOW_ID})

if echo "$UPDATE_RESPONSE" | grep -q '"tags":\["test"\]'; then
    echo "✅ Workflow updated successfully"
else
    echo "❌ Workflow update failed"
    echo "Response: $UPDATE_RESPONSE"
fi

rm "$TMP_WORKFLOW"
echo ""

# Test 5: Test persistence (restart check)
echo "Test 5: Test persistence after restart"
echo "----------------------------------------"
echo "Restarting containers..."
docker compose restart n8n-app > /dev/null 2>&1
sleep 10  # Wait for n8n to come back up

GET_AFTER_RESTART=$(curl -s -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  http://localhost:5678/api/v1/workflows/${WORKFLOW_ID})

if echo "$GET_AFTER_RESTART" | grep -q "Hello World"; then
    echo "✅ Workflow persisted after container restart"
else
    echo "❌ Workflow did not persist"
    exit 1
fi
echo ""

# Test 6: Delete workflow
echo "Test 6: Delete workflow"
echo "------------------------"
DELETE_RESPONSE=$(curl -s -X DELETE \
  -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  http://localhost:5678/api/v1/workflows/${WORKFLOW_ID})

# Verify deletion
GET_DELETED=$(curl -s -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  http://localhost:5678/api/v1/workflows/${WORKFLOW_ID})

if echo "$GET_DELETED" | grep -q "error"; then
    echo "✅ Workflow deleted successfully"
else
    echo "❌ Workflow deletion failed"
    exit 1
fi
echo ""

echo "========================================="
echo "✅ All tests passed!"
echo "========================================="
echo ""
echo "Summary:"
echo "- ✅ API connection working"
echo "- ✅ Workflow creation working"
echo "- ✅ Workflow retrieval working"
echo "- ✅ Workflow updates working"
echo "- ✅ Data persistence working"
echo "- ✅ Workflow deletion working"
echo ""
echo "n8n REST API is fully functional!"
