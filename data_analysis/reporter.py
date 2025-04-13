"""
Reporter module for generating human-readable reports from data analysis.
"""
import json
from pathlib import Path
from typing import Dict, Any, Optional, List, cast
import logging
from collections import Counter

class AnalysisReporter:
    """
    Generates human-readable reports from data analysis results.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """Initialize the reporter."""
        self.logger = logger or logging.getLogger(__name__)
        
    def generate_version_report(self, analysis: Dict[str, Any]) -> str:
        """Generate a report for the version analysis."""
        if "error" in analysis:
            return f"Error: {analysis['error']}"
            
        report = [
            "Version Analysis Report",
            "======================="
        ]
        
        report.append(f"Version ID: {analysis.get('version_id', 'Not found')}")
        report.append(f"Version detected: {'Yes' if analysis.get('version_found') else 'No'}")
        report.append(f"Timestamp: {analysis.get('timestamp', 'Not available')}")
        
        return "\n".join(report)
        
    def generate_data_json_init_report(self, analysis: Dict[str, Any]) -> str:
        """Generate a report for the data.json initialization analysis."""
        if "error" in analysis:
            return f"Error: {analysis['error']}"
            
        report = [
            "Data.json Initialization Report",
            "=============================="
        ]
        
        # Basic structure info
        report.append(f"Version included: {'Yes' if analysis.get('contains_version') else 'No'}")
        report.append(f"Version value: {analysis.get('version_value', 'Not available')}")
        report.append(f"Items array initialized: {'Yes' if analysis.get('items_initialized') else 'No'}")
        
        # Structure details
        report.append("\nData.json Structure:")
        for key, type_name in analysis.get('structure', {}).items():
            report.append(f"  - {key}: {type_name}")
            
        return "\n".join(report)
        
    def generate_xml_extraction_report(self, analysis: Dict[str, Any]) -> str:
        """Generate a report for the XML extraction analysis."""
        if "error" in analysis:
            return f"Error: {analysis['error']}"
            
        report = [
            "XML Extraction Report",
            "===================="
        ]
        
        # Files info
        combined_xml_status = "Present" if analysis.get("combined_items_xml_exists") else "Missing"
        report.append(f"Combined items XML: {combined_xml_status}")
        report.append(f"XML files extracted: {analysis.get('xml_file_count', 0)}")
        
        # Dictionary sizes
        report.append(f"Combined dictionary items: {analysis.get('combined_dict_item_count', 0)}")
        report.append(f"Text UI dictionary items: {analysis.get('text_ui_dict_item_count', 0)}")
        
        # List XML files if there are fewer than 20
        xml_files = analysis.get("xml_files", [])
        if xml_files and len(xml_files) < 20:
            report.append("\nExtracted XML files:")
            for file in xml_files:
                report.append(f"  - {file}")
                
        return "\n".join(report)
        
    def generate_parsed_items_report(self, analysis: Dict[str, Any]) -> str:
        """Generate a report for the parsed items analysis."""
        if "error" in analysis:
            return f"Error: {analysis['error']}"
            
        report = [
            "Parsed Items Analysis Report",
            "============================"
        ]
        
        # Basic counts
        report.append(f"Total items: {analysis.get('total_item_count', 0)}")
        report.append(f"Unique icons: {analysis.get('unique_icon_count', 0)}")
        
        # Data format
        data_format = analysis.get('data_format', 'unknown')
        report.append(f"Data format: {data_format}")
        
        # Note about UI slots
        ui_slots_expected = analysis.get('ui_slots_expected', True)
        if not ui_slots_expected:
            report.append("\nNote: UI slots are not expected at this stage (s04). They are implemented in s05_fill_items.")
        
        # Item types breakdown
        report.append("\nItem Types:")
        for item_type, count in sorted(analysis.get('item_types', {}).items(), key=lambda x: x[1], reverse=True):
            report.append(f"  - {item_type}: {count}")
            
        # UI slots breakdown (if any are present)
        ui_slots = analysis.get('ui_slots', {})
        if ui_slots:
            report.append("\nUI Slots:")
            for slot, count in sorted(ui_slots.items(), key=lambda x: x[1], reverse=True):
                report.append(f"  - {slot}: {count}")
        elif ui_slots_expected:
            report.append("\nUI Slots: None found (unexpected)")
            
        # Categories (for nested dictionary format)
        categories = analysis.get('categories', [])
        if categories:
            report.append("\nCategories:")
            for category in sorted(categories):
                report.append(f"  - {category}")
            
        # Missing properties summary
        missing_props_count = analysis.get('items_with_missing_props_count', 0)
        if missing_props_count > 0:
            report.append(f"\nItems with missing properties: {missing_props_count}")
            
            # List a sample of items with missing properties (limit to 10)
            missing_items = list(analysis.get('items_missing_properties', {}).items())
            sample_size = min(10, len(missing_items))
            report.append(f"\nSample of items with missing properties (showing {sample_size} of {len(missing_items)}):")
            
            for item_id, props in missing_items[:sample_size]:
                missing_props_list = ", ".join(props.keys())
                report.append(f"  - {item_id}: Missing {missing_props_list}")
                
        return "\n".join(report)
        
    def generate_filled_items_report(self, analysis: Dict[str, Any]) -> str:
        """Generate a report for the filled items analysis."""
        if "error" in analysis:
            return f"Error: {analysis['error']}"
            
        report = [
            "Filled Items Analysis Report",
            "============================"
        ]
        
        # Basic counts
        report.append(f"Total items: {analysis.get('total_item_count', 0)}")
        report.append(f"Items modified during filling: {analysis.get('items_changed_during_filling', 0)}")
        
        # Property changes
        report.append("\nProperties modified during filling:")
        for prop, count in sorted(analysis.get('property_change_counts', {}).items(), key=lambda x: x[1], reverse=True):
            report.append(f"  - {prop}: {count} items")
            
        # Categories by UI slot
        report.append("\nCategories by UI Slot:")
        for slot, categories in sorted(analysis.get('categories_by_ui_slot', {}).items()):
            report.append(f"  {slot}:")
            for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                report.append(f"    - {category}: {count}")
                
        return "\n".join(report)
        
    def generate_processed_items_report(self, analysis: Dict[str, Any]) -> str:
        """Generate a report for the processed items analysis."""
        if "error" in analysis:
            return f"Error: {analysis['error']}"
            
        report = [
            "Processed Items Analysis Report",
            "==============================="
        ]
        
        # Basic counts
        report.append(f"Items in final array: {analysis.get('item_count_in_array', 0)}")
        report.append(f"Items in data.json: {analysis.get('item_count_in_data_json', 0)}")
        
        items_added = analysis.get('items_successfully_added', False)
        report.append(f"Items successfully added to data.json: {'Yes' if items_added else 'No'}")
        
        # Categories
        report.append("\nItem Categories:")
        for category, count in sorted(analysis.get('categories', {}).items(), key=lambda x: x[1], reverse=True):
            report.append(f"  - {category}: {count}")
            
        # Display Name Analysis
        display_name_counts = analysis.get('display_name_counts', {})
        if display_name_counts:
            # Total unique display names
            report.append(f"\nTotal unique display names: {len(display_name_counts)}")
            
            # Most common display names
            report.append("\nMost Common Display Names (across all categories):")
            for name, count in Counter(display_name_counts).most_common(20):
                report.append(f"  - {name}: {count}")
            
            # Display names by category
            display_names_by_category = analysis.get('display_names_by_category', {})
            if display_names_by_category:
                report.append("\nDisplay Names by Category:")
                
                # Process each category
                for category in sorted(display_names_by_category.keys()):
                    category_counts = display_names_by_category[category]
                    if not category_counts:
                        continue
                        
                    # Add category header and count
                    report.append(f"\n  {category.upper()} - {len(category_counts)} unique names:")
                    
                    # Show top 5 most common display names in this category
                    for name, count in Counter(category_counts).most_common(5):
                        report.append(f"    - {name}: {count}")
        
        return "\n".join(report)
        
    def generate_item_outliers_report(self, analysis: Dict[str, Any]) -> str:
        """Generate a report for the item outliers analysis."""
        if "error" in analysis:
            return f"Error: {analysis['error']}"
            
        report = [
            "Item Outliers Analysis Report",
            "============================="
        ]
        
        # Item type counts
        type_counts = analysis.get("type_counts", {})
        
        report.append("\nItem Distribution by Type:")
        
        # Armor types
        armor_types = type_counts.get("armor", {})
        if armor_types:
            report.append("\nArmor Types:")
            for armor_type, count in sorted(armor_types.items(), key=lambda x: x[1], reverse=True):
                report.append(f"  - {armor_type}: {count} items")
                
        # Weapon types
        weapon_types = type_counts.get("weapons", {})
        if weapon_types:
            report.append("\nWeapon Types:")
            for weapon_type, count in sorted(weapon_types.items(), key=lambda x: x[1], reverse=True):
                report.append(f"  - {weapon_type}: {count} items")
                
        # Dice badges
        badge_types = type_counts.get("diceBadges", {})
        if badge_types:
            report.append("\nDice Badge Types:")
            for badge_type, count in sorted(badge_types.items(), key=lambda x: x[1], reverse=True):
                report.append(f"  - {badge_type}: {count} items")
                
        # Dice
        dice_count = type_counts.get("dice", 0)
        if dice_count:
            report.append(f"\nDice Items: {dice_count}")
            
        # Outliers section
        outliers = analysis.get("outliers", {})
        
        # Function to format outlier sections
        def format_outliers(category_outliers, category_name):
            section = []
            if not category_outliers:
                return section
                
            section.append(f"\n{category_name.upper()} OUTLIERS:")
            
            # Special handling for dice since it has a different structure
            if category_name.lower() == "dice" and isinstance(category_outliers, dict):
                for prop_name, prop_data in sorted(category_outliers.items()):
                    mean = prop_data.get("mean", 0)
                    std_dev = prop_data.get("std_dev", 0)
                    value_range = prop_data.get("range", [0, 0])
                    
                    section.append(f"  {prop_name.upper()}:")
                    section.append(f"    Mean: {mean:.2f}, StdDev: {std_dev:.2f}, Range: [{value_range[0]:.1f} - {value_range[1]:.1f}]")
                    
                    # Show the top 5 outliers at most
                    top_outliers = prop_data.get("outliers", [])[:5]
                    for outlier in top_outliers:
                        name = outlier.get("name", "Unknown")
                        value = outlier.get("value", 0)
                        z_score = outlier.get("z_score", 0)
                        deviation = outlier.get("deviation", 0)
                        
                        # Format the deviation with a + or - sign
                        dev_sign = "+" if deviation >= 0 else ""
                        section.append(f"    • {name}: {value:.1f} (z-score: {z_score:.2f}, {dev_sign}{deviation:.1f} from mean)")
                
                return section
            
            # Standard handling for other categories
            for type_name, properties in sorted(category_outliers.items()):
                if not properties:
                    continue
                    
                section.append(f"\n  {type_name}:")
                
                for prop_name, prop_data in sorted(properties.items()):
                    mean = prop_data.get("mean", 0)
                    std_dev = prop_data.get("std_dev", 0)
                    value_range = prop_data.get("range", [0, 0])
                    
                    section.append(f"    {prop_name.upper()}:")
                    section.append(f"      Mean: {mean:.2f}, StdDev: {std_dev:.2f}, Range: [{value_range[0]:.1f} - {value_range[1]:.1f}]")
                    
                    # Show the top 5 outliers at most
                    top_outliers = prop_data.get("outliers", [])[:5]
                    for outlier in top_outliers:
                        name = outlier.get("name", "Unknown")
                        value = outlier.get("value", 0)
                        z_score = outlier.get("z_score", 0)
                        deviation = outlier.get("deviation", 0)
                        
                        # Format the deviation with a + or - sign
                        dev_sign = "+" if deviation >= 0 else ""
                        section.append(f"      • {name}: {value:.1f} (z-score: {z_score:.2f}, {dev_sign}{deviation:.1f} from mean)")
            
            return section
        
        # Add outlier sections for each category
        report.extend(format_outliers(outliers.get("armor", {}), "Armor"))
        report.extend(format_outliers(outliers.get("weapons", {}), "Weapons"))
        report.extend(format_outliers(outliers.get("dice", {}), "Dice"))
        report.extend(format_outliers(outliers.get("diceBadges", {}), "Dice Badges"))
        
        return "\n".join(report)
        
    def generate_display_name_variants_report(self, analysis: Dict[str, Any]) -> str:
        """Generate a report for the display name variants analysis."""
        if "error" in analysis:
            return f"Error: {analysis['error']}"
            
        report = [
            "Display Name & Icon ID Variants Report",
            "====================================="
        ]
        
        # Summary statistics
        total_items = analysis.get("total_items", 0)
        unique_names = analysis.get("unique_display_names", 0)
        unique_icons = analysis.get("unique_icon_ids", 0)
        
        report.append(f"\nTotal items: {total_items}")
        report.append(f"Unique display names: {unique_names}")
        report.append(f"Unique icon IDs: {unique_icons}")
        
        # Display Name Variants (same name, different icons)
        display_variants = analysis.get("display_name_variants", {})
        
        if display_variants:
            variant_count = len(display_variants)
            total_variants = sum(data.get("count", 0) for data in display_variants.values())
            
            report.append(f"\nItems with same name but different icons: {variant_count} names, {total_variants} total items")
            report.append("\nTOP DISPLAY NAME VARIANTS (same name, different icons):")
            
            # Sort by number of variants and take top 20
            top_variants = sorted(
                display_variants.items(), 
                key=lambda x: x[1].get("unique_icons", 0), 
                reverse=True
            )[:20]
            
            for name, data in top_variants:
                icons = data.get("unique_icons", 0)
                count = data.get("count", 0)
                category = data.get("category", "unknown")
                
                report.append(f"\n  {name} ({category}):")
                report.append(f"    • {count} items with {icons} different icons")
                
                # Show stat differences if available
                stats_diff = data.get("stats_differences", {})
                if stats_diff:
                    report.append("    • Stats that vary between variants:")
                    for stat, diff in stats_diff.items():
                        min_val = diff.get("min", 0)
                        max_val = diff.get("max", 0)
                        range_val = diff.get("range", 0)
                        report.append(f"      - {stat}: {min_val:.1f} to {max_val:.1f} (range: {range_val:.1f})")
        else:
            report.append("\nNo display name variants found (no items with same name but different icons)")
        
        # Icon ID Variants (same icon, different names)
        icon_variants = analysis.get("icon_id_variants", {})
        
        if icon_variants:
            icon_count = len(icon_variants)
            total_icons = sum(data.get("count", 0) for data in icon_variants.values())
            
            report.append(f"\nItems with same icon but different names: {icon_count} icons, {total_icons} total items")
            report.append("\nTOP ICON ID VARIANTS (same icon, different names):")
            
            # Sort by number of variants and take top 20
            top_icons = sorted(
                icon_variants.items(), 
                key=lambda x: x[1].get("unique_names", 0), 
                reverse=True
            )[:20]
            
            for icon, data in top_icons:
                names = data.get("unique_names", 0)
                count = data.get("count", 0)
                category = data.get("category", "unknown")
                
                report.append(f"\n  Icon {icon} ({category}):")
                report.append(f"    • {count} items with {names} different names")
                
                # Show variant names if 5 or fewer
                name_counts = data.get("name_counts", {})
                if 0 < len(name_counts) <= 5:
                    report.append("    • Variant names:")
                    for var_name, var_count in name_counts.items():
                        report.append(f"      - {var_name} ({var_count} items)")
                
                # Show stat differences if available
                stats_diff = data.get("stats_differences", {})
                if stats_diff:
                    report.append("    • Stats that vary between variants:")
                    for stat, diff in stats_diff.items():
                        min_val = diff.get("min", 0)
                        max_val = diff.get("max", 0)
                        range_val = diff.get("range", 0)
                        report.append(f"      - {stat}: {min_val:.1f} to {max_val:.1f} (range: {range_val:.1f})")
        else:
            report.append("\nNo icon ID variants found (no items with same icon but different names)")
            
        return "\n".join(report)
        
    def generate_full_report(self, analysis: Dict[str, Dict[str, Any]]) -> Dict[str, str]:
        """
        Generate reports for all analysis results.
        
        Returns:
            Dict mapping step names to report strings
        """
        reports: Dict[str, str] = {}
        
        if "s01_version" in analysis:
            reports["s01_version"] = self.generate_version_report(analysis["s01_version"])
            
        if "s02_data_json_init" in analysis:
            reports["s02_data_json_init"] = self.generate_data_json_init_report(analysis["s02_data_json_init"])
            
        if "s03_xml_extraction" in analysis:
            reports["s03_xml_extraction"] = self.generate_xml_extraction_report(analysis["s03_xml_extraction"])
            
        if "s04_parsed_items" in analysis:
            reports["s04_parsed_items"] = self.generate_parsed_items_report(analysis["s04_parsed_items"])
            
        if "s05_filled_items" in analysis:
            reports["s05_filled_items"] = self.generate_filled_items_report(analysis["s05_filled_items"])
            
        if "s06_processed_items" in analysis:
            reports["s06_processed_items"] = self.generate_processed_items_report(analysis["s06_processed_items"])
            
        if "s07_item_outliers" in analysis:
            reports["s07_item_outliers"] = self.generate_item_outliers_report(analysis["s07_item_outliers"])
            
        if "s08_display_name_variants" in analysis:
            reports["s08_display_name_variants"] = self.generate_display_name_variants_report(analysis["s08_display_name_variants"])
            
        # Cast to satisfy the type checker
        return reports
        
    def save_reports_to_files(self, reports: Dict[str, str], output_dir: Path) -> None:
        """
        Save reports to files in the specified directory.
        
        Args:
            reports: Dict mapping step names to report strings
            output_dir: Directory to save reports in
        """
        output_dir.mkdir(exist_ok=True, parents=True)
        
        for step, report in reports.items():
            file_path = output_dir / f"{step}_report.txt"
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(report)
                self.logger.info(f"Saved report to {file_path}")
            except Exception as e:
                self.logger.error(f"Failed to save report to {file_path}: {e}")

class DataReporter:
    """Generates reports from analyzed KCD2 game data."""
    
    def __init__(self, reports_dir: Optional[Path] = None, logger: Optional[logging.Logger] = None):
        """Initialize the reporter with output directory and logger."""
        self.reports_dir = reports_dir or Path("reports")
        self.logger = logger or logging.getLogger(__name__)
        self.analysis_results: Dict[str, Dict[str, Any]] = {}
        
    def load_json_file(self, filename: str) -> Optional[Dict[str, Any]]:
        """Helper method to load JSON data."""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return cast(Dict[str, Any], json.load(f))
        except Exception as e:
            self.logger.error(f"Failed to load {filename}: {e}")
            return None

    def generate_reports(self) -> Dict[str, str]:
        """Generate all reports and return a dictionary of report paths."""
        analysis_reporter = AnalysisReporter(logger=self.logger)
        
        reports = {}
        if "version" in self.analysis_results:
            reports["version"] = analysis_reporter.generate_version_report(self.analysis_results["version"])
        if "data_json_init" in self.analysis_results:
            reports["data_json_init"] = analysis_reporter.generate_data_json_init_report(self.analysis_results["data_json_init"])
        if "xml_extraction" in self.analysis_results:
            reports["xml_extraction"] = analysis_reporter.generate_xml_extraction_report(self.analysis_results["xml_extraction"])
        if "parsed_items" in self.analysis_results:
            reports["parsed_items"] = analysis_reporter.generate_parsed_items_report(self.analysis_results["parsed_items"])
        if "filled_items" in self.analysis_results:
            reports["filled_items"] = analysis_reporter.generate_filled_items_report(self.analysis_results["filled_items"])
        if "processed_items" in self.analysis_results:
            reports["processed_items"] = analysis_reporter.generate_processed_items_report(self.analysis_results["processed_items"])
        
        return reports

    # ...existing code...

    def generate_item_outliers_report(self) -> Optional[str]:
        """Generate a report for the item outliers analysis."""
        key = "item_outliers"
        if key not in self.analysis_results:
            self.logger.error(f"Missing analysis results for: {key}")
            return None

        analysis = self.analysis_results[key]
        if "error" in analysis:
            self.logger.error(f"Error in analysis results: {analysis['error']}")
            return None

        report_text = "Item Outliers Analysis Report\n"
        report_text += "=============================\n\n"

        # Item distribution by type
        report_text += "Item Distribution by Type:\n\n"
        
        type_counts = analysis.get("type_counts", {})
        
        # Armor types
        if "armor" in type_counts:
            report_text += "Armor Types:\n"
            armor_counts = type_counts["armor"]
            for armor_type, count in sorted(armor_counts.items(), key=lambda x: x[1], reverse=True):
                report_text += f"  - {armor_type}: {count} items\n"
            report_text += "\n"
            
        # Weapon types
        if "weapons" in type_counts:
            report_text += "Weapon Types:\n"
            weapon_counts = type_counts["weapons"]
            for weapon_type, count in sorted(weapon_counts.items(), key=lambda x: x[1], reverse=True):
                report_text += f"  - {weapon_type}: {count} items\n"
            report_text += "\n"
            
        # Dice badge types
        if "diceBadges" in type_counts:
            report_text += "Dice Badge Types:\n"
            badge_counts = type_counts["diceBadges"]
            for badge_type, count in sorted(badge_counts.items(), key=lambda x: x[1], reverse=True):
                report_text += f"  - {badge_type}: {count} items\n"
            report_text += "\n"
            
        # Dice items
        if "dice" in type_counts:
            report_text += f"Dice Items: {type_counts['dice']}\n\n"
        
        # Report outliers
        outliers = analysis.get("outliers", {})
        
        # Armor outliers
        if "armor" in outliers:
            report_text += "ARMOR OUTLIERS:\n\n"
            armor_outliers = outliers["armor"]
            for armor_type, properties in sorted(armor_outliers.items()):
                report_text += f"  {armor_type}:\n"
                for prop_name, prop_data in sorted(properties.items()):
                    mean = prop_data.get("mean", 0)
                    std_dev = prop_data.get("std_dev", 0)
                    value_range = prop_data.get("range", [0, 0])
                    
                    report_text += f"    {prop_name.upper()}:\n"
                    report_text += f"      Mean: {mean:.2f}, StdDev: {std_dev:.2f}, Range: {value_range}\n"
                    
                    # List the top outliers
                    for outlier in prop_data.get("outliers", [])[:5]:  # Show top 5 outliers
                        name = outlier.get("name", "Unknown")
                        value = outlier.get("value", 0)
                        z_score = outlier.get("z_score", 0)
                        deviation = outlier.get("deviation", 0)
                        
                        report_text += f"      • {name}: {value} (z-score: {z_score:.2f}, {deviation:+.1f} from mean)\n"
                    
                report_text += "\n"
        
        # Weapon outliers
        if "weapons" in outliers:
            report_text += "WEAPON OUTLIERS:\n\n"
            weapon_outliers = outliers["weapons"]
            for weapon_type, properties in sorted(weapon_outliers.items()):
                report_text += f"  {weapon_type}:\n"
                for prop_name, prop_data in sorted(properties.items()):
                    mean = prop_data.get("mean", 0)
                    std_dev = prop_data.get("std_dev", 0)
                    value_range = prop_data.get("range", [0, 0])
                    
                    report_text += f"    {prop_name.upper()}:\n"
                    report_text += f"      Mean: {mean:.2f}, StdDev: {std_dev:.2f}, Range: {value_range}\n"
                    
                    # List the top outliers
                    for outlier in prop_data.get("outliers", [])[:5]:  # Show top 5 outliers
                        name = outlier.get("name", "Unknown")
                        value = outlier.get("value", 0)
                        z_score = outlier.get("z_score", 0)
                        deviation = outlier.get("deviation", 0)
                        
                        report_text += f"      • {name}: {value} (z-score: {z_score:.2f}, {deviation:+.1f} from mean)\n"
                    
                report_text += "\n"
        
        # Dice badge outliers
        if "diceBadges" in outliers:
            report_text += "DICE BADGE OUTLIERS:\n\n"
            badge_outliers = outliers["diceBadges"]
            for badge_type, properties in sorted(badge_outliers.items()):
                report_text += f"  {badge_type}:\n"
                for prop_name, prop_data in sorted(properties.items()):
                    mean = prop_data.get("mean", 0)
                    std_dev = prop_data.get("std_dev", 0)
                    value_range = prop_data.get("range", [0, 0])
                    
                    report_text += f"    {prop_name.upper()}:\n"
                    report_text += f"      Mean: {mean:.2f}, StdDev: {std_dev:.2f}, Range: {value_range}\n"
                    
                    # List the top outliers
                    for outlier in prop_data.get("outliers", [])[:5]:  # Show top 5 outliers
                        name = outlier.get("name", "Unknown")
                        value = outlier.get("value", 0)
                        z_score = outlier.get("z_score", 0)
                        deviation = outlier.get("deviation", 0)
                        
                        report_text += f"      • {name}: {value} (z-score: {z_score:.2f}, {deviation:+.1f} from mean)\n"
                    
                report_text += "\n"
        
        # Dice outliers
        if "dice" in outliers:
            report_text += "DICE OUTLIERS:\n\n"
            dice_outliers = outliers["dice"]
            for prop_name, prop_data in sorted(dice_outliers.items()):
                mean = prop_data.get("mean", 0)
                std_dev = prop_data.get("std_dev", 0)
                value_range = prop_data.get("range", [0, 0])
                
                report_text += f"  {prop_name.upper()}:\n"
                report_text += f"    Mean: {mean:.2f}, StdDev: {std_dev:.2f}, Range: {value_range}\n"
                
                # List the top outliers
                for outlier in prop_data.get("outliers", [])[:5]:  # Show top 5 outliers
                    name = outlier.get("name", "Unknown")
                    value = outlier.get("value", 0)
                    z_score = outlier.get("z_score", 0)
                    deviation = outlier.get("deviation", 0)
                    
                    report_text += f"    • {name}: {value} (z-score: {z_score:.2f}, {deviation:+.1f} from mean)\n"
                
                report_text += "\n"
        
        # Save the report
        report_path = self.save_report("item_outliers_analysis_report.txt", report_text)
        return report_path
        
    def generate_display_name_variants_report(self) -> Optional[str]:
        """Generate a report for display name and icon ID variants analysis."""
        key = "display_name_variants"
        if key not in self.analysis_results:
            self.logger.error(f"Missing analysis results for: {key}")
            return None

        analysis = self.analysis_results[key]
        if "error" in analysis:
            self.logger.error(f"Error in analysis results: {analysis['error']}")
            return None

        report_text = "Display Name & Icon ID Variants Report\n"
        report_text += "=====================================\n\n"

        # Summary statistics
        total_items = analysis.get("total_items", 0)
        unique_display_names = analysis.get("unique_display_names", 0)
        unique_icon_ids = analysis.get("unique_icon_ids", 0)
        
        report_text += f"Total items: {total_items}\n"
        report_text += f"Unique display names: {unique_display_names}\n"
        report_text += f"Unique icon IDs: {unique_icon_ids}\n\n"
        
        # Display name variants (same name, different icons)
        display_name_variants = analysis.get("display_name_variants", {})
        variants_count = len(display_name_variants)
        
        # Count total items with variants
        total_variant_items = sum(variant_data.get("count", 0) for variant_data in display_name_variants.values())
        
        report_text += f"Items with same name but different icons: {variants_count} names, {total_variant_items} total items\n\n"
        
        # Display the top variants by count
        report_text += "TOP DISPLAY NAME VARIANTS (same name, different icons):\n\n"
        
        # Sort variants by count (descending)
        sorted_variants = sorted(
            display_name_variants.items(),
            key=lambda x: x[1].get("count", 0),
            reverse=True
        )
        
        # Show the top 20 variants
        for display_name, variant_data in sorted_variants[:20]:
            count = variant_data.get("count", 0)
            unique_icons = variant_data.get("unique_icons", 0)
            category = variant_data.get("category", "unknown")
            
            report_text += f"  {display_name} ({category}):\n"
            report_text += f"    • {count} items with {unique_icons} different icons\n"
            
            # Show stat differences between variants
            stats_diffs = variant_data.get("stats_differences", {})
            if stats_diffs:
                report_text += "    • Stats that vary between variants:\n"
                for stat_name, stat_data in stats_diffs.items():
                    min_val = stat_data.get("min", 0)
                    max_val = stat_data.get("max", 0)
                    stat_range = stat_data.get("range", 0)
                    
                    report_text += f"      - {stat_name}: {min_val} to {max_val} (range: {stat_range})\n"
            
            report_text += "\n"
        
        # Icon ID variants (same icon, different names)
        icon_id_variants = analysis.get("icon_id_variants", {})
        icon_variants_count = len(icon_id_variants)
        
        # Count total items with icon variants
        total_icon_variant_items = sum(variant_data.get("count", 0) for variant_data in icon_id_variants.values())
        
        report_text += f"Items with same icon but different names: {icon_variants_count} icons, {total_icon_variant_items} total items\n\n"
        
        # Display the top icon variants by count
        report_text += "TOP ICON ID VARIANTS (same icon, different names):\n\n"
        
        # Sort icon variants by unique names (descending)
        sorted_icon_variants = sorted(
            icon_id_variants.items(),
            key=lambda x: x[1].get("unique_names", 0),
            reverse=True
        )
        
        # Show the top 20 icon variants
        for icon_id, variant_data in sorted_icon_variants[:20]:
            count = variant_data.get("count", 0)
            unique_names = variant_data.get("unique_names", 0)
            category = variant_data.get("category", "unknown")
            
            report_text += f"  Icon {icon_id} ({category}):\n"
            report_text += f"    • {count} items with {unique_names} different names\n"
            
            # Show the different names for this icon
            name_counts = variant_data.get("name_counts", {})
            if name_counts:
                report_text += "    • Variant names:\n"
                for name, name_count in name_counts.items():
                    report_text += f"      - {name} ({name_count} items)\n"
            
            # Show stat differences between variants
            stats_diffs = variant_data.get("stats_differences", {})
            if stats_diffs:
                report_text += "    • Stats that vary between variants:\n"
                for stat_name, stat_data in stats_diffs.items():
                    min_val = stat_data.get("min", 0)
                    max_val = stat_data.get("max", 0)
                    stat_range = stat_data.get("range", 0)
                    
                    report_text += f"      - {stat_name}: {min_val} to {max_val} (range: {stat_range})\n"
            
            report_text += "\n"
        
        # Save the report
        report_path = self.save_report("display_name_variants_report.txt", report_text)
        return report_path

    def save_report(self, filename: str, report_text: str) -> Optional[str]:
        """Save a report to a file in the reports directory."""
        try:
            # Ensure reports directory exists
            self.reports_dir.mkdir(exist_ok=True, parents=True)
            
            # Create full path
            file_path = self.reports_dir / filename
            
            # Write report to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(report_text)
                
            self.logger.info(f"Saved report to {file_path}")
            return str(file_path)
            
        except Exception as e:
            self.logger.error(f"Failed to save report to {filename}: {e}")
            return None