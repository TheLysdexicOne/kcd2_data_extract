from pathlib import Path
from typing import Dict, Optional, Any
from .logger import logger
from .helpers import ensure_dir
from .json_helpers import read_json, write_json

def init_data_json(root_dir: Path, version_id: str) -> Optional[Dict[str, Any]]:
    """
    Initialize a fresh data.json file in the version directory,
    based on templates/data.template.
    
    Args:
        root_dir: Path to the project root directory
        version_id: Version ID (e.g. "1_2")
    
    Returns:
        The initialized data structure or None if initialization failed
    """
    # Construct version directory path and ensure it exists
    version_dir = root_dir / "data" / "version" / version_id
    ensure_dir(version_dir)
    logger.info(f"Initializing fresh data.json in {version_dir}")
    
    # Load the template
    template_path = root_dir / "templates" / "data.template"
    data = read_json(template_path)
    if not data:
        return None
    
    try:
        # Load version info from version.json
        version_json_path = root_dir / "data" / "version.json"
        version_data = read_json(version_json_path)
        
        if version_data and "latest" in version_data:
            latest_data = version_data["latest"]
            
            # Update the version in the data
            data["version"] = {
                "id": latest_data.get("Id", 0),
                "name": latest_data.get("Name", ""),
                "branch": latest_data.get("Branch", {}).get("Name", ""),
                "platform": latest_data.get("Platform", {}).get("Name", "")
            }
            
            logger.info(f"Updated version info: {data['version']}")
        
        # Save the initialized data
        data_path = version_dir / "data.json"
        if write_json(data_path, data):
            logger.info(f"Saved data to {data_path}")
            return data
        return None
        
    except Exception as e:
        logger.error(f"Error initializing data: {e}")
        return None

def save_data_json(data: Dict[str, Any], version_dir: Path) -> bool:
    """
    Save the data structure to data.json in the version directory.
    
    Args:
        data: The data structure to save
        version_dir: Path to the version directory
    
    Returns:
        True if successful, False otherwise
    """
    # Ensure the directory exists
    ensure_dir(version_dir)
    
    # Save the data
    data_path = version_dir / "data.json"
    if write_json(data_path, data):
        logger.info(f"Saved data to {data_path}")
        return True
    return False

def load_data_json(version_dir: Path) -> Optional[Dict[str, Any]]:
    """
    Load the data structure from data.json in the version directory.
    
    Args:
        version_dir: Path to the version directory
    
    Returns:
        The loaded data structure or None if loading failed
    """
    data_path = version_dir / "data.json"
    data = read_json(data_path)
    
    if data:
        logger.info(f"Loaded data from {data_path}")
    
    return data