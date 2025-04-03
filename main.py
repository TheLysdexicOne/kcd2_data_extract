import os
from pathlib import Path
from utils.logger import logger
from config import ROOT_DIR, KCD2_DIR
from scripts.get_version import get_version
from utils.data_helper import initialize_data

# Later in your code
version_info = get_version(KCD2_DIR, ROOT_DIR)
if version_info["game_version"]:
    # Use version information
    version_dir = version_info["version_dir"]
    game_version = version_info["game_version"]
    # ...
else:
    # Handle error
    logger.error("Failed to check game version")

# Initialize data.json in the version directory
data = initialize_data(ROOT_DIR, version_dir)

# Extract the appropriate XMLs