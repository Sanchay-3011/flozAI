"""Test Intent Parser"""
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
from flozai.schemas.intent_schema import IntentStatus


def test_clear_intent():
    """Test parsing clear workflow intent"""
    print("🧪 Test 1: Clear Intent (Form to Email)")
    print("=" * 60)

    parser = IntentParser()

    user_input = "When someone submits my contact form, send me an email"

    intent = parser.parse(user_input)

    print(f"Status: {intent.status}")
    print(f"Workflow Name: {intent.workflow_name}")
    print(f"Trigger: {intent.trigger.type if intent.trigger else 'None'}")
    print(f"Actions: {[a.type for a in intent.actions]}")
    print(f"Valid: {parser.validate_intent(intent)}")
    print(f"\nFull Intent JSON:")
    print(json.dumps(intent.model_dump(), indent=2))
    print("\n")


def test_needs_clarification():
    """Test ambiguous input that needs clarification"""
    print("🧪 Test 2: Needs Clarification (Vague Input)")
    print("=" * 60)

    parser = IntentParser()

    user_input = "Send a message when something happens"

    intent = parser.parse(user_input)

    print(f"Status: {intent.status}")
    print(f"Clarification Question: {intent.clarification_question}")
    print(f"Missing Info: {intent.missing_info}")
    print("\n")


def test_out_of_scope():
    """Test request that's out of MVP scope"""
    print("🧪 Test 3: Out of Scope (Conditional Logic)")
    print("=" * 60)

    parser = IntentParser()

    user_input = "If the form response says urgent, send email, otherwise send Slack"

    intent = parser.parse(user_input)

    print(f"Status: {intent.status}")
    print(f"Reason: {intent.out_of_scope_reason}")
    print(f"Alternative: {intent.suggested_alternative}")
    print("\n")


def test_multi_action():
    """Test workflow with multiple actions"""
    print("🧪 Test 4: Multiple Actions (Form → Sheet → Email)")
    print("=" * 60)

    parser = IntentParser()

    user_input = "When my contact form is submitted, add a row to my spreadsheet and send me an email"

    intent = parser.parse(user_input)

    print(f"Status: {intent.status}")
    print(f"Trigger: {intent.trigger.type if intent.trigger else 'None'}")
    print(f"Actions ({len(intent.actions)}):")
    for i, action in enumerate(intent.actions, 1):
        print(f"  {i}. {action.type} ({action.integration})")
    print(f"Valid: {parser.validate_intent(intent)}")
    print("\n")


def test_multilingual():
    """Test non-English input"""
    print("🧪 Test 5: Multilingual (Spanish)")
    print("=" * 60)

    parser = IntentParser()

    user_input = "Cuando alguien envía mi formulario de contacto, envíame un correo electrónico"

    intent = parser.parse(user_input, user_language="es")

    print(f"Detected Language: {intent.detected_language}")
    print(f"Status: {intent.status}")
    print(f"Workflow Name: {intent.workflow_name}")
    print("\n")


if __name__ == "__main__":
    try:
        test_clear_intent()
        test_needs_clarification()
        test_out_of_scope()
        test_multi_action()
        test_multilingual()

        print("=" * 60)
        print("🎉 All intent parser tests completed!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()