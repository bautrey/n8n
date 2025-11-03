#!/usr/bin/env python3
"""Deploy the webhook-based Hello World workflow"""

import json
import requests

API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkODMzOTQ0ZC1hZjc0LTQwMWYtODIwZC1mZTBhODYzNmJkZmEiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzYxOTQ3ODkyfQ.3Pdr_v8HXdfkGcSV2oZlVgnp3ToN5sxKjVoRWnDAXgk'
BASE_URL = 'http://localhost:5678/api/v1'
HEADERS = {
    'X-N8N-API-KEY': API_KEY,
    'Content-Type': 'application/json'
}

# Load the workflow
with open('workflows/example-hello-world.json', 'r') as f:
    workflow_data = json.load(f)

print("📤 Deploying webhook-based Hello World workflow...")
response = requests.post(f'{BASE_URL}/workflows', json=workflow_data, headers=HEADERS)

if response.status_code in [200, 201]:
    workflow = response.json()
    workflow_id = workflow['id']
    print(f"✅ Workflow deployed! ID: {workflow_id}")

    # Activate the workflow to get production webhook URL
    print(f"\n🔄 Activating workflow...")
    activate_response = requests.post(f'{BASE_URL}/workflows/{workflow_id}/activate', headers=HEADERS)

    if activate_response.status_code == 200:
        print(f"✅ Workflow activated!")

        # Get the webhook URL
        updated_workflow = requests.get(f'{BASE_URL}/workflows/{workflow_id}', headers=HEADERS).json()

        # Extract webhook path from the workflow
        webhook_path = None
        for node in updated_workflow['nodes']:
            if node['type'] == 'n8n-nodes-base.webhook':
                webhook_path = node['parameters'].get('path', 'hello-world')
                break

        webhook_url = f"http://localhost:5678/webhook/{webhook_path}"

        print(f"\n🎯 Webhook URL: {webhook_url}")
        print(f"\n🧪 Testing webhook execution...")

        # Execute via webhook
        test_response = requests.get(webhook_url)

        if test_response.status_code == 200:
            result = test_response.json()
            print(f"✅ SUCCESS! Workflow executed via webhook!")
            print(f"\n📊 Response:")
            print(json.dumps(result, indent=2))
        else:
            print(f"❌ Test failed: {test_response.status_code}")
            print(test_response.text)
    else:
        print(f"❌ Activation failed: {activate_response.status_code}")
        print(activate_response.text)
else:
    print(f"❌ Deployment failed: {response.status_code}")
    print(response.text)
