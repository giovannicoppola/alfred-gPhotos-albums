#!/usr/bin/env python3
"""
Script to list all tags with album counts.
Returns Alfred JSON format with all tags.
"""

import json
import sys
import os
import re
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
    except Exception:
        return []
    
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
    
    # Sort by count (descending), then alphabetically
    sorted_tags = sorted(tag_counts.items(), key=lambda x: (-x[1], x[0].lower()))
    return sorted_tags

def normalize_text(text):
    """Normalize text for searching: lowercase."""
    if not text:
        return ""
    return text.lower().strip()

def alfred_response(items, variables=None):
    """Create an Alfred JSON response with multiple items and optional variables."""
    response = {"items": items}
    if variables:
        response["variables"] = variables
    return json.dumps(response, ensure_ascii=False)

def main():
    # Get search query from arguments (empty string if none provided)
    search_query = sys.argv[1].strip() if len(sys.argv) > 1 else ""
    
    # Read database
    albums = read_database()
    
    if not albums:
        print(alfred_response(
            items=[{
                "title": "No albums found",
                "subtitle": "The database is empty. Add some albums first!",
                "valid": False
            }],
            variables={"userInputString": search_query}
        ))
        return
    
    # Get all tags
    all_tags = get_all_tags(albums)
    
    if not all_tags:
        print(alfred_response(
            items=[{
                "title": "No tags found",
                "subtitle": "Add some tags to your albums first!",
                "valid": False
            }],
            variables={"userInputString": search_query}
        ))
        return
    
    # Filter tags based on search query
    normalized_query = normalize_text(search_query)
    matching_tags = []
    
    for tag, count in all_tags:
        # Filter by search query if provided
        if search_query and normalized_query not in normalize_text(tag):
            continue
        
        matching_tags.append((tag, count))
    
    # Create Alfred items with position counters
    total_count = len(matching_tags)
    matching_items = []
    
    for idx, (tag, count) in enumerate(matching_tags, 1):
        subtitle = f"{format_number(idx)}/{format_number(total_count)} Show {format_number(count)} album{'s' if count != 1 else ''} with this tag"
        
        matching_items.append({
            "title": f"{tag} ({count})",
            "subtitle": subtitle,
            "arg": tag,
            "valid": True,
            "variables": {
                "searchTag": tag,
                "mySource": "tagList"
            },
            "icon": {
                "path": "icon.png" if Path(__file__).parent.joinpath("icon.png").exists() else ""
            }
        })
    
    # If no matches, show a helpful message
    if not matching_items:
        matching_items.append({
            "title": "No tags match your search",
            "subtitle": f"No results for: {search_query}",
            "valid": False
        })
    
    # Output with environment variable
    print(alfred_response(matching_items, variables={"userInputString": search_query}))

if __name__ == "__main__":
    main()

