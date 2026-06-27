"""Test schema definitions"""
import pytest
from flozai.schemas.workflow_schema import WorkflowDefinition, WorkflowTrigger, WorkflowAction
from flozai.schemas.intent_schema import ParsedIntent, IntentStatus, ExtractedTrigger
from flozai.schemas.api_schemas import ParseIntentRequest


def test_workflow_schema_valid():
    """Test valid workflow creation"""
    workflow = WorkflowDefinition(
        name="Test Workflow",
        description="A test workflow",
        triggers=[
            WorkflowTrigger(
                type="form_submission",
                integration="google_forms",
                params={"form_id": "123"}
            )
        ],
        actions=[
            WorkflowAction(
                type="send_email",
                integration="gmail",
                params={"to": "test@example.com", "subject": "Test", "body": "Test"}
            )
        ]
    )
    assert workflow.name == "Test Workflow"
    assert workflow.validate_linear_structure()


def test_intent_schema_needs_clarification():
    """Test intent that needs clarification"""
    intent = ParsedIntent(
        status=IntentStatus.NEEDS_CLARIFICATION,
        original_text="Send an email when something happens",
        clarification_question="What should trigger this workflow?",
        missing_info=["trigger"]
    )
    assert intent.status == IntentStatus.NEEDS_CLARIFICATION
    assert "trigger" in intent.missing_info


def test_api_request_schema():
    """Test API request schema"""
    request = ParseIntentRequest(
        user_input="When form is submitted, send email"
    )
    assert request.user_input == "When form is submitted, send email"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
