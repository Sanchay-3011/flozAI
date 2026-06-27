import sys
from pathlib import Path
from dotenv import load_dotenv

# Add src to python path to ensure imports work correctly in tests
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

# Load environment variables from .env file
load_dotenv(dotenv_path=project_root / ".env")
