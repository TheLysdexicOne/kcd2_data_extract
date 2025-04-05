import xml.etree.ElementTree as ET
from pathlib import Path
from collections import Counter
import json

def analyze_xml(xml_path, output_json=None):
    """
    Analyze XML file and print statistics about element types.
    Optionally write detailed element information to a JSON file.
    """
    print(f"Analyzing {xml_path}...")
    
    try:
        # Parse the XML
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        # Count all element types
        tag_counter = Counter()
        for elem in root.iter():
            tag_counter[elem.tag] += 1
        
        # Print results sorted by count (highest first)
        print("\nElement types found:")
        print("-" * 50)
        print(f"{'Tag Name':<30} {'Count':>10}")
        print("-" * 50)
        
        for tag, count in tag_counter.most_common():
            print(f"{tag:<30} {count:>10}")
            
        total_elements = sum(tag_counter.values())
        print("-" * 50)
        print(f"{'Total Elements:':<30} {total_elements:>10}")
        
        # Check for ItemClasses specifically
        item_classes = root.find(".//ItemClasses")
        element_data = {}
        
        if item_classes is not None:
            direct_children = list(item_classes)
            item_types = Counter(child.tag for child in direct_children)
            
            print("\nItem types inside ItemClasses:")
            print("-" * 50)
            print(f"{'Item Type':<30} {'Count':>10}")
            print("-" * 50)
            
            for tag, count in item_types.most_common():
                print(f"{tag:<30} {count:>10}")
                
                # Collect detailed information for each element type
                elements_of_type = [elem for elem in direct_children if elem.tag == tag]
                
                # Gather all attributes used by this element type
                all_attrs = set()
                for elem in elements_of_type:
                    all_attrs.update(elem.attrib.keys())
                
                # Create data structure for this element type
                element_data[tag] = {
                    "count": count,
                    "attributes": sorted(list(all_attrs))
                }
                
            print("-" * 50)
            print(f"{'Total Items:':<30} {len(direct_children):>10}")
            
            # Write element data to JSON if requested
            if output_json:
                with open(output_json, 'w', encoding='utf-8') as f:
                    json.dump(element_data, f, indent=2)
                print(f"\nDetailed element information written to {output_json}")
            
            return element_data
            
    except Exception as e:
        print(f"Error analyzing XML: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    # Path to the combined_items.xml file
    script_dir = Path(__file__).parent
    xml_path = script_dir / "combined_items.xml"
    
    # Alternatively, look for it in the final directory
    if not xml_path.exists():
        xml_path = script_dir.parent / "final" / "combined_items.xml"
    
    if xml_path.exists():
        json_output = script_dir / "elements.json"
        analyze_xml(xml_path, json_output)
    else:
        print(f"Error: Could not find combined_items.xml in expected locations")