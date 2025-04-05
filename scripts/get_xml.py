import zipfile
import json
import hashlib
import os
import shutil
import sys
from pathlib import Path
from datetime import datetime

# Add the project root to Python path when needed
sys.path.insert(0, str(Path(__file__).parent.parent.absolute()))
from utils.logger import logger
from utils.helpers import read_json_file, write_json_file, ensure_directory, format_xml
import xml.etree.ElementTree as ET

def compute_file_hash(file_path):
    """
    Compute SHA-256 hash of a file.
    
    Args:
        file_path (Path): Path to the file
    
    Returns:
        str: Hex digest of the file hash
    """
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        # Read in chunks to handle large files efficiently
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def convert_element(item, target_type):
    """
    Convert an XML element to a different element type.
    
    Args:
        item (Element): The XML element to convert
        target_type (str): The target element type
    
    Returns:
        Element: A new element of the target type with copied attributes and children
    """
    # Create a new element with the target type
    new_element = ET.Element(target_type)
    
    # Copy all attributes
    for key, value in item.attrib.items():
        new_element.set(key, value)
    
    # Copy all child elements
    for child in item:
        new_element.append(child)
    
    return new_element

def extract_xml_files(kcd2_dir, root_dir, version_dir, xml_config):
    """
    Extract XML files from PAK files.
    
    Args:
        kcd2_dir (Path): Path to KCD2 directory
        root_dir (Path): Path to project root directory
        version_dir (Path): Path to version directory
        xml_config (dict): XML configuration
    
    Returns:
        dict: Dictionary mapping XML file names to their paths
    """
    # Ensure directories exist
    raw_dir = ensure_directory(version_dir / "xml" / "raw")
    temp_dir = ensure_directory(version_dir / "xml" / "temp")
    
    # Load hash file
    hash_file = version_dir / "xml" / "file_hashes.json"
    existing_hashes = read_json_file(hash_file) or {}
    new_hashes = {}
    
    # Extract XML files
    extracted_files = {}
    
    for _, pak_info in xml_config.items():
        pak_path = kcd2_dir / pak_info["kcd2_pak_file"]
        if not pak_path.exists():
            logger.error(f"PAK file not found: {pak_path}")
            continue
        
        logger.info(f"Processing {pak_path.name}")
        
        try:
            with zipfile.ZipFile(pak_path, 'r') as pak_file:
                # Process each XML to extract
                for xml_name in pak_info["xmls_to_extract"]:
                    # Setup paths
                    xml_in_pak = f"{pak_info['in_pak_dir1']}{xml_name}.xml"
                    output_path = raw_dir / f"{xml_name}.xml"
                    rel_path = str(output_path.relative_to(root_dir))
                    
                    # Check if we need to extract based on hash
                    need_extract = True
                    if output_path.exists() and rel_path in existing_hashes:
                        current_hash = compute_file_hash(output_path)
                        if current_hash == existing_hashes[rel_path]["xml_hash"]:
                            logger.info(f"Skipping {xml_name}.xml (unchanged)")
                            need_extract = False
                        else:
                            logger.warning(f"{xml_name}.xml has changed, restoring from PAK")
                    
                    # Extract if needed
                    if need_extract:
                        try:
                            # Clean temp dir
                            for item in temp_dir.iterdir():
                                if item.is_file():
                                    item.unlink()
                                elif item.is_dir():
                                    shutil.rmtree(item)
                            
                            # Extract to temp
                            pak_file.extract(xml_in_pak, temp_dir)
                            extracted_file = temp_dir / xml_in_pak
                            
                            # Copy to raw dir
                            shutil.copy2(extracted_file, output_path)
                            
                            # Update hash
                            new_hash = compute_file_hash(output_path)
                            new_hashes[rel_path] = {"xml_hash": new_hash, "extracted": datetime.now().isoformat()}
                            
                            logger.info(f"Extracted {xml_name}.xml")
                        except Exception as e:
                            logger.error(f"Failed to extract {xml_name}.xml: {e}")
                            continue
                    
                    # Add to extracted files
                    extracted_files[xml_name] = output_path
        except Exception as e:
            logger.error(f"Error processing {pak_path.name}: {e}")
    
    # Update hash file
    if new_hashes:
        existing_hashes.update(new_hashes)
        write_json_file(hash_file, existing_hashes)
    
    return extracted_files, raw_dir, temp_dir

