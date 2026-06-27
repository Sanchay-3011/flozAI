"""
Unit tests for Mock/Sandbox execution mode in action handlers and LLM providers
"""
import pytest
from unittest.mock import patch

from flozai.core.executor import WorkflowExecutor
from flozai.core.integrations import validate_api_key, save_integration, delete_integration, get_user_integrations
from flozai.core.llm.llm_factory import get_llm_client

def test_mock_api_key_validation():
    """Verify mock API keys pass validation immediately."""
    for provider in ["openai", "stripe", "perplexity", "notion", "airtable", "whatsapp"]:
        is_valid, msg = validate_api_key(provider, "mock_test_key")
        assert is_valid
        assert "key accepted" in msg.lower()

        is_valid, msg = validate_api_key(provider, "sk-test-abc")
        assert is_valid
        assert "key accepted" in msg.lower()

def test_mock_llm_providers():
    """Verify LLM providers return simulated responses if key is mock."""
    from flozai.core.llm.openai_provider import OpenAIProvider
    from flozai.core.llm.groq_provider import GroqProvider
    from flozai.core.llm.anthropic_provider import AnthropicProvider
    from flozai.core.llm.gemini_provider import GeminiProvider

    openai = OpenAIProvider(api_key="mock_key")
    res = openai._raw_chat("Sys", "User")
    assert "[Simulated Response from OpenAI" in res
    assert "Sys" in res
    assert "User" in res

    groq = GroqProvider(api_key="sk-test-123")
    res = groq._raw_chat("Sys", "User")
    assert "[Simulated Response from Groq" in res

    anthropic = AnthropicProvider(api_key="test_key")
    res = anthropic._raw_chat("Sys", "User")
    assert "[Simulated Response from Anthropic" in res

    gemini = GeminiProvider(api_key="mock-key")
    res = gemini._raw_chat("Sys", "User")
    assert "[Simulated Response from Gemini" in res

def test_workflow_executor_mock_credentials():
    """Verify executing workflow steps with mock credentials returns simulated payloads."""
    # Save mock credentials for tests
    user_id = "test_executor_mock_user"
    
    save_integration("slack", {"apiKey": "mock_slack_token"}, user_id)
    save_integration("hubspot", {"apiKey": "mock_hubspot_token"}, user_id)
    save_integration("salesforce", {"access_token": "mock_sf_token"}, user_id)
    save_integration("openai", {"apiKey": "sk-test-openai"}, user_id)
    save_integration("gmail", {"access_token": "mock_gmail_token"}, user_id)
    save_integration("airtable", {"apiKey": "mock_airtable_token"}, user_id)
    save_integration("notion", {"apiKey": "mock_notion_token"}, user_id)
    save_integration("stripe", {"apiKey": "mock_stripe_token"}, user_id)
    save_integration("whatsapp", {"apiKey": "mock_whatsapp_token", "phone_number_id": "12345"}, user_id)
    save_integration("linkedin", {"access_token": "mock_linkedin_token"}, user_id)
    save_integration("google_calendar", {"access_token": "mock_calendar_token"}, user_id)
    save_integration("google_sheets", {"access_token": "mock_sheets_token"}, user_id)

    # Compile workflow steps that cover all updated handlers
    workflow = {
        "name": "Full Mock Workflow",
        "steps": [
            {
                "type": "ACTION",
                "integration": "slack",
                "action": "send_message",
                "params": {"channel": "#general", "message": "Hi"}
            },
            {
                "type": "ACTION",
                "integration": "hubspot",
                "action": "create_record",
                "params": {"data": {"firstname": "Test"}}
            },
            {
                "type": "ACTION",
                "integration": "salesforce",
                "action": "create_record",
                "params": {"object_type": "Lead", "data": {"LastName": "Test"}}
            },
            {
                "type": "ACTION",
                "integration": "openai",
                "action": "generate_content",
                "params": {"prompt": "Write a poem"}
            },
            {
                "type": "ACTION",
                "integration": "gmail",
                "action": "send_email",
                "params": {"to": "recipient@example.com", "subject": "Test", "body": "Body"}
            },
            {
                "type": "ACTION",
                "integration": "airtable",
                "action": "create_record",
                "params": {"base_id": "app123", "table_name": "tbl123", "fields": {"Name": "Val"}}
            },
            {
                "type": "ACTION",
                "integration": "notion",
                "action": "create_page",
                "params": {"title": "Page title"}
            },
            {
                "type": "ACTION",
                "integration": "stripe",
                "action": "create_invoice",
                "params": {"customer": "cus_123"}
            },
            {
                "type": "ACTION",
                "integration": "whatsapp",
                "action": "send_message",
                "params": {"to": "123456", "message": "Hi"}
            },
            {
                "type": "ACTION",
                "integration": "linkedin",
                "action": "publish_post",
                "params": {"message": "Post content"}
            },
            {
                "type": "ACTION",
                "integration": "google_calendar",
                "action": "create_event",
                "params": {"start": "2026-06-17T12:00:00Z", "end": "2026-06-17T13:00:00Z", "summary": "Meeting"}
            },
            {
                "type": "ACTION",
                "integration": "google_sheets",
                "action": "add_row",
                "params": {"spreadsheet_id": "sheet123", "values": [["1", "2"]]}
            }
        ]
    }

    try:
        executor = WorkflowExecutor(user_id=user_id)
        result = executor.execute(workflow)

        assert result["status"] == "completed"
        assert len(result["steps"]) == len(workflow["steps"])

        # Check that simulated is True for all steps
        for step in result["steps"]:
            assert step["status"] == "success", f"Step {step['integration']} failed: {step['error']}"
            assert step["result"].get("simulated") is True, f"Step {step['integration']} was not simulated"

    finally:
        # Clean up saved integrations
        for provider in ["slack", "hubspot", "salesforce", "openai", "gmail", "airtable", "notion", "stripe", "whatsapp", "linkedin", "google_calendar", "google_sheets"]:
            delete_integration(provider, user_id)
