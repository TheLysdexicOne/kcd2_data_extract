from dotenv import load_dotenv
import os
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

# Export environment variables as constants
ROOT_DIR = Path(os.getenv("ROOT_DIR", ".")).resolve()
KCD2_DIR = Path(os.getenv("KCD2_DIR", ".")).resolve()