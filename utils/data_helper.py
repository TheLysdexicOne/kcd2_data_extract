import json
import os
from pathlib import Path
from utils.logger import logger

def initialize_data(root_dir, version_dir):
    """
    Initialize a fresh data.json file in the version directory,
    based on templates/data.template.
    
    Args:
        root_dir (Path): Path to the project root directory
        version_dir (Path): Path to the version directory
    
    Returns:
        dict: The initialized data structure
    """
    logger.info(f"Initializing fresh data.json in {version_dir}")
    
    # Load the template
    template_path = root_dir / "templates" / "data.template"
    if not template_path.exists():
        logger.error(f"Template file not found: {template_path}")
        return None
    
    try:
        # Load the template
        with open(template_path, 'r') as f:
            data = json.load(f)
        
        # Load version info from version.json
        version_json_path = root_dir / "data" / "version.json"
        if version_json_path.exists():
            try:
                with open(version_json_path, 'r') as f:
                    version_data = json.load(f)
                
                # Update the version in the data to match the new structure
                data["version"]["id"] = version_data.get("id", 0)
                data["version"]["name"] = version_data.get("name", "")
                data["version"]["version"] = version_data.get("version", "")
                
                logger.info(f"Updated version info: {data['version']}")
            except Exception as e:
                logger.warning(f"Error reading version.json: {e}")
        
        # Save the initialized data
        success = save_data(data, version_dir)
        if not success:
            logger.error("Failed to save initialized data")
            return None
        
        return data
        
    except Exception as e:
        logger.error(f"Error initializing data: {e}")
        return None

def save_data(data, version_dir):
    """
    Save the data structure to data.json in the version directory.
    
    Args:
        data (dict): The data structure to save
        version_dir (Path): Path to the version directory
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Ensure the directory exists
        os.makedirs(version_dir, exist_ok=True)
        
        # Save the data
        data_path = version_dir / "data.json"
        with open(data_path, 'w') as f:
            json.dump(data, f, indent=4)
        
        logger.info(f"Saved data to {data_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error saving data: {e}")
        return False

def load_data(version_dir):
    """
    Load the data structure from data.json in the version directory.
    
    Args:
        version_dir (Path): Path to the version directory
    
    Returns:
        dict: The loaded data structure, or None if an error occurred
    """
    try:
        data_path = version_dir / "data.json"
        
        if not data_path.exists():
            logger.warning(f"Data file not found: {data_path}")
            return None
        
        with open(data_path, 'r') as f:
            data = json.load(f)
        
        logger.info(f"Loaded data from {data_path}")
        return data
        
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        return None