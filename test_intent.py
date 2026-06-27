import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from dotenv import load_dotenv
load_dotenv()

from flozai.core.intent_parser import IntentParser

def test():
    print("Initializing IntentParser...")
    parser = IntentParser()
    print("Parsing intent...")
    result = parser.parse("post AI news on LinkedIn daily at 9am")
    print("\nResult:")
    print(result.model_dump_json(indent=2))

if __name__ == "__main__":
    test()
