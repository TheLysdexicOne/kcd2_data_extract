import zipfile
import hashlib
import shutil
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
from typing import Dict, Tuple, Optional, Any, List, Set, Mapping
from utils import logger, read_json, write_json, ensure_dir, format_xml

def get_xml(root_dir: Path, version_id: str, kcd2_dir: Path) -> Dict[str, ET.ElementTree]:
    """
    Extract XML files from PAK files and create a combined items file.
    
    Args:
        root_dir: Path to project root directory
        kcd2_dir: Path to KCD2 directory
        version_id: Version ID (e.g. "1_2")
    
    Returns:
        Dictionary mapping XML names to their parsed ElementTree objects
    """
    # Initialize result dictionary
    xml_trees: Dict[str, ET.ElementTree] = {}
    
    try:
        # Validate inputs
        if not isinstance(root_dir, Path) or not isinstance(kcd2_dir, Path) or not isinstance(version_id, str):
            logger.error("Invalid input parameters to get_xml")
            return {}
        
        # Construct version directory path
        version_dir = root_dir / "data" / "version" / version_id
        
        # Load XML configuration
        xml_config = read_json(root_dir / "config" / "xml_files.json")
        if not xml_config:
            logger.error("Failed to load XML configuration")
            return {}
        
        # Extract XML files
        extracted_files, xml_dir, temp_dir = extract_xml_files(kcd2_dir, version_dir, xml_config)
        if not extracted_files:
            logger.error("No XML files were successfully extracted")
            return {}
        
        # Create combined items file if we have the base item.xml
        if "item" in extracted_files:
            logger.info("Combining items from XML files...")
            combined_root, combined_path = create_combined_items_file(extracted_files, xml_dir)
            if combined_root is not None and combined_path is not None:
                xml_trees["combined_items"] = ET.ElementTree(combined_root)
                logger.debug(f"Added combined_items to XML trees from {combined_path}")
            else:
                logger.error("Failed to create combined items file")
                return {}
        else:
            logger.error("Could not create combined items file: item.xml not found")
            return {}
        
        # Add text_ui_items to result if extracted
        if "text_ui_items" in extracted_files:
            try:
                text_ui_path = extracted_files["text_ui_items"]
                xml_trees["text_ui_items"] = ET.parse(text_ui_path)
                logger.debug(f"Added text_ui_items to XML trees from {text_ui_path}")
            except Exception as e:
                logger.error(f"Failed to parse text_ui_items.xml: {e}")
                return {}
        
        # Clean up temp directory
        clean_directory(temp_dir)
        
        # Final validation
        required_keys = ["combined_items", "text_ui_items"]
        missing_keys = [key for key in required_keys if key not in xml_trees]
        if missing_keys:
            logger.error(f"Missing required XML trees: {missing_keys}")
            return {}
        
        logger.info(f"XML extraction complete. Loaded {len(xml_trees)} XML trees")
        return xml_trees
        
    except Exception as e:
        logger.error(f"Critical error in get_xml: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return {}

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
    
    # Add counters for tracking file processing
    total_files = 0
    extracted_count = 0
    skipped_count = 0
    
    # Collect valid PAK files first
    valid_pak_files = []
    for pak_name, pak_info in xml_config.items():
        pak_path = kcd2_dir / pak_info["kcd2_pak_file"]
        if pak_path.exists():
            valid_pak_files.append((pak_path, pak_info))
        else:
            logger.error(f"PAK file not found: {pak_path}")
    
    # Log all PAK files to be processed
    if valid_pak_files:
        pak_names = ", ".join([pak_path.name for pak_path, _ in valid_pak_files])
        logger.info(f"Extracting XML files: {pak_names}...")
    else:
        logger.warning("No valid PAK files found to extract")
        return {}, xml_dir, temp_dir

    for pak_path, pak_info in valid_pak_files:
        try:
            with zipfile.ZipFile(pak_path, 'r') as pak_file:
                # Process each XML to extract
                for file_info in pak_info["files"]:
                    xml_name = file_info["name"]
                    in_pak_dir = file_info["in_pak_dir"]
                    total_files += 1
                    
                    # Extract the file
                    output_path, was_extracted = extract_xml_file(
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
                        
                        # Update counters
                        if was_extracted:
                            extracted_count += 1
                        else:
                            skipped_count += 1
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
    
    # Log summary of extraction process
    logger.info(f"XML extraction summary: {total_files} total files, {extracted_count} extracted, {skipped_count} skipped (unchanged)")
    
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
) -> Tuple[Optional[Path], bool]:
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
        Tuple containing:
        - Path to the extracted XML file if successful, None otherwise
        - Boolean indicating whether the file was freshly extracted (True) or skipped (False)
    """
    # Input validation
    if not isinstance(pak_file, zipfile.ZipFile) or not isinstance(xml_name, str):
        logger.error(f"Invalid input parameters for extract_xml_file: {xml_name}")
        return None, False
        
    if not isinstance(raw_dir, Path) or not isinstance(temp_dir, Path):
        logger.error(f"Invalid directory paths for extract_xml_file: {xml_name}")
        return None, False
    
    # Setup paths
    xml_in_pak = f"{in_pak_dir}{xml_name}.xml"
    output_path = raw_dir / f"{xml_name}.xml"
    
    try:
        # Compute relative path for hash tracking
        rel_path = str(output_path.relative_to(version_dir.parent.parent))
        
        # Check if we need to extract based on hash
        need_extract = True
        if output_path.exists() and rel_path in existing_hashes:
            try:
                current_hash = compute_file_hash(output_path)
                if current_hash == existing_hashes[rel_path]["xml_hash"]:
                    logger.debug(f"Skipping {xml_name}.xml (unchanged)")
                    return output_path, False
            except (IOError, OSError) as e:
                logger.warning(f"Error computing hash for {output_path}: {e}")
                # Continue with extraction as fallback
        
        # Clean temp dir before extraction
        clean_directory(temp_dir)
        
        # Extract to temp
        pak_file.extract(xml_in_pak, temp_dir)
        extracted_file = temp_dir / xml_in_pak
        
        if not extracted_file.exists():
            logger.error(f"Extraction failed: {xml_in_pak} not found in temp directory")
            return None, False
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Copy to output path
        shutil.copy2(extracted_file, output_path)
        
        # Verify the file was copied successfully
        if not output_path.exists() or output_path.stat().st_size == 0:
            logger.error(f"Failed to copy {xml_name}.xml to output path or file is empty")
            return None, False
        
        # Update hash
        new_hash = compute_file_hash(output_path)
        new_hashes[rel_path] = {
            "xml_hash": new_hash, 
            "extracted": datetime.now().isoformat(),
            "source": xml_in_pak
        }
        
        logger.info(f"Extracted {xml_name}.xml to {output_path}")
        return output_path, True
        
    except KeyError:
        logger.error(f"File not found in PAK: {xml_in_pak}")
        return None, False
    except (IOError, OSError) as e:
        logger.error(f"I/O error extracting {xml_name}.xml: {e}")
        return None, False
    except Exception as e:
        logger.error(f"Failed to extract {xml_name}.xml: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return None, False

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
    
    try:
        # Input validation
        if not isinstance(extracted_files, dict) or not isinstance(xml_dir, Path):
            logger.error("Invalid input parameters to create_combined_items_file")
            return None, None
            
        # Check if required files exist
        if "item" not in extracted_files:
            logger.error("Required file 'item.xml' not found in extracted files")
            logger.debug(f"Available files: {list(extracted_files.keys())}")
            return None, None
        
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
        
        # Process main file items - use extend for better performance
        for item in main_classes:
            combined_classes.append(item)
        
        # Track item count for logging
        item_count = len(list(main_classes))
        
        # Dictionary to track items added from each file
        items_added_by_file: Dict[str, int] = {}
        
        # Process other files more efficiently
        for name, path in extracted_files.items():
            if not name.startswith("item__") or name == "text_ui_items":
                continue
                
            try:
                if not path.exists():
                    logger.warning(f"File not found: {path}")
                    continue
                    
                file_tree = ET.parse(path)
                file_root = file_tree.getroot()
                file_classes = file_root.find(".//ItemClasses")
                
                if file_classes is None:
                    logger.warning(f"No ItemClasses found in {name}.xml")
                    continue
                
                # For better performance, process in batches
                items_to_add = []
                for item in file_classes:
                    # Add all items directly without type conversion
                    items_to_add.append(item)
                
                # Add all items at once for better performance
                for item in items_to_add:
                    combined_classes.append(item)
                
                items_added = len(items_to_add)
                item_count += items_added
                
                # Store the count for summary logging
                file_type = name.replace('item__', '')
                items_added_by_file[file_type] = items_added
                
                logger.debug(f"Added {items_added} items from {name}.xml")
                
            except ET.ParseError as pe:
                logger.error(f"XML parse error in {name}.xml: {pe}")
                return None, None
            except Exception as e:
                logger.error(f"Error processing {name}.xml: {e}")
                import traceback
                logger.debug(traceback.format_exc())
                return None, None
        
        # Log summary of added items
        if items_added_by_file:
            sorted_items = sorted(items_added_by_file.items(), key=lambda x: x[1], reverse=True)
            items_summary = ", ".join([f"{count} {file_type}" for file_type, count in sorted_items])
            logger.info(f"Added items: {items_summary}")
        
        logger.info(f"Created combined items file with {item_count} items")
        return combined_root, combined_path
    
    except ET.ParseError as pe:
        logger.error(f"XML parse error in main item.xml: {pe}")
        return None, None
    except Exception as e:
        logger.error(f"Error creating combined file: {e}")
        import traceback
        logger.debug(traceback.format_exc())
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