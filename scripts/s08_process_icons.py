import json
import math
from PIL import Image
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from utils import logger, ensure_dir, write_json


def process_icons(root_dir: Path, version_id: str, items_array: List[Dict[str, Any]], extracted_icons: Dict[str, Path]) -> List[Dict[str, str]]:
    """
    Process extracted icons and create a spritesheet with position coordinates.
    
    Args:
        root_dir: Path to the root directory
        version_id: Version identifier string
        items_array: Array of processed items
        extracted_icons: Dictionary mapping icon IDs to icon file paths
        
    Returns:
        List of icon data objects with id and position information
    """
    logger.info("Processing icons and creating spritesheet...")
    
    try:
        # Input validation
        if not items_array:
            logger.error("No items data provided for icon processing")
            return []
            
        if not extracted_icons:
            logger.warning("No extracted icons to process")
            return []
            
        # Prepare directories
        version_dir = root_dir / "data" / "version" / version_id
        icon_dir = version_dir / "icon"
        processed_dir = ensure_dir(icon_dir / "processed")
        
        # Create spritesheet
        icons_data, sprite_path = create_spritesheet(extracted_icons, version_dir)
        if not icons_data:
            logger.error("Failed to create spritesheet")
            return []
            
        # Save icons data to json (for debugging only)
        icons_data_path = version_dir / "icons_data.json"
        if write_json(icons_data_path, icons_data):
            logger.info(f"Saved icons position data to {icons_data_path}")
        
        logger.info(f"Successfully created spritesheet at {sprite_path}")
        logger.info(f"Generated position data for {len(icons_data)} icons")
        
        # Return the icons data directly
        return icons_data
        
    except Exception as e:
        logger.error(f"Error processing icons: {str(e)}")
        import traceback
        logger.debug(traceback.format_exc())
        return []


def create_spritesheet(extracted_icons: Dict[str, Path], version_dir: Path) -> Tuple[List[Dict[str, str]], Optional[Path]]:
    """
    Create a spritesheet from the extracted icons.
    
    Args:
        extracted_icons: Dictionary mapping icon IDs to icon file paths
        version_dir: Path to the version directory
        
    Returns:
        Tuple containing:
        - List of icon data objects with id and position
        - Path to the generated spritesheet or None if failed
    """
    try:
        # Constants
        ICON_SIZE = 64  # Icon size in pixels
        PADDING = 2     # Padding between icons in pixels
        
        # Calculate grid dimensions
        icon_count = len(extracted_icons)
        if icon_count == 0:
            logger.warning("No icons to process for spritesheet")
            return [], None
            
        # Calculate grid dimensions (roughly square)
        cols = math.ceil(math.sqrt(icon_count))
        rows = math.ceil(icon_count / cols)
        
        # Create blank spritesheet with the right dimensions
        spritesheet_width = cols * (ICON_SIZE + PADDING) - PADDING
        spritesheet_height = rows * (ICON_SIZE + PADDING) - PADDING
        
        logger.info(f"Creating {cols}x{rows} spritesheet ({spritesheet_width}x{spritesheet_height}px) for {icon_count} icons")
        
        # Create a new blank image with an alpha channel
        spritesheet = Image.new('RGBA', (spritesheet_width, spritesheet_height), (0, 0, 0, 0))
        
        # Sort icon IDs to ensure consistent positioning across builds
        sorted_icon_ids = sorted(extracted_icons.keys())
        
        # Dictionary to store icon positions
        icons_data = []
        
        # Place icons on the spritesheet
        for index, icon_id in enumerate(sorted_icon_ids):
            icon_path = extracted_icons[icon_id]
            
            try:
                # Load the icon image
                icon = Image.open(icon_path)
                
                # Resize if necessary
                if icon.size != (ICON_SIZE, ICON_SIZE):
                    icon = icon.resize((ICON_SIZE, ICON_SIZE), Image.Resampling.LANCZOS)
                
                # Calculate position in grid
                col = index % cols
                row = index // cols
                
                x = col * (ICON_SIZE + PADDING)
                y = row * (ICON_SIZE + PADDING)
                
                # Paste the icon onto the spritesheet
                spritesheet.paste(icon, (x, y), icon)
                
                # Store position information
                icons_data.append({
                    "id": icon_id,
                    "position": f"{x}px {y}px"
                })
                
            except Exception as e:
                logger.error(f"Error processing icon {icon_id}: {str(e)}")
                continue
        
        # Save the spritesheet
        spritesheet_path = version_dir / "icons.webp"
        spritesheet.save(spritesheet_path, 'WEBP', quality=90)
        
        return icons_data, spritesheet_path
        
    except Exception as e:
        logger.error(f"Error creating spritesheet: {str(e)}")
        import traceback
        logger.debug(traceback.format_exc())
        return [], None


# This allows the module to be run directly for testing
if __name__ == "__main__":
    from config import ROOT_DIR
    import json
    
    # For testing, load a sample items array
    test_version_id = "1_2"
    version_dir = ROOT_DIR / "data" / "version" / test_version_id
    
    # Check if processed items exists
    processed_file = version_dir / "processed_items.json"
    if processed_file.exists():
        with open(processed_file, 'r') as f:
            items_data = json.load(f)
        
        # Check if icons mapping exists
        icons_mapping_file = version_dir / "icon" / "icons_mapping.json"
        if icons_mapping_file.exists():
            with open(icons_mapping_file, 'r') as f:
                icons_mapping = json.load(f)
                
            # Convert string paths back to Path objects
            extracted_icons = {k: Path(v) for k, v in icons_mapping.items()}
            
            # Process the icons
            updated_items = process_icons(ROOT_DIR, test_version_id, items_data, extracted_icons)
            logger.info(f"Processed {len(updated_items)} items with icons")
        else:
            logger.error(f"Icons mapping file not found: {icons_mapping_file}")
    else:
        logger.error(f"Processed items file not found: {processed_file}")