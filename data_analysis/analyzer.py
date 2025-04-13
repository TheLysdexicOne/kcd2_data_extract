"""
Data analyzer for KCD2 extracted data files.
"""
import json
import os
import re
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Any, Optional, Tuple, cast
import logging

class DataAnalyzer:
    """
    Analyzes data files produced by KCD2 data extraction process.
    Provides statistics, validation, and insights about the data.
    """

    def __init__(self, root_dir: str, version_id: Optional[str] = None, logger: Optional[logging.Logger] = None):
        """
        Initialize the analyzer with the paths to the data files.
        
        Args:
            root_dir: The root directory of the project
            version_id: Optional version ID (e.g. "1_2"). If not provided, uses the latest version
            logger: Optional logger instance
        """
        self.root_dir = Path(root_dir)
        self.logger = logger or logging.getLogger(__name__)
        
        # Find all version directories
        versions_dir = self.root_dir / "data" / "version"
        if not versions_dir.exists():
            self.logger.error(f"Versions directory not found: {versions_dir}")
            self.version_id = None
            self.version_dir = None
            return
            
        # If version_id is not provided, find the latest version
        if not version_id:
            version_id = self._find_latest_version(versions_dir)
            
        self.version_id = version_id
        self.version_dir = versions_dir / version_id if version_id else None
        
        if self.version_dir and not self.version_dir.exists():
            self.logger.error(f"Version directory not found: {self.version_dir}")
            self.version_dir = None
    
    def _find_latest_version(self, versions_dir: Path) -> Optional[str]:
        """
        Find the latest version directory.
        
        Args:
            versions_dir: Path to the versions directory
            
        Returns:
            The latest version ID or None if no versions found
        """
        # Get all directories in the versions directory
        try:
            version_dirs = [d for d in versions_dir.iterdir() if d.is_dir()]
            if not version_dirs:
                self.logger.error(f"No version directories found in {versions_dir}")
                return None
                
            # Sort version directories by semantic versioning logic
            # This handles cases like 1_2, 1_2_5, 1_12 correctly
            sorted_versions = sorted(version_dirs, 
                                     key=lambda x: [int(n) if n.isdigit() else n 
                                                   for n in re.findall(r'\d+|\D+', x.name)])
            latest_version = sorted_versions[-1].name
            self.logger.info(f"Using latest version: {latest_version}")
            return latest_version
            
        except Exception as e:
            self.logger.error(f"Error finding latest version: {e}")
            return None
        
    def load_json_file(self, filename: str) -> Optional[Dict[str, Any]]:
        """Load a JSON file from the version directory."""
        if not self.version_dir:
            self.logger.error("No version directory specified")
            return None
            
        file_path = self.version_dir / filename
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return cast(Dict[str, Any], json.load(f))
        except Exception as e:
            self.logger.error(f"Failed to load {file_path}: {e}")
            return None
            
    def analyze_version(self) -> Dict[str, Any]:
        """
        Analyze the version.json file (output of s01_get_version).
        
        Returns:
            Dict containing analysis results
        """
        # First check the version-specific file
        version_data = self.load_json_file("version.json")
        
        # If not found, try the global version file
        if not version_data:
            global_version_path = self.root_dir / "data" / "version.json"
            try:
                with open(global_version_path, 'r', encoding='utf-8') as f:
                    version_data = json.load(f)
            except Exception as e:
                self.logger.error(f"Failed to load {global_version_path}: {e}")
                return {"error": "Could not load version.json"}
        
        if not version_data:
            return {"error": "Could not load version.json"}
            
        # Extract version info from the data structure
        latest_data = version_data.get("latest", {})
        branch_data = latest_data.get("Branch", {})
        
        analysis = {
            "version_id": self.version_id,
            "version_found": bool(self.version_id),
            "branch_name": branch_data.get("Name"),
            "branch_id": branch_data.get("Id"),
            "timestamp": latest_data.get("UpdateDateTime"),
            "versions_tracked": list(version_data.keys())
        }
        
        return analysis
        
    def analyze_data_json_init(self) -> Dict[str, Any]:
        """
        Analyze the initialized data.json file (output of s02_init_data_json).
        
        Returns:
            Dict containing analysis results
        """
        if not self.version_dir:
            return {"error": "No version directory specified"}
            
        data_json = self.load_json_file("data.json")
        if not data_json:
            return {"error": "Could not load data.json"}
            
        # Analyze the structure of the initialized data.json
        structure = {key: type(value).__name__ for key, value in data_json.items()}
        
        analysis = {
            "contains_version": "version" in data_json,
            "version_value": data_json.get("version"),
            "structure": structure,
            "top_level_keys": list(data_json.keys()),
            "has_items_array": "items" in data_json,
            "items_initialized": bool(data_json.get("items", [])),
        }
        
        return analysis
        
    def analyze_xml_extraction(self) -> Dict[str, Any]:
        """
        Analyze the XML extraction results (output of s03_get_xml).
        
        Returns:
            Dict containing analysis results
        """
        if not self.version_dir:
            return {"error": "No version directory specified"}
            
        combined_dict = self.load_json_file("combined_dict.json")
        text_ui_dict = self.load_json_file("text_ui_dict.json")
        
        if not combined_dict or not text_ui_dict:
            missing = []
            if not combined_dict:
                missing.append("combined_dict.json")
            if not text_ui_dict:
                missing.append("text_ui_dict.json")
            return {"error": f"Could not load: {', '.join(missing)}"}
            
        # Check XML file existence
        xml_path = self.version_dir / "combined_items.xml"
        xml_exists = xml_path.exists()
        
        # XML directory analysis
        xml_dir = self.version_dir / "xml"
        xml_files = list(xml_dir.glob("*.xml")) if xml_dir.exists() else []
        
        analysis = {
            "combined_items_xml_exists": xml_exists,
            "xml_file_count": len(xml_files),
            "combined_dict_item_count": len(combined_dict) if isinstance(combined_dict, dict) else 0,
            "text_ui_dict_item_count": len(text_ui_dict) if isinstance(text_ui_dict, dict) else 0,
            "xml_files": [f.name for f in xml_files],
        }
        
        return analysis
        
    def analyze_parsed_items(self) -> Dict[str, Any]:
        """
        Analyze the parsed items (output of s04_parse_items).
        
        Returns:
            Dict containing analysis results
        """
        if not self.version_dir:
            return {"error": "No version directory specified"}
            
        parsed_items = self.load_json_file("parsed_items.json")
        if not parsed_items:
            return {"error": "Could not load parsed_items.json"}
            
        # Handle different data formats
        is_dict_format = isinstance(parsed_items, dict)
        
        # Count items by category
        item_types: Counter = Counter()
        missing_properties: Dict[str, Counter] = defaultdict(Counter)
        icon_ids: set[str] = set()
        ui_slots: Counter = Counter()
        total_items = 0
        
        if is_dict_format:
            # Check if it's a nested structure with arrays
            has_nested_arrays = any(isinstance(value, list) for value in parsed_items.values())
            
            if has_nested_arrays:
                # Format: {"Category1": [item1, item2, ...], "Category2": [...]}
                for category, items in parsed_items.items():
                    if isinstance(items, list):
                        total_items += len(items)
                        for i, item in enumerate(items):
                            item_id = f"{category}_{i}"
                            if isinstance(item, dict):
                                # Add category to item for analysis
                                item_with_category = item.copy()
                                if "category" not in item_with_category:
                                    item_with_category["category"] = category
                                if "itemType" not in item_with_category:
                                    item_with_category["itemType"] = category
                                self._analyze_item(item_id, item_with_category, item_types, missing_properties, icon_ids, ui_slots)
            else:
                # Dictionary format: {item_id: item_data, ...}
                total_items = len(parsed_items)
                for item_id, item_data in parsed_items.items():
                    if isinstance(item_data, dict):
                        self._analyze_item(item_id, item_data, item_types, missing_properties, icon_ids, ui_slots)
        else:
            # List format: [{item data}, {item data}, ...]
            total_items = len(parsed_items)
            for i, item_data in enumerate(parsed_items):
                if isinstance(item_data, dict):
                    item_id = item_data.get("id", f"item_{i}")
                    self._analyze_item(item_id, item_data, item_types, missing_properties, icon_ids, ui_slots)
        
        analysis = {
            "total_item_count": total_items,
            "data_format": "nested dictionary" if (is_dict_format and has_nested_arrays) else 
                          "dictionary" if is_dict_format else "list",
            "item_types": dict(item_types),
            "unique_icon_count": len(icon_ids),
            "ui_slots": dict(ui_slots),
            "ui_slots_expected": False,  # UI slots are not expected at s04, they're added in s05
            "items_missing_properties": {
                item_id: dict(props) 
                for item_id, props in missing_properties.items() 
                if props
            },
            "items_with_missing_props_count": len(missing_properties),
            "categories": list(parsed_items.keys()) if (is_dict_format and has_nested_arrays) else []  # type: ignore
        }
        
        return analysis
        
    def _analyze_item(self, item_id, item_data, item_types, missing_properties, icon_ids, ui_slots):
        """Helper method to analyze an individual item."""
        # Count by item type
        item_type = item_data.get("itemType", "unknown")
        item_types[item_type] += 1
        
        # Track missing important properties
        for prop in ["name", "description", "itemType", "uiSlot", "iconId"]:
            if prop not in item_data or not item_data[prop]:
                missing_properties[item_id][prop] += 1
        
        # Track unique icon IDs
        if "iconId" in item_data and item_data["iconId"]:
            icon_ids.add(item_data["iconId"])
            
        # Track UI slots
        if "uiSlot" in item_data and item_data["uiSlot"]:
            ui_slots[item_data["uiSlot"]] += 1
        
    def analyze_filled_items(self) -> Dict[str, Any]:
        """
        Analyze the filled items (output of s05_fill_items).
        
        Returns:
            Dict containing analysis results
        """
        if not self.version_dir:
            return {"error": "No version directory specified"}
            
        filled_items = self.load_json_file("filled_items.json")
        parsed_items = self.load_json_file("parsed_items.json")
        
        if not filled_items:
            return {"error": "Could not load filled_items.json"}
            
        if not parsed_items:
            return {"error": "Could not load parsed_items.json for comparison"}
        
        # Handle different data formats
        filled_is_dict = isinstance(filled_items, dict)
        parsed_is_dict = isinstance(parsed_items, dict)
        
        # Check for nested array structure
        filled_has_nested = filled_is_dict and any(isinstance(value, list) for value in filled_items.values())
        parsed_has_nested = parsed_is_dict and any(isinstance(value, list) for value in parsed_items.values())
        
        # Compare with parsed items to check what was filled
        changed_items = 0
        property_changes: Dict[str, int] = defaultdict(int)
        slot_categories: Dict[str, Counter] = defaultdict(Counter)
        total_items = 0
        
        # Handle nested dictionary format: {"Category1": [item1, item2, ...], "Category2": [...]}
        if filled_has_nested and parsed_has_nested:
            # Process nested arrays
            for category, filled_category_items in filled_items.items():
                if isinstance(filled_category_items, list):
                    total_items += len(filled_category_items)
                    # Check if category exists in parsed items
                    if category in parsed_items and isinstance(parsed_items[category], list):
                        parsed_category_items = parsed_items[category]
                        # Compare items by index within the same category
                        for i, filled_item in enumerate(filled_category_items):
                            if i < len(parsed_category_items):
                                parsed_item = parsed_category_items[i]
                                if isinstance(filled_item, dict) and isinstance(parsed_item, dict):
                                    self._compare_items(filled_item, parsed_item, property_changes)
                                    self._track_categories(filled_item, slot_categories)
                                    if filled_item != parsed_item:
                                        changed_items += 1
        elif filled_is_dict and parsed_is_dict:
            # Both are flat dictionaries
            total_items = len(filled_items)
            for item_id, filled_item in filled_items.items():
                if item_id in parsed_items:
                    parsed_item = parsed_items[item_id]
                    self._compare_items(filled_item, parsed_item, property_changes)
                    self._track_categories(filled_item, slot_categories)
                    if filled_item != parsed_item:
                        changed_items += 1
        elif not filled_is_dict and not parsed_is_dict:
            # Both are lists, compare by index
            total_items = len(filled_items)
            for i, filled_item in enumerate(filled_items):
                if i < len(parsed_items):
                    parsed_item = cast(List[Any], parsed_items)[i]
                    self._compare_items(filled_item, parsed_item, property_changes)
                    self._track_categories(filled_item, slot_categories)
                    if filled_item != parsed_item:
                        changed_items += 1
        else:
            # Mixed formats - this is trickier, but let's handle the most common case
            total_items = len(filled_items) if isinstance(filled_items, list) else sum(len(items) if isinstance(items, list) else 1 for items in filled_items.values())
            # We can't easily compare mismatched formats, so we'll just analyze the filled items
            if filled_has_nested:
                for category, items in filled_items.items():
                    if isinstance(items, list):
                        for item in items:
                            if isinstance(item, dict):
                                self._track_categories(item, slot_categories)
            elif filled_is_dict:
                for item_id, item in filled_items.items():
                    if isinstance(item, dict):
                        self._track_categories(item, slot_categories)
            else:
                for item in filled_items:
                    if isinstance(item, dict):
                        self._track_categories(item, slot_categories)
        
        analysis: Dict[str, Any] = {
            "total_item_count": total_items,
            "data_format": "nested dictionary" if filled_has_nested else 
                          "dictionary" if filled_is_dict else "list",
            "items_changed_during_filling": changed_items,
            "property_change_counts": dict(property_changes),
            "categories_by_ui_slot": {
                slot: dict(categories) 
                for slot, categories in slot_categories.items()
            },
        }
        
        if filled_has_nested:
            # Change the key name to avoid type conflicts
            analysis["category_list"] = list(filled_items.keys())
            analysis["items_per_category"] = {category: len(items) if isinstance(items, list) else 1 
                                            for category, items in filled_items.items()}
        
        return analysis
        
    def _compare_items(self, filled_item: Dict[str, Any], parsed_item: Dict[str, Any], property_changes: Dict[str, int]):
        """Helper method to compare items and track property changes."""
        # Both are dictionaries
        for key in set(filled_item.keys()) | set(parsed_item.keys()):
            if key not in parsed_item or key not in filled_item or filled_item[key] != parsed_item[key]:
                property_changes[key] += 1

    # Ensure slot_categories is a defaultdict with Counter as default factory
    def _track_categories(self, item: Dict[str, Any], slot_categories: Dict[str, Counter]):
        """Helper method to track categories by UI slot."""
        if "uiSlotName" in item and "categoryName" in item:
            ui_slot = item["uiSlotName"]
            category = item["categoryName"]
            slot_categories[ui_slot][category] += 1
        elif "uiSlotName" in item:
            ui_slot = item["uiSlotName"]
            category = item.get("armorTypeName") or item.get("weaponTypeName") or ("diceBadge" if "badgeTypeName" in item else None)
            if category:
                slot_categories[ui_slot][category] += 1
        
    def analyze_processed_items(self) -> Dict[str, Any]:
        """
        Analyze the processed items (output of s06_process_items).
        
        Returns:
            Dict containing analysis results
        """
        if not self.version_dir:
            return {"error": "No version directory specified"}
            
        items_array = self.load_json_file("items_array.json")
        final_data = self.load_json_file("data.json")
        
        if not items_array:
            return {"error": "Could not load items_array.json"}
            
        if not final_data:
            return {"error": "Could not load final data.json"}
        
        # Check if items were successfully added to data.json
        items_in_data = final_data.get("items", [])
        
        # Count items by various properties
        categories: Counter = Counter()
        tier_counts: Counter = Counter()
        rarities: Counter = Counter()
        sources: Counter = Counter()
        display_name_counter: Counter = Counter()
        # Track display names by category
        display_names_by_category: Dict[str, Counter] = defaultdict(Counter)
        
        for item in items_array:
            # Handle both dictionary and list formats
            if isinstance(item, dict):
                category = item.get("category", "unknown")
                categories[category] += 1
                tier_counts[item.get("tier", "unknown")] += 1
                rarities[item.get("rarity", "unknown")] += 1
                
                # Count display names
                display_name = item.get("displayName")
                if display_name:
                    display_name_counter[display_name] += 1
                    # Also track by category
                    display_names_by_category[category][display_name] += 1
                
                # Track sources (if present)
                if "source" in item:
                    if isinstance(item["source"], list):
                        for source in item["source"]:
                            sources[source] += 1
                    else:
                        sources[item["source"]] += 1
        
        analysis = {
            "item_count_in_array": len(items_array),
            "item_count_in_data_json": len(items_in_data),
            "items_successfully_added": len(items_array) == len(items_in_data),
            "categories": dict(categories),
            "tier_distribution": dict(tier_counts),
            "rarity_distribution": dict(rarities),
            "source_distribution": dict(sources),
            "display_name_counts": dict(display_name_counter),
            "display_names_by_category": {category: dict(counts) for category, counts in display_names_by_category.items()},
            "unique_display_names_count": len(display_name_counter),
            "items": items_in_data  # Include the actual items for additional processing
        }
        
        return analysis
        
    def run_full_analysis(self) -> Dict[str, Dict[str, Any]]:
        """Run all analysis methods and return the combined results."""
        results = {
            "version": self.analyze_version(),
            "data_json_init": self.analyze_data_json_init(),
            "xml_extraction": self.analyze_xml_extraction(),
            "parsed_items": self.analyze_parsed_items(),
            "filled_items": self.analyze_filled_items(),
            "processed_items": self.analyze_processed_items(),
            "item_outliers": self.analyze_item_outliers(),
            "display_name_variants": self.analyze_display_name_variants(),
        }
        return results

    def analyze_item_outliers(self) -> Dict[str, Any]:
        """
        Analyze processed items to find statistical outliers in each item type.
        Uses the most specific category type available for each item.
        
        Returns:
            Dict containing outlier analysis results
        """
        if not self.version_dir:
            return {"error": "No version directory specified"}
            
        # Load the final processed data
        final_data = self.load_json_file("data.json")
        
        if not final_data or "items" not in final_data:
            return {"error": "Could not load data.json or items array not found"}
        
        items = final_data.get("items", [])
        
        # Group items by their most specific type
        armor_by_type = defaultdict(list)
        weapons_by_type = defaultdict(list)
        dice_items = []
        dice_badges_by_type = defaultdict(list)
        
        for item in items:
            # Skip items without category information
            if "category" not in item:
                continue
                
            category = item.get("category")
            
            if category in ["head", "torso", "hands", "legs", "horse", "jewelry", "pouch"]:
                # Armor items
                armor_type = item.get("armorTypeName")
                if armor_type:
                    armor_by_type[armor_type].append(item)
            elif category in ["melee", "ranged", "dagger", "shield"]:
                # Weapon items
                weapon_type = item.get("weaponTypeName")
                if weapon_type:
                    weapons_by_type[weapon_type].append(item)
            elif category == "dice":
                # Dice items
                dice_items.append(item)
            elif category == "dicebadge":
                # Dice badge items - group by combination of type and subtype
                badge_type = item.get("badgeTypeName")
                badge_subtype = item.get("badgeSubTypeName")
                if badge_type and badge_subtype:
                    badge_key = f"{badge_type}_{badge_subtype}"
                    dice_badges_by_type[badge_key].append(item)
        
        # Analyze each group for outliers
        armor_outliers = self._find_outliers_in_groups(armor_by_type, "armor")
        weapon_outliers = self._find_outliers_in_groups(weapons_by_type, "weapon")
        dice_outliers = self._find_outliers_in_list(dice_items, "dice")
        badge_outliers = self._find_outliers_in_groups(dice_badges_by_type, "diceBadge")
        
        # Combine results
        all_outliers = {
            "armor": armor_outliers,
            "weapons": weapon_outliers,
            "dice": dice_outliers,
            "diceBadges": badge_outliers
        }
        
        # Count items by type
        type_counts = {
            "armor": {k: len(v) for k, v in armor_by_type.items()},
            "weapons": {k: len(v) for k, v in weapons_by_type.items()},
            "dice": len(dice_items),
            "diceBadges": {k: len(v) for k, v in dice_badges_by_type.items()}
        }
        
        return {
            "type_counts": type_counts,
            "outliers": all_outliers
        }
    
    def _find_outliers_in_groups(self, groups: Dict[str, List[Dict[str, Any]]], item_category: str) -> Dict[str, Dict[str, Any]]:
        """
        Find outliers in each group of items.
        
        Args:
            groups: Dictionary mapping type names to lists of items
            item_category: Category name for context
            
        Returns:
            Dictionary mapping type names to outlier information
        """
        results = {}
        
        for type_name, items in groups.items():
            if len(items) <= 1:
                continue  # Skip types with only one item - no outliers possible
                
            outliers = {}
            
            # Determine which properties to check based on item category
            if item_category == "armor":
                # Armor-specific properties
                properties_to_check = [
                    "defense", "defenseSlash", "defenseSmash", "defenseStab",
                    "noise", "conspicuousness", "visibility", "durability", "price", "weight"
                ]
                
            elif item_category == "weapon":
                # Weapon-specific properties
                properties_to_check = [
                    "attack", "attackSlash", "attackSmash", "attackStab",
                    "durability", "price", "weight", "strReq", "agiReq"
                ]
                
            elif item_category == "diceBadge":
                # Dice badge properties
                properties_to_check = ["price", "tier"]
                
            else:
                # Generic properties for any item type
                properties_to_check = ["price", "weight", "durability"]
            
            # Find outliers for numeric properties
            for prop in properties_to_check:
                prop_values = []
                
                # Collect property values from all items
                for item in items:
                    # Look in item stats if available
                    prop_key = str(prop)  # Always convert to string to fix the index type error
                    if "stats" in item and prop_key in item["stats"]:
                        value = item["stats"][prop_key]
                        if isinstance(value, (int, float)):
                            prop_values.append((item.get("displayName", "Unknown"), value))
                    # Look in main item dictionary
                    elif prop_key in item:
                        value = item[prop_key]
                        if isinstance(value, (int, float)):
                            prop_values.append((item.get("displayName", "Unknown"), value))
                
                if not prop_values:
                    continue  # No values found for this property
                
                # Calculate statistics
                values = [v[1] for v in prop_values]
                if len(values) <= 3:
                    continue  # Not enough data for meaningful outlier detection
                    
                mean = sum(values) / len(values)
                
                # Calculate standard deviation
                variance = sum((x - mean) ** 2 for x in values) / len(values)
                std_dev = variance ** 0.5
                
                if std_dev < 0.01:  # All values nearly identical
                    continue
                
                # Find outliers (values beyond 2 standard deviations from the mean)
                prop_outliers = []
                for name, value in prop_values:
                    z_score = abs(value - mean) / std_dev
                    if z_score > 2.0:  # More than 2 standard deviations from mean
                        prop_outliers.append({
                            "name": name,
                            "value": value,
                            "z_score": z_score,
                            "deviation": value - mean
                        })
                
                if prop_outliers:
                    # Sort outliers by z-score (most extreme first)
                    prop_outliers.sort(key=lambda x: abs(x["z_score"]), reverse=True)
                    outliers[prop] = {
                        "mean": mean,
                        "std_dev": std_dev,
                        "range": [min(values), max(values)],
                        "outliers": prop_outliers
                    }
            
            if outliers:
                results[type_name] = outliers
        
        return results
    
    def _find_outliers_in_list(self, items: List[Dict[str, Any]], item_category: str) -> Dict[str, Any]:
        """
        Find outliers in a list of items (treats the whole list as one group).
        
        Args:
            items: List of items to analyze
            item_category: Category name for context
            
        Returns:
            Dictionary with outlier information
        """
        if not items or len(items) <= 1:
            return {}
            
        # Create a single group with a fixed name
        return self._find_outliers_in_groups({item_category: items}, item_category).get(item_category, {})
        
    def analyze_display_name_variants(self) -> Dict[str, Any]:
        """
        Analyze the relationship between displayName and iconId to identify variants.
        
        Returns:
            Dict containing analysis of item variants
        """
        if not self.version_dir:
            return {"error": "No version directory specified"}
            
        # Load the final processed data
        final_data = self.load_json_file("data.json")
        
        if not final_data or "items" not in final_data:
            return {"error": "Could not load data.json or items array not found"}
        
        items = final_data.get("items", [])
        
        # Group items by display name
        items_by_display_name = defaultdict(list)
        items_by_icon_id = defaultdict(list)
        
        # Collect items with both displayName and iconId
        for item in items:
            display_name = item.get("displayName")
            icon_id = item.get("iconId")
            
            if display_name and icon_id:
                items_by_display_name[display_name].append(item)
                items_by_icon_id[icon_id].append(item)
        
        # Analyze display name variants (same name, different icons)
        display_name_variants = {}
        for display_name, name_items in items_by_display_name.items():
            # Skip items with only one instance
            if len(name_items) <= 1:
                continue
                
            # Count unique icon IDs for this display name
            icon_counts: Counter = Counter()
            for item in name_items:
                icon_counts[item.get("iconId")] += 1
            
            # Only include display names with multiple icon IDs
            if len(icon_counts) > 1:
                # Calculate stats differences between variants
                stats_differences = self._analyze_variant_differences(name_items)
                
                display_name_variants[display_name] = {
                    "count": len(name_items),
                    "icon_counts": dict(icon_counts),
                    "unique_icons": len(icon_counts),
                    "category": name_items[0].get("category", "unknown"),
                    "stats_differences": stats_differences
                }
        
        # Analyze icon ID variants (same icon, different names)
        icon_id_variants = {}
        for icon_id, icon_items in items_by_icon_id.items():
            # Skip items with only one instance
            if len(icon_items) <= 1:
                continue
                
            # Count unique display names for this icon ID
            name_counts: Counter = Counter()
            for item in icon_items:
                name_counts[item.get("displayName")] += 1
            
            # Only include icon IDs with multiple display names
            if len(name_counts) > 1:
                # Calculate stats differences between variants
                stats_differences = self._analyze_variant_differences(icon_items)
                
                icon_id_variants[icon_id] = {
                    "count": len(icon_items),
                    "name_counts": dict(name_counts),
                    "unique_names": len(name_counts),
                    "category": icon_items[0].get("category", "unknown"),
                    "stats_differences": stats_differences
                }
        
        # Summary statistics
        total_items = len(items)
        display_name_count = len(items_by_display_name)
        icon_id_count = len(items_by_icon_id)
        
        return {
            "total_items": total_items,
            "unique_display_names": display_name_count,
            "unique_icon_ids": icon_id_count,
            "display_name_variants": display_name_variants,
            "icon_id_variants": icon_id_variants
        }
    
    def _analyze_variant_differences(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze the stat differences between variants of the same item.
        
        Args:
            items: List of item variants to compare
            
        Returns:
            Dictionary with stat difference information
        """
        if not items or len(items) <= 1:
            return {}
            
        # Collect all stats keys across all items
        all_stat_keys: set[str] = set()
        for item in items:
            if "stats" in item and isinstance(item["stats"], dict):
                # Convert any non-string keys to strings before adding to the set
                for key in item["stats"].keys():
                    all_stat_keys.add(str(key))
        
        # Compare stat values across variants
        stat_differences: Dict[str, Dict[str, Any]] = {}
        for stat_key in all_stat_keys:
            # Collect values for this stat from all items
            stat_values = []
            for item in items:
                if "stats" in item:
                    prop_key = str(stat_key)  # Explicitly convert to string
                    if prop_key in item["stats"]:
                        value = item["stats"][prop_key]
                        if isinstance(value, (int, float)):
                            stat_values.append(value)
            
            # Only include stats with variation
            if len(stat_values) > 1 and len(set(stat_values)) > 1:
                stat_differences[stat_key] = {
                    "min": min(stat_values),
                    "max": max(stat_values),
                    "range": max(stat_values) - min(stat_values),
                    "values": stat_values
                }
        
        return stat_differences