#!/usr/bin/env python3
"""
Script to delete an album from the database.

Usage:
  delete_album.py <album_json>

The album_json should contain at least the 'url' field to identify the album.
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
        return []
    
    return albums

def write_database(albums):
    """Write all albums to the database."""
    db_path = get_database_path()
    
    try:
        with open(db_path, 'w', encoding='utf-8') as f:
            for album in albums:
                f.write(json.dumps(album, ensure_ascii=False) + '\n')
        return True
    except Exception as e:
        print(f"Error writing database: {e}", file=sys.stderr)
        return False

def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            "alfredworkflow": {
                "variables": {
                    "notification_title": "Error: Missing arguments",
                    "notification_subtitle": "Usage: delete_album.py <album_json>"
                }
            }
        }))
        sys.exit(1)
    
    # Parse arguments
    try:
        album_data = json.loads(sys.argv[1])
    except json.JSONDecodeError:
        print(json.dumps({
            "alfredworkflow": {
                "variables": {
                    "notification_title": "Error: Invalid album data",
                    "notification_subtitle": "Could not parse album JSON"
                }
            }
        }))
        sys.exit(1)
    
    # Get album URL
    album_url = album_data.get("url", "")
    album_title = album_data.get("title", "Unknown Album")
    
    if not album_url:
        print(json.dumps({
            "alfredworkflow": {
                "variables": {
                    "notification_title": "Error: Album URL not found",
                    "notification_subtitle": "Cannot identify album to delete"
                }
            }
        }))
        sys.exit(1)
    
    # Read database
    albums = read_database()
    
    # Find and remove the album
    album_found = False
    original_count = len(albums)
    albums_filtered = []
    
    for album in albums:
        if album.get("url") == album_url:
            album_found = True
            # Skip this album (don't add to filtered list)
        else:
            albums_filtered.append(album)
    
    if not album_found:
        print(json.dumps({
            "alfredworkflow": {
                "variables": {
                    "notification_title": "Error: Album not found",
                    "notification_subtitle": "Album not in database"
                }
            }
        }))
        sys.exit(1)
    
    # Check if album was actually removed
    if len(albums_filtered) == original_count:
        print(json.dumps({
            "alfredworkflow": {
                "variables": {
                    "notification_title": "Error: Album not deleted",
                    "notification_subtitle": "Something went wrong"
                }
            }
        }))
        sys.exit(1)
    
    # Write updated database
    if not write_database(albums_filtered):
        print(json.dumps({
            "alfredworkflow": {
                "variables": {
                    "notification_title": "Error: Failed to save",
                    "notification_subtitle": "Could not write to database"
                }
            }
        }))
        sys.exit(1)
    
    # Success message - output as environment variables for notification
    print(json.dumps({
        "alfredworkflow": {
            "variables": {
                "notification_title": "✓ Album deleted successfully",
                "notification_subtitle": f"Deleted: {album_title}"
            }
        }
    }))

if __name__ == "__main__":
    main()

