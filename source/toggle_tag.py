#!/usr/bin/env python3
"""
Script to add or remove a tag from an album.
Updates the photoAlbums.json database.
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

def write_database(albums):
    """Write all albums back to the database."""
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
    # Get action data from argument
    if len(sys.argv) < 2:
        print(json.dumps({
            "alfredworkflow": {
                "variables": {
                    "notification_title": "Error: No action data provided",
                    "notification_subtitle": ""
                }
            }
        }))
        sys.exit(1)
    
    try:
        action_data = json.loads(sys.argv[1])
        url = action_data.get("url", "")
        title = action_data.get("title", "Untitled")
        tag = action_data.get("tag", "")
        action = action_data.get("action", "add")
        
    except json.JSONDecodeError as e:
        print(json.dumps({
            "alfredworkflow": {
                "variables": {
                    "notification_title": f"Error: Invalid action data - {str(e)}",
                    "notification_subtitle": ""
                }
            }
        }))
        sys.exit(1)
    
    if not url or not tag:
        print(json.dumps({
            "alfredworkflow": {
                "variables": {
                    "notification_title": "Error: URL and tag are required",
                    "notification_subtitle": ""
                }
            }
        }))
        sys.exit(1)
    
    # Read database
    albums = read_database()
    
    # Find and update the album
    album_found = False
    for album in albums:
        if album.get("url") == url:
            album_found = True
            
            # Ensure tags array exists
            if "tags" not in album:
                album["tags"] = []
            
            if action == "add":
                # Add tag if not already present
                if tag not in album["tags"]:
                    album["tags"].append(tag)
                    print(json.dumps({
                        "alfredworkflow": {
                            "variables": {
                                "notification_title": "✓ Tag added successfully",
                                "notification_subtitle": f"Added '{tag}' to {title}"
                            }
                        }
                    }))
                else:
                    print(json.dumps({
                        "alfredworkflow": {
                            "variables": {
                                "notification_title": "Tag already exists",
                                "notification_subtitle": f"'{tag}' already on {title}"
                            }
                        }
                    }))
            
            elif action == "remove":
                # Remove tag if present
                if tag in album["tags"]:
                    album["tags"].remove(tag)
                    print(json.dumps({
                        "alfredworkflow": {
                            "variables": {
                                "notification_title": "✓ Tag removed successfully",
                                "notification_subtitle": f"Removed '{tag}' from {title}"
                            }
                        }
                    }))
                else:
                    print(json.dumps({
                        "alfredworkflow": {
                            "variables": {
                                "notification_title": "Tag not found",
                                "notification_subtitle": f"'{tag}' not on {title}"
                            }
                        }
                    }))
            
            break
    
    if not album_found:
        print(json.dumps({
            "alfredworkflow": {
                "variables": {
                    "notification_title": f"Error: Album not found: {title}",
                    "notification_subtitle": ""
                }
            }
        }))
        sys.exit(1)
    
    # Write back to database
    if not write_database(albums):
        print(json.dumps({
            "alfredworkflow": {
                "variables": {
                    "notification_title": "Error: Failed to update database",
                    "notification_subtitle": ""
                }
            }
        }))
        sys.exit(1)

if __name__ == "__main__":
    main()

