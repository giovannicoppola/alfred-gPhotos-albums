#!/usr/bin/env python3
"""
Script to show comprehensive album statistics.
Returns an Alfred JSON response with various album categories that can be clicked to view.

Shows:
- Total albums
- Complete albums (have both item count and date)
- Incomplete albums (missing item count or date)
- Albums with tags
- Albums without tags
- Albums missing item count
- Albums missing date
- Albums missing both

Each category can be clicked to view those specific albums in search_albums.py.
"""

import json
import sys
import os
from pathlib import Path

def format_number(num):
    """Format a number with thousand separators."""
    if num is None:
        return "0"
    try:
        return f"{int(num):,}"
    except (ValueError, TypeError):
        return str(num)

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

def read_database():
    """Read all albums from the database."""
    db_path = get_database_path()
    albums = []
    
    if not db_path.exists():
        return albums
    
    try:
        with open(db_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    albums.append(json.loads(line))
    except Exception as e:
        return []
    
    return albums

def is_missing_item_count(album):
    """Check if album is missing item count."""
    item_count = album.get("itemCount")
    return item_count is None or item_count == 0

def is_missing_date(album):
    """Check if album is missing date information."""
    start_date = album.get("startDate", "")
    date_range = album.get("dateRange", "")
    return not start_date and not date_range

def alfred_response(items):
    """Create an Alfred JSON response with items."""
    return json.dumps({"items": items}, ensure_ascii=False)

def plural(count, singular, plural_form):
    """Format a number with thousand separators and pluralize."""
    return f"{format_number(count)} {singular if count == 1 else plural_form}"

def main():
    # Read database
    albums = read_database()
    
    if not albums:
        print(alfred_response([{
            "title": "No albums in database",
            "subtitle": "The database is empty. Add some albums first!",
            "valid": False
        }]))
        return
    
    # Calculate all statistics
    all_ids = []
    complete_ids = []
    incomplete_ids = []
    missing_count_ids = []
    missing_date_ids = []
    missing_both_ids = []
    with_tags_ids = []
    without_tags_ids = []
    
    for album in albums:
        album_id = album.get("id", "")
        if not album_id:
            continue
        
        all_ids.append(album_id)
        
        # Check completeness
        missing_count = is_missing_item_count(album)
        missing_date = is_missing_date(album)
        
        if missing_count and missing_date:
            missing_both_ids.append(album_id)
            missing_count_ids.append(album_id)
            missing_date_ids.append(album_id)
            incomplete_ids.append(album_id)
        elif missing_count:
            missing_count_ids.append(album_id)
            incomplete_ids.append(album_id)
        elif missing_date:
            missing_date_ids.append(album_id)
            incomplete_ids.append(album_id)
        else:
            complete_ids.append(album_id)
        
        # Check tags
        tags = album.get("tags", [])
        if tags and len(tags) > 0:
            with_tags_ids.append(album_id)
        else:
            without_tags_ids.append(album_id)
    
    # Create Alfred items
    items = []
    
   
    
    # Incomplete albums
    if incomplete_ids:
        items.append({
            "title": f"🔍 Incomplete: {plural(len(incomplete_ids), 'album', 'albums')}",
            "subtitle": "Albums missing item count or date information",
            "arg": "",
            "valid": True,
            "variables": {
                "ID_list": ",".join(incomplete_ids),
                "mySource": "album_stats"
            },
            "icon": {"path": "icon.png"}
        })
    
    # Albums with tags
    if with_tags_ids:
        items.append({
            "title": f"🏷️ With tags: {plural(len(with_tags_ids), 'album', 'albums')}",
            "subtitle": "Albums that have at least one tag",
            "arg": "",
            "valid": True,
            "variables": {
                "ID_list": ",".join(with_tags_ids),
                "mySource": "album_stats"
            },
            "icon": {"path": "icon.png"}
        })
    
    # Albums without tags
    if without_tags_ids:
        items.append({
            "title": f"📋 Without tags: {plural(len(without_tags_ids), 'album', 'albums')}",
            "subtitle": "Albums that have no tags",
            "arg": "",
            "valid": True,
            "variables": {
                "ID_list": ",".join(without_tags_ids),
                "mySource": "album_stats"
            },
            "icon": {"path": "icon.png"}
        })
    
    # Missing item count
    if missing_count_ids:
        items.append({
            "title": f"📊 Missing item count: {plural(len(missing_count_ids), 'album', 'albums')}",
            "subtitle": "Albums without item count information",
            "arg": "",
            "valid": True,
            "variables": {
                "ID_list": ",".join(missing_count_ids),
                "mySource": "album_stats"
            },
            "icon": {"path": "icon.png"}
        })
    
    # Missing date
    if missing_date_ids:
        items.append({
            "title": f"📅 Missing date: {plural(len(missing_date_ids), 'album', 'albums')}",
            "subtitle": "Albums without date information",
            "arg": "",
            "valid": True,
            "variables": {
                "ID_list": ",".join(missing_date_ids),
                "mySource": "album_stats"
            },
            "icon": {"path": "icon.png"}
        })
    
    # Missing both
    if missing_both_ids:
        items.append({
            "title": f"⚠️ Missing both item count and date: {plural(len(missing_both_ids), 'album', 'albums')}",
            "subtitle": "Albums missing both item count and date",
            "arg": "",
            "valid": True,
            "variables": {
                "ID_list": ",".join(missing_both_ids),
                "mySource": "album_stats"
            },
            "icon": {"path": "icon.png"}
        })
    


 # Total albums
    items.append({
        "title": f"📚 Total: {plural(len(all_ids), 'album', 'albums')}",
        "subtitle": "Click to view all albums",
        "arg": "",
        "valid": True,
        "variables": {
            "ID_list": ",".join(all_ids),
            "mySource": "album_stats"
        },
        "icon": {"path": "icon.png"}
    })
    
    # Complete albums
    if complete_ids:
        items.append({
            "title": f"✅ Complete: {plural(len(complete_ids), 'album', 'albums')}",
            "subtitle": "Albums with both item count and date information",
            "arg": "",
            "valid": True,
            "variables": {
                "ID_list": ",".join(complete_ids),
                "mySource": "album_stats"
            },
            "icon": {"path": "icon.png"}
        })

    # Summary (non-clickable)
    items.append({
        "title": "📈 Summary",
        "subtitle": f"{format_number(len(complete_ids))} complete, {format_number(len(incomplete_ids))} incomplete • {format_number(len(with_tags_ids))} tagged, {format_number(len(without_tags_ids))} untagged",
        "valid": False,
        "icon": {"path": "icon.png"}
    })

    print(alfred_response(items))

if __name__ == "__main__":
    main()

