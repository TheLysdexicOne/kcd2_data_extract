import zipfile
import hashlib
import shutil
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
from typing import Dict, Tuple, Optional, Any, List, Set, Mapping
from utils import logger, read_json, write_json, ensure_dir, format_xml

def get_xml(root_dir: Path, kcd2_dir: Path, version_id: str) -> Dict[str, ET.ElementTree]:
    """
    Extract XML files from PAK files and create a combined items file.
    
    Args:
        root_dir: Path to project root directory
        kcd2_dir: Path to KCD2 directory
        version_id: Version ID (e.g. "1_2")
    
    Returns:
        Dictionary mapping XML names to their parsed ElementTree objects
    """
    
    # Construct version directory path
    version_dir = root_dir / "data" / "version" / version_id
    
    # Initialize result dictionary
    xml_trees: Dict[str, ET.ElementTree] = {}
    
    # Load XML configuration
    xml_config = read_json(root_dir / "config" / "xml_files.json")
    if not xml_config:
        logger.error("Failed to load XML configuration")
        return xml_trees
    
    # Extract XML files
    extracted_files, xml_dir, temp_dir = extract_xml_files(kcd2_dir, version_dir, xml_config)
    
    # Create combined items file if we have the base item.xml
    if "item" in extracted_files:
        combined_root, combined_path = create_combined_items_file(extracted_files, xml_dir)
        if combined_root is not None and combined_path is not None:
            xml_trees["combined_items"] = ET.ElementTree(combined_root)
            logger.debug(f"Added combined_items to XML trees from {combined_path}")
    else:
        logger.warning("Could not create combined items file: item.xml not found")
    
    # Add text_ui_items to result if extracted
    if "text_ui_items" in extracted_files:
        try:
            text_ui_path = extracted_files["text_ui_items"]
            xml_trees["text_ui_items"] = ET.parse(text_ui_path)
            logger.debug(f"Added text_ui_items to XML trees from {text_ui_path}")
        except Exception as e:
            logger.error(f"Failed to parse text_ui_items.xml: {e}")
    
    # Clean up temp directory
    clean_directory(temp_dir)
    
    logger.info(f"XML extraction complete. Loaded {len(xml_trees)} XML trees")
    return xml_trees

def compute_file_hash(file_path: Path) -> str:
    """
    Compute SHA-256 hash of a file.
    
    Args:
        file_path: Path to the file to hash
        
    Returns:
        Hexadecimal digest of the file's SHA-256 hash
    """
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        # Read in chunks to avoid loading large files into memory
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def convert_element(item: ET.Element, target_type: str) -> ET.Element:
    """
    Convert an XML element to a different element type, preserving attributes and children.
    
    Args:
        item: Source XML element to convert
        target_type: Target element type (tag name)
        
    Returns:
        New XML element with the target type and copied attributes/children
    """
    new_element = ET.Element(target_type)
    
    # Copy all attributes
    for key, value in item.attrib.items():
        new_element.set(key, value)
    
    # Copy all child elements
    for child in item:
        new_element.append(child)
    
    return new_element

def clean_directory(directory: Path) -> None:
    """
    Clean all files and subdirectories from a directory.
    
    Args:
        directory: Path to the directory to clean
    """
    if not directory.exists():
        logger.debug(f"Directory doesn't exist, nothing to clean: {directory}")
        return
        
    try:
        for item in directory.iterdir():
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)
        logger.debug(f"Cleaned directory: {directory}")
    except Exception as e:
        logger.warning(f"Failed to clean directory {directory}: {e}")

