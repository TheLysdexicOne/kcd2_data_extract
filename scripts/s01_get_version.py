from pathlib import Path
import traceback
from typing import Dict, Any, Optional
from utils import logger, read_json, ensure_dir, write_json

def get_version(root_dir: Path, kcd2_dir: Path) -> Optional[str]:
    """
    Get the KCD2 game version and ensure version directory exists.
    
    Args:
        root_dir: Path to the project root directory
        kcd2_dir: Path to the KCD2 directory
        
    Returns:
        Version ID (e.g. "1_2" from "release_1_2") or None if error
    """
    # Get the game version from whdlversions.json
    whdl_path = kcd2_dir / "whdlversions.json"
    if not whdl_path.exists():
        logger.error(f"Version file not found: {whdl_path}")
        return None
    
    try:
        # Get preset data and extract version information
        preset_data = get_preset_data(whdl_path)
        if not preset_data:
            return None
        
        # Extract the version from Preset.Branch.Name
        game_version = preset_data.get("Branch", {}).get("Name")
        if not game_version:
            logger.error("Version information not found in whdlversions.json")
            return None
        logger.info(f"Game version: {game_version}")
        
        # Create or update version.json
        version_json_path = root_dir / "data" / "version.json"
        update_version_json(version_json_path, preset_data)
        
        # Create version directory with cleaned name
        version_id = clean_version_id(game_version)
        ensure_version_directories(root_dir, version_id)
        
        return version_id
        
    except Exception as e:
        logger.error(f"Error checking version: {e}")
        logger.error(traceback.format_exc())
        return None

def get_preset_data(whdl_path: Path) -> Optional[Dict[str, Any]]:
    """Extract preset data from whdlversions.json file."""
    version_data = read_json(whdl_path)
    if not version_data:
        logger.error("Failed to read version data from whdlversions.json")
        return None
    
    preset_data = version_data.get("Preset")
    if not preset_data:
        logger.error("Preset data not found in whdlversions.json")
        return None
        
    return preset_data

def clean_version_id(game_version):
    """Convert release_X_Y to X_Y for directory naming."""
    return game_version.replace("release_", "") if game_version.startswith("release_") else game_version

def ensure_version_directories(root_dir: Path, version_id: str) -> Path:
    """Create necessary version directories."""
    version_dir = root_dir / "data" / "version" / version_id
    xml_dir = version_dir / "xml"
    icon_dir = version_dir / "icon"

    ensure_dir(version_dir)
    ensure_dir(xml_dir)
    ensure_dir(icon_dir)
    
    return version_dir

def update_version_json(version_json_path: Path, preset_data: Dict[str, Any]) -> bool:
    """Update the version.json file with version information."""
    is_new_version = False
    versions: Dict[str, Any] = {"latest": preset_data}
    
    # If version.json exists, read it
    if version_json_path.exists():
        existing_versions = read_json(version_json_path)
        if existing_versions:
            # Process existing versions
            is_new_version = process_existing_versions(existing_versions, preset_data, versions)
    else:
        # Create parent directories if needed
        version_json_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Update with the latest version information
    versions["latest"] = preset_data
    
    # Write the updated version information
    write_json(version_json_path, versions)
    logger.info(f"Updated version information in {version_json_path}")
    
    return is_new_version

def process_existing_versions(existing_versions: Dict[str, Any], preset_data: Dict[str, Any], versions: Dict[str, Any]) -> bool:
    """Process existing versions and detect changes."""
    is_new_version = False
    latest = existing_versions.get("latest", {})
    
    # Check if version has changed
    if is_version_different(latest, preset_data):
        logger.info(f"New version detected: {preset_data.get('Name')} (previous: {latest.get('Name')})")
        
        # Store the previous version under its name
        previous_name = latest.get("Branch", {}).get("Name")
        if previous_name:
            existing_versions[previous_name] = latest
        
        is_new_version = True
    
    # Keep any historical versions
    for key, value in existing_versions.items():
        if key != "latest":
            versions[key] = value
            
    return is_new_version

def is_version_different(latest: Dict[str, Any], preset_data: Dict[str, Any]) -> bool:
    """Check if version information has changed."""
    if not latest:
        return False
        
    return (latest.get("Id") != preset_data.get("Id") or
            latest.get("Name") != preset_data.get("Name") or
            latest.get("Branch", {}).get("Id") != preset_data.get("Branch", {}).get("Id") or
            latest.get("Branch", {}).get("Name") != preset_data.get("Branch", {}).get("Name"))

# This allows the module to be run directly for testing
if __name__ == "__main__":
    from config import KCD2_DIR, ROOT_DIR
    
    result = get_version(ROOT_DIR, KCD2_DIR)
    logger.info(f"Version check result: {result}")