def create_combined_items_file(extracted_files, raw_dir):
    """
    Create a combined items XML file from individual XML files.
    
    Args:
        extracted_files (dict): Dictionary mapping XML file names to their paths
        raw_dir (Path): Directory for raw XML files
    
    Returns:
        Path: Path to the combined items file
    """
    combined_path = raw_dir / "combined_items.xml"
    
    try:
        # Parse main item.xml
        main_tree = ET.parse(extracted_files["item"])
        main_root = main_tree.getroot()
        
        # Create combined root
        combined_root = ET.Element(main_root.tag, main_root.attrib)
        
        # Find ItemClasses element
        main_classes = main_root.find(".//ItemClasses")
        if main_classes is None:
            logger.error("Could not find ItemClasses in item.xml")
            return None
        
        # Create ItemClasses element in combined file
        combined_classes = ET.SubElement(combined_root, "ItemClasses", main_classes.attrib)
        
        # Process main file items
        for item in main_classes:
            if item.tag in ("Hood", "Helmet", "QuickSlotContainer"):
                # Convert to Armor
                armor_item = convert_element(item, "Armor")
                combined_classes.append(armor_item)
                logger.debug(f"Converted {item.tag} element to Armor: {item.get('Name', 'unnamed')}")
            else:
                # For other items, just add them directly
                combined_classes.append(item)
        
        # Process other files
        for name, path in extracted_files.items():
            if name.startswith("item__") and name != "text_ui_items":
                try:
                    file_tree = ET.parse(path)
                    file_root = file_tree.getroot()
                    file_classes = file_root.find(".//ItemClasses")
                    
                    if file_classes is not None:
                        # Check if this is the horse items file
                        is_horse_file = name == "item__horse"
                        
                        for item in file_classes:
                            if is_horse_file and item.tag == "Armor":
                                # Convert to Horse for horse file
                                horse_item = convert_element(item, "Horse")
                                combined_classes.append(horse_item)
                            elif item.tag in ("Hood", "Helmet", "QuickSlotContainer"):
                                # Convert to Armor
                                armor_item = convert_element(item, "Armor")
                                combined_classes.append(armor_item)
                                logger.debug(f"Converted {item.tag} element to Armor: {item.get('Name', 'unnamed')}")
                            else:
                                # For other items, just add them directly
                                combined_classes.append(item)
                        
                        logger.info(f"Added items from {name}.xml")
                        if is_horse_file:
                            logger.info(f"Converted Armor elements to Horse elements in {name}.xml")
                except Exception as e:
                    logger.error(f"Error processing {name}.xml: {e}")
        
        # Write the combined XML to file with proper formatting
        formatted_xml = format_xml(combined_root)
        
        with open(combined_path, 'wb') as f:
            f.write(formatted_xml)
        
        logger.info(f"Created combined items file with {len(combined_classes)} items")
        return combined_path
    
    except Exception as e:
        logger.error(f"Error creating combined file: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None

def get_xml(kcd2_dir, root_dir, version_info):
    """
    Extract XML files from PAK files and create a combined items file.
    
    Args:
        kcd2_dir (Path): Path to KCD2 directory
        root_dir (Path): Path to project root directory
        version_info (dict): Version information from get_version()
    
    Returns:
        dict: Dictionary with paths to 'text_ui_items' and 'combined_items'
    """
    logger.info("Extracting XML files from PAK files...")
    version_dir = Path(version_info["version_dir"])
    
    # Initialize result dictionary
    result = {}
    
    # Load XML configuration
    xml_config = read_json_file(root_dir / "config" / "xml_files.json")
    if not xml_config:
        logger.error("Failed to load XML configuration")
        return result
    
    # Extract XML files
    extracted_files, raw_dir, temp_dir = extract_xml_files(kcd2_dir, root_dir, version_dir, xml_config)
    
    # Create combined items file if we have the base item.xml
    if "item" in extracted_files:
        combined_path = create_combined_items_file(extracted_files, raw_dir)
        if combined_path:
            result["combined_items"] = combined_path
    
    # Add text_ui_items to result if extracted
    if "text_ui_items" in extracted_files:
        result["text_ui_items"] = extracted_files["text_ui_items"]
    
    # Clean up temp directory contents
    try:
        for item in temp_dir.iterdir():
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)
    except Exception as e:
        logger.warning(f"Failed to clean up temp dir: {e}")
    
    # Return result with just the two files we need
    logger.info(f"XML extraction complete. Extracted: {len(extracted_files)}, Result files: {len(result)}")
    return result

# This allows the module to be run directly for testing
if __name__ == "__main__":
    from config import ROOT_DIR, KCD2_DIR
    from scripts.get_version import get_version
    
    # Get version info
    version_info = get_version(KCD2_DIR, ROOT_DIR)
    if not version_info["game_version"]:
        logger.error("Failed to get version info")
        sys.exit(1)
    
    # Run the extraction
    xml_files = get_xml(KCD2_DIR, ROOT_DIR, version_info)
    logger.info(f"Extraction complete. Found {len(xml_files)} XML files")
    
    # Print the XML file mapping
    for name, path in xml_files.items():
        logger.info(f"{name}: {path}")