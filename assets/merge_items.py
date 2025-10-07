#!/usr/bin/env python3
"""
Merge roomitemtypes.json and wallitemtypes.json into FurnitureData.json
Checks for duplicate IDs and logs warnings for existing entries.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Set

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def load_json(filepath: str) -> Dict | List:
    """Load JSON data from file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"File not found: {filepath}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {filepath}: {e}")
        raise


def save_json(filepath: str, data: Dict) -> None:
    """Save JSON data to file with indentation."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    logger.info(f"Successfully saved merged data to {filepath}")


def get_item_info(item: Dict) -> str:
    """Get item identification string for logging."""
    classname = item.get('classname', 'N/A')
    name = item.get('name', 'N/A')
    item_id = item.get('id', 'N/A')
    return f"ID: {item_id}, Classname: {classname}, Name: {name}"


def check_duplicates_in_list(items: List[Dict], item_type: str) -> Set:
    """Check for duplicate IDs within a list and return set of IDs."""
    id_map = {}
    duplicate_ids = set()
    
    for item in items:
        item_id = item.get('id')
        if item_id is None:
            continue
            
        if item_id in id_map:
            if item_id not in duplicate_ids:
                # Log the first occurrence
                logger.warning(f"Duplicate ID found in source {item_type}: {get_item_info(id_map[item_id])}")
                duplicate_ids.add(item_id)
            # Log the duplicate
            logger.warning(f"Duplicate ID found in source {item_type}: {get_item_info(item)}")
        else:
            id_map[item_id] = item
    
    return set(id_map.keys())


def merge_into_furniture_data(
    roomitems_file: str = './roomitemtypes.json',
    wallitems_file: str = './wallitemtypes.json',
    furniture_data_file: str = './assets/gamedata/FurnitureData.json'
) -> None:
    """
    Merge room and wall item types into FurnitureData.json.
    Only adds items with IDs that don't already exist.
    """
    logger.info("Starting furniture data merge (INTO FurnitureData.json)...")
    
    # Load all files
    logger.info(f"Loading {roomitems_file}...")
    roomitems = load_json(roomitems_file)
    
    logger.info(f"Loading {wallitems_file}...")
    wallitems = load_json(wallitems_file)
    
    logger.info(f"Loading {furniture_data_file}...")
    furniture_data = load_json(furniture_data_file)
    
    # Ensure proper structure exists
    if 'roomitemtypes' not in furniture_data:
        furniture_data['roomitemtypes'] = {'furnitype': []}
    if 'furnitype' not in furniture_data['roomitemtypes']:
        furniture_data['roomitemtypes']['furnitype'] = []
        
    if 'wallitemtypes' not in furniture_data:
        furniture_data['wallitemtypes'] = {'furnitype': []}
    if 'furnitype' not in furniture_data['wallitemtypes']:
        furniture_data['wallitemtypes']['furnitype'] = []
    
    # Check for duplicates in source files
    logger.info("Checking for duplicates in source files...")
    check_duplicates_in_list(roomitems, "roomitemtypes.json")
    check_duplicates_in_list(wallitems, "wallitemtypes.json")
    
    # Get existing IDs from furniture_data
    existing_room_ids = {
        item.get('id') for item in furniture_data['roomitemtypes']['furnitype']
        if item.get('id') is not None
    }
    existing_wall_ids = {
        item.get('id') for item in furniture_data['wallitemtypes']['furnitype']
        if item.get('id') is not None
    }
    
    # Merge room items
    logger.info("Merging room items...")
    room_added = 0
    room_skipped = 0
    
    for item in roomitems:
        item_id = item.get('id')
        
        if item_id is None:
            logger.warning(f"Skipping room item with null ID: {get_item_info(item)}")
            room_skipped += 1
            continue
        
        if item_id in existing_room_ids:
            logger.warning(f"Room item ID already exists, skipping: {get_item_info(item)}")
            room_skipped += 1
            continue
        
        furniture_data['roomitemtypes']['furnitype'].append(item)
        existing_room_ids.add(item_id)
        room_added += 1
    
    # Merge wall items
    logger.info("Merging wall items...")
    wall_added = 0
    wall_skipped = 0
    
    for item in wallitems:
        item_id = item.get('id')
        
        if item_id is None:
            logger.warning(f"Skipping wall item with null ID: {get_item_info(item)}")
            wall_skipped += 1
            continue
        
        if item_id in existing_wall_ids:
            logger.warning(f"Wall item ID already exists, skipping: {get_item_info(item)}")
            wall_skipped += 1
            continue
        
        furniture_data['wallitemtypes']['furnitype'].append(item)
        existing_wall_ids.add(item_id)
        wall_added += 1
    
    # Save merged data
    save_json(furniture_data_file, furniture_data)
    
    # Summary
    logger.info("=" * 60)
    logger.info("MERGE SUMMARY (INTO FurnitureData.json)")
    logger.info("=" * 60)
    logger.info(f"Room items added: {room_added}")
    logger.info(f"Room items skipped: {room_skipped}")
    logger.info(f"Wall items added: {wall_added}")
    logger.info(f"Wall items skipped: {wall_skipped}")
    logger.info(f"Total items added: {room_added + wall_added}")
    logger.info(f"Total items skipped: {room_skipped + wall_skipped}")
    logger.info("=" * 60)


def extract_from_furniture_data(
    furniture_data_file: str = './assets/gamedata/FurnitureData.json',
    other_furniture_data_file: str = './assets/gamedata/FurnitureData_other.json',
    roomitems_file: str = './roomitemtypes.json',
    wallitems_file: str = './wallitemtypes.json'
) -> None:
    """
    Compare two FurnitureData files and extract items that exist in the first
    but not in the second. Add those items to roomitemtypes.json and wallitemtypes.json
    if they don't already exist there.
    """
    logger.info("Starting furniture data extraction (FROM FurnitureData.json)...")
    
    # Load all files
    logger.info(f"Loading {furniture_data_file}...")
    furniture_data = load_json(furniture_data_file)
    
    logger.info(f"Loading {other_furniture_data_file}...")
    other_furniture_data = load_json(other_furniture_data_file)
    
    logger.info(f"Loading {roomitems_file}...")
    try:
        roomitems = load_json(roomitems_file)
    except FileNotFoundError:
        logger.warning(f"{roomitems_file} not found, creating empty list")
        roomitems = []
    
    logger.info(f"Loading {wallitems_file}...")
    try:
        wallitems = load_json(wallitems_file)
    except FileNotFoundError:
        logger.warning(f"{wallitems_file} not found, creating empty list")
        wallitems = []
    
    # Get IDs from other_furniture_data (items we DON'T want to extract)
    other_room_ids = {
        item.get('id') for item in other_furniture_data.get('roomitemtypes', {}).get('furnitype', [])
        if item.get('id') is not None
    }
    other_wall_ids = {
        item.get('id') for item in other_furniture_data.get('wallitemtypes', {}).get('furnitype', [])
        if item.get('id') is not None
    }
    
    # Get existing IDs from roomitems and wallitems files
    existing_room_ids = {
        item.get('id') for item in roomitems
        if item.get('id') is not None
    }
    existing_wall_ids = {
        item.get('id') for item in wallitems
        if item.get('id') is not None
    }
    
    # Check for duplicates in target files
    logger.info("Checking for duplicates in target files...")
    check_duplicates_in_list(roomitems, roomitems_file)
    check_duplicates_in_list(wallitems, wallitems_file)
    
    # Extract room items
    logger.info("Extracting room items...")
    room_added = 0
    room_skipped = 0
    
    for item in furniture_data.get('roomitemtypes', {}).get('furnitype', []):
        item_id = item.get('id')
        
        if item_id is None:
            logger.warning(f"Skipping room item with null ID: {get_item_info(item)}")
            room_skipped += 1
            continue
        
        # Skip if exists in other furniture data
        if item_id in other_room_ids:
            room_skipped += 1
            continue
        
        # Skip if already exists in roomitems
        if item_id in existing_room_ids:
            logger.warning(f"Room item ID already exists in {roomitems_file}, skipping: {get_item_info(item)}")
            room_skipped += 1
            continue
        
        roomitems.append(item)
        existing_room_ids.add(item_id)
        room_added += 1
        logger.info(f"Added room item: {get_item_info(item)}")
    
    # Extract wall items
    logger.info("Extracting wall items...")
    wall_added = 0
    wall_skipped = 0
    
    for item in furniture_data.get('wallitemtypes', {}).get('furnitype', []):
        item_id = item.get('id')
        
        if item_id is None:
            logger.warning(f"Skipping wall item with null ID: {get_item_info(item)}")
            wall_skipped += 1
            continue
        
        # Skip if exists in other furniture data
        if item_id in other_wall_ids:
            wall_skipped += 1
            continue
        
        # Skip if already exists in wallitems
        if item_id in existing_wall_ids:
            logger.warning(f"Wall item ID already exists in {wallitems_file}, skipping: {get_item_info(item)}")
            wall_skipped += 1
            continue
        
        wallitems.append(item)
        existing_wall_ids.add(item_id)
        wall_added += 1
        logger.info(f"Added wall item: {get_item_info(item)}")
    
    # Save extracted data
    if room_added > 0:
        save_json(roomitems_file, roomitems)
    else:
        logger.info(f"No room items to add, skipping save of {roomitems_file}")
    
    if wall_added > 0:
        save_json(wallitems_file, wallitems)
    else:
        logger.info(f"No wall items to add, skipping save of {wallitems_file}")
    
    # Summary
    logger.info("=" * 60)
    logger.info("EXTRACTION SUMMARY (FROM FurnitureData.json)")
    logger.info("=" * 60)
    logger.info(f"Room items added: {room_added}")
    logger.info(f"Room items skipped: {room_skipped}")
    logger.info(f"Wall items added: {wall_added}")
    logger.info(f"Wall items skipped: {wall_skipped}")
    logger.info(f"Total items added: {room_added + wall_added}")
    logger.info(f"Total items skipped: {room_skipped + wall_skipped}")
    logger.info("=" * 60)


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'extract':
        # Extract mode: compare FurnitureData files and extract differences
        try:
            if len(sys.argv) >= 3:
                # Custom other furniture data file provided
                extract_from_furniture_data(
                    other_furniture_data_file=sys.argv[2]
                )
            else:
                extract_from_furniture_data()
        except Exception as e:
            logger.error(f"Error during extraction: {e}")
            raise
    else:
        # Merge mode: merge roomitems and wallitems into FurnitureData
        try:
            merge_into_furniture_data()
        except Exception as e:
            logger.error(f"Error during merge: {e}")
            raise