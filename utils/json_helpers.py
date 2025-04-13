import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from .logger import logger

def read_json(file_path: Path) -> Optional[Dict[str, Any]]:
    """
    Read and parse a JSON file.

    Args:
        file_path: Path to the JSON file

    Returns:
        dict: Parsed JSON data or None if an error occurred
    """
    try:
        if not file_path.exists():
            logger.warning(f"File not found: {file_path}")
            return None
            
        with open(file_path, 'r') as f:
            data = json.load(f)
            # Explicitly return the typed value to help Mypy
            return data if isinstance(data, dict) else None
            
    except Exception as e:
        logger.error(f"Error reading JSON file {file_path}: {e}")
        return None

def write_json(file_path: Path, data: Any, indent: int = 4) -> bool:
    """
    Write data to a JSON file.

    Args:
        file_path: Path to the JSON file to write
        data: The data to write to the JSON file
        indent: The number of spaces to use for indentation in the JSON file (default is 4)

    Returns:
        bool: True if the file was written successfully, False if an error occurred
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
    
def unwrap_key(data: Any, key: str) -> Any:
    """
    Unwrap a key from a dictionary.

    Args:
        data: The dictionary or other data structure to unwrap the key from.
        key: The key to look for in the dictionary.

    Returns:
        The value associated with the key if it exists in the dictionary,
        otherwise returns the original data.
    """
    if isinstance(data, dict) and key in data:
        return data[key]
    return data

def xform_ui_dict(data: List[Dict[str, Any]]) -> Dict[str, List[Any]]:
    """
    Transform a list of dictionaries with "Cell" arrays into a single dictionary 
    where the first element of each "Cell" array becomes the key.
    
    Args:
        data: List of dictionaries in format [{"Cell": ["key", "value1", "value2"]}, ...]
        
    Returns:
        Dictionary in format {"key": ["value1", "value2"], ...}
    """
    result: Dict[str, List[Any]] = {}
    
    for item in data:
        # Skip empty items
        if not item or "Cell" not in item:
            continue
            
        cell_array = item["Cell"]
        
        # Skip empty arrays or arrays without at least a key and one value
        if not cell_array or len(cell_array) < 2:
            continue
            
        # Use first element as key, remaining elements as values
        key = str(cell_array[0])  # Ensure the key is a string
        values = cell_array[1:]
        
        # Skip items with null keys
        if key is None:
            continue
            
        # Store in result dictionary
        result[key] = values
    
    return result