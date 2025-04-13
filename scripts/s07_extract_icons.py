import os
import re
import zipfile
import subprocess
import shutil
import json
from PIL import Image
import traceback
from pathlib import Path
from typing import Dict, List, Any, Optional, Set

from utils import logger, ensure_dir

def extract_icons(root_dir: Path, version_id: str, kcd2_dir: Path, items_array: List[Dict[str, Any]]) -> Optional[Dict[str, Path]]:
    """
    Extract icon files from KCD2 data.
    
    Args:
        root_dir: Path to the root directory
        version_id: Version identifier string
        kcd2_dir: Path to the KCD2 directory
        items_array: Array of processed items
        
    Returns:
        Dictionary mapping icon IDs to icon file paths, or None if failed
    """
    logger.info("Extracting icons...")
    
    try:
        # Input validation
        if not items_array:
            logger.error("No items data provided for icon extraction")
            return None
            
        # Prepare directories
        version_dir = root_dir / "data" / "version" / version_id
        icon_dir = version_dir / "icon"
        ensure_dir(icon_dir)
        
        # Create subdirectories
        raw_icon_dir = icon_dir / "raw"
        ensure_dir(raw_icon_dir)
        temp_dds_dir = icon_dir / "temp"
        ensure_dir(temp_dds_dir)
        conv_dds_dir = temp_dds_dir / "conv"
        ensure_dir(conv_dds_dir)
        webp_icon_dir = icon_dir / "webp"
        ensure_dir(webp_icon_dir)
        
        # Check for existing icons mapping
        icons_mapping_file = icon_dir / "icons_mapping.json"
        existing_icons: Dict[str, Path] = {}
        if icons_mapping_file.exists():
            try:
                with open(icons_mapping_file, 'r') as f:
                    existing_mapping = json.load(f)
                    # Convert string paths back to Path objects
                    existing_icons = {k: Path(v) for k, v in existing_mapping.items() if Path(v).exists()}
                logger.info(f"Found {len(existing_icons)} previously extracted icons")
            except Exception as e:
                logger.warning(f"Failed to load existing icons mapping: {e}")
        
        # Paths to tools
        dds_unsplitter_file = root_dir / "bin" / "DDS-Unsplitter.exe"
        texconv_file = root_dir / "bin" / "texconv.exe"
        
        # Define the path to the compressed icons file
        compressed_icons_file = kcd2_dir / "Data" / "IPL_GameData.pak"
        if not compressed_icons_file.exists():
            logger.error(f"Compressed icons file not found: {compressed_icons_file}")
            return None
            
        # Extract icon IDs from items array to only process needed icons
        icon_ids_to_extract = set()
        for item in items_array:
            if "iconId" in item and item["iconId"]:
                icon_id = item["iconId"]
                # Only add to extraction list if not already extracted
                if icon_id not in existing_icons:
                    icon_ids_to_extract.add(icon_id)
        
        logger.info(f"Found {len(icon_ids_to_extract)} new unique icon IDs to extract")
        
        # If no new icons to extract, return the existing icons
        if not icon_ids_to_extract:
            logger.info("No new icons to extract, using existing icons")
            return existing_icons
        
        # Process the icons
        extracted_icons = process_icons(
            version_id=version_id,
            compressed_icons_file=compressed_icons_file,
            dds_unsplitter_file=dds_unsplitter_file,
            texconv_file=texconv_file,
            icon_dir=icon_dir,
            temp_dds_dir=temp_dds_dir,
            conv_dds_dir=conv_dds_dir,
            webp_icon_dir=webp_icon_dir,
            icon_ids_to_extract=icon_ids_to_extract
        )
        
        # Merge with existing icons
        all_icons = {**existing_icons, **extracted_icons}
        
        # Clean up temporary files if successful
        if extracted_icons and is_empty_directory_tree(temp_dds_dir):
            logger.info("Cleaning up temporary icon files...")
            shutil.rmtree(temp_dds_dir)
        
        return all_icons
        
    except Exception as e:
        logger.error(f"Error extracting icons: {str(e)}")
        logger.debug(traceback.format_exc())
        return None

def is_empty_directory_tree(directory: Path) -> bool:
    """
    Check if a directory tree is empty (no files).
    
    Args:
        directory: Path to check
        
    Returns:
        True if the directory tree is empty, False otherwise
    """
    for root, _, files in os.walk(directory):
        if files:
            return False
    return True

