import copy
import math
from pathlib import Path
from typing import Dict, List, Any, Optional
from utils import logger, write_json


def process_items(root_dir: Path, version_id: str, filled_items: Dict[str, Any], data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Process items from filled_items.json into a unified array according to keys.template.
    
    Args:
        root_dir: Path to the root directory
        version_id: Version identifier string
        filled_items: Dictionary of items with filled properties
        data: Data dictionary containing categorization information
        
    Returns:
        Array of processed items
    """
    try:
        # Input validation
        if not filled_items:
            logger.error("No filled items data provided")
            return []
            
        version_dir = root_dir / "data" / "version" / version_id
        logger.info("Processing items into final structure...")

        # Initialize the items array
        items_array = []
        
        # Process each category of items
        total_count = 0
        category_counts = {}
        
        for category, items_list in filled_items.items():
            count = len(items_list)
            logger.info(f"Processing {count} {category} items")
            category_counts[category] = count
            total_count += count
            
            for item in items_list:
                processed_item = process_single_item(item, category)
                items_array.append(processed_item)
        
        # Check if we have items after processing
        processed_count = len(items_array)
        if processed_count == 0:
            logger.error("No items found after processing")
            return []
        
        logger.info(f"Successfully processed {processed_count} items out of {total_count} total items")
        logger.info(f"Items by category: {category_counts}")
        
        items_array.sort(key=lambda x: x["displayName"])

        return items_array
            
    except Exception as e:
        logger.error(f"Critical error in process_items: {str(e)}")
        import traceback
        logger.debug(traceback.format_exc())
        return []


def safe_int(value):
    """Safely convert a value to integer."""
    try:
        if value is None or value == "" or (isinstance(value, str) and value.lower() == "n/a"):
            return 0
        return int(float(value))
    except (ValueError, TypeError):
        return 0


def safe_float(value):
    """Safely convert a value to float."""
    try:
        if value is None or value == "" or (isinstance(value, str) and value.lower() == "n/a"):
            return 0.0
        return float(value)
    except (ValueError, TypeError):
        return 0.0


def round_up_half(value):
    """Round a number, with .5 always rounded up."""
    return math.floor(value + 0.5)


def process_single_item(item, category):
    """
    Process a single item according to keys.template rules.
    
    Args:
        item: The original item data
        category: Item category (Armor, Weapons, Die, DiceBadge)
        
    Returns:
        A processed item dictionary
    """
    processed = {}
    
    # Base properties
    processed["id"] = item.get("Id", "")
    processed["name"] = item.get("Name", "")
    processed["displayName"] = item.get("DisplayName", "")
    processed["uiName"] = item.get("UIName", "")
    processed["iconId"] = item.get("IconId", "")
    processed["uiInfo"] = item.get("UIInfo", "")
    
    # Category information
    if "categoryId" in item:
        processed["categoryId"] = safe_int(item["categoryId"])
    if "categoryName" in item:
        processed["categoryName"] = item["categoryName"]
        processed["category"] = item["categoryName"].lower()
    
    # UI Slot information
    if "uiSlotId" in item:
        processed["uiSlotId"] = safe_int(item["uiSlotId"])
    if "uiSlotName" in item:
        processed["uiSlotName"] = item["uiSlotName"]
    
    # Type-specific attributes
    if category == "Armor" and "armorTypeId" in item and "armorTypeName" in item:
        processed["armorTypeId"] = safe_int(item["armorTypeId"])
        processed["armorTypeName"] = item["armorTypeName"]
    
    elif category == "Weapons" and "weaponTypeId" in item and "weaponTypeName" in item:
        processed["weaponTypeId"] = safe_int(item["weaponTypeId"])
        processed["weaponTypeName"] = item["weaponTypeName"]
        
        # Add ammo info for ranged weapons
        if "ammo" in item:
            processed["ammo"] = item["ammo"]
    
    elif category == "DiceBadge":
        if "badgeTypeId" in item:
            processed["badgeTypeId"] = safe_int(item["badgeTypeId"])
        if "badgeTypeName" in item:
            processed["badgeTypeName"] = item["badgeTypeName"]
        if "badgeSubTypeId" in item:
            processed["badgeSubTypeId"] = safe_int(item["badgeSubTypeId"])
        if "badgeSubTypeName" in item:
            processed["badgeSubTypeName"] = item["badgeSubTypeName"]
    
    # Other properties
    if "Clothing" in item:
        processed["clothing"] = item["Clothing"]
    
    if "NumberOfQuickSlots" in item:
        processed["slots"] = safe_int(item["NumberOfQuickSlots"])
    
    # Dice-specific array properties
    if "SideWeights" in item and item["SideWeights"]:
        try:
            processed["sideWeights"] = [safe_int(w) for w in item["SideWeights"].split()]
        except Exception:
            processed["sideWeights"] = []
    
    if "SideValues" in item and item["SideValues"]:
        try:
            processed["sideValues"] = [safe_int(v) for v in item["SideValues"].split()]
        except Exception:
            processed["sideValues"] = []
    
    # Stats object
    stats = {}
    
    # Basic stats with direct mapping
    if "Weight" in item:
        stats["weight"] = round_up_half(safe_float(item["Weight"]) * 10) / 10  # Keep 1 decimal place
    
    if "Price" in item:
        stats["price"] = round_up_half(safe_float(item["Price"]) * 0.1)
    
    if "MaxQuality" in item:
        stats["maxQuality"] = safe_int(item["MaxQuality"])
    
    if "MaxStatus" in item:
        stats["durability"] = safe_int(item["MaxStatus"])
    
    if "StrReq" in item:
        stats["strReq"] = safe_int(item["StrReq"])
    
    if "AgiReq" in item:
        stats["agiReq"] = safe_int(item["AgiReq"])
    
    if "Charisma" in item:
        stats["charisma"] = safe_int(item["Charisma"])
    
    # Stats with calculations
    if "Conspicuousness" in item:
        conspicuousness = 50 + (safe_float(item["Conspicuousness"]) * 50)
        stats["conspicuousness"] = round_up_half(conspicuousness)
    
    if "Noise" in item:
        noise = safe_float(item["Noise"]) * 100
        stats["noise"] = round_up_half(noise)
    
    if "Visibility" in item:
        visibility = 50 + (safe_float(item["Visibility"]) * 50)
        stats["visibility"] = round_up_half(visibility)
    
    # Defense stats
    if "Defense" in item:
        stats["defense"] = safe_int(item["Defense"])
    
    if "DefenseSlash" in item:
        stats["defenseSlash"] = safe_int(item["DefenseSlash"])
    
    if "DefenseSmash" in item:
        stats["defenseSmash"] = safe_int(item["DefenseSmash"])
    
    if "DefenseStab" in item:
        stats["defenseStab"] = safe_int(item["DefenseStab"])
    
    # Attack stats and calculations
    if "Attack" in item:
        attack = safe_int(item["Attack"])
        stats["attack"] = attack
        
        # Attack modifiers
        if "AttackModSlash" in item:
            mod_slash = safe_float(item["AttackModSlash"])
            stats["attackModSlash"] = mod_slash
            stats["attackSlash"] = round_up_half(attack * mod_slash)
        
        if "AttackModSmash" in item:
            mod_smash = safe_float(item["AttackModSmash"])
            stats["attackModSmash"] = mod_smash
            stats["attackSmash"] = round_up_half(attack * mod_smash)
        
        if "AttackModStab" in item:
            mod_stab = safe_float(item["AttackModStab"])
            stats["attackModStab"] = mod_stab
            stats["attackStab"] = round_up_half(attack * mod_stab)
    
    # Add stats to processed item if any exist
    if stats:
        processed["stats"] = stats
    
    return processed
