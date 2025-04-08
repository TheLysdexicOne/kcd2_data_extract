from pathlib import Path
from typing import Optional
from .logger import logger

def ensure_dir(directory_path: Path) -> Optional[Path]:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        directory_path: The path to the directory to ensure exists
        
    Returns:
        The directory path if successful, None if an error occurred
    """
    try:
        if not directory_path.exists():
            logger.info(f"Creating directory: {directory_path}")
            directory_path.mkdir(parents=True, exist_ok=True)
        return directory_path
    except Exception as e:
        logger.error(f"Error creating directory {directory_path}: {e}")
        return None

def rel_path(path: Path, base: Optional[Path] = None) -> Path:
    """
    Convert paths to relative form for logging purposes.
    
    Args:
        path: The path to convert to a relative path
        base: The base path to make the path relative to
              (defaults to ROOT_DIR from config if None)
        
    Returns:
        Relative path if possible, otherwise the original path
    """
    if base is None:
        from config import ROOT_DIR
        base = ROOT_DIR
    
    try:
        return path.relative_to(base)
    except ValueError:
        # If path can't be made relative to base, return as is
        return path