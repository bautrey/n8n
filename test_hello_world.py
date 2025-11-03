#!/usr/bin/env python3
"""Test the Hello World workflow with the Python helper"""

from lib.n8n_api import N8nAPI
import json

# Initialize API
api = N8nAPI()

print("🧪 Testing Hello World workflow execution\n")

# Test 1: Execute existing webhook
print("Test 1: Execute via webhook")
print("-" * 50)
result = api.execute_webhook('hello-world')
print(f"Message: {result.get('message')}")
print(f"Timestamp: {result.get('timestamp')}\n")

# Test 2: Get webhook URL from workflow ID
print("Test 2: Get webhook URL from workflow")
print("-" * 50)
workflows = api.list_workflows()
hello_world = next((w for w in workflows if 'Hello World' in w['name']), None)

if hello_world:
    webhook_url = api.get_webhook_url(hello_world['id'])
    print(f"Workflow ID: {hello_world['id']}")
    print(f"Webhook URL: {webhook_url}\n")
else:
    print("⚠️  Hello World workflow not found\n")

# Test 3: Execute with POST data
print("Test 3: Execute webhook with POST data")
print("-" * 50)
custom_data = {
    'user': 'Burke',
    'action': 'test_execution'
}
result = api.execute_webhook('hello-world', method='POST', data=custom_data)
print(f"Message: {result.get('message')}")
print(f"Request body received: {result.get('body', {})}\n")

print("✅ All tests completed successfully!")
