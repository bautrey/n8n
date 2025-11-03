"""
n8n REST API Helper Functions

Simple HTTP wrappers for n8n workflow management via REST API.
Provides create, update, get, list, and delete operations for workflows.

Usage:
    from lib.n8n_api import N8nAPI

    api = N8nAPI()
    api.create_workflow('workflows/my-workflow.json')
"""

import json
import os
import requests
from pathlib import Path
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()


class N8nAPI:
    """n8n REST API client for workflow management"""

    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        """
        Initialize n8n API client

        Args:
            base_url: n8n instance URL (defaults to http://localhost:5678)
            api_key: n8n API key (defaults to N8N_API_KEY from .env)
        """
        self.base_url = base_url or os.getenv('N8N_HOST', 'http://localhost:5678')
        self.api_key = api_key or os.getenv('N8N_API_KEY')

        if not self.api_key or self.api_key == 'your_api_key_here':
            raise ValueError(
                "N8N_API_KEY not set. Create API key in n8n UI at Settings > n8n API, "
                "then add it to .env file"
            )

        self.headers = {
            'X-N8N-API-KEY': self.api_key,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

    def create_workflow(self, json_file: str) -> Dict:
        """
        Create a new workflow from JSON file

        Args:
            json_file: Path to workflow JSON file

        Returns:
            Created workflow object with id

        Raises:
            requests.HTTPError: If API call fails
            FileNotFoundError: If JSON file doesn't exist
        """
        workflow_data = self._load_json_file(json_file)

        url = f"{self.base_url}/api/v1/workflows"
        response = requests.post(url, headers=self.headers, json=workflow_data)
        response.raise_for_status()

        result = response.json()
        print(f"✅ Created workflow: {result.get('name')} (ID: {result.get('id')})")
        return result

    def update_workflow(self, workflow_id: str, json_file: str) -> Dict:
        """
        Update an existing workflow from JSON file

        Args:
            workflow_id: ID of workflow to update
            json_file: Path to workflow JSON file

        Returns:
            Updated workflow object

        Raises:
            requests.HTTPError: If API call fails
            FileNotFoundError: If JSON file doesn't exist
        """
        workflow_data = self._load_json_file(json_file)

        url = f"{self.base_url}/api/v1/workflows/{workflow_id}"
        response = requests.put(url, headers=self.headers, json=workflow_data)
        response.raise_for_status()

        result = response.json()
        print(f"✅ Updated workflow: {result.get('name')} (ID: {workflow_id})")
        return result

    def get_workflow(self, workflow_id: str, save_to: Optional[str] = None) -> Dict:
        """
        Get a workflow by ID

        Args:
            workflow_id: ID of workflow to retrieve
            save_to: Optional path to save workflow JSON

        Returns:
            Workflow object

        Raises:
            requests.HTTPError: If API call fails
        """
        url = f"{self.base_url}/api/v1/workflows/{workflow_id}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()

        result = response.json()

        if save_to:
            self._save_json_file(save_to, result)
            print(f"✅ Retrieved and saved workflow to: {save_to}")
        else:
            print(f"✅ Retrieved workflow: {result.get('name')} (ID: {workflow_id})")

        return result

    def list_workflows(self, active_only: bool = False) -> List[Dict]:
        """
        List all workflows

        Args:
            active_only: If True, only return active workflows

        Returns:
            List of workflow objects

        Raises:
            requests.HTTPError: If API call fails
        """
        url = f"{self.base_url}/api/v1/workflows"
        if active_only:
            url += "?active=true"

        response = requests.get(url, headers=self.headers)
        response.raise_for_status()

        result = response.json()
        workflows = result.get('data', [])
        print(f"✅ Found {len(workflows)} workflow(s)")
        return workflows

    def delete_workflow(self, workflow_id: str) -> None:
        """
        Delete a workflow by ID

        Args:
            workflow_id: ID of workflow to delete

        Raises:
            requests.HTTPError: If API call fails
        """
        url = f"{self.base_url}/api/v1/workflows/{workflow_id}"
        response = requests.delete(url, headers=self.headers)
        response.raise_for_status()

        print(f"✅ Deleted workflow ID: {workflow_id}")

    def execute_workflow(self, workflow_id: str) -> Dict:
        """
        Execute a workflow by ID (DEPRECATED - use webhook trigger instead)

        NOTE: The /execute endpoint is not available in many n8n versions.
        For reliable workflow execution, use webhook triggers and execute_webhook().

        Args:
            workflow_id: ID of workflow to execute

        Returns:
            Execution result

        Raises:
            requests.HTTPError: If API call fails
        """
        url = f"{self.base_url}/api/v1/workflows/{workflow_id}/execute"
        response = requests.post(url, headers=self.headers, json={})
        response.raise_for_status()

        result = response.json()
        print(f"✅ Executed workflow ID: {workflow_id}")
        return result

    def activate_workflow(self, workflow_id: str) -> Dict:
        """
        Activate a workflow (enables automatic execution)

        Args:
            workflow_id: ID of workflow to activate

        Returns:
            Updated workflow object

        Raises:
            requests.HTTPError: If API call fails
        """
        url = f"{self.base_url}/api/v1/workflows/{workflow_id}/activate"
        response = requests.post(url, headers=self.headers)
        response.raise_for_status()

        result = response.json()
        print(f"✅ Activated workflow ID: {workflow_id}")
        return result

    def deactivate_workflow(self, workflow_id: str) -> Dict:
        """
        Deactivate a workflow

        Args:
            workflow_id: ID of workflow to deactivate

        Returns:
            Updated workflow object

        Raises:
            requests.HTTPError: If API call fails
        """
        url = f"{self.base_url}/api/v1/workflows/{workflow_id}/deactivate"
        response = requests.post(url, headers=self.headers)
        response.raise_for_status()

        result = response.json()
        print(f"✅ Deactivated workflow ID: {workflow_id}")
        return result

    def execute_webhook(self, webhook_path: str, method: str = 'GET', data: Optional[Dict] = None) -> Dict:
        """
        Execute a workflow via its webhook trigger (RECOMMENDED METHOD)

        This is the reliable way to execute workflows programmatically.
        The workflow must have a webhook trigger node.

        Args:
            webhook_path: Path portion of the webhook URL (e.g., 'hello-world')
            method: HTTP method (GET, POST, PUT, DELETE)
            data: Optional data to send to webhook (for POST/PUT)

        Returns:
            Workflow execution result

        Raises:
            requests.HTTPError: If webhook call fails
        """
        webhook_url = f"{self.base_url}/webhook/{webhook_path.lstrip('/')}"

        if method.upper() == 'GET':
            response = requests.get(webhook_url)
        elif method.upper() == 'POST':
            response = requests.post(webhook_url, json=data)
        elif method.upper() == 'PUT':
            response = requests.put(webhook_url, json=data)
        elif method.upper() == 'DELETE':
            response = requests.delete(webhook_url)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        response.raise_for_status()
        result = response.json()
        print(f"✅ Executed webhook: {webhook_path}")
        return result

    def get_webhook_url(self, workflow_id: str) -> Optional[str]:
        """
        Get the webhook URL for a workflow (if it has a webhook trigger)

        Args:
            workflow_id: ID of workflow

        Returns:
            Webhook URL string or None if no webhook trigger found

        Raises:
            requests.HTTPError: If API call fails
        """
        workflow = self.get_workflow(workflow_id)

        for node in workflow.get('nodes', []):
            if node['type'] == 'n8n-nodes-base.webhook':
                webhook_path = node['parameters'].get('path', '')
                return f"{self.base_url}/webhook/{webhook_path}"

        return None

    def deploy_and_execute(self, json_file: str, webhook_path: Optional[str] = None) -> Dict:
        """
        Convenience method: Deploy a workflow, activate it, and execute via webhook

        Args:
            json_file: Path to workflow JSON file
            webhook_path: Webhook path (auto-detected if not provided)

        Returns:
            Dict with workflow info and execution result

        Raises:
            ValueError: If workflow has no webhook trigger
            requests.HTTPError: If any API call fails
        """
        # Deploy workflow
        workflow = self.create_workflow(json_file)
        workflow_id = workflow['id']

        # Activate it
        self.activate_workflow(workflow_id)

        # Get webhook URL
        if webhook_path is None:
            webhook_url = self.get_webhook_url(workflow_id)
            if not webhook_url:
                raise ValueError("Workflow has no webhook trigger")
            webhook_path = webhook_url.split('/webhook/')[-1]

        # Execute via webhook
        result = self.execute_webhook(webhook_path)

        return {
            'workflow_id': workflow_id,
            'workflow_name': workflow['name'],
            'webhook_url': f"{self.base_url}/webhook/{webhook_path}",
            'execution_result': result
        }

    def _load_json_file(self, file_path: str) -> Dict:
        """Load JSON file and return as dictionary"""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Workflow JSON file not found: {file_path}")

        with open(path, 'r') as f:
            return json.load(f)

    def _save_json_file(self, file_path: str, data: Dict) -> None:
        """Save dictionary as JSON file"""
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'w') as f:
            json.dump(data, f, indent=2)


# Convenience functions for quick access
def create_workflow(json_file: str) -> Dict:
    """Create workflow from JSON file"""
    return N8nAPI().create_workflow(json_file)


def update_workflow(workflow_id: str, json_file: str) -> Dict:
    """Update workflow from JSON file"""
    return N8nAPI().update_workflow(workflow_id, json_file)


def get_workflow(workflow_id: str, save_to: Optional[str] = None) -> Dict:
    """Get workflow by ID"""
    return N8nAPI().get_workflow(workflow_id, save_to)


def list_workflows(active_only: bool = False) -> List[Dict]:
    """List all workflows"""
    return N8nAPI().list_workflows(active_only)


def delete_workflow(workflow_id: str) -> None:
    """Delete workflow by ID"""
    return N8nAPI().delete_workflow(workflow_id)


def execute_workflow(workflow_id: str) -> Dict:
    """Execute workflow by ID"""
    return N8nAPI().execute_workflow(workflow_id)
