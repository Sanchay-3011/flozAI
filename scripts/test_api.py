"""Test API endpoints"""
import requests
import json
import time
import sys

BASE_URL = "http://127.0.0.1:8000"


def wait_for_server(max_attempts=10):
    """Wait for server to be ready"""
    print("⏳ Waiting for server to start...")
    for i in range(max_attempts):
        try:
            response = requests.get(f"{BASE_URL}/", timeout=1)
            if response.status_code in [200, 404]:
                print("✅ Server is ready!\n")
                return True
        except requests.exceptions.RequestException:
            time.sleep(1)

    print("❌ Server not responding. Make sure it's running:")
    print("   python main.py")
    sys.exit(1)


def test_health():
    """Test health check"""
    print("🧪 Test: Health Check")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}\n")
    except Exception as e:
        print(f"❌ Error: {e}\n")


def test_capabilities():
    """Test capabilities endpoint"""
    print("🧪 Test: Get Capabilities")
    try:
        response = requests.get(f"{BASE_URL}/capabilities")
        data = response.json()
        print(f"Status: {response.status_code}")
        print(f"Triggers: {len(data['triggers'])}")
        print(f"Actions: {len(data['actions'])}")
        print(f"Integrations: {len(data['integrations'])}\n")
    except Exception as e:
        print(f"❌ Error: {e}\n")


def test_parse():
    """Test parse endpoint"""
    print("🧪 Test: Parse Intent")

    test_cases = [
        "When someone submits my contact form, send me an email",
        "Send a message",  # Needs clarification
        "If urgent send email else slack",  # Out of scope
    ]

    for user_input in test_cases:
        print(f"\nInput: {user_input}")
        print("-" * 60)

        try:
            response = requests.post(
                f"{BASE_URL}/parse",
                json={"user_input": user_input},
                timeout=30  # LLM calls can take time
            )

            if response.status_code == 200:
                data = response.json()
                print(f"Status: {data['intent']['status']}")
                print(f"Explanation: {data['explanation'][:200]}...")

                if data.get('workflow'):
                    print(f"Workflow: {data['workflow']['name']}")
            else:
                print(f"Error {response.status_code}: {response.text[:200]}")

        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    wait_for_server()

    try:
        test_health()
        test_capabilities()
        test_parse()
        print("\n🎉 All API tests completed!")
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()