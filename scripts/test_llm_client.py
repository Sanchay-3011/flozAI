"""Test Groq LLM client"""
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from flozai.utils.llm_client import LLMClient


def test_basic_completion():
    """Test basic text completion"""
    print("🧪 Testing basic completion...")

    client = LLMClient()

    response = client.complete(
        system_prompt="You are a helpful assistant.",
        user_message="Say 'Hello from Groq!' and nothing else."
    )

    print(f"✅ Response: {response}\n")


def test_json_completion():
    """Test JSON structured output"""
    print("🧪 Testing JSON completion...")

    client = LLMClient()

    system_prompt = """You are a JSON generator. 
Extract the person's name and age from the user's message.
Respond with JSON in this format:
{
  "name": "string",
  "age": number
}"""

    user_message = "My name is Alice and I'm 25 years old."

    response = client.complete_json(
        system_prompt=system_prompt,
        user_message=user_message
    )

    print(f"✅ Parsed JSON: {response}")
    print(f"   Name: {response.get('name')}")
    print(f"   Age: {response.get('age')}\n")


def test_workflow_intent():
    """Test workflow intent parsing"""
    print("🧪 Testing workflow intent parsing...")

    client = LLMClient()

    system_prompt = """Extract workflow intent from user input.
Respond with JSON:
{
  "trigger": "what starts the workflow",
  "action": "what the workflow does"
}"""

    user_message = "When someone fills out my contact form, send me an email"

    response = client.complete_json(
        system_prompt=system_prompt,
        user_message=user_message
    )

    print(f"✅ Workflow Intent: {response}\n")


if __name__ == "__main__":
    try:
        test_basic_completion()
        test_json_completion()
        test_workflow_intent()
        print("🎉 All LLM client tests passed!")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()