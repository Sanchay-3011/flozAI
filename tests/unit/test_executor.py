"""
Unit tests for the workflow executor and the execute API route
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from flozai.api.routes import app
from flozai.core.executor import WorkflowExecutor

client = TestClient(app)

def test_workflow_executor_builtins():
    """Test executing a workflow with built-in integrations that require no credentials."""
    workflow = {
        "name": "Test Builtins Workflow",
        "steps": [
            {
                "type": "TRIGGER",
                "integration": "scheduler",
                "action": "scheduled_time",
                "params": {"schedule": "0 0 * * *"}
            },
            {
                "type": "ACTION",
                "integration": "weather",
                "action": "get_weather",
                "params": {"location": "London"}
            }
        ]
    }

    # Execute directly via WorkflowExecutor
    executor = WorkflowExecutor(user_id="test_user")
    result = executor.execute(workflow)

    assert result["status"] == "completed"
    assert len(result["steps"]) == 2
    
    # Trigger step assertion
    assert result["steps"][0]["integration"] == "scheduler"
    assert result["steps"][0]["status"] == "success"

    # Action step assertion
    assert result["steps"][1]["integration"] == "weather"
    assert result["steps"][1]["status"] == "success"
    assert "temperature" in result["steps"][1]["result"]


def test_execute_api_route():
    """Test calling the POST /api/execute route."""
    workflow = {
        "name": "API Route Test Workflow",
        "steps": [
            {
                "type": "TRIGGER",
                "integration": "scheduler",
                "action": "scheduled_time",
                "params": {"schedule": "0 0 * * *"}
            },
            {
                "type": "ACTION",
                "integration": "weather",
                "action": "get_weather",
                "params": {"location": "London"}
            }
        ]
    }

    # Bypassing Supabase authentication dependencies for routing
    headers = {"Authorization": "Bearer mock-token"}
    with patch("flozai.services.auth_service.AuthService.get_current_user") as mock_get_user:
        mock_get_user.return_value = {
            "user": {
                "id": "test_user_id",
                "email": "test@example.com"
            }
        }
        
        response = client.post("/api/execute", json=workflow, headers=headers)
        assert response.status_code == 200
        
        result = response.json()
        assert result["status"] == "completed"
        assert len(result["steps"]) == 2
        assert result["steps"][0]["integration"] == "scheduler"
        assert result["steps"][1]["integration"] == "weather"
