import copy
from pathlib import Path
from typing import Dict, List, Any, Optional
from utils import logger, write_json


def fill_item_properties(root_dir, version_id, parsed_items: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
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
    try:
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
            import traceback
            logger.debug(traceback.format_exc())
            return {}

        # Execute processing steps with error handling
        try:
            # Add armor types to items
            logger.info("Adding armor types to items...")
            filled_items = fill_armor_items(filled_items, data)
            if not filled_items:
                logger.error("Failed to fill armor items, returning original items")
                return parsed_items
            
            # Add weapon types to items
            logger.info("Adding weapon types to items...")
            filled_items = fill_weapon_items(filled_items, data)
            if not filled_items:
                logger.error("Failed to fill weapon items, returning items with armor types only")
                return filled_items
            
            # Add dice information to items
            logger.info("Adding dice information to items...")
            filled_items = fill_dice_items(filled_items, data)
            if not filled_items:
                logger.error("Failed to fill dice items, returning items with armor and weapon types only")
                return filled_items
            
            # Add dice badge types to items
            logger.info("Adding dice badge types to items...")
            filled_items = fill_dice_badge_types(filled_items, data)
            if not filled_items:
                logger.error("Failed to fill dice badge types, returning items with armor, weapon types, and dice info only")
                return filled_items
                
            # Validate results
            armor_items = filled_items.get("Armor", [])
            weapon_items = filled_items.get("Weapons", [])
            dice_items = filled_items.get("Die", [])
            dice_badge_items = filled_items.get("DiceBadge", [])
            logger.info(f"Categorized {len(armor_items)} armor items, {len(weapon_items)} weapon items, {len(dice_items)} dice items, and {len(dice_badge_items)} dice badge items")
            
            return filled_items
            
        except Exception as e:
            logger.error(f"Error during item categorization: {str(e)}")
            import traceback
            logger.debug(traceback.format_exc())
            # Return what we have so far, which is the original items
            return parsed_items
            
    except Exception as e:
        logger.error(f"Critical error in fill_item_properties: {str(e)}")
        import traceback
        logger.debug(traceback.format_exc())
        return {}

def fill_armor_items(filled_items: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fill armor types for items in the filled_items dictionary.
    
    Args:
        filled_items: Dictionary of items organized by category
        data: Data dictionary containing categorization information
        
    Returns:
        Dictionary with filled armor types
    """
    # Extract armor types from data
    armor_types = data.get("armorTypes", [])
    ui_slots = data.get("uiSlots", [])
    categories = data.get("categories", [])
    
    # Initialize counter for statistics
    filled_count = 0
    total_items = len(filled_items.get("Armor", []))
    
    # Iterate through armor items
    for i, armor_item in enumerate(filled_items.get("Armor", [])):
        # Check if the item has a Clothing property
        if not "Clothing" in armor_item:
            logger.info(f"Item {armor_item.get('Name', 'Unknown')} does not have a Clothing property")
            continue
        
        # Get the clothing value for matching
        clothing_value = armor_item["Clothing"]
        matched = False
        
        # Try to match the clothing value with armor type filters
        for armor_type in armor_types:
            filters = armor_type.get("filters", [])
            
            # First attempt: Check if any filter matches the start of the clothing value (standard armor)
            for filter_string in filters:
                if clothing_value.startswith(filter_string):
                    # Found a match, add armor type info
                    armor_item["armorTypeId"] = armor_type["id"]
                    armor_item["armorTypeName"] = armor_type["name"]
                    
                    # Get UI slot info
                    ui_slot_id = armor_type["uiSlot"]
                    for ui_slot in ui_slots:
                        if ui_slot["id"] == ui_slot_id:
                            armor_item["uiSlotId"] = ui_slot_id
                            armor_item["uiSlotName"] = ui_slot["name"]
                            
                            # Get category info
                            category_id = ui_slot.get("uiCategory", -1)
                            for category in categories:
                                if category["id"] == category_id:
                                    armor_item["categoryId"] = category_id
                                    armor_item["categoryName"] = category["name"]
                                    break
                            break
                    
                    filled_count += 1
                    matched = True
                    break
            
            # If not matched yet, try second approach: contains check (for horse items)
            if not matched:
                for filter_string in filters:
                    # Skip very short filters to avoid false positives
                    if len(filter_string) < 3:
                        continue
                        
                    if filter_string in clothing_value:
                        # Found a match using contains, add armor type info
                        armor_item["armorTypeId"] = armor_type["id"]
                        armor_item["armorTypeName"] = armor_type["name"]
                        
                        # Get UI slot info
                        ui_slot_id = armor_type["uiSlot"]
                        for ui_slot in ui_slots:
                            if ui_slot["id"] == ui_slot_id:
                                armor_item["uiSlotId"] = ui_slot_id
                                armor_item["uiSlotName"] = ui_slot["name"]
                                
                                # Get category info
                                category_id = ui_slot.get("uiCategory", -1)
                                for category in categories:
                                    if category["id"] == category_id:
                                        armor_item["categoryId"] = category_id
                                        armor_item["categoryName"] = category["name"]
                                        break
                                break
                        
                        filled_count += 1
                        matched = True
                        break
            
            if matched:
                break
        
        if not matched:
            logger.info(f"Could not find armor type for item {armor_item.get('DisplayName', 'Unknown')} with clothing {clothing_value}")
    
    logger.debug(f"Filled armor types for {filled_count} items out of {total_items} total armor items")
    
    return filled_items

def fill_weapon_items(filled_items: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fill weapon types for items in the filled_items dictionary.
    
    Args:
        filled_items: Dictionary of items organized by category
        data: Data dictionary containing categorization information
        
    Returns:
        Dictionary with filled weapon types
    """
    # Extract weapon types from data
    weapon_types = data.get("weaponTypes", [])
    ui_slots = data.get("uiSlots", [])
    categories = data.get("categories", [])
    
    # Initialize counter for statistics
    filled_count = 0
    total_items = len(filled_items.get("Weapons", []))
    
    # Iterate through weapon items
    for i, weapon_item in enumerate(filled_items.get("Weapons", [])):
        # Check if the item has a Class property
        if not "Class" in weapon_item:
            logger.info(f"Item {weapon_item.get('DisplayName', 'Unknown')} does not have a Class property")
            continue
        
        # Get the class value for matching
        class_value = weapon_item["Class"]
        matched = False
        
        # Try to match the class value with weapon type ids
        for weapon_type in weapon_types:
            if str(weapon_type["id"]) == str(class_value):
                # Found a match, add weapon type info
                weapon_item["weaponTypeId"] = weapon_type["id"]
                weapon_item["weaponTypeName"] = weapon_type["name"]
                
                # Get UI slot info
                ui_slot_id = weapon_type["uiSlot"]
                for ui_slot in ui_slots:
                    if ui_slot["id"] == ui_slot_id:
                        weapon_item["uiSlotId"] = ui_slot_id
                        weapon_item["uiSlotName"] = ui_slot["name"]
                        
                        # Get category info
                        category_id = ui_slot.get("uiCategory", -1)
                        for category in categories:
                            if category["id"] == category_id:
                                weapon_item["categoryId"] = category_id
                                weapon_item["categoryName"] = category["name"]
                                break
                        break
                
                filled_count += 1
                matched = True
                break
        
        if not matched:
            logger.info(f"Could not find weapon type for item {weapon_item.get('DisplayName', 'Unknown')} with class {class_value}")
    
    logger.debug(f"Filled weapon types for {filled_count} items out of {total_items} total weapon items")
    
    return filled_items

def fill_dice_items(filled_items: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fill dice items with category information.
    
    Args:
        filled_items: Dictionary of items organized by category
        data: Data dictionary containing categorization information
        
    Returns:
        Dictionary with filled dice items
    """
    # Get the categories from data
    categories = data.get("categories", [])
    
    # Find the dice category
    dice_category = None
    for category in categories:
        if category["name"] == "dice":
            dice_category = category
            break
    
    if not dice_category:
        logger.error("Could not find dice category in data")
        return None
    
    # Initialize counter for statistics
    filled_count = 0
    total_items = len(filled_items.get("Die", []))
    
    # Iterate through dice items
    for i, dice_item in enumerate(filled_items.get("Die", [])):
        # Add category info
        dice_item["categoryId"] = dice_category["id"]
        dice_item["categoryName"] = dice_category["name"]
        filled_count += 1
    
    logger.debug(f"Filled category for {filled_count} items out of {total_items} total dice items")
    
    return filled_items

def fill_dice_badge_types(filled_items: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fill dice badge items with type, subtype and category information.
    
    Args:
        filled_items: Dictionary of items organized by category
        data: Data dictionary containing categorization information
        
    Returns:
        Dictionary with filled dice badge items
    """
    # Get the categories and badge type information from data
    categories = data.get("categories", [])
    badge_types = data.get("diceBadges", {}).get("types", [])
    badge_subtypes = data.get("diceBadges", {}).get("subtypes", [])
    
    # Find the dice badge category
    dice_badge_category = None
    for category in categories:
        if category["name"] == "diceBadge":
            dice_badge_category = category
            break
    
    if not dice_badge_category:
        logger.error("Could not find diceBadge category in data")
        return None
    
    # Initialize counter for statistics
    filled_count = 0
    total_items = len(filled_items.get("DiceBadge", []))
    
    # Iterate through dice badge items
    for i, badge_item in enumerate(filled_items.get("DiceBadge", [])):
        # Check if Type and SubType exist
        if "Type" not in badge_item or "SubType" not in badge_item:
            logger.info(f"Item {badge_item.get('DisplayName', 'Unknown')} missing Type or SubType")
            continue
        
        # Rename Type/SubType to badgeTypeId/badgeSubTypeId
        badge_item["badgeTypeId"] = badge_item.pop("Type")
        badge_item["badgeSubTypeId"] = badge_item.pop("SubType")
        
        # Find and add badge type name
        badge_type_name = "Unknown"
        for badge_type in badge_types:
            if str(badge_type["id"]) == str(badge_item["badgeTypeId"]):
                badge_type_name = badge_type["name"]
                break
        badge_item["badgeTypeName"] = badge_type_name
        
        # Find and add badge subtype name
        badge_subtype_name = "Unknown"
        for badge_subtype in badge_subtypes:
            if str(badge_subtype["id"]) == str(badge_item["badgeSubTypeId"]):
                badge_subtype_name = badge_subtype["name"]
                break
        badge_item["badgeSubTypeName"] = badge_subtype_name
        
        # Add category info
        badge_item["categoryId"] = dice_badge_category["id"]
        badge_item["categoryName"] = dice_badge_category["name"]
        
        filled_count += 1
    
    logger.debug(f"Filled types for {filled_count} items out of {total_items} total dice badge items")
    
    return filled_items