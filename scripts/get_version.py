import json
import os
import sys
from pathlib import Path

# Add the project root to Python path when needed
sys.path.insert(0, str(Path(__file__).parent.parent.absolute()))
from utils.logger import logger
from utils.helpers import read_json_file, ensure_directory

def get_version(kcd2_dir, root_dir):
    """
    Get the KCD2 game version and ensure version directory exists.
    
    Args:
        kcd2_dir (Path): Path to the KCD2 directory
        root_dir (Path): Path to the project root directory
        
    Returns:
        dict: Dictionary containing:
            - game_version: The game version string
            - version_id: The cleaned version string (without "release_")
            - version_dir: Path to the version directory
            - is_new_version: True if game version differs from stored version
            - branch_id: The numeric ID of the branch
    """
    result = {
        "game_version": None,
        "version_id": None,
        "version_dir": None,
        "is_new_version": False,
        "branch_id": None  # Added branch_id to result
    }
    
    # Get the game version from whdlversions.json
    whdl_path = kcd2_dir / "whdlversions.json"
    if not whdl_path.exists():
        logger.error(f"Version file not found: {whdl_path}")
        return result
    
    try:
        version_data = read_json_file(whdl_path)
        if not version_data:
            logger.error("Failed to read version data from whdlversions.json")
            return result
        
        # Extract the version from Preset.Branch.Name
        game_version = version_data.get("Preset", {}).get("Branch", {}).get("Name")
        
        # Extract the branch ID from Preset.Branch.Id
        branch_id = version_data.get("Preset", {}).get("Branch", {}).get("Id")
        
        if not game_version:
            logger.error("Version information not found in whdlversions.json")
            return result
        
        result["game_version"] = game_version
        result["branch_id"] = branch_id  # Store the branch ID
        
        # Clean the version string (remove "release_")
        version_id = game_version.replace("release_", "") if game_version.startswith("release_") else game_version
        result["version_id"] = version_id
        
        # Check against stored version
        stored_version = None
        version_json_path = root_dir / "data" / "version.json"
        
        if version_json_path.exists():
            try:
                stored_data = read_json_file(version_json_path)
                # Use the "name" field instead of "version" for comparison
                stored_version = stored_data.get("name")
            except Exception as e:
                logger.warning(f"Error reading stored version: {e}")
        
        result["is_new_version"] = stored_version != game_version
        
        # Create version directory
        version_dir = root_dir / "data" / "version" / version_id
        ensure_directory(version_dir)
        
        result["version_dir"] = version_dir
        
        logger.info(f"Game version: {game_version}")
        logger.info(f"Branch ID: {branch_id}")
        logger.info(f"Version directory: {version_dir}")
        if result["is_new_version"]:
            logger.info(f"New version detected (previous: {stored_version})")
        
        return result
        
    except Exception as e:
        logger.error(f"Error checking version: {e}")
        return result

# This allows the module to be run directly for testing
if __name__ == "__main__":
    # When run directly, this sys.path addition should already be done at the top
    from config import KCD2_DIR, ROOT_DIR
    
    result = get_version(KCD2_DIR, ROOT_DIR)
    logger.info(f"Version check result: {result}")