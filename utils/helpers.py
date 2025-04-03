import json
from pathlib import Path
from utils.logger import logger

def parse_version_string(version_string):
    """
    Parse a version string like "release_1_2" into a cleaner format "1_2".
    Also works with formats like "release_1_2_3".
    
    Args:
        version_string (str): Version string (e.g., "release_1_2")
        
    Returns:
        str: Cleaned version string (e.g., "1_2")
    """
    if version_string.startswith("release_"):
        return version_string.replace("release_", "")
    return version_string

def read_json_file(file_path):
    """
    Read and parse a JSON file.
    
    Args:
        file_path (Path): Path to the JSON file
        
    Returns:
        dict: Parsed JSON data or None if an error occurred
    """
    try:
        if not file_path.exists():
            logger.warning(f"File not found: {file_path}")
            return None
            
        with open(file_path, 'r') as f:
            return json.load(f)
            
    except Exception as e:
        logger.error(f"Error reading JSON file {file_path}: {e}")
        return None

def write_json_file(file_path, data, indent=4):
    """
    Write data to a JSON file.
    
    Args:
        file_path (Path): Path to the JSON file
        data: Data to write
        indent (int): Indentation level
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Ensure directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
            
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=indent)
        return True
            
    except Exception as e:
        logger.error(f"Error writing JSON file {file_path}: {e}")
        return False

def ensure_directory(directory_path):
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        directory_path (Path): Path to the directory
        
    Returns:
        Path: Path to the directory
    """
    try:
        if not directory_path.exists():
            logger.info(f"Creating directory: {directory_path}")
            directory_path.mkdir(parents=True, exist_ok=True)
        return directory_path
    except Exception as e:
        logger.error(f"Error creating directory {directory_path}: {e}")
        return None

def rel_path(path, base=None):
    """Convert paths to relative form for logging purposes."""
    if base is None:
        from config import ROOT_DIR
        base = ROOT_DIR
    
    try:
        return path.relative_to(base)
    except ValueError:
        # If path can't be made relative to base, return as is
        return path