def extract_xml_files(kcd2_dir: Path, version_dir: Path, xml_config: Mapping[str, Any]) -> Tuple[Dict[str, Path], Path, Path]:
    """
    Extract XML files from PAK files based on configuration.
    
    Args:
        kcd2_dir: Path to KCD2 directory
        version_dir: Path to version directory
        xml_config: XML configuration dictionary
    
    Returns:
        Tuple containing:
        - Dictionary mapping XML names to their file paths
        - Path to the XML directory
        - Path to the temporary directory
    """
    # Ensure directories exist
    xml_dir = ensure_dir(version_dir / "xml")
    temp_dir = ensure_dir(version_dir / "xml" / "temp")
    raw_dir = ensure_dir(version_dir / "xml" / "raw")
    
    # Load hash file
    hash_file = version_dir / "xml" / "file_hashes.json"
    existing_hashes = read_json(hash_file) or {}
    new_hashes: Dict[str, Dict[str, str]] = {}
    
    # Extract XML files
    extracted_files: Dict[str, Path] = {}
    
    for pak_name, pak_info in xml_config.items():
        pak_path = kcd2_dir / pak_info["kcd2_pak_file"]
        if not pak_path.exists():
            logger.error(f"PAK file not found: {pak_path}")
            continue
        
        logger.info(f"Processing {pak_path.name}")
        
        try:
            with zipfile.ZipFile(pak_path, 'r') as pak_file:
                # Process each XML to extract
                for file_info in pak_info["files"]:
                    xml_name = file_info["name"]
                    in_pak_dir = file_info["in_pak_dir"]
                    
                    # Extract the file
                    output_path = extract_xml_file(
                        pak_file=pak_file,
                        xml_name=xml_name,
                        in_pak_dir=in_pak_dir,
                        raw_dir=raw_dir,
                        xml_dir=xml_dir,
                        temp_dir=temp_dir,
                        version_dir=version_dir,
                        existing_hashes=existing_hashes,
                        new_hashes=new_hashes
                    )
                    
                    if output_path:
                        # Store absolute path to avoid confusion with relative paths
                        extracted_files[xml_name] = output_path.resolve()
                        logger.debug(f"Stored extracted file path: {xml_name} -> {output_path.resolve()}")
        except zipfile.BadZipFile:
            logger.error(f"Invalid PAK file format: {pak_path}")
        except PermissionError:
            logger.error(f"Permission denied accessing PAK file: {pak_path}")
        except Exception as e:
            logger.error(f"Error processing {pak_path.name}: {e}")
            logger.debug(f"Exception details:", exc_info=True)
    
    # Update hash file
    if new_hashes:
        existing_hashes.update(new_hashes)
        write_json(hash_file, existing_hashes)
        logger.debug(f"Updated file hashes in {hash_file}")
    
    # Check if we have all required files
    required_files = ["item"]
    missing_files = [f for f in required_files if f not in extracted_files]
    if missing_files:
        logger.error(f"Missing required XML files: {missing_files}")
        for name, path in extracted_files.items():
            logger.debug(f"Available file: {name} -> {path}")
    
    return extracted_files, xml_dir, temp_dir

def extract_xml_file(
    pak_file: zipfile.ZipFile, 
    xml_name: str, 
    in_pak_dir: str,
    raw_dir: Path,
    xml_dir: Path, 
    temp_dir: Path, 
    version_dir: Path, 
    existing_hashes: Dict[str, Any], 
    new_hashes: Dict[str, Dict[str, str]]
) -> Optional[Path]:
    """
    Extract a single XML file from a PAK file.
    
    Args:
        pak_file: Open ZipFile object for the PAK file
        xml_name: Name of the XML file without extension
        in_pak_dir: Directory within the PAK file
        raw_dir: Directory to save raw XML files
        xml_dir: Directory for processed XML files
        temp_dir: Temporary directory for extraction
        version_dir: Version directory
        existing_hashes: Dictionary of existing file hashes
        new_hashes: Dictionary to store new file hashes
    
    Returns:
        Path to the extracted XML file if successful, None otherwise
    """
    # Setup paths
    xml_in_pak = f"{in_pak_dir}{xml_name}.xml"
    output_path = raw_dir / f"{xml_name}.xml"
    
    # Compute relative path for hash tracking
    rel_path = str(output_path.relative_to(version_dir.parent.parent))
    
    # Check if we need to extract based on hash
    need_extract = True
    if output_path.exists() and rel_path in existing_hashes:
        try:
            current_hash = compute_file_hash(output_path)
            if current_hash == existing_hashes[rel_path]["xml_hash"]:
                logger.info(f"Skipping {xml_name}.xml (unchanged)")
                need_extract = False
        except (IOError, OSError) as e:
            logger.warning(f"Error computing hash for {output_path}: {e}")
    
    # Extract if needed
    if need_extract:
        try:
            # Clean temp dir before extraction
            clean_directory(temp_dir)
            
            # Extract to temp
            pak_file.extract(xml_in_pak, temp_dir)
            extracted_file = temp_dir / xml_in_pak
            
            if not extracted_file.exists():
                logger.error(f"Extraction failed: {xml_in_pak} not found in temp directory")
                return None
            
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy to output path
            shutil.copy2(extracted_file, output_path)
            
            # Update hash
            new_hash = compute_file_hash(output_path)
            new_hashes[rel_path] = {
                "xml_hash": new_hash, 
                "extracted": datetime.now().isoformat(),
                "source": xml_in_pak
            }
            
            logger.info(f"Extracted {xml_name}.xml to {output_path}")
        except KeyError:
            logger.error(f"File not found in PAK: {xml_in_pak}")
            return None
        except (IOError, OSError) as e:
            logger.error(f"I/O error extracting {xml_name}.xml: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to extract {xml_name}.xml: {e}")
            logger.debug(f"Exception details:", exc_info=True)
            return None
    
    return output_path

