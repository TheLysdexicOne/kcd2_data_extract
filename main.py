import sys
from pathlib import Path
from typing import Dict, Any, Optional
from xml.etree.ElementTree import ElementTree
from utils import logger, ensure_dir, init_data_json, write_json, unwrap_key, xform_ui_dict, convert_xml
from config import ROOT_DIR, KCD2_DIR
from scripts import get_version, get_xml, parse_items, process_items

def main(debug: bool = False) -> int:
    """Main function for KCD2 data extraction."""
    # Directories
    root_dir = Path(ROOT_DIR)
    kcd2_dir = Path(KCD2_DIR)
    log_dir = root_dir / "logs"
    debug_dir = log_dir / "debug"

    # Ensure directories exist
    ensure_dir(debug_dir)

    # Check version
    version_id: Optional[str] = get_version(root_dir, kcd2_dir)
    if not version_id:
        logger.error("Failed to check game version")
        return 1

    # Initialize data.json in the version directory
    data: Optional[Dict[str, Any]] = init_data_json(root_dir, version_id)
    if not data:
        logger.error("Failed to initialize data")
        return 1

    # Extract XML files
    xml_trees: Dict[str, ElementTree] = get_xml(root_dir, kcd2_dir, version_id)
    if not xml_trees or "combined_items" not in xml_trees or "text_ui_items" not in xml_trees:
        logger.error("XML extraction failed: Missing required XML trees")
        return 1

    logger.info(f"Working with {len(xml_trees)} XML trees")

    # Convert XML trees to dictionaries
    logger.info("Converting XML trees to dictionaries...")
    combined_dict: Optional[Dict[str, Any]]
    text_ui_dict: Optional[Dict[str, Any]]
    combined_dict, text_ui_dict = convert_xml(xml_trees)
    if debug:
        write_json(debug_dir / "combined_dict.json", combined_dict, indent=4)
        write_json(debug_dir / "text_ui_dict.json", text_ui_dict, indent=4)
    if not combined_dict and not text_ui_dict:
        logger.error("Failed to convert XML trees to dictionaries")
        return 1

    logger.info("Successfully converted XML to dictionaries")
    
    # Fix text_ui_dict and combined_dict format
    text_ui_dict = unwrap_key(unwrap_key(text_ui_dict, "Table"), "Row")
    text_ui_dict = xform_ui_dict(text_ui_dict)
    combined_dict = unwrap_key(unwrap_key(combined_dict,"database"), "ItemClasses")
    combined_dict.pop("@version")

    if debug:
        write_json(log_dir / "debug" / "text_ui_dict.json", text_ui_dict, indent=4)
        write_json(log_dir / "debug" / "combined_dict.json", combined_dict, indent=4)
    
    # Parse the combined_items dictionary
    parsed_items = parse_items(root_dir, version_id, combined_dict, text_ui_dict, data)
    if not parsed_items:
        logger.error("Failed to parse items")
        return 1
    
    # Prep parsed items for writing to data.json
    logger.info("Preparing parsed items for writing to data.json...")
    items_dict = Optional[Dict[str, Any]]
    items_dict = process_items(parsed_items)
    if not items_dict:
        logger.error("Failed to process items")
        return 1
    write_json(debug_dir / "items_dict.json", items_dict, indent=4)

    # Return 0 for success
    return 0

if __name__ == "__main__":
    # Parse command line arguments if needed
    # args = parse_args()
    
    # Run the main function and get the exit code
    exit_code = main(debug=True)
    
    # Exit with the appropriate code
    sys.exit(exit_code)