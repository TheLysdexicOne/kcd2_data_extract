import xml.etree.ElementTree as ET
import xmltodict
from .logger import logger
from .json_helpers import unwrap_key, xform_ui_dict

def xml_tree_to_dict(elem):
    """
    Given an xml.etree.ElementTree.Element, return a native Python dict.
    """
    # xmltodict wants bytes or string; serialize just the subtree
    xml_str = ET.tostring(elem, encoding="utf-8")
    return xmltodict.parse(xml_str)

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

def convert_xml(xml_trees):
    """
    Process XML files by converting to dictionaries and fixing aliases.
    
    Args:
        xml_files (dict): Dictionary containing parsed XML trees
        debug (bool): Whether to save processed data to JSON
    
    Returns:
        tuple: (combined_items_dict, text_ui_items_dict) after processing
    """
    
    try:
        # Convert XML trees to dictionaries using a loop
        combined_items_tree = xml_trees["combined_items"]
        text_ui_items_tree = xml_trees["text_ui_items"]
        
        combined_dict = xml_tree_to_dict(combined_items_tree.getroot())
        text_ui_dict = xml_tree_to_dict(text_ui_items_tree.getroot())
        
        text_ui_dict = unwrap_key(unwrap_key(text_ui_dict, "Table"), "Row")
        text_ui_dict = xform_ui_dict(text_ui_dict)
        combined_dict = unwrap_key(unwrap_key(combined_dict,"database"), "ItemClasses")
        combined_dict.pop("@version")

        return (combined_dict, text_ui_dict)
        
    except Exception as e:
        logger.error(f"Error processing XML: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None

def xml_tree_to_dict(elem):
    """
    Given an xml.etree.ElementTree.Element, return a native Python dict.
    """
    # xmltodict wants bytes or string; serialize just the subtree
    xml_str = ET.tostring(elem, encoding="utf-8")
    return xmltodict.parse(xml_str)