def create_combined_items_file(extracted_files: Dict[str, Path], xml_dir: Path) -> Tuple[Optional[ET.Element], Optional[Path]]:
    """
    Create a combined items XML file from individual XML files.
    
    Args:
        extracted_files: Dictionary mapping XML names to their file paths
        xml_dir: Directory for XML files
    
    Returns:
        Tuple containing:
        - Root Element of the combined XML if successful, None otherwise
        - Path to the combined XML file if successful, None otherwise
    """
    # Always create the combined file in the standard xml directory
    combined_path = xml_dir / "combined_items.xml"
    
    # Check if required files exist
    if "item" not in extracted_files:
        logger.error("Required file 'item.xml' not found in extracted files")
        logger.debug(f"Available files: {list(extracted_files.keys())}")
        return None, None
    
    try:
        # Parse main item.xml
        item_path = extracted_files["item"]
        logger.debug(f"Loading item.xml from {item_path}")
        
        if not item_path.exists():
            logger.error(f"File not found: {item_path}")
            return None, None
            
        main_tree = ET.parse(item_path)
        main_root = main_tree.getroot()
        
        # Create combined root
        combined_root = ET.Element(main_root.tag, main_root.attrib)
        
        # Find ItemClasses element
        main_classes = main_root.find(".//ItemClasses")
        if main_classes is None:
            logger.error("Could not find ItemClasses in item.xml")
            return None, None
        
        # Create ItemClasses element in combined file
        combined_classes = ET.SubElement(combined_root, "ItemClasses", main_classes.attrib)
        
        # Process main file items
        for item in main_classes:
            combined_classes.append(item)
        
        # Track item count for logging
        item_count = len(list(main_classes))
        
        # Process other files
        for name, path in extracted_files.items():
            if name.startswith("item__") and name != "text_ui_items":
                try:
                    logger.debug(f"Processing additional item file: {name}")
                    
                    if not path.exists():
                        logger.warning(f"File not found: {path}")
                        continue
                        
                    file_tree = ET.parse(path)
                    file_root = file_tree.getroot()
                    file_classes = file_root.find(".//ItemClasses")
                    
                    if file_classes is None:
                        logger.warning(f"No ItemClasses found in {name}.xml")
                        continue
                    
                    # Check if this is the horse items file
                    is_horse_file = name == "item__horse"
                    
                    item_count_before = len(list(combined_classes))
                    
                    for item in file_classes:
                        if is_horse_file and item.tag == "Armor":
                            # Convert to Horse for horse file
                            horse_item = convert_element(item, "Horse")
                            combined_classes.append(horse_item)
                        else:
                            # For all other items, add them directly
                            combined_classes.append(item)
                    
                    items_added = len(list(combined_classes)) - item_count_before
                    item_count += items_added
                    
                    logger.info(f"Added {items_added} items from {name}.xml")
                    if is_horse_file and items_added > 0:
                        logger.info(f"Converted Armor elements to Horse elements in {name}.xml")
                except ET.ParseError as pe:
                    logger.error(f"XML parse error in {name}.xml: {pe}")
                except Exception as e:
                    logger.error(f"Error processing {name}.xml: {e}")
                    logger.debug(f"Exception details:", exc_info=True)
        
        # Write the combined XML to file with proper formatting
        try:
            formatted_xml = format_xml(combined_root)
            
            with open(combined_path, 'wb') as f:
                f.write(formatted_xml)
            
            logger.info(f"Created combined items file with {item_count} items")
            return combined_root, combined_path
        except Exception as e:
            logger.error(f"Error writing combined XML file: {e}")
            return combined_root, None
    
    except ET.ParseError as pe:
        logger.error(f"XML parse error in main item.xml: {pe}")
        return None, None
    except Exception as e:
        logger.error(f"Error creating combined file: {e}")
        logger.debug(f"Exception details:", exc_info=True)
        return None, None

# This allows the module to be run directly for testing
if __name__ == "__main__":
    from config import ROOT_DIR, KCD2_DIR
    from scripts import get_version
    
    # Get version info
    version_id = get_version(ROOT_DIR, KCD2_DIR)
    if not version_id:
        logger.error("Failed to get version info")
        sys.exit(1)
    
    # Run the extraction
    xml_files = get_xml(ROOT_DIR, KCD2_DIR, version_id)
    logger.info(f"Extraction complete. Found {len(xml_files)} XML files")
    
    # Print the XML file mapping
    for name in xml_files:
        logger.info(f"Loaded XML: {name}")