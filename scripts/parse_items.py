import copy
import constants as const
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union
from utils import logger, write_json


def parse_items(root_dir: Path, version_id: str, combined_items: Dict[str, Any], text_ui_items: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process and transform items data from XML-derived dictionaries.
    
    Args:
        root_dir: Project root directory path
        version_id: Version identifier (e.g. "1_2")
        combined_items: Dictionary containing combined items data
        text_ui_items: Dictionary containing text UI items data
    
    Returns:
        Dictionary of processed items organized by category
    """
    logger.info("Parsing items...")
    debug_dir = root_dir / "logs" / "debug"

    # Create copies of the dictionaries to avoid modifying the originals
    parsed_items = copy.deepcopy(combined_items)
    ui_text = copy.deepcopy(text_ui_items)  # Not used yet, but kept for future expansion

    # Remove unwanted item categories
    item_classes_to_remove = [
        "AlchemyBase", "Ammo", "CraftingMaterial", "Document", "Food", 
        "Herb", "MiscItem", "NPCTool", "Ointment", "PickableItem", "Poison"
    ]
    for item_class in item_classes_to_remove:
        if item_class in parsed_items:
            del parsed_items[item_class]

    # Process items data in steps
    logger.info("Removing @ symbol from keys...")
    parsed_items = remove_at_signs(parsed_items)
    
    logger.info("Transforming named lists...")
    parsed_items = transform_named_lists(parsed_items)

    logger.info("Fixing aliases...")
    parsed_items = fix_alias(parsed_items)

    # Remove Item Alias category if it still exists
    if "ItemAlias" in parsed_items:
        logger.info("Removing ItemAlias category with unresolved aliases...")
        del parsed_items["ItemAlias"]
    
    logger.info("Condensing categories...")
    parsed_items = condense_categories(parsed_items)
    
    # Save processed data for debugging
    write_json(debug_dir / "parsed_items.json", parsed_items, indent=4)

    return parsed_items


def remove_at_signs(obj: Any) -> Any:
    """
    Recursively remove '@' prefix from dictionary keys.
    
    Args:
        obj: Object to process (can be dict, list, or primitive value)
        
    Returns:
        Object with '@' signs removed from dictionary keys
    """
    if isinstance(obj, dict):
        return {key.lstrip('@'): remove_at_signs(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [remove_at_signs(item) for item in obj]
    else:
        return obj


def transform_named_lists(obj: Any) -> Any:
    """
    Convert lists of objects with "Name" fields to dictionaries.
    
    This transforms structures like:
    [{"Name": "item1", "Value": 10}, {"Name": "item2", "Value": 20}]
    
    Into:
    {"item1": {"Value": 10}, "item2": {"Value": 20}}
    
    Args:
        obj: Object to transform (can be dict, list, or primitive value)
        
    Returns:
        Transformed object with named lists converted to dictionaries
    """
    if isinstance(obj, dict):
        return {
            k: transform_named_lists(v)
            for k, v in obj.items()
        }
    elif isinstance(obj, list):
        # Check if every item is a dict and contains "Name"
        if all(isinstance(item, dict) and "Name" in item for item in obj):
            return {
                item["Name"]: transform_named_lists({k: v for k, v in item.items() if k != "Name"})
                for item in obj
            }
        else:
            return [transform_named_lists(item) for item in obj]
    else:
        return obj


def fix_alias(parsed_items: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fix aliases in the parsed items by merging source item properties.
    
    For each item in the "ItemAlias" category:
    1. Find its source item using SourceItemId
    2. Copy all properties from the source item
    3. Override with any properties defined in the alias
    4. Move the alias to the same category as its source item
    
    Args:
        parsed_items: Dictionary containing parsed items data
    
    Returns:
        Dictionary with fixed aliases
    """
    # Check if ItemAlias section exists
    if "ItemAlias" not in parsed_items:
        logger.warning("No ItemAlias section found in parsed items")
        return parsed_items
    
    alias_count = 0
    missing_count = 0
    moved_count = 0
    
    # Create source ID mapping for faster lookups
    source_id_map: Dict[str, Tuple[str, Dict[str, Any]]] = {}
    
    # Build a map of all item IDs to their categories and data
    for category, items in parsed_items.items():
        if category == "ItemAlias":
            continue
            
        for item_name, item_data in items.items():
            if isinstance(item_data, dict) and "Id" in item_data:
                source_id_map[item_data["Id"]] = (category, item_data)
    
    # Process each alias item
    for alias_name, alias_data in list(parsed_items["ItemAlias"].items()):
        if "SourceItemId" not in alias_data:
            logger.warning(f"Alias '{alias_name}' has no SourceItemId")
            continue
            
        source_id = alias_data["SourceItemId"]
        
        # Look up source item in our map
        source_info = source_id_map.get(source_id)
        
        if source_info is None:
            logger.debug(f"Source item with ID '{source_id}' not found for alias '{alias_name}'")
            missing_count += 1
            continue
            
        source_category, source_item = source_info
            
        # Create a deep copy of the source item
        merged_item = dict(source_item)
        
        # Override with the alias properties (except SourceItemId)
        for key, value in alias_data.items():
            if key != "SourceItemId":
                merged_item[key] = value
        
        # Move the alias to the same category
        parsed_items[source_category][alias_name] = merged_item
        
        # Remove from ItemAlias category
        del parsed_items["ItemAlias"][alias_name]
        
        moved_count += 1
        alias_count += 1
        
    logger.info(f"Processed {alias_count} aliases: {moved_count} moved to source categories, {missing_count} with missing sources")
        
    return parsed_items


def condense_categories(parsed_items: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge multiple item categories into consolidated categories.
    
    This combines related categories (e.g., different armor types) into a single category
    for easier access and organization.
    
    Args:
        parsed_items: Dictionary of items organized by category
        
    Returns:
        Dictionary with consolidated categories
    """
    categories_to_merge = { 
        "Armor": ["Armor", "Hood", "Helmet", "QuickSlotContainer"],
        "Weapons": ["MeleeWeapon", "MissileWeapon"]
    }

    # Track condensed category counts for logging
    condensed_item_counts = {}

    for target_category, source_categories in categories_to_merge.items():
        if target_category not in condensed_item_counts:
            condensed_item_counts[target_category] = 0

        for category in source_categories:
            if category == target_category:
                continue  # Don't merge a category into itself
                
            if category in parsed_items:
                # Count items being merged
                category_item_count = len(parsed_items[category])
                condensed_item_counts[target_category] += category_item_count
                
                # Ensure target category exists
                if target_category not in parsed_items:
                    parsed_items[target_category] = {}
                    
                # Merge the items
                parsed_items[target_category].update(parsed_items[category])
                
                # Remove the source category
                del parsed_items[category]
                
                logger.debug(f"Merged {category_item_count} items from {category} into {target_category}")

    # Log summary of condensation
    for category, count in condensed_item_counts.items():
        if count > 0:
            logger.info(f"Condensed {count} items into {category} category")

    return parsed_items