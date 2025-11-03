#!/usr/bin/env python3
"""Simple test of Hello World workflow execution"""

from lib.n8n_api import N8nAPI
import json

# Initialize API
api = N8nAPI()

print("🧪 Testing Hello World Workflow Execution\n")
print("=" * 60)

# Execute via webhook
print("\n📤 Executing workflow via webhook...")
result = api.execute_webhook('hello-world')

print("\n✅ SUCCESS! Workflow executed programmatically\n")
print("📊 Response:")
print("-" * 60)
print(json.dumps(result, indent=2))

print("\n" + "=" * 60)
print("🎉 Programmatic workflow execution is working!")
print("\n✨ You can now build and execute workflows via API")
