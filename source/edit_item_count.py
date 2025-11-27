#!/usr/bin/env python3
"""
Script to edit an album's item count in the database.
Receives the album JSON object from environment variable 'albumToEdit'
and the new item count from command line argument.
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
    except Exception as e:
        print(json.dumps({
            "alfredworkflow": {
                "variables": {
                    "notification_title": "Error reading database",
                    "notification_subtitle": str(e)
                }
            }
        }))
        sys.exit(1)
    
    return albums

def write_database(albums):
    """Write all albums back to the database."""
    db_path = get_database_path()
    
    try:
        with open(db_path, 'w', encoding='utf-8') as f:
            for album in albums:
                f.write(json.dumps(album, ensure_ascii=False) + '\n')
    except Exception as e:
        print(json.dumps({
            "alfredworkflow": {
                "variables": {
                    "notification_title": "Error writing database",
                    "notification_subtitle": str(e)
                }
            }
        }))
        sys.exit(1)

def main():
    # Get the new item count from command line argument
    if len(sys.argv) < 2:
        print(json.dumps({
            "alfredworkflow": {
                "variables": {
                    "notification_title": "No item count provided",
                    "notification_subtitle": "Please enter a number"
                }
            }
        }))
        return
    
    count_str = sys.argv[1].strip()
    
    # Try to parse as integer
    try:
        new_count = int(count_str)
        if new_count < 0:
            raise ValueError("Count must be non-negative")
    except ValueError as e:
        print(json.dumps({
            "alfredworkflow": {
                "variables": {
                    "notification_title": "Invalid item count",
                    "notification_subtitle": "Please enter a valid number (0 or greater)"
                }
            }
        }))
        return
    
    # Get the album to edit from environment variable
    album_json = os.environ.get("albumToEdit", "")
    
    if not album_json:
        print(json.dumps({
            "alfredworkflow": {
                "variables": {
                    "notification_title": "Error: No album data found",
                    "notification_subtitle": "albumToEdit environment variable is missing"
                }
            }
        }))
        return
    
    try:
        album_to_edit = json.loads(album_json)
    except json.JSONDecodeError as e:
        print(json.dumps({
            "alfredworkflow": {
                "variables": {
                    "notification_title": "Error: Invalid album data",
                    "notification_subtitle": f"Could not parse JSON: {str(e)}"
                }
            }
        }))
        return
    
    # Get the album URL for matching
    album_url = album_to_edit.get("url", "")
    
    if not album_url:
        print(json.dumps({
            "alfredworkflow": {
                "variables": {
                    "notification_title": "Error: Album URL not found",
                    "notification_subtitle": "Cannot identify album to update"
                }
            }
        }))
        return
    
    # Read all albums
    albums = read_database()
    
    # Find and update the album
    album_found = False
    old_count = None
    album_title = ""
    
    for album in albums:
        if album.get("url") == album_url:
            old_count = album.get("itemCount")
            album_title = album.get("title", "Untitled")
            album["itemCount"] = new_count
            album_found = True
            break
    
    if not album_found:
        print(json.dumps({
            "alfredworkflow": {
                "variables": {
                    "notification_title": "Error: Album not found in database",
                    "notification_subtitle": f"Could not find album: {album_url}"
                }
            }
        }))
        return
    
    # Write updated database
    write_database(albums)
    
    # Success response - output as environment variables for notification
    old_count_str = str(old_count) if old_count is not None else "not set"
    print(json.dumps({
        "alfredworkflow": {
            "variables": {
                "notification_title": "✓ Item count updated successfully",
                "notification_subtitle": f"{album_title}: {old_count_str} → {new_count}"
            }
        }
    }))

if __name__ == "__main__":
    main()

