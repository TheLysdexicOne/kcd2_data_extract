import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from xml.etree.ElementTree import ElementTree
from utils import logger, ensure_dir, write_json, convert_xml
from config import ROOT_DIR, KCD2_DIR
from scripts import get_version, init_data_json, get_xml, parse_items, fill_item_properties, process_items, extract_icons, process_icons

def main(debug: bool = False) -> int:
    """Main function for KCD2 data extraction."""
    # Directories
    root_dir = Path(ROOT_DIR)
    kcd2_dir = Path(KCD2_DIR)
    log_dir = root_dir / "logs"    

    # s01_check_version.py
    # Check version
    logger.info("Checking game version...")
    version_id: Optional[str] = get_version(root_dir, kcd2_dir)
    if not version_id:
        logger.error("Failed to check game version")
        return 1

    # Specify version and debug directories
    version_dir = root_dir / "data" / "version" / version_id

    # s02_init_data_json.py
    # Initialize data.json in the version directory
    logger.info(f"Initializing data.json for version {version_id}...")
    data: Optional[Dict[str, Any]] = init_data_json(root_dir, version_id)
    if not data:
        logger.error("Failed to initialize data")
        return 1

    # s03_get_xmpl.py
    # Extract XML files
    logger.info("Extracting XML files...")
    xml_trees: Dict[str, ElementTree] = get_xml(root_dir, version_id, kcd2_dir)
    if not xml_trees or "combined_items" not in xml_trees or "text_ui_items" not in xml_trees:
        logger.error("XML extraction failed: Missing required XML trees")
        return 1

    # Convert XML trees to dictionaries
    logger.info("Converting XML trees to dictionaries...")
    combined_dict: Optional[Dict[str, Any]]
    text_ui_dict: Optional[Dict[str, Any]]
    combined_dict, text_ui_dict = convert_xml(xml_trees)   

    # Write XML trees and dictionaries to files
    try:
        xml_trees["combined_items"].write(version_dir / "combined_items.xml", encoding="utf-8", xml_declaration=True)
        write_json(version_dir / "text_ui_dict.json", text_ui_dict, indent=4)
        write_json(version_dir / "combined_dict.json", combined_dict, indent=4)
    except Exception as e:
        logger.error(f"Failed to write XML trees or dictionaries to files: {e}")
        return 1
    
    # s04_parse_items.py
    # Parse the combined_items dictionary
    logger.info("Parsing combined_items dictionary...")
    parsed_items: Optional[Dict[str, Any]] = parse_items(root_dir, version_id, combined_dict, text_ui_dict, data)
    if not parsed_items:
        logger.error("Failed to parse items")
        return 1
    
    # Write parsed items to a file
    try:
        write_json(version_dir / "parsed_items.json", parsed_items, indent=4)
    except Exception as e:
        logger.error(f"Failed to write parsed items to file: {e}")
        return 1

    # s05_fill_items.py
    # Filling out categorization keys
    logger.info("Filling out categorization keys...")
    filled_items: Optional[Dict[str, Any]] = fill_item_properties(root_dir, version_id, parsed_items, data)
    if not filled_items:
        logger.error("Failed to fill item properties")
        return 1

    # Write filled items to a file
    try:
        write_json(version_dir / "filled_items.json", filled_items, indent=4)
    except Exception as e:
        logger.error(f"Failed to write parsed items to file: {e}")
        return 1

    # s06_process_items.py
    # Create the items dictionary for writing to data.json
    logger.info("Creating items dictionary for writing to data.json...")
    items_array: List[Dict[str, Any]] = process_items(root_dir, version_id, filled_items, data)
    if not items_array:
        logger.error("Failed to process items")
        return 1
    
    # Write items dictionary to a file
    try:
        write_json(version_dir / "items_array.json", items_array, indent=4)
    except Exception as e:
        logger.error(f"Failed to write items dictionary to file: {e}")
        return 1
    
    # Immplant the items into data.json
    logger.info("Implanting items into data.json...")
    data["items"] = items_array
    try:
        write_json(version_dir / "data.json", data, indent=4)
    except Exception as e:
        logger.error(f"Failed to write data.json: {e}")
        return 1
    
    # s07_extract_icons.py
    # Extract icons from the game directory
    logger.info("Extracting icons from the game directory...")
    icons: Optional[Dict[str, Any]] = extract_icons(root_dir, version_id, kcd2_dir, items_array)
    if not icons:
        logger.error("Failed to extract icons")
        return 1
    
    # Implant the icons into data.json
    logger.info("Implanting icons into data.json...")
    data["icons"] = icons
    try:
        write_json(version_dir / "data.json", data, indent=4)
    except Exception as e:
        logger.error(f"Failed to write data.json: {e}")
        return 1
    
    # Return 0 for success
    return 0

if __name__ == "__main__":
    # Parse command line arguments if needed
    # args = parse_args()
    
    # Run the main function and get the exit code
    exit_code = main(debug=True)
    
    # Exit with the appropriate code
    sys.exit(exit_code)