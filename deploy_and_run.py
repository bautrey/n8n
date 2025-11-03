#!/usr/bin/env python3
"""Deploy and execute the Hello World workflow"""

import json
import os
import requests

# Get API key from environment
API_KEY = os.getenv('N8N_API_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkODMzOTQ0ZC1hZjc0LTQwMWYtODIwZC1mZTBhODYzNmJkZmEiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzYxOTQ3ODkyfQ.3Pdr_v8HXdfkGcSV2oZlVgnp3ToN5sxKjVoRWnDAXgk')
BASE_URL = 'http://localhost:5678/api/v1'
HEADERS = {
    'X-N8N-API-KEY': API_KEY,
    'Content-Type': 'application/json'
}

# Load workflow
with open('workflows/example-hello-world.json', 'r') as f:
    workflow_data = json.load(f)

print("Deploying Hello World workflow...")
response = requests.post(f'{BASE_URL}/workflows', json=workflow_data, headers=HEADERS)

if response.status_code in [200, 201]:
    workflow = response.json()
    workflow_id = workflow['id']
    print(f"✅ Workflow deployed successfully! ID: {workflow_id}")

    # Execute the workflow
    print(f"\nExecuting workflow {workflow_id}...")
    exec_response = requests.post(f'{BASE_URL}/workflows/{workflow_id}/execute', headers=HEADERS)

    if exec_response.status_code == 200:
        result = exec_response.json()
        print(f"✅ Workflow executed successfully!")
        print(f"\nExecution result:")
        print(json.dumps(result, indent=2))
    else:
        print(f"❌ Execution failed: {exec_response.status_code}")
        print(exec_response.text)
else:
    print(f"❌ Deployment failed: {response.status_code}")
    print(response.text)
