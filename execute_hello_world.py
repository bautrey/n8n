#!/usr/bin/env python3
"""Execute the Hello World workflow"""

import json
import requests

API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkODMzOTQ0ZC1hZjc0LTQwMWYtODIwZC1mZTBhODYzNmJkZmEiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzYxOTQ3ODkyfQ.3Pdr_v8HXdfkGcSV2oZlVgnp3ToN5sxKjVoRWnDAXgk'
BASE_URL = 'http://localhost:5678/api/v1'
WORKFLOW_ID = 'GB7C1GfTk6UiGetm'
HEADERS = {
    'X-N8N-API-KEY': API_KEY,
    'Content-Type': 'application/json'
}

# Activate the workflow first
print("Activating workflow...")
activate_response = requests.patch(
    f'{BASE_URL}/workflows/{WORKFLOW_ID}',
    json={'active': True},
    headers=HEADERS
)

if activate_response.status_code == 200:
    print("✅ Workflow activated!")

    # Try to trigger it via webhook
    # First, let's check the webhook URL from the workflow
    workflow = requests.get(f'{BASE_URL}/workflows/{WORKFLOW_ID}', headers=HEADERS).json()

    print("\nWorkflow details:")
    print(f"  Name: {workflow['name']}")
    print(f"  Active: {workflow['active']}")

    # Since this is a manual trigger workflow, we need to test it differently
    # The workflow has a "Manual Trigger" node, which means it needs to be triggered via the UI
    # or via the test-webhook endpoint

    print("\n🎯 This is a manual trigger workflow.")
    print("To execute it, you need to:")
    print("1. Open http://localhost:5678 in your browser")
    print("2. Open the 'Hello World' workflow")
    print("3. Click the 'Execute Workflow' button")
    print("\nAlternatively, we can check the workflow structure to understand its output:")

    # Show the nodes
    print("\n📋 Workflow structure:")
    for node in workflow['nodes']:
        print(f"  - {node['name']} ({node['type']})")
        if node['type'] == 'n8n-nodes-base.set':
            print(f"    Output: {json.dumps(node['parameters'], indent=6)}")

else:
    print(f"❌ Activation failed: {activate_response.status_code}")
    print(activate_response.text)
