import copy
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union
from utils import logger, write_json


def parse_items(root_dir: Path, version_id: str, combined_items: Dict[str, Any], text_ui_items: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
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
    version_dir = root_dir / "data" / "version" / version_id

    # Input validation
    if not combined_items:
        logger.error("No combined items data provided")
        return {}
        
    if not text_ui_items:
        logger.warning("No text UI items data provided, display names will be missing")
    
    try:
        # Create copies of the dictionaries to avoid modifying the originals
        parsed_items = copy.deepcopy(combined_items)
        ui_text = copy.deepcopy(text_ui_items)
        
        # Execute processing steps with error handling
        try:
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
            
            logger.info("Fixing aliases...")
            parsed_items = fix_alias(parsed_items)

            # Remove Item Alias category if it still exists
            if "ItemAlias" in parsed_items:
                logger.info("Removing ItemAlias category with unresolved aliases...")
                del parsed_items["ItemAlias"]
            
            logger.info("Condensing categories...")
            parsed_items = condense_categories(parsed_items)
            
            logger.info("Removing unnecessary items...")
            parsed_items = remove_items(parsed_items)

            logger.info("Adding display names to items...")
            parsed_items = add_display_names(parsed_items, ui_text)

            # Armor and weapon types are now handled in categorize_items.py
            # We'll call that function from main.py after this one
            
            # Validate final data structure
            category_counts = {category: len(items) for category, items in parsed_items.items()}
            logger.info(f"Final category counts: {category_counts}")
            total_items = sum(category_counts.values())
            logger.info(f"Total items after processing: {total_items}")
            
            if total_items == 0:
                logger.warning("No items remain after processing! Check for errors.")

        except Exception as e:
            logger.error(f"Error during item processing: {str(e)}")
            import traceback
            logger.debug(traceback.format_exc())
            # Continue with what we have so far
        
        # Save processed data for debugging and versioning
        try:
            write_json(debug_dir / "parsed_items.json", parsed_items)
            write_json(version_dir / "parsed_items.json", parsed_items)
        except Exception as e:
            logger.error(f"Error writing debug JSON: {str(e)}")

        return parsed_items
        
    except Exception as e:
        logger.error(f"Critical error in parse_items: {str(e)}")
        import traceback
        logger.debug(traceback.format_exc())
        return {}


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
            
        if not isinstance(items, list):
            logger.warning(f"Category {category} is not a list - skipping")
            continue
            
        for item_data in items:
            if isinstance(item_data, dict) and "Id" in item_data and "Name" in item_data:
                source_id_map[item_data["Id"]] = (category, item_data)
    
    # Process each alias item
    if not isinstance(parsed_items["ItemAlias"], list):
        logger.warning("ItemAlias is not a list - skipping alias processing")
        return parsed_items
        
    # Keep track of aliases to remove
    aliases_to_keep = []
    
    # Process each alias item
    for alias_data in parsed_items["ItemAlias"]:
        if not isinstance(alias_data, dict) or "SourceItemId" not in alias_data or "Name" not in alias_data:
            aliases_to_keep.append(alias_data)  # Keep invalid aliases for now
            continue
            
        alias_name = alias_data["Name"]
        source_id = alias_data["SourceItemId"]
        
        # Look up source item in our map
        source_info = source_id_map.get(source_id)
        
        if source_info is None:
            logger.debug(f"Source item with ID '{source_id}' not found for alias '{alias_name}'")
            missing_count += 1
            aliases_to_keep.append(alias_data)  # Keep aliases with missing sources
            continue
            
        source_category, source_item = source_info
            
        # Create a deep copy of the source item
        merged_item = dict(source_item)
        
        # Override with the alias properties (except SourceItemId)
        for key, value in alias_data.items():
            if key != "SourceItemId":
                merged_item[key] = value
        
        # Move the alias to the same category as its source
        parsed_items[source_category].append(merged_item)
        
        moved_count += 1
        alias_count += 1
    
    # Replace ItemAlias with only the aliases we want to keep
    parsed_items["ItemAlias"] = aliases_to_keep
    
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

        # Ensure target category exists and is a list
        if target_category not in parsed_items:
            parsed_items[target_category] = []
            
        for category in source_categories:
            if category == target_category:
                continue  # Don't merge a category into itself
                
            if category in parsed_items:
                # Skip if not a list
                if not isinstance(parsed_items[category], list):
                    logger.warning(f"Category {category} is not a list - skipping")
                    continue
                    
                # Count items being merged
                category_item_count = len(parsed_items[category])
                condensed_item_counts[target_category] = condensed_item_counts.get(target_category, 0) + category_item_count
                
                # Merge the items - extend the target list with source list
                parsed_items[target_category].extend(parsed_items[category])
                
                # Remove the source category
                del parsed_items[category]
                
                logger.debug(f"Merged {category_item_count} items from {category} into {target_category}")

    # Log summary of condensation
    for category, count in condensed_item_counts.items():
        if count > 0:
            logger.info(f"Condensed {count} items into {category} category")
    
    # Move "Weapons" category to the first key in the dictionary
    if "Weapons" in parsed_items:
        weapons_data = parsed_items.pop("Weapons")
        parsed_items = {"Weapons": weapons_data, **parsed_items}

    return parsed_items

def remove_items(parsed_items: Dict[str, Any]) -> Dict[str, Any]:
    """
    Remove items that are not needed or are duplicates.
    
    Args:
        parsed_items: Dictionary of items organized by category

    Returns:
        Dictionary with unnecessary items removed
    """
    # Define word filters for item names
    key_filters = [
        "_empty", "duel", "_broken", "torch"
    ]

    icon_filters = [ #IconId
        "trafficCone"
    ]

    ui_name_filters = [ #UIName
        "_warning"
    ]
    
    # Define key-value pairs to filter out
    kv_filters = [
        {"key": "SubClass", "value": "5"},
        # Add more key-value filters as needed
    ]
    
    # Counters for logging
    removed_counts = {
        "key_filter": 0,
        "icon_filter": 0,
        "ui_name_filter": 0,
        "kv_filter": 0
    }

    for category, items in list(parsed_items.items()):
        # Skip if not a list
        if not isinstance(items, list):
            logger.warning(f"Category {category} is not a list - skipping")
            continue
            
        # Create a new list to keep only the items we want
        filtered_items = []
        
        for item in items:
            # Skip non-dictionary items
            if not isinstance(item, dict) or "Name" not in item:
                filtered_items.append(item)  # Keep items without Name
                continue
                
            item_name = item["Name"]
            should_keep = True
            
            # Check key-value filters
            for kv_filter in kv_filters:
                filter_key = kv_filter["key"]
                filter_value = kv_filter["value"]
                
                if filter_key in item and str(item[filter_key]) == filter_value:
                    should_keep = False
                    removed_counts["kv_filter"] += 1
                    break
            
            # Check other filters if the item wasn't already flagged for removal
            if should_keep:
                if any(filter_word.lower() in item_name.lower() for filter_word in key_filters):
                    should_keep = False
                    removed_counts["key_filter"] += 1
                elif any(filter_word.lower() in item.get("IconId", "").lower() for filter_word in icon_filters):
                    should_keep = False
                    removed_counts["icon_filter"] += 1
                elif any(filter_word.lower() in item.get("UIName", "").lower() for filter_word in ui_name_filters):
                    should_keep = False
                    removed_counts["ui_name_filter"] += 1
            
            # Keep the item if it passed all filters
            if should_keep:
                filtered_items.append(item)
        
        # Replace the original list with the filtered list
        parsed_items[category] = filtered_items

    # Log results
    total_removed = sum(removed_counts.values())
    if total_removed > 0:
        logger.info(f"Removed {total_removed} items total:")
        for filter_type, count in removed_counts.items():
            if count > 0:
                if filter_type == "kv_filter":
                    kv_details = ", ".join([f"{kv['key']}={kv['value']}" for kv in kv_filters])
                    logger.info(f"  - {count} items with {kv_details}")
                else:
                    logger.info(f"  - {count} items by {filter_type.replace('_', ' ')}")

    return parsed_items

def add_display_names(parsed_items: Dict[str, Any], ui_text: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add display names to items based on their UIName or other properties.
    Properly capitalizes display names including handling apostrophes.
    
    Args:
        parsed_items: Dictionary of items organized by category
        ui_text: Dictionary containing text UI items
    
    Returns:
        Dictionary with display names added to items
    """
    items_processed = 0
    display_names_found = 0
    display_names_missing = 0
    
    def proper_title_case(text: str) -> str:
        """
        Properly capitalize text while respecting apostrophes and other punctuation.
        Ensures "servant's hood" becomes "Servant's Hood" not "Servant'S Hood".
        """
        # Handle empty strings
        if not text:
            return text
            
        # Split the text into words
        words = text.split()
        # Process each word to properly capitalize it
        capitalized_words = []
        
        for word in words:
            if not word:
                capitalized_words.append(word)
                continue
                
            # If word contains apostrophe, handle specially
            apostrophe_pos = word.find("'")
            if apostrophe_pos > 0 and apostrophe_pos < len(word) - 1:
                # Capitalize only the first part before the apostrophe
                word = word[0].upper() + word[1:apostrophe_pos+1] + word[apostrophe_pos+1].lower() + word[apostrophe_pos+2:]
            else:
                # Normal case: capitalize first letter, lowercase the rest
                word = word[0].upper() + word[1:].lower()
                
            capitalized_words.append(word)
            
        return " ".join(capitalized_words)
    
    # Iterate through all categories
    for category, items in parsed_items.items():
        # Skip if not a list
        if not isinstance(items, list):
            logger.warning(f"Category {category} is not a list - skipping")
            continue
        
        # Iterate through all items in the category
        for item in items:
            items_processed += 1
            
            # Skip if not a dictionary or doesn't have UIName
            if not isinstance(item, dict) or "UIName" not in item:
                # Set DisplayName to null for items without UIName
                if isinstance(item, dict):
                    item["DisplayName"] = "Null"
                    display_names_missing += 1
                continue
            
            ui_name = item["UIName"]
            
            # Try to find the UI name in the text dictionary
            if ui_name in ui_text:
                # Get the text array
                text_array = ui_text[ui_name]
                
                # Use the second element if available, otherwise use the first
                if len(text_array) > 1:
                    display_name = text_array[1]
                elif len(text_array) == 1:
                    display_name = text_array[0]
                else:
                    display_name = "Null"
                
                # Apply our improved title case function
                display_name = proper_title_case(display_name)
                
                # Set the display name in the item data
                item["DisplayName"] = display_name
                display_names_found += 1
            else:
                # Set DisplayName to null if no match found
                item["DisplayName"] = "Null"
                display_names_missing += 1
    
    # Log the results
    logger.info(f"Processed {items_processed} items")
    logger.info(f"Found display names for {display_names_found} items")
    logger.info(f"Missing display names for {display_names_missing} items")
    
    return parsed_items