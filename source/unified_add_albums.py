#!/usr/bin/env python3
"""
Unified script to add/update albums in the database from scraped data.
Handles both bulk imports and single album imports.
Features:
- Adds unique IDs to all albums (UUID format)
- For single albums: adds date information (dateRange, startDate, endDate) if available
- For existing URLs: preserves title, updates itemCount and dates intelligently
- For new URLs: creates new entry with all provided data
- Outputs Alfred-compatible JSON report with clickable summary
"""

import json
import sys
import os
import uuid
import re
from pathlib import Path
from datetime import datetime

def get_database_path():
    """Get the path to the photoAlbums.json database."""
    data_folder = os.getenv('alfred_workflow_data')
    if not data_folder:
        # Fallback to script directory if env var not set
        data_folder = Path(__file__).parent
    else:
        data_folder = Path(data_folder)
    
    # Create data folder if it doesn't exist
    if not os.path.exists(data_folder):
        os.makedirs(data_folder)
    
    return data_folder / "photoAlbums.json"

def generate_unique_id():
    """Generate a unique ID for an album."""
    return str(uuid.uuid4())

def convert_date_to_storage_format(date_string):
    """
    Convert date from display format to storage format (yyyy-mm-dd).
    Handles: "Nov 27, 2014", "Nov 27", "2024-11-27"
    Returns the date in yyyy-mm-dd format, or the original if already correct or invalid.
    """
    if not date_string:
        return date_string
    
    # Already in yyyy-mm-dd format
    if re.match(r'^\d{4}-\d{2}-\d{2}$', date_string.strip()):
        return date_string.strip()
    
    try:
        # Try format with year: "Nov 27, 2014"
        if ',' in date_string:
            dt = datetime.strptime(date_string.strip(), "%b %d, %Y")
            return dt.strftime("%Y-%m-%d")
        else:
            # Format without year: "Nov 27" - use current year
            current_year = datetime.now().year
            # Parse with current year to avoid deprecation warning
            dt = datetime.strptime(f"{date_string.strip()}, {current_year}", "%b %d, %Y")
            return dt.strftime("%Y-%m-%d")
    except:
        # If parsing fails, return original
        return date_string

def normalize_date_range(start_date, end_date):
    """
    Create normalized date range string.
    Single date: "2024-11-27"
    Date range: "2024-11-27--2024-11-28"
    """
    if not start_date:
        return None
    
    start_normalized = convert_date_to_storage_format(start_date)
    
    if end_date:
        end_normalized = convert_date_to_storage_format(end_date)
        return f"{start_normalized}--{end_normalized}"
    
    return start_normalized

