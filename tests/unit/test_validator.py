"""
Unit tests for the WorkflowValidator
"""
from flozai.schemas.workflow_schema import WorkflowDefinition
from flozai.core.validator import WorkflowValidator

def test_validator_weather_location_bypass():
    """Verify that get_weather action without a location parameter passes validation."""
    workflow_data = {
        "name": "Weather test workflow",
        "description": "Weather test description",
        "triggers": [
            {
                "type": "scheduled_time",
                "integration": "scheduler",
                "params": {"schedule": "0 10 * * *"}
            }
        ],
        "actions": [
            {
                "type": "get_weather",
                "integration": "weather",
                "params": {}  # location is missing, but should be bypassed as TEMPLATE_PARAMS
            }
        ]
    }
    
    workflow = WorkflowDefinition(**workflow_data)
    validator = WorkflowValidator()
    is_valid, errors = validator.validate(workflow)
    
    assert is_valid, f"Validation failed with errors: {errors}"
    assert len(errors) == 0

def test_validator_wait_duration_bypass():
    """Verify that wait action without a duration parameter passes validation."""
    workflow_data = {
        "name": "Wait test workflow",
        "description": "Wait test description",
        "triggers": [
            {
                "type": "manual",
                "integration": "scheduler",
                "params": {}
            }
        ],
        "actions": [
            {
                "type": "wait",
                "integration": "scheduler",
                "params": {}  # duration is missing, but should be bypassed as TEMPLATE_PARAMS
            }
        ]
    }
    
    workflow = WorkflowDefinition(**workflow_data)
    validator = WorkflowValidator()
    is_valid, errors = validator.validate(workflow)
    
    assert is_valid, f"Validation failed with errors: {errors}"
    assert len(errors) == 0

def test_validator_unsupported_action():
    """Verify that an unsupported action type fails validation."""
    workflow_data = {
        "name": "Invalid action workflow",
        "description": "Invalid action description",
        "triggers": [
            {
                "type": "manual",
                "integration": "scheduler",
                "params": {}
            }
        ],
        "actions": [
            {
                "type": "non_existent_action_type_123",
                "integration": "slack",
                "params": {}
            }
        ]
    }
    
    workflow = WorkflowDefinition(**workflow_data)
    validator = WorkflowValidator()
    is_valid, errors = validator.validate(workflow)
    
    assert not is_valid
    assert any("Unsupported action type" in e for e in errors)
