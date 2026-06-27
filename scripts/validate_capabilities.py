"""Validate capabilities.yaml loads correctly"""
import sys
from pathlib import Path

# Add src to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from flozai.schemas.capabilities import load_capabilities

def main():
    try:
        caps = load_capabilities()
        print("✅ Capabilities loaded successfully!")
        print(f"\n📊 Summary:")
        print(f"   Triggers: {len(caps.triggers)}")
        print(f"   Actions: {len(caps.actions)}")
        print(f"   Integrations: {len(caps.integrations)}")

        print(f"\n🔧 Triggers:")
        for trigger in caps.triggers:
            print(f"   - {trigger.display_name} ({trigger.id})")

        print(f"\n⚡ Actions:")
        for action in caps.actions:
            print(f"   - {action.display_name} ({action.id})")

        print(f"\n🔌 Integrations:")
        for integration in caps.integrations:
            print(f"   - {integration.display_name} ({integration.id})")
            print(f"     Triggers: {integration.supported_triggers}")
            print(f"     Actions: {integration.supported_actions}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    main()