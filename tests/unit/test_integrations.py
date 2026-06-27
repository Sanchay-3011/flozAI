"""
Unit tests for integrations credentials manager and validation functions
"""
import pytest
from unittest.mock import patch, MagicMock
from flozai.core.integrations import (
    validate_api_key,
    save_integration,
    delete_integration,
    get_user_integrations
)

def test_validate_api_key_openai_test_key():
    """Test validation of OpenAI mock/test key without API calls."""
    is_valid, msg = validate_api_key("openai", "sk-test-123")
    assert is_valid
    assert "Test OpenAI key accepted" in msg

@patch("requests.get")
def test_validate_api_key_openai_valid(mock_get):
    """Test validation of OpenAI key with mock successful API response."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_get.return_value = mock_response

    is_valid, msg = validate_api_key("openai", "sk-real-key-123")
    assert is_valid
    assert "is valid" in msg
    mock_get.assert_called_once_with(
        "https://api.openai.com/v1/models",
        headers={"Authorization": "Bearer sk-real-key-123"},
        timeout=10
    )

@patch("requests.get")
def test_validate_api_key_openai_invalid(mock_get):
    """Test validation of OpenAI key with mock invalid credentials."""
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_get.return_value = mock_response

    is_valid, msg = validate_api_key("openai", "sk-invalid")
    assert not is_valid
    assert "Invalid OpenAI API key" in msg

@patch("requests.get")
def test_validate_api_key_stripe_valid(mock_get):
    """Test validation of Stripe API key with mock success."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_get.return_value = mock_response

    is_valid, msg = validate_api_key("stripe", "sk_live_123")
    assert is_valid
    assert "Stripe API key is valid" in msg
    mock_get.assert_called_once_with(
        "https://api.stripe.com/v1/balance",
        auth=("sk_live_123", ""),
        timeout=10
    )

def test_validate_api_key_no_validator():
    """Test that integrations without validators are accepted automatically."""
    is_valid, msg = validate_api_key("linkedin", "random_member_token")
    assert is_valid
    assert "Key accepted" in msg

def test_save_and_delete_local_integration():
    """Test saving and deleting integrations for non-UUID (local) user."""
    user_id = "test_local_user"
    integration_type = "openai"
    credential_data = {"apiKey": "sk-test-123"}

    # Save
    save_integration(integration_type, credential_data, user_id)
    
    # Retrieve
    user_ints = get_user_integrations(user_id)
    assert integration_type in user_ints
    assert user_ints[integration_type]["credential_data"] == credential_data
    assert user_ints[integration_type]["status"] == "connected"

    # Delete
    delete_integration(integration_type, user_id)
    
    # Retrieve again
    user_ints = get_user_integrations(user_id)
    assert integration_type not in user_ints

def test_save_invalid_api_key_raises_error():
    """Test that saving an integration with an invalid API key raises ValueError."""
    # Since we test with openai, mock OpenAI verification to fail
    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response
        
        with pytest.raises(ValueError, match="Invalid OpenAI API key"):
            save_integration("openai", {"apiKey": "sk-invalid"}, "test_user")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