def read_existing_albums():
    """Read all existing albums from the database into a dict keyed by URL."""
    db_path = get_database_path()
    albums_dict = {}
    
    if not db_path.exists():
        return albums_dict
    
    try:
        with open(db_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    album = json.loads(line)
                    url = album.get('url', '')
                    if url:
                        # Add ID if missing
                        if 'id' not in album:
                            album['id'] = generate_unique_id()
                        albums_dict[url] = album
    except Exception as e:
        return {}
    
    return albums_dict

def write_albums_database(albums_dict):
    """Write the entire albums database (overwrites existing file)."""
    db_path = get_database_path()
    
    try:
        with open(db_path, 'w', encoding='utf-8') as f:
            for album in albums_dict.values():
                f.write(json.dumps(album, ensure_ascii=False) + '\n')
        return True
    except Exception as e:
        print(f"Error writing database: {e}", file=sys.stderr)
        return False

def alfred_response(items):
    """Create an Alfred JSON response with items."""
    return json.dumps({"items": items}, ensure_ascii=False)

def create_alfred_report(unchanged_ids, updated_ids, added_ids, albums_dict):
    """Create Alfred JSON response with summary and clickable items."""
    items = []
    
    def format_number(num):
        """Format a number with thousand separators."""
        if num is None:
            return "0"
        try:
            return f"{int(num):,}"
        except (ValueError, TypeError):
            return str(num)
    
    # Helper function for proper pluralization with formatted numbers
    def plural(count, singular, plural_form):
        return f"{format_number(count)} {singular if count == 1 else plural_form}"
    
    # Helper function to get album data by ID
    def get_album_by_id(album_id):
        for album in albums_dict.values():
            if album.get('id') == album_id:
                return album
        return None
    
    # Check if this is a single album import
    total_count = len(added_ids) + len(updated_ids) + len(unchanged_ids)
    is_single = (total_count == 1)
    
    # Function to add markdown link modifier and title for single album
    def enhance_single_album_item(item, album_ids, base_title):
        if is_single and len(album_ids) == 1:
            album = get_album_by_id(album_ids[0])
            if album:
                url = album.get('url', '')
                title = album.get('clean_title', album.get('title', 'Untitled'))
                # Add album title to the item title
                item['title'] = f"{base_title} ({title})"
                item['subtitle'] = "Shift+Cmd to copy markdown link"
                item['mods'] = {
                    "shift+cmd": {
                        "subtitle": "Copy markdown link",
                        "arg": f"[Photos: {title}]({url})",
                        "valid": True
                    }
                }
        return item
    
    # Summary items with variables to pass IDs as environment variable
    added_item = {
        "title": f"✅ Added: {plural(len(added_ids), 'album', 'albums')}",
        "subtitle": "Click to view newly added albums" if added_ids else "No new albums",
        "arg": "",  # Empty arg - we use variables instead
        "valid": bool(added_ids),
        "variables": {
            "ID_list": ",".join(added_ids) if added_ids else ""
        },
        "icon": {"path": "icon.png"}
    }
    items.append(enhance_single_album_item(
        added_item, 
        added_ids, 
        f"✅ Added: {plural(len(added_ids), 'album', 'albums')}"
    ))
    
    updated_item = {
        "title": f"🔄 Updated: {plural(len(updated_ids), 'album', 'albums')}",
        "subtitle": "Click to view updated albums" if updated_ids else "No albums were updated",
        "arg": "",  # Empty arg - we use variables instead
        "valid": bool(updated_ids),
        "variables": {
            "ID_list": ",".join(updated_ids) if updated_ids else ""
        },
        "icon": {"path": "icon.png"}
    }
    items.append(enhance_single_album_item(
        updated_item, 
        updated_ids, 
        f"🔄 Updated: {plural(len(updated_ids), 'album', 'albums')}"
    ))
    
    unchanged_item = {
        "title": f"⚪ Unchanged: {plural(len(unchanged_ids), 'album', 'albums')}",
        "subtitle": "Click to view unchanged albums" if unchanged_ids else "No unchanged albums",
        "arg": "",  # Empty arg - we use variables instead
        "valid": bool(unchanged_ids),
        "variables": {
            "ID_list": ",".join(unchanged_ids) if unchanged_ids else ""
        },
        "icon": {"path": "icon.png"}
    }
    items.append(enhance_single_album_item(
        unchanged_item, 
        unchanged_ids, 
        f"⚪ Unchanged: {plural(len(unchanged_ids), 'album', 'albums')}"
    ))
    
    return alfred_response(items)

def process_single_album(album_data, albums_dict):
    """Process a single album import with date information."""
    url = album_data.get("url", "").strip()
    if not url:
        return None, None, None
    
    title = album_data.get("title", "Untitled Album")
    new_item_count = album_data.get("itemCount")
    
    # Get and normalize date information to yyyy-mm-dd format
    raw_start_date = album_data.get("startDate")
    raw_end_date = album_data.get("endDate")
    
    # Convert dates to storage format (yyyy-mm-dd)
    start_date = convert_date_to_storage_format(raw_start_date) if raw_start_date else None
    end_date = convert_date_to_storage_format(raw_end_date) if raw_end_date else None
    date_range = normalize_date_range(start_date, end_date) if start_date else None
    
    if url in albums_dict:
        # Album exists - update it
        existing_album = albums_dict[url]
        album_id = existing_album.get('id')
        if not album_id:
            album_id = generate_unique_id()
            existing_album['id'] = album_id
        
        updated = False
        
        # Update itemCount only if existing count is missing or 0 (preserve user corrections)
        # Normalize types for comparison (handle string/int differences)
        existing_item_count = existing_album.get("itemCount")
        if new_item_count is not None:
            # Convert to int for consistent comparison
            try:
                new_count_int = int(new_item_count) if new_item_count is not None else None
                existing_count_int = int(existing_item_count) if existing_item_count is not None else None
            except (ValueError, TypeError):
                new_count_int = new_item_count
                existing_count_int = existing_item_count
            
            # Only update if existing is missing or 0, AND new value is different
            if existing_count_int is None or existing_count_int == 0:
                if existing_count_int != new_count_int:
                    existing_album["itemCount"] = new_count_int
                    updated = True
        
        # Update date fields if new data is provided (normalize existing dates for comparison)
        if date_range:
            # Normalize existing dates for comparison
            existing_start = existing_album.get("startDate")
            existing_end = existing_album.get("endDate")
            
            # Build normalized existing date range for comparison
            normalized_existing_range = None
            if existing_start:
                normalized_existing_start = convert_date_to_storage_format(existing_start)
                if existing_end:
                    normalized_existing_end = convert_date_to_storage_format(existing_end)
                    normalized_existing_range = f"{normalized_existing_start}--{normalized_existing_end}"
                else:
                    normalized_existing_range = normalized_existing_start
            
            if normalized_existing_range != date_range:
                existing_album["dateRange"] = date_range
                updated = True
        
        if start_date:
            existing_start_raw = existing_album.get("startDate")
            normalized_existing_start = convert_date_to_storage_format(existing_start_raw) if existing_start_raw else None
            if normalized_existing_start != start_date:
                existing_album["startDate"] = start_date
                updated = True
        
        if end_date:
            existing_end_raw = existing_album.get("endDate")
            normalized_existing_end = convert_date_to_storage_format(existing_end_raw) if existing_end_raw else None
            if normalized_existing_end != end_date:
                existing_album["endDate"] = end_date
                updated = True
        
        if updated:
            return None, album_id, None
        else:
            return album_id, None, None
    else:
        # New album - create entry
        album_id = generate_unique_id()
        new_album = {
            "id": album_id,
            "url": url,
            "title": title,
            "tags": []
        }
        
        if new_item_count is not None:
            new_album["itemCount"] = new_item_count
        
        if date_range:
            new_album["dateRange"] = date_range
        
        if start_date:
            new_album["startDate"] = start_date
        
        if end_date:
            new_album["endDate"] = end_date
        
        albums_dict[url] = new_album
        return None, None, album_id

def process_bulk_albums(albums_data, albums_dict):
    """Process bulk album imports (without dates)."""
    unchanged_ids = []
    updated_ids = []
    added_ids = []
    
    for album_input in albums_data:
        url = album_input.get("url", "").strip()
        if not url:
            continue
        
        new_item_count = album_input.get("itemCount")
        
        if url in albums_dict:
            # Album exists
            existing_album = albums_dict[url]
            album_id = existing_album.get('id')
            if not album_id:
                album_id = generate_unique_id()
                existing_album['id'] = album_id
            
            existing_item_count = existing_album.get("itemCount")
            
            # Update itemCount only if existing count is missing or 0 (preserve user corrections)
            # Normalize types for comparison (handle string/int differences)
            should_update = False
            if new_item_count is not None:
                # Convert to int for consistent comparison
                try:
                    new_count_int = int(new_item_count) if new_item_count is not None else None
                    existing_count_int = int(existing_item_count) if existing_item_count is not None else None
                except (ValueError, TypeError):
                    new_count_int = new_item_count
                    existing_count_int = existing_item_count
                
                # Only update if existing is missing or 0, AND new value is different
                if existing_count_int is None or existing_count_int == 0:
                    if existing_count_int != new_count_int:
                        existing_album["itemCount"] = new_count_int
                        should_update = True
            
            if should_update:
                updated_ids.append(album_id)
            else:
                unchanged_ids.append(album_id)
        else:
            # New album
            album_id = generate_unique_id()
            new_album = {
                "id": album_id,
                "url": url,
                "title": album_input.get("title", "Untitled Album"),
                "tags": []
            }
            if new_item_count is not None:
                new_album["itemCount"] = new_item_count
            
            albums_dict[url] = new_album
            added_ids.append(album_id)
    
    return unchanged_ids, updated_ids, added_ids

def main():
    if len(sys.argv) < 2:
        print(alfred_response([{
            "title": "Error: No data provided",
            "subtitle": "Usage: unified_add_albums.py '<json_data>'",
            "valid": False
        }]))
        sys.exit(1)
    
    try:
        # Parse the input JSON
        data = json.loads(sys.argv[1])
        
        # Handle error objects from the scraper
        if isinstance(data, dict) and 'error' in data:
            print(alfred_response([{
                "title": f"Error: {data['error']}",
                "subtitle": "Make sure you're on a Google Photos page",
                "valid": False
            }]))
            sys.exit(1)
        
        # Read existing albums
        albums_dict = read_existing_albums()
        
        # Determine type and process accordingly
        data_type = data.get('type') if isinstance(data, dict) else None
        
        unchanged_ids = []
        updated_ids = []
        added_ids = []
        
        if data_type == 'single':
            # Single album import
            unchanged_id, updated_id, added_id = process_single_album(data, albums_dict)
            if unchanged_id:
                unchanged_ids.append(unchanged_id)
            if updated_id:
                updated_ids.append(updated_id)
            if added_id:
                added_ids.append(added_id)
        
        elif data_type == 'bulk':
            # Bulk import
            albums_data = data.get('albums', [])
            if not albums_data:
                print(alfred_response([{
                    "title": "No albums to process",
                    "subtitle": "No albums found on this page",
                    "valid": False
                }]))
                return
            unchanged_ids, updated_ids, added_ids = process_bulk_albums(albums_data, albums_dict)
        
        else:
            print(alfred_response([{
                "title": "Error: Invalid data format",
                "subtitle": "Unexpected data structure from scraper",
                "valid": False
            }]))
            sys.exit(1)
        
        # Write the updated database
        if updated_ids or added_ids:
            success = write_albums_database(albums_dict)
            if not success:
                print(alfred_response([{
                    "title": "ERROR: Failed to write to database!",
                    "subtitle": "Check file permissions",
                    "valid": False
                }]))
                sys.exit(1)
        
        # Output Alfred JSON report
        print(create_alfred_report(unchanged_ids, updated_ids, added_ids, albums_dict))
    
    except json.JSONDecodeError as e:
        print(alfred_response([{
            "title": f"Error: Invalid JSON data",
            "subtitle": str(e),
            "valid": False
        }]))
        sys.exit(1)
    except Exception as e:
        print(alfred_response([{
            "title": f"Error processing albums",
            "subtitle": str(e),
            "valid": False
        }]))
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

