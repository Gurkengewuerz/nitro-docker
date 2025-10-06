#!/usr/bin/env python3
"""
Habbo Badge Name and Description Updater
Downloads external flash texts from multiple TLDs and generates SQL updates
"""

import os
import sys
import json
import requests
from typing import Dict, List, Optional

# Configuration
TLDS = ['com.br', 'com.tr', 'com', 'de', 'es', 'fi', 'fr', 'it', 'nl']
PRIORITY_ORDER = ['de', 'com', 'nl', 'fi', 'es', 'fr', 'com.br', 'com.tr']
ALBUM_PATH = './swf/c_images/album1584'
LOCAL_JSON_PATH = './assets/gamedata/ExternalTexts.json'
OUTPUT_SQL_FILE = 'update_badge_names.sql'


def log(message: str) -> None:
    """Print log message to stdout"""
    print(f"[INFO] {message}")


def log_error(message: str) -> None:
    """Print error message to stdout"""
    print(f"[ERROR] {message}")


def log_warning(message: str) -> None:
    """Print warning message to stdout"""
    print(f"[WARNING] {message}")


def list_badge_files(directory: str) -> List[str]:
    """List all PNG and GIF files in the album directory and extract badge keys"""
    log(f"Scanning directory: {directory}")
    
    if not os.path.exists(directory):
        log_error(f"Directory does not exist: {directory}")
        return []
    
    badge_keys = []
    file_count = 0
    
    for filename in os.listdir(directory):
        if filename.endswith('.png') or filename.endswith('.gif'):
            file_count += 1
            # Extract badge key (filename without extension)
            badge_key = filename.rsplit('.', 1)[0]
            badge_keys.append(badge_key)
            log(f"Found badge: {badge_key} ({filename})")
    
    log(f"Total files found: {file_count}")
    log(f"Total badge keys extracted: {len(badge_keys)}")
    return badge_keys


def parse_flash_texts(content: str) -> Dict[str, str]:
    """Parse external_flash_texts content into a dictionary"""
    result = {}
    lines = content.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if not line or '=' not in line:
            continue
        
        # Split only on first '=' to handle values containing '='
        parts = line.split('=', 1)
        if len(parts) == 2:
            key = parts[0].strip()
            value = parts[1].strip()
            result[key] = value
    
    return result


def download_external_texts(tlds: List[str]) -> Dict[str, Dict[str, str]]:
    """Download external_flash_texts from all TLDs"""
    log("Starting download of external_flash_texts from TLDs")
    
    texts_by_tld = {}
    
    for tld in tlds:
        url = f"https://www.habbo.{tld}/gamedata/external_flash_texts/0"
        log(f"Downloading from {tld}: {url}")
        
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            parsed_texts = parse_flash_texts(response.text)
            texts_by_tld[tld] = parsed_texts
            
            log(f"Successfully downloaded {len(parsed_texts)} entries from {tld}")
            
        except requests.exceptions.RequestException as e:
            log_error(f"Failed to download from {tld}: {e}")
            texts_by_tld[tld] = {}
    
    return texts_by_tld


def load_local_json(filepath: str) -> Dict[str, str]:
    """Load local ExternalTexts.json file"""
    log(f"Loading local JSON file: {filepath}")
    
    if not os.path.exists(filepath):
        log_warning(f"Local JSON file does not exist: {filepath}")
        return {}
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        log(f"Successfully loaded {len(data)} entries from local JSON")
        return data
    except Exception as e:
        log_error(f"Failed to load local JSON: {e}")
        return {}


def get_best_values(badge_key: str, local_data: Dict[str, str], 
                    tld_data: Dict[str, Dict[str, str]], 
                    priority_order: List[str], force_update: bool) -> tuple:
    """Get the best non-empty name and desc values from the same source"""
    
    name_key = f"badge_name_{badge_key}"
    desc_key = f"badge_desc_{badge_key}"
    
    # If not forcing update and local has non-empty name, use local data
    if not force_update and name_key in local_data and local_data[name_key]:
        name_value = local_data[name_key]
        desc_value = local_data.get(desc_key, '')
        return (name_value, desc_value, 'local')
    
    # Search through TLDs in priority order
    for tld in priority_order:
        if tld in tld_data and name_key in tld_data[tld]:
            name_value = tld_data[tld][name_key]
            if name_value:  # Non-empty string
                # Get desc from same TLD only
                desc_value = tld_data[tld].get(desc_key, '')
                return (name_value, desc_value, tld)
    
    # Fallback to local data if exists
    if name_key in local_data:
        name_value = local_data[name_key]
        desc_value = local_data.get(desc_key, '')
        return (name_value, desc_value, 'local')
    
    return (None, None, None)


