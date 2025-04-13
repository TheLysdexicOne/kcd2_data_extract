import copy
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

from utils import logger, write_json


def fill_item_properties(
    root_dir: Path, 
    version_id: str, 
    parsed_items: Dict[str, List[Dict[str, Any]]], 
    data: Dict[str, Any]
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Categorize items by adding armor types and weapon types.
    
    Args:
        root_dir: Path to the root directory
        version_id: Version identifier string
        parsed_items: Dictionary of items organized by category
        data: Data dictionary containing categorization information
        
    Returns:
        Dictionary with categorized items or empty dict if error occurred
    """
    # Input validation
    if not parsed_items:
        logger.error("No parsed items data provided")
        return {}
        
    if not data:
        logger.error("No categorization data provided")
        return {}
        
    version_dir = root_dir / "data" / "version" / version_id
    logger.info("Categorizing items...")

    # Create a deep copy to avoid modifying the original
    try:
        filled_items = copy.deepcopy(parsed_items)
    except Exception as e:
        logger.error(f"Failed to create a deep copy of parsed_items: {str(e)}")
        logger.debug(traceback.format_exc())
        return {}

    # Processing steps with detailed error handling
    processing_steps = [
        ("armor types", fill_armor_items, "armor"),
        ("weapon types", fill_weapon_items, "armor types"),
        ("dice information", fill_dice_items, "armor and weapon types"),
        ("dice badge types", fill_dice_badge_types, "armor, weapon types, and dice info")
    ]
    
    try:
        for step_name, step_func, previous_steps in processing_steps:
            logger.info(f"Adding {step_name} to items...")
            result = step_func(filled_items, data)
            if not result:
                logger.error(f"Failed to fill {step_name}, returning items with {previous_steps} only")
                return filled_items
            filled_items = result
            
        # Validate results
        item_counts = {
            "Armor": len(filled_items.get("Armor", [])),
            "Weapons": len(filled_items.get("Weapons", [])),
            "Die": len(filled_items.get("Die", [])),
            "DiceBadge": len(filled_items.get("DiceBadge", []))
        }
        
        count_str = ", ".join([f"{count} {category.lower()} items" 
                              for category, count in item_counts.items()])
        logger.info(f"Categorized {count_str}")
        
        return filled_items
        
    except Exception as e:
        logger.error(f"Error during item categorization: {str(e)}")
        import traceback
        logger.debug(traceback.format_exc())
        return parsed_items


def add_type_info(
    item: Dict[str, Any], 
    type_info: Dict[str, Any], 
    ui_slots: List[Dict[str, Any]], 
    categories: List[Dict[str, Any]],
    type_prefix: str
) -> None:
    """Helper function to add type, UI slot, and category information to an item."""
    # Add type info
    item[f"{type_prefix}TypeId"] = type_info["id"]
    item[f"{type_prefix}TypeName"] = type_info["name"]
    
    # Get UI slot info
    ui_slot_id = type_info["uiSlot"]
    for ui_slot in ui_slots:
        if ui_slot["id"] == ui_slot_id:
            item["uiSlotId"] = ui_slot_id
            item["uiSlotName"] = ui_slot["name"]
            
            # Get category info
            category_id = ui_slot.get("uiCategory", -1)
            for category in categories:
                if category["id"] == category_id:
                    item["categoryId"] = category_id
                    item["categoryName"] = category["name"]
                    break
            break


def fill_armor_items(
    filled_items: Dict[str, List[Dict[str, Any]]], 
    data: Dict[str, Any]
) -> Optional[Dict[str, List[Dict[str, Any]]]]:
    """
    Fill armor types for items in the filled_items dictionary.
    
    Args:
        filled_items: Dictionary of items organized by category
        data: Data dictionary containing categorization information
        
    Returns:
        Dictionary with filled armor types or None if error occurred
    """
    # Extract data
    armor_types = data.get("armorTypes", [])
    ui_slots = data.get("uiSlots", [])
    categories = data.get("categories", [])
    
    # Statistics
    filled_count = 0
    total_items = len(filled_items.get("Armor", []))
    
    # Process each armor item
    for armor_item in filled_items.get("Armor", []):
        # Skip items without Clothing property
        if "Clothing" not in armor_item:
            logger.debug(f"Item {armor_item.get('Name', 'Unknown')} does not have a Clothing property")
            continue
        
        clothing_value = armor_item["Clothing"]
        matched = False
        
        # Try to match using different strategies
        for armor_type in armor_types:
            filters = armor_type.get("filters", [])
            
            # Strategy 1: Prefix matching (standard armor)
            for filter_string in filters:
                if clothing_value.startswith(filter_string):
                    add_type_info(armor_item, armor_type, ui_slots, categories, "armor")
                    filled_count += 1
                    matched = True
                    break
            
            # Strategy 2: Contains matching (for horse items and others)
            if not matched:
                for filter_string in filters:
                    if len(filter_string) < 3:
                        continue  # Skip short filters to avoid false positives
                        
                    if filter_string in clothing_value:
                        add_type_info(armor_item, armor_type, ui_slots, categories, "armor")
                        filled_count += 1
                        matched = True
                        break
            
            if matched:
                break
        
        if not matched:
            logger.debug(f"Could not find armor type for item {armor_item.get('DisplayName', 'Unknown')} with clothing {clothing_value}")
    
    logger.info(f"Filled armor types for {filled_count}/{total_items} armor items")
    
    return filled_items


def fill_weapon_items(
    filled_items: Dict[str, List[Dict[str, Any]]], 
    data: Dict[str, Any]
) -> Optional[Dict[str, List[Dict[str, Any]]]]:
    """
    Fill weapon types for items in the filled_items dictionary.
    
    Args:
        filled_items: Dictionary of items organized by category
        data: Data dictionary containing categorization information
        
    Returns:
        Dictionary with filled weapon types or None if error occurred
    """
    # Extract data
    weapon_types = data.get("weaponTypes", [])
    ui_slots = data.get("uiSlots", [])
    categories = data.get("categories", [])
    
    # Statistics
    filled_count = 0
    total_items = len(filled_items.get("Weapons", []))
    
    # Process each weapon item
    for weapon_item in filled_items.get("Weapons", []):
        # Skip items without Class property
        if "Class" not in weapon_item:
            logger.debug(f"Item {weapon_item.get('DisplayName', 'Unknown')} does not have a Class property")
            continue
        
        class_value = weapon_item["Class"]
        matched = False
        
        # Match class value with weapon type ids
        for weapon_type in weapon_types:
            if str(weapon_type["id"]) == str(class_value):
                add_type_info(weapon_item, weapon_type, ui_slots, categories, "weapon")
                filled_count += 1
                matched = True
                break
        
        if not matched:
            logger.debug(f"Could not find weapon type for item {weapon_item.get('DisplayName', 'Unknown')} with class {class_value}")
    
    logger.info(f"Filled weapon types for {filled_count}/{total_items} weapon items")
    
    return filled_items


def fill_dice_items(
    filled_items: Dict[str, List[Dict[str, Any]]], 
    data: Dict[str, Any]
) -> Optional[Dict[str, List[Dict[str, Any]]]]:
    """
    Fill dice items with category information.
    
    Args:
        filled_items: Dictionary of items organized by category
        data: Data dictionary containing categorization information
        
    Returns:
        Dictionary with filled dice items or None if error occurred
    """
    # Find dice category
    categories = data.get("categories", [])
    dice_category = next((c for c in categories if c["name"] == "dice"), None)
    
    if not dice_category:
        logger.error("Could not find dice category in data")
        return None
    
    # Statistics
    filled_count = 0
    total_items = len(filled_items.get("Die", []))
    
    # Add category info to all dice items
    for dice_item in filled_items.get("Die", []):
        dice_item["categoryId"] = dice_category["id"]
        dice_item["categoryName"] = dice_category["name"]
        filled_count += 1
    
    logger.info(f"Filled category for {filled_count}/{total_items} dice items")
    
    return filled_items


def fill_dice_badge_types(
    filled_items: Dict[str, List[Dict[str, Any]]], 
    data: Dict[str, Any]
) -> Optional[Dict[str, List[Dict[str, Any]]]]:
    """
    Fill dice badge items with type, subtype and category information.
    
    Args:
        filled_items: Dictionary of items organized by category
        data: Data dictionary containing categorization information
        
    Returns:
        Dictionary with filled dice badge items or None if error occurred
    """
    # Extract data
    categories = data.get("categories", [])
    badge_types = data.get("diceBadges", {}).get("types", [])
    badge_subtypes = data.get("diceBadges", {}).get("subtypes", [])
    
    # Find dice badge category
    dice_badge_category = next((c for c in categories if c["name"] == "diceBadge"), None)
    
    if not dice_badge_category:
        logger.error("Could not find diceBadge category in data")
        return None
    
    # Statistics
    filled_count = 0
    total_items = len(filled_items.get("DiceBadge", []))
    
    # Process each dice badge item
    for badge_item in filled_items.get("DiceBadge", []):
        # Skip items without required properties
        if "Type" not in badge_item or "SubType" not in badge_item:
            logger.debug(f"Item {badge_item.get('DisplayName', 'Unknown')} missing Type or SubType")
            continue
        
        # Rename Type/SubType to badgeTypeId/badgeSubTypeId
        badge_item["badgeTypeId"] = badge_item.pop("Type")
        badge_item["badgeSubTypeId"] = badge_item.pop("SubType")
        
        # Find and add badge type and subtype names
        badge_item["badgeTypeName"] = next(
            (t["name"] for t in badge_types if str(t["id"]) == str(badge_item["badgeTypeId"])), 
            "Unknown"
        )
        
        badge_item["badgeSubTypeName"] = next(
            (st["name"] for st in badge_subtypes if str(st["id"]) == str(badge_item["badgeSubTypeId"])),
            "Unknown"
        )
        
        # Add category info
        badge_item["categoryId"] = dice_badge_category["id"]
        badge_item["categoryName"] = dice_badge_category["name"]
        
        filled_count += 1
    
    logger.info(f"Filled types for {filled_count}/{total_items} dice badge items")
    
    return filled_items