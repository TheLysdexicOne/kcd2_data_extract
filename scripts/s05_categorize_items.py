from pathlib import Path
from typing import Dict, List, Any, Optional
from utils import logger, write_json


def categorize_items(parsed_items: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Categorize items by adding armor types and weapon types.
    
    Args:
        parsed_items: Dictionary of items organized by category
        data: Data dictionary containing categorization information
        
    Returns:
        Dictionary with categorized items
    """
    logger.info("Categorizing items...")
    
    # Add armor types to items
    logger.info("Adding armor types to items...")
    parsed_items = add_armor_types(parsed_items, data)
    
    # Add weapon types to items
    logger.info("Adding weapon types to items...")
    parsed_items = add_weapon_types(parsed_items, data)
    
    return parsed_items


def add_armor_types(parsed_items: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add armor types to items in the parsed items dictionary.
    
    Args:
        parsed_items: Dictionary of items organized by category
        data: Data dictionary containing armor types information
    
    Returns:
        Dictionary with armor types added to items
    """
    armor_type_counts = {
        "by_clothing": 0,
        "by_filter": 0,
        "unmatched": 0
    }
    
    # Keep track of unmatched items for debugging
    unmatched_items = []
    
    # Get armor types from data
    armor_types = data.get("armorTypes", [])
    if not armor_types:
        logger.warning("No armor types found in data")
        return parsed_items
    
    # Create filter to armor type id mapping for quick lookups
    filter_to_armor_type = {}
    for armor_type in armor_types:
        for filter_text in armor_type.get("filters", []):
            filter_to_armor_type[filter_text] = armor_type["id"]
    
    # Process armor items
    if "Armor" in parsed_items:
        # Skip if not a list
        if not isinstance(parsed_items["Armor"], list):
            logger.warning("Armor category is not a list - skipping")
            return parsed_items
            
        for item in parsed_items["Armor"]:
            if not isinstance(item, dict) or "Name" not in item:
                continue
                
            item_name = item["Name"]
            armor_type_id = -1  # Default to undefined
            
            # Check if the item has a Clothing property and try to match it to filters
            if "Clothing" in item and item["Clothing"]:
                clothing_value = item["Clothing"]
                
                # Try to match the Clothing value against filters
                for filter_text, type_id in filter_to_armor_type.items():
                    # Check if the filter appears at the start of the Clothing string
                    if clothing_value.startswith(filter_text) or filter_text in clothing_value:
                        armor_type_id = type_id
                        armor_type_counts["by_clothing"] += 1
                        break
            
            # If still no match, try to match by filter patterns in the item name
            if armor_type_id == -1:
                for filter_text, type_id in filter_to_armor_type.items():
                    if filter_text in item_name:
                        armor_type_id = type_id
                        armor_type_counts["by_filter"] += 1
                        break
            
            # If still no match, log it and add to unmatched list
            if armor_type_id == -1:
                armor_type_counts["unmatched"] += 1
                logger.debug(f"Could not determine armor type for item: {item_name}")
                
                # Collect relevant info about unmatched item
                unmatched_info = {
                    "name": item_name,
                    "display_name": item.get("DisplayName", "Unknown"),
                    "ui_name": item.get("UIName", "Not specified"),
                    "id": item.get("Id", "Unknown"),
                    "clothing": item.get("Clothing", "Not specified")
                }
                unmatched_items.append(unmatched_info)
            
            # Add the armor type ID to the item
            item["ArmorType"] = armor_type_id
    
    # Log results
    total_processed = sum(armor_type_counts.values())
    logger.info(f"Processed {total_processed} armor items:")
    logger.info(f"  - {armor_type_counts['by_clothing']} matched by clothing property")
    logger.info(f"  - {armor_type_counts['by_filter']} matched by filter in name")
    logger.info(f"  - {armor_type_counts['unmatched']} unmatched (assigned to undefined)")
    
    # Write detailed unmatched items to debug file
    if unmatched_items:
        try:
            debug_file_path = Path("logs/debug/unmatched_armor_items.json")
            # Ensure parent directory exists
            debug_file_path.parent.mkdir(parents=True, exist_ok=True)
            write_json(debug_file_path, unmatched_items)
            logger.info(f"Wrote {len(unmatched_items)} unmatched armor items to {debug_file_path}")
        except Exception as e:
            logger.error(f"Error writing unmatched armor items to debug file: {str(e)}")
    else:
        logger.info("All armor items successfully matched to armor types")
    
    return parsed_items


def add_weapon_types(parsed_items: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add weapon types to items in the parsed items dictionary.
    
    Args:
        parsed_items: Dictionary of items organized by category
        data: Data dictionary containing weapon types information
    
    Returns:
        Dictionary with weapon types added to items
    """
    # Implementation to be added
    logger.info("Weapon type categorization not yet implemented")
    return parsed_items