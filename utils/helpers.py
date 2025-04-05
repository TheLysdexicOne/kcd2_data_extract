import json
from pathlib import Path
from utils.logger import logger
from xml.etree import ElementTree as ET

def read_json_file(file_path):
    """Read and parse a JSON file."""
    try:
        if not file_path.exists():
            logger.warning(f"File not found: {file_path}")
            return None
            
        with open(file_path, 'r') as f:
            return json.load(f)
            
    except Exception as e:
        logger.error(f"Error reading JSON file {file_path}: {e}")
        return None

def write_json_file(file_path, data, indent=4):
    """Write data to a JSON file."""
    try:
        # Ensure directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
            
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=indent)
        return True
            
    except Exception as e:
        logger.error(f"Error writing JSON file {file_path}: {e}")
        return False

def ensure_directory(directory_path):
    """Ensure a directory exists, creating it if necessary."""
    try:
        if not directory_path.exists():
            logger.info(f"Creating directory: {directory_path}")
            directory_path.mkdir(parents=True, exist_ok=True)
        return directory_path
    except Exception as e:
        logger.error(f"Error creating directory {directory_path}: {e}")
        return None

def rel_path(path, base=None):
    """Convert paths to relative form for logging purposes."""
    if base is None:
        from config import ROOT_DIR
        base = ROOT_DIR
    
    try:
        return path.relative_to(base)
    except ValueError:
        # If path can't be made relative to base, return as is
        return path

def format_xml(xml_element):
    """
    Format XML with proper indentation and without excessive blank lines.
    
    Args:
        xml_element: ElementTree element or XML string
        
    Returns:
        bytes or str: Formatted XML content
    """
    import xml.etree.ElementTree as ET
    
    try:
        # If lxml is available, use it for better formatting
        from lxml import etree as lxml_etree
        
        # Convert to string if it's an ElementTree element
        if isinstance(xml_element, ET.Element):
            xml_str = ET.tostring(xml_element, encoding='utf-8')
        else:
            xml_str = xml_element
            
        # Parse with lxml
        parser = lxml_etree.XMLParser(remove_blank_text=True)
        elem = lxml_etree.XML(xml_str, parser)
        
        # Format with proper indentation
        return lxml_etree.tostring(elem, encoding='utf-8', pretty_print=True)
    except ImportError:
        # Fallback to minidom with regex cleanup for excessive blank lines
        import xml.dom.minidom
        import re
        
        # Convert to string if it's an ElementTree element
        if isinstance(xml_element, ET.Element):
            xml_str = ET.tostring(xml_element, encoding='utf-8')
        else:
            xml_str = xml_element
            
        # Use minidom for basic formatting
        pretty_xml = xml.dom.minidom.parseString(xml_str).toprettyxml(indent="  ")
        
        # Remove excessive blank lines
        return re.sub(r'>\s*\n\s*\n+', '>\n', pretty_xml.encode('utf-8'))

def find_element_by_id(root, element_id):
    """
    Find an element with the specified ID using multiple search strategies.
    
    Args:
        root: XML root element
        element_id: ID to search for
    
    Returns:
        Element if found, None otherwise
    """
    # Try direct XPath first
    element = root.find(f".//*[@Id='{element_id}']")
    if element is not None:
        return element
    
    # Try case-insensitive search as a fallback
    for elem in root.findall(".//*[@Id]"):
        if elem.get("Id", "").lower() == element_id.lower():
            return elem
    
    return None

def copy_xml_element(elem):
    """
    Deep copy an XML element and all its children safely.
    
    Args:
        elem: Element to copy
    
    Returns:
        New Element that's a deep copy of the original
    """
    new_elem = ET.Element(elem.tag)
    
    # Copy attributes
    for key, value in elem.attrib.items():
        new_elem.set(key, value)
    
    # Copy children (recursively)
    for child in elem:
        new_child = copy_xml_element(child)
        new_elem.append(new_child)
    
    # Copy text content
    if elem.text:
        new_elem.text = elem.text
    if elem.tail:
        new_elem.tail = elem.tail
    
    return new_elem