def process_badges(badge_keys: List[str], local_data: Dict[str, str],
                   tld_data: Dict[str, Dict[str, str]], 
                   priority_order: List[str], force_update: bool) -> Dict[str, Dict[str, str]]:
    """Process all badges and get best name and description values from same source"""
    log(f"Processing {len(badge_keys)} badges")
    
    results = {}
    
    for badge_key in badge_keys:
        name_value, desc_value, source = get_best_values(
            badge_key, local_data, tld_data, priority_order, force_update
        )
        
        results[badge_key] = {
            'name': name_value if name_value else '',
            'desc': desc_value if desc_value else '',
            'source': source if source else 'none'
        }
        
        if name_value:
            log(f"Badge {badge_key}: name='{name_value}' (source: {source})")
        else:
            log_warning(f"Badge {badge_key}: no name found")
        
        if desc_value:
            log(f"Badge {badge_key}: desc='{desc_value[:50]}...' (source: {source})")
    
    log(f"Processed {len(results)} badges")
    return results


def escape_sql_string(value: str) -> str:
    """Escape string for SQL"""
    return value.replace("'", "''").replace("\\", "\\\\")


def generate_sql_updates(badge_data: Dict[str, Dict[str, str]], output_file: str) -> None:
    """Generate optimized SQL update statements"""
    log(f"Generating SQL updates to file: {output_file}")
    
    updates = []
    
    for badge_key, data in badge_data.items():
        name = escape_sql_string(data['name'])
        
        # Only update if we have a name
        if name:
            sql = f"UPDATE `catalog_items` SET `catalog_name`='{name}' WHERE `badge`='{badge_key}';"
            updates.append(sql)
    
    if not updates:
        log_warning("No SQL updates to generate (no badges with names found)")
        return
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            # Write optimized transaction wrapper
            f.write("-- Habbo Badge Name Updates\n")
            f.write("-- Generated by Habbo Badge Updater\n")
            f.write(f"-- Total updates: {len(updates)}\n\n")

            # Write all updates
            for sql in updates:
                f.write(sql + "\n")
        
        log(f"Successfully generated {len(updates)} SQL updates in {output_file}")
    except Exception as e:
        log_error(f"Failed to write SQL file: {e}")


def update_local_json(badge_data: Dict[str, Dict[str, str]], 
                      local_json_path: str, force_update: bool) -> None:
    """Update local JSON file with new values"""
    log(f"Updating local JSON file: {local_json_path}")
    
    # Load existing data
    existing_data = load_local_json(local_json_path)
    
    # Update with new values
    for badge_key, data in badge_data.items():
        name_key = f"badge_name_{badge_key}"
        desc_key = f"badge_desc_{badge_key}"
        
        # Update name if it exists
        if data['name']:
            existing_data[name_key] = data['name']
            
            # If name exists, always update desc (even if empty)
            # This allows empty desc when name is found
            existing_data[desc_key] = data['desc']
        elif force_update:
            # In force update mode, allow setting empty values
            existing_data[name_key] = data['name']
            existing_data[desc_key] = data['desc']
    
    # Write back to file
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(local_json_path), exist_ok=True)
        
        with open(local_json_path, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)
        
        log(f"Successfully updated local JSON with {len(badge_data)} badges")
    except Exception as e:
        log_error(f"Failed to update local JSON: {e}")


def main():
    """Main execution function"""
    # Parse command line arguments
    force_update = False
    
    if len(sys.argv) > 1:
        if sys.argv[1] in ['--force', '-f']:
            force_update = True
        elif sys.argv[1] in ['--help', '-h']:
            print("Usage: python script.py [--force|-f]")
            print("  --force, -f    Force update all values, ignoring local cache")
            print("  --help, -h     Show this help message")
            return
        else:
            log_error(f"Unknown argument: {sys.argv[1]}")
            print("Use --help for usage information")
            return
    
    log("=== Habbo Badge Name Updater Started ===")
    log(f"Force update mode: {force_update}")
    
    # Step 1: List all badge files
    badge_keys = list_badge_files(ALBUM_PATH)
    
    if not badge_keys:
        log_error("No badge files found. Exiting.")
        return
    
    # Step 2: Download external texts from all TLDs
    tld_data = download_external_texts(TLDS)
    
    # Step 3: Load local JSON
    local_data = load_local_json(LOCAL_JSON_PATH)
    
    # Step 4: Process all badges and get best values
    badge_data = process_badges(badge_keys, local_data, tld_data, 
                                PRIORITY_ORDER, force_update)
    
    # Step 5: Update local JSON with new values
    update_local_json(badge_data, LOCAL_JSON_PATH, force_update)
    
    # Step 6: Generate SQL updates
    generate_sql_updates(badge_data, OUTPUT_SQL_FILE)
    
    log("=== Habbo Badge Name Updater Completed ===")


if __name__ == "__main__":
    main()