import logging
from logging import Logger
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime
from typing import List
from dotenv import load_dotenv
import os
import re

# Load environment variables from .env
load_dotenv()
ROOT_DIR = Path(os.getenv("ROOT_DIR", ".")).resolve()

# Ensure logs directory exists relative to ROOT_DIR
LOG_DIR: Path = ROOT_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Define log files
timestamp: str = datetime.now().strftime('%Y%m%d_%H%M%S')
TIMED_LOG_FILE: Path = LOG_DIR / f"kcd2_data_extract_{timestamp}.log"
STATIC_LOG_FILE: Path = LOG_DIR / "latest.log"

# Custom formatter that converts Path objects to relative paths
class RelativePathFormatter(logging.Formatter):
    def format(self, record):
        # Convert all Path objects in args to relative paths
        if hasattr(record, 'args') and isinstance(record.args, tuple):
            new_args = []
            for arg in record.args:
                if isinstance(arg, Path):
                    try:
                        new_args.append(arg.relative_to(ROOT_DIR))
                    except ValueError:
                        try:
                            from config import KCD2_DIR
                            new_args.append(f"KCD2:{arg.relative_to(KCD2_DIR)}")
                        except (ValueError, ImportError):
                            new_args.append(arg)
                else:
                    new_args.append(arg)
            record.args = tuple(new_args)
        
        # Handle Path objects in the message itself (using string replacement)
        if hasattr(record, 'msg') and isinstance(record.msg, str):
            # Look for Windows-style absolute paths that match ROOT_DIR pattern
            root_str = str(ROOT_DIR).replace('\\', '\\\\')  # Escape backslashes for regex
            pattern = f"{root_str}\\\\([^'\"]*)"
            record.msg = re.sub(pattern, r'\1', record.msg)
            
            # Also handle KCD2_DIR paths
            try:
                from config import KCD2_DIR
                kcd2_str = str(KCD2_DIR).replace('\\', '\\\\')
                kcd2_pattern = f"{kcd2_str}\\\\([^'\"]*)"
                record.msg = re.sub(kcd2_pattern, r'KCD2:\1', record.msg)
            except ImportError:
                pass
        
        return super().format(record)

# Create logger
logger: Logger = logging.getLogger("kcd2_data_extract")
logger.setLevel(logging.DEBUG)  # Set minimum log level

# Create rotating file handler for timestamped log file
unique_handler: RotatingFileHandler = RotatingFileHandler(
    TIMED_LOG_FILE, maxBytes=10 * 1024 * 1024, backupCount=5
)
unique_handler.setLevel(logging.DEBUG)

# Create file handler for statically named log file
static_handler: logging.FileHandler = logging.FileHandler(
    STATIC_LOG_FILE, mode='w'  # 'w' mode to start with an empty file each run
)
static_handler.setLevel(logging.DEBUG)

# Create console handler
console_handler: logging.StreamHandler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)  # Show only INFO+ logs in console

# Define custom formatter that handles Path objects
formatter: RelativePathFormatter = RelativePathFormatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
unique_handler.setFormatter(formatter)
static_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers to logger
logger.addHandler(unique_handler)
logger.addHandler(static_handler)
logger.addHandler(console_handler)

# Keep only the latest 5 logs
MAX_LOGS: int = 5  # Keep only the latest 5 logs
log_files: List[Path] = sorted(
    LOG_DIR.glob("kcd2_data_extract_*.log"), key=lambda f: f.stat().st_mtime, reverse=True
)
for old_log in log_files[MAX_LOGS:]:  # Delete logs beyond limit
    old_log.unlink()

# Create a wrapper function for easier path handling in f-strings
def rel_path(path):
    """
    Return path relative to ROOT_DIR or KCD2_DIR for logging purposes.
    Paths relative to KCD2_DIR will be prefixed with 'KCD2:'.
    
    Args:
        path: Path to convert to relative form
        
    Returns:
        Path or str: Relative path with appropriate prefix
    """
    try:
        # First try to make it relative to ROOT_DIR
        return path.relative_to(ROOT_DIR)
    except (ValueError, AttributeError):
        try:
            # If that fails, try to make it relative to KCD2_DIR
            from config import KCD2_DIR
            return f"KCD2:{path.relative_to(KCD2_DIR)}"
        except (ValueError, AttributeError, ImportError):
            # If both fail, return the original path
            return path

# Example log entry to demonstrate relative paths
logger.info(f"Logger initialized. Logs directory: {LOG_DIR}")