"""Test Workflow Validator"""
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from flozai.core.validator import WorkflowValidator
from flozai.schemas.workflow_schema import (
    WorkflowDefinition,
    WorkflowTrigger,
    WorkflowAction
)


def test_valid_workflow():
    """Test validation of a valid workflow"""
    print("🧪 Test 1: Valid Workflow")
    print("=" * 60)

    validator = WorkflowValidator()

    workflow = WorkflowDefinition(
        name="Test Workflow",
        description="A valid test workflow",
        trigger=WorkflowTrigger(
            type="form_submission",
            integration="google_forms",
            params={"form_id": "abc123"}
        ),
        actions=[
            WorkflowAction(
                type="send_email",
                integration="gmail",
                params={
                    "to": "test@example.com",
                    "subject": "Test",
                    "body": "Test email"
                }
            )
        ]
    )

    is_valid, errors = validator.validate(workflow)

    print(f"Valid: {is_valid}")
    print(f"Errors: {errors}")
    assert is_valid, f"Should be valid but got errors: {errors}"
    print("✅ Passed\n")


def test_invalid_trigger_type():
    """Test validation catches invalid trigger type"""
    print("🧪 Test 2: Invalid Trigger Type (Hallucination)")
    print("=" * 60)

    validator = WorkflowValidator()

    workflow = WorkflowDefinition(
        name="Invalid Workflow",
        description="Workflow with hallucinated trigger",
        trigger=WorkflowTrigger(
            type="ai_generated_fake_trigger",  # HALLUCINATION
            integration="google_forms",
            params={}
        ),
        actions=[
            WorkflowAction(
                type="send_email",
                integration="gmail",
                params={
                    "to": "test@example.com",
                    "subject": "Test",
                    "body": "Test"
                }
            )
        ]
    )

    is_valid, errors = validator.validate(workflow)

    print(f"Valid: {is_valid}")
    print(f"Errors: {errors}")
    assert not is_valid, "Should catch hallucinated trigger"
    assert any("Invalid trigger type" in e for e in errors)
    print("✅ Correctly caught hallucination\n")


def test_invalid_integration():
    """Test validation catches invalid integration"""
    print("🧪 Test 3: Invalid Integration")
    print("=" * 60)

    validator = WorkflowValidator()

    workflow = WorkflowDefinition(
        name="Invalid Workflow",
        description="Workflow with hallucinated integration",
        trigger=WorkflowTrigger(
            type="form_submission",
            integration="fake_integration",  # HALLUCINATION
            params={"form_id": "123"}
        ),
        actions=[
            WorkflowAction(
                type="send_email",
                integration="gmail",
                params={
                    "to": "test@example.com",
                    "subject": "Test",
                    "body": "Test"
                }
            )
        ]
    )

    is_valid, errors = validator.validate(workflow)

    print(f"Valid: {is_valid}")
    print(f"Errors: {errors}")
    assert not is_valid, "Should catch hallucinated integration"
    print("✅ Correctly caught hallucination\n")


def test_wrong_integration_for_action():
    """Test validation catches action-integration mismatch"""
    print("🧪 Test 4: Wrong Integration for Action")
    print("=" * 60)

    validator = WorkflowValidator()

    workflow = WorkflowDefinition(
        name="Mismatched Workflow",
        description="send_email with wrong integration",
        trigger=WorkflowTrigger(
            type="form_submission",
            integration="google_forms",
            params={"form_id": "123"}
        ),
        actions=[
            WorkflowAction(
                type="send_email",
                integration="slack",  # WRONG - should be gmail
                params={
                    "to": "test@example.com",
                    "subject": "Test",
                    "body": "Test"
                }
            )
        ]
    )

    is_valid, errors = validator.validate(workflow)

    print(f"Valid: {is_valid}")
    print(f"Errors: {errors}")
    assert not is_valid, "Should catch integration mismatch"
    print("✅ Correctly caught mismatch\n")


def test_missing_required_params():
    """Test validation catches missing required parameters"""
    print("🧪 Test 5: Missing Required Parameters")
    print("=" * 60)

    validator = WorkflowValidator()

    workflow = WorkflowDefinition(
        name="Incomplete Workflow",
        description="Missing required params",
        trigger=WorkflowTrigger(
            type="form_submission",
            integration="google_forms",
            params={}  # Missing form_id
        ),
        actions=[
            WorkflowAction(
                type="send_email",
                integration="gmail",
                params={}  # Missing to, subject, body
            )
        ]
    )

    is_valid, errors = validator.validate(workflow)

    print(f"Valid: {is_valid}")
    print(f"Errors: {errors}")
    assert not is_valid, "Should catch missing parameters"
    print("✅ Correctly caught missing params\n")


if __name__ == "__main__":
    try:
        test_valid_workflow()
        test_invalid_trigger_type()
        test_invalid_integration()
        test_wrong_integration_for_action()
        test_missing_required_params()

        print("=" * 60)
        print("🎉 All validator tests passed!")
        print("✅ Safety layer is working - will catch LLM hallucinations")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()