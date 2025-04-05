import os
from pathlib import Path
from utils.logger import logger
from config import ROOT_DIR, KCD2_DIR
from scripts.get_version import get_version
from utils.data_helper import initialize_data
from scripts.get_xml import get_xml
from scripts.process_xml import fix_alias

# Check version
version_info = get_version(KCD2_DIR, ROOT_DIR)
if version_info["game_version"]:
    # Use version information
    version_dir = version_info["version_dir"]
    game_version = version_info["game_version"]
else:
    # Handle error
    logger.error("Failed to check game version")
    exit(1)

# Initialize data.json in the version directory
data = initialize_data(ROOT_DIR, version_dir)
if not data:
    logger.error("Failed to initialize data")
    exit(1)

# Create necessary folders if they do not exist
folders_to_create = [
    version_dir / "xml" / "raw",
    version_dir / "xml" / "temp",
    version_dir / "xml" / "final",
    version_dir / "icon" / "raw",
    version_dir / "icon" / "temp",
    version_dir / "icon" / "final",
]

for folder in folders_to_create:
    folder.mkdir(parents=True, exist_ok=True)
    logger.info(f"Ensured folder exists: {folder}")

# Extract XML files
xml_files = get_xml(KCD2_DIR, ROOT_DIR, version_info)
if not xml_files:
    logger.error("XML extraction failed: No files found")
    exit(1)

logger.info(f"Working with {len(xml_files)} XML files")

# Process the combined items file to fix aliases
if "combined_items" in xml_files:
    combined_items_path = xml_files["combined_items"]
    logger.info(f"Processing aliases in combined items file: {combined_items_path}")
    
    # Fix aliases in the combined items file
    processed_file = fix_alias(combined_items_path)
    if processed_file is None:
        logger.error("Failed to fix aliases in combined items file")
        exit(1)
    
    logger.info(f"Successfully processed aliases in combined items file")
else:
    logger.error("Combined items file not found in extraction results")
    exit(1)

# Continue with further processing steps...