def process_icons(
    version_id: str,
    compressed_icons_file: Path,
    dds_unsplitter_file: Path,
    texconv_file: Path,
    icon_dir: Path,
    temp_dds_dir: Path,
    conv_dds_dir: Path,
    webp_icon_dir: Path,
    icon_ids_to_extract: Set[str]
) -> Dict[str, Path]:
    """
    Process icons from the compressed file and convert them to webp format.
    
    Args:
        version_id: Version identifier string
        compressed_icons_file: Path to the compressed icons file
        dds_unsplitter_file: Path to the DDS-Unsplitter executable
        texconv_file: Path to the texconv executable
        icon_dir: Path to the icon directory
        temp_dds_dir: Path to the temp directory for DDS files
        conv_dds_dir: Path to the directory for converted DDS files
        webp_icon_dir: Path to the directory for webp files
        icon_ids_to_extract: Set of icon IDs to extract
        
    Returns:
        Dictionary mapping icon IDs to their file paths
    """
    merge_success_count = 0
    merge_fail_count = 0
    convert_success_count = 0
    convert_fail_count = 0
    convert_skipped_count = 0
    
    # Dictionary to store extracted icon paths
    extracted_icons: Dict[str, Path] = {}
    
    # Step 1: Extract icons from pak file
    logger.info("Extracting icons from compressed file...")
    with zipfile.ZipFile(compressed_icons_file, 'r') as pak:
        # Get list of files to extract
        icon_files = [f for f in pak.namelist() if f.startswith('Libs/UI/Textures/Icons/Items/')]
        logger.info(f"Found {len(icon_files)} icon files in the compressed file")
        
        # Process each file
        for file in icon_files:
            # Get the icon ID from the file name
            file_path = (temp_dds_dir / os.path.relpath(file, 'Libs/UI/Textures/Icons/Items/')).resolve()
            icon_id = re.sub(r'\.[^.]+$', '', os.path.splitext(os.path.basename(file_path))[0].replace('_icon', ''))
            
            # Skip if not in our list of icons to extract
            if icon_id not in icon_ids_to_extract:
                continue
                
            # Skip if already extracted
            if icon_id in extracted_icons:
                logger.debug(f"Skipped extracting (already exists): {icon_id}")
                convert_skipped_count += 1
                continue
                
            # Extract the file
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with pak.open(file) as source, open(file_path, 'wb') as target:
                target.write(source.read())
            logger.debug(f"Extracted {file} to {file_path}")
    
    # Step 2: Try to convert DDS files directly to webp
    logger.info("Converting DDS files to WEBP format...")
    for root, _, files in os.walk(temp_dds_dir):
        for file in files:
            if file.endswith('.dds') and not any(char.isdigit() for char in file.split('.')[-1]):
                dds_file_path = Path(root) / file
                icon_id = os.path.splitext(os.path.basename(file))[0].replace('_icon', '')
                webp_file_path = webp_icon_dir / f"{icon_id}.webp"
                webp_file_path.parent.mkdir(parents=True, exist_ok=True)
                
                try:
                    with Image.open(dds_file_path) as img:
                        img.save(webp_file_path, 'WEBP')
                    extracted_icons[icon_id] = webp_file_path
                    os.remove(dds_file_path)  # Delete the original file after successful conversion
                    logger.debug(f"Successfully converted {dds_file_path.name} to {webp_file_path.name} using Pillow")
                    convert_success_count += 1
                except Exception as e:
                    logger.debug(f"Failed to convert {dds_file_path.name} directly: {e}")
                    # Will try with DDS-Unsplitter next
    
    # Step 3: Use DDS-Unsplitter on files that failed direct conversion
    logger.info("Using DDS-Unsplitter on split DDS files...")
    for root, _, files in os.walk(temp_dds_dir):
        for file in files:
            if file.endswith('.dds'):
                dds_file_path = Path(root) / file
                
                try:
                    logger.debug(f"Running DDS-Unsplitter on {dds_file_path.name}")
                    process = subprocess.run(
                        [str(dds_unsplitter_file), str(dds_file_path)],
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    logger.debug(f"DDS-Unsplitter output: {process.stdout}")
                    
                    # Delete any .dds.[0-9] files
                    for i in range(10):
                        part_file = Path(f"{dds_file_path}.{i}")
                        if part_file.exists():
                            part_file.unlink()
                    
                    logger.info(f"Successfully merged {dds_file_path.name} using DDS-Unsplitter")
                    merge_success_count += 1
                except subprocess.CalledProcessError as e:
                    logger.error(f"Failed to merge {dds_file_path.name} using DDS-Unsplitter: {e}")
                    logger.debug(f"Error details: stdout={e.stdout}, stderr={e.stderr}")
                    merge_fail_count += 1
    
    # Step 4: Convert merged DDS files to BC7_UNORM format
    logger.info("Converting merged DDS files to BC7_UNORM format...")
    for file in os.listdir(temp_dds_dir):
        dds_file_path = temp_dds_dir / file
        if dds_file_path.is_file() and file.endswith('.dds'):
            try:
                logger.debug(f"Running texconv on {dds_file_path.name}")
                process = subprocess.run(
                    [str(texconv_file), '-f', 'BC7_UNORM', '-y', '-o', str(conv_dds_dir), str(dds_file_path)],
                    capture_output=True,
                    text=True,
                    check=True
                )
                logger.debug(f"texconv output: {process.stdout}")
                
                # Delete the original file after successful conversion
                dds_file_path.unlink()
                logger.info(f"Successfully converted {dds_file_path.name} to BC7_UNORM format")
                convert_success_count += 1
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to convert {dds_file_path.name} to BC7_UNORM using texconv: {e}")
                logger.debug(f"Error details: stdout={e.stdout}, stderr={e.stderr}")
                convert_fail_count += 1
    
    # Step 5: Convert the BC7_UNORM format DDS files to webp
    logger.info("Converting BC7_UNORM DDS files to WEBP format...")
    for root, _, files in os.walk(conv_dds_dir):
        for file in files:
            if file.endswith('.dds'):
                dds_file_path = Path(root) / file
                icon_id = os.path.splitext(os.path.basename(file))[0].replace('_icon', '')
                webp_file_path = webp_icon_dir / f"{icon_id}.webp"
                webp_file_path.parent.mkdir(parents=True, exist_ok=True)
                
                try:
                    with Image.open(dds_file_path) as img:
                        img.save(webp_file_path, 'WEBP')
                    extracted_icons[icon_id] = webp_file_path
                    os.remove(dds_file_path)  # Delete the original file after successful conversion
                    logger.info(f"Successfully converted {dds_file_path.name} to {webp_file_path.name}")
                    convert_success_count += 1
                except Exception as e:
                    logger.error(f"Failed to convert {dds_file_path.name} to {webp_file_path.name}: {e}")
                    convert_fail_count += 1
    
    # Log summary
    logger.info(f"Icon extraction summary:")
    logger.info(f"- Merged DDS files: {merge_success_count} successful, {merge_fail_count} failed")
    logger.info(f"- Converted files: {convert_success_count} successful, {convert_fail_count} failed, {convert_skipped_count} skipped")
    logger.info(f"- Total icons extracted: {len(extracted_icons)}")
    
    return extracted_icons

# This allows the module to be run directly for testing
if __name__ == "__main__":
    from config import ROOT_DIR, KCD2_DIR
    import json
    
    # For testing, load a sample items array
    test_version_id = "1_2"
    version_dir = ROOT_DIR / "data" / "version" / test_version_id
    
    # Check if processed items exists
    processed_file = version_dir / "processed_items.json"
    if processed_file.exists():
        with open(processed_file, 'r') as f:
            items_data = json.load(f)
        
        # Run the extraction
        extracted_icons = extract_icons(ROOT_DIR, test_version_id, KCD2_DIR, items_data)
        
        # Report results
        if extracted_icons:
            logger.info(f"Successfully extracted {len(extracted_icons)} icons")
            
            # Save extracted icons mapping
            icons_mapping_file = version_dir / "icon" / "icons_mapping.json"
            with open(icons_mapping_file, 'w') as f:
                # Convert Path objects to strings
                icons_mapping = {k: str(v) for k, v in extracted_icons.items()}
                json.dump(icons_mapping, f, indent=2)
            
            logger.info(f"Saved icons mapping to {icons_mapping_file}")
        else:
            logger.error("Failed to extract icons")
    else:
        logger.error(f"Test file not found: {processed_file}")