from pathlib import Path
from typing import Dict, Optional, Any
from utils import logger, ensure_dir, read_json, write_json
from constants.categories import (
    ITEM_CATEGORIES,
    UI_SLOTS,
    ARMOR_TYPES,
    WEAPON_TYPES, 
    DICE_BADGE_TYPES,
    DICE_BADGE_SUBTYPES
)


def init_data_json(root_dir: Path, version_id: str) -> Optional[Dict[str, Any]]:
    """
    Initialize a fresh data.json file in the version directory,
    based on templates/data.template and populated with constants data.
    
    Args:
        root_dir: Path to the project root directory
        version_id: Version ID (e.g. "1_2")
    
    Returns:
        The initialized data structure or None if initialization failed
    """
    # Construct version directory path and ensure it exists
    version_dir = root_dir / "data" / "version" / version_id
    ensure_dir(version_dir)
    
    # Load the template
    template_path = root_dir / "templates" / "data.template"
    data = read_json(template_path)
    if not data:
        logger.error("Failed to load data template")
        return None
    
    try:
        # 1. Populate with constant data
        # data["iconGroups"] = ICON_CATEGORIES
        data["categories"] = ITEM_CATEGORIES
        data["uiSlots"] = UI_SLOTS
        data["weaponTypes"] = WEAPON_TYPES
        data["armorTypes"] = ARMOR_TYPES
        data["diceBadges"]["types"] = DICE_BADGE_TYPES
        data["diceBadges"]["subtypes"] = DICE_BADGE_SUBTYPES
        
        logger.debug("Populated data with constants:")
        # logger.debug(f"- {len(ICON_CATEGORIES)} icon categories")
        logger.debug(f"- {len(ITEM_CATEGORIES)} item categories")
        logger.debug(f"- {len(UI_SLOTS)} UI slots")
        logger.debug(f"- {len(WEAPON_TYPES)} weapon types")
        logger.debug(f"- {len(ARMOR_TYPES)} armor types")
        logger.debug(f"- {len(DICE_BADGE_TYPES)} dice badge types")
        logger.debug(f"- {len(DICE_BADGE_SUBTYPES)} dice badge subtypes")
        
        # 2. Load filters from config/filters.json
        filters_path = root_dir / "config" / "filters.json"
        filters = read_json(filters_path)
        if not filters:
            logger.warning("Failed to load filters, armor types will have empty filters")
        else:
            logger.debug(f"Loaded {len(filters)} armor type filters")
            
            # Populate the armor types with the appropriate filters
            for armor_type in data.get("armorTypes", []):
                if "name" in armor_type and armor_type["name"] in filters:
                    armor_type["filters"] = filters[armor_type["name"]]
                    logger.debug(f"Added {len(armor_type['filters'])} filters to {armor_type['name']}")
        
        # 3. Load version info from version.json
        version_json_path = root_dir / "data" / "version.json"
        version_data = read_json(version_json_path)
        
        if version_data and "latest" in version_data:
            latest_data = version_data["latest"]
            
            # Update the version in the data
            data["version"] = {
                "id": latest_data.get("Id", 0),
                "name": latest_data.get("Name", ""),
                "branch": latest_data.get("Branch", {}).get("Name", ""),
                "platform": latest_data.get("Platform", {}).get("Name", "")
            }
            
            logger.debug(f"Updated version info: {data['version']}")
        
        # Save the initialized data
        data_path = version_dir / "data.json"
        if write_json(data_path, data):
            logger.info(f"Saved data to {data_path}")
            return data
        return None
        
    except Exception as e:
        logger.error(f"Error initializing data: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return None