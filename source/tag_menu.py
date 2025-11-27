#!/usr/bin/env python3
"""
Script to show available tags for adding/removing from an album.
Similar to AlfreDo's tag management.
"""

import json
import sys
import os
from pathlib import Path

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
    except Exception:
        return albums
    
    return albums

def get_all_tags(albums):
    """Get all unique tags from the database with counts."""
    tag_counts = {}
    for album in albums:
        for tag in album.get('tags', []):
            if tag in tag_counts:
                tag_counts[tag] += 1
            else:
                tag_counts[tag] = 1
    
    # Sort by count (descending)
    sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
    return sorted_tags

def alfred_response(items):
    """Create an Alfred JSON response with items."""
    return json.dumps({"items": items}, ensure_ascii=False)

def main():
    # Get album data from argument
    if len(sys.argv) < 2:
        print(alfred_response([{
            "title": "Error: No album data provided",
            "subtitle": "Please try again",
            "valid": False
        }]))
        sys.exit(1)
    
    try:
        album_data = json.loads(sys.argv[1])
        url = album_data.get("url", "")
        title = album_data.get("title", "Untitled")
        current_tags = album_data.get("tags", [])
    except json.JSONDecodeError:
        print(alfred_response([{
            "title": "Error: Invalid album data",
            "subtitle": "Please try again",
            "valid": False
        }]))
        sys.exit(1)
    
    # Get filter query if provided
    filter_query = sys.argv[2].lower().strip() if len(sys.argv) > 2 else ""
    
    # Read all albums to get all available tags
    albums = read_database()
    all_tags = get_all_tags(albums)
    
    items = []
    
    # If no filter, show title first
    if not filter_query:
        items.append({
            "title": f"Manage tags for: {title}",
            "subtitle": f"Currently: {', '.join(current_tags) if current_tags else 'No tags'} • Type to filter or create new tag",
            "valid": False
        })
    
    # Show existing tags
    for tag, count in all_tags:
        # Apply filter if provided
        if filter_query and filter_query not in tag.lower():
            continue
        
        # Check if this tag is already on the album
        if tag in current_tags:
            subtitle = f"❌️ Remove this tag ({count} albums)"
            action = "remove"
        else:
            subtitle = f"🏷️️ Add this tag ({count} albums)"
            action = "add"
        
        items.append({
            "title": tag,
            "subtitle": subtitle,
            "arg": json.dumps({
                "url": url,
                "title": title,
                "tag": tag,
                "action": action,
                "tags": current_tags
            }),
            "valid": True,
            "icon": {
                "path": "icon.png" if Path(__file__).parent.joinpath("icon.png").exists() else ""
            }
        })
    
    # If there's a filter query and no exact match, offer to create new tag
    if filter_query:
        existing_tags_lower = [tag.lower() for tag, _ in all_tags]
        if filter_query not in existing_tags_lower:
            items.append({
                "title": f"Create new tag: {filter_query}",
                "subtitle": "➕ Press Enter to create and add this tag",
                "arg": json.dumps({
                    "url": url,
                    "title": title,
                    "tag": filter_query,
                    "action": "add",
                    "tags": current_tags
                }),
                "valid": True,
                "icon": {
                    "path": "icon.png" if Path(__file__).parent.joinpath("icon.png").exists() else ""
                }
            })
    
    # If no items (only possible if there's a filter with no matches)
    if not items:
        items.append({
            "title": "No tags found",
            "subtitle": "Type a new tag name to create it",
            "valid": False
        })
    
    print(alfred_response(items))

if __name__ == "__main__":
    main()

