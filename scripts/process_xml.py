from pathlib import Path
import sys
import xml.etree.ElementTree as ET
import traceback

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.absolute()))
from utils.logger import logger
from utils.helpers import format_xml, find_element_by_id, copy_xml_element

def fix_alias(xml_file_path):
    """
    Process XML file to convert ItemAlias elements to their full parent elements.
    Always overwrites the input file.
    
    Args:
        xml_file_path (Path): Path to the XML file to process
    
    Returns:
        Path: Path to the processed XML file, or None on error
    """
    logger.info(f"Processing XML aliases in {xml_file_path}")
    
    try:
        # Parse the XML file
        tree = ET.parse(xml_file_path)
        root = tree.getroot()
        
        # Find all ItemAlias elements
        aliases = root.findall(".//ItemAlias")
        alias_count = len(aliases)
        logger.info(f"Found {alias_count} ItemAlias elements to process")
        
        # Process each alias
        replaced_count = 0
        skipped_count = 0
        
        for alias in list(aliases):  # Convert to list to safely modify during iteration
            source_id = alias.get('SourceItemId')
            if not source_id:
                logger.warning(f"ItemAlias missing SourceItemId attribute, skipping")
                skipped_count += 1
                continue
            
            # Find the source item
            source_item = find_element_by_id(root, source_id)
            
            if source_item is not None:
                # Create a deep copy of the source item
                new_item = copy_xml_element(source_item)
                
                # Override with attributes from the alias (except SourceItemId)
                for key, value in alias.attrib.items():
                    if key != 'SourceItemId':
                        new_item.set(key, value)
                
                # Find the parent of the alias
                parent = None
                for p in root.iter():
                    if alias in list(p):
                        parent = p
                        break
                
                if parent is not None:
                    # Replace the alias with the new expanded item
                    for i, child in enumerate(list(parent)):
                        if child is alias:
                            parent[i] = new_item
                            replaced_count += 1
                            logger.debug(f"Replaced alias {alias.get('Id')} with expanded item from {source_id}")
                            break
                else:
                    logger.warning(f"Could not find parent for alias {alias.get('Id')}")
                    skipped_count += 1
            else:
                logger.warning(f"Source item not found for ID: {source_id}")
                skipped_count += 1
        
        # Write the processed XML to file (overwriting the original)
        formatted_xml = format_xml(root)
        with open(xml_file_path, 'wb') as f:
            f.write(formatted_xml)
            
        logger.info(f"Successfully processed {replaced_count} of {alias_count} aliases, skipped {skipped_count}")
        logger.info(f"Updated file: {xml_file_path}")
        
        return xml_file_path
    
    except Exception as e:
        logger.error(f"Error processing XML aliases: {e}")
        logger.error(traceback.format_exc())
        return None

if __name__ == "__main__":
    # This allows the script to be run directly for testing
    import argparse
    
    parser = argparse.ArgumentParser(description='Process XML files to expand alias elements')
    parser.add_argument('--input', '-i', type=str, help='Path to input XML file (will be overwritten)')
    
    args = parser.parse_args()
    
    # Setup paths
    root_dir = Path(__file__).parent.parent
    
    if args.input:
        input_path = Path(args.input)
    else:
        # Default to combined_items.xml in raw directory
        version_dir = root_dir / "data" / "version" / "1_2"
        input_path = version_dir / "xml" / "raw" / "combined_items.xml"
        
        # If not found, check final directory
        if not input_path.exists():
            input_path = version_dir / "xml" / "final" / "combined_items.xml"
    
    if input_path.exists():
        fix_alias(input_path)
    else:
        logger.error(f"Input file not found: {input_path}")