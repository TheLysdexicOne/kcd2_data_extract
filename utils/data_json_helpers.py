from pathlib import Path
from typing import Dict, Optional, Any
from .logger import logger
from .helpers import ensure_dir
from .json_helpers import read_json, write_json

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