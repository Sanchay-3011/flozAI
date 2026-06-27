"""Test Workflow Builder"""
import sys
from pathlib import Path
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from flozai.core.intent_parser import IntentParser
from flozai.core.workflow_builder import WorkflowBuilder
from flozai.schemas.intent_schema import IntentStatus


def test_end_to_end_workflow_creation():
    """Test complete flow: User input → Intent → Workflow JSON"""
    print("🧪 End-to-End Workflow Creation Test")
    print("=" * 60)

    # Initialize components
    parser = IntentParser()
    builder = WorkflowBuilder()

    # Test cases
    test_cases = [
        "When someone submits my contact form, send me an email",
        "When a new row is added to my spreadsheet, send a Slack message to #general",
        "Every day at 9 AM, send a WhatsApp message to +1234567890",
    ]

    for i, user_input in enumerate(test_cases, 1):
        print(f"\n📝 Test Case {i}: {user_input}")
        print("-" * 60)

        # Parse intent
        intent = parser.parse(user_input)
        print(f"✓ Intent Status: {intent.status}")

        # Build workflow
        workflow = builder.build(intent)

        if workflow:
            print(f"✓ Workflow Created: {workflow.name}")
            print(f"✓ Trigger: {workflow.trigger.type} ({workflow.trigger.integration})")
            print(f"✓ Actions: {len(workflow.actions)}")

            # Display full workflow JSON
            print(f"\n📄 Workflow JSON:")
            print(json.dumps(workflow.model_dump(), indent=2, default=str))
        else:
            print(f"⚠ No workflow created (Status: {intent.status})")
            if intent.clarification_question:
                print(f"  Question: {intent.clarification_question}")
            if intent.out_of_scope_reason:
                print(f"  Reason: {intent.out_of_scope_reason}")

        print()


def test_clarification_no_workflow():
    """Test that workflows are not created when clarification is needed"""
    print("\n🧪 Test: Clarification (Should NOT create workflow)")
    print("=" * 60)

    parser = IntentParser()
    builder = WorkflowBuilder()

    user_input = "Send a message"

    intent = parser.parse(user_input)
    workflow = builder.build(intent)

    print(f"User Input: {user_input}")
    print(f"Intent Status: {intent.status}")
    print(f"Workflow Created: {workflow is not None}")

    assert workflow is None, "Workflow should not be created for clarification requests"
    print("✅ Correctly returned None for clarification status")
    print()


def test_out_of_scope_no_workflow():
    """Test that workflows are not created for out-of-scope requests"""
    print("\n🧪 Test: Out of Scope (Should NOT create workflow)")
    print("=" * 60)

    parser = IntentParser()
    builder = WorkflowBuilder()

    user_input = "If urgent send email else send slack"

    intent = parser.parse(user_input)
    workflow = builder.build(intent)

    print(f"User Input: {user_input}")
    print(f"Intent Status: {intent.status}")
    print(f"Workflow Created: {workflow is not None}")

    assert workflow is None, "Workflow should not be created for out-of-scope requests"
    print("✅ Correctly returned None for out-of-scope status")
    print()


if __name__ == "__main__":
    try:
        test_end_to_end_workflow_creation()
        test_clarification_no_workflow()
        test_out_of_scope_no_workflow()

        print("=" * 60)
        print("🎉 All workflow builder tests passed!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()