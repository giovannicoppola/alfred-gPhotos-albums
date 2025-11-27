#!/usr/bin/env python3
"""
Script to edit date information for an album.
Accepts dates in yyyy-mm-dd format.

Usage:
  edit_date.py <album_json> <date_input>

Date formats:
  - Single date: 2025-11-10
  - Date range: 2020-11-10--2025-11-10 (note: double dash separator)

The script will update:
  - dateRange: stores the date or range in yyyy-mm-dd or yyyy-mm-dd--yyyy-mm-dd format
  - startDate: the start date in yyyy-mm-dd format
  - endDate: the end date (for ranges) in yyyy-mm-dd format
"""

import json
import sys
import os
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

def validate_date(date_string):
    """Validate that a date string is in yyyy-mm-dd format."""
    try:
        datetime.strptime(date_string, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def parse_date_input(date_input):
    """
    Parse date input and return (start_date, end_date, date_range).
    
    Formats:
      - Single date: "2025-11-10" -> ("2025-11-10", None, "2025-11-10")
      - Date range: "2020-11-10--2025-11-10" -> ("2020-11-10", "2025-11-10", "2020-11-10--2025-11-10")
    
    Returns None if invalid format.
    """
    date_input = date_input.strip()
    
    # Check for date range (double dash)
    if '--' in date_input:
        parts = date_input.split('--')
        if len(parts) != 2:
            return None
        
        start_date, end_date = parts[0].strip(), parts[1].strip()
        
        # Validate both dates
        if not validate_date(start_date) or not validate_date(end_date):
            return None
        
        # Ensure start is before end
        if start_date > end_date:
            return None
        
        date_range = f"{start_date}--{end_date}"
        return (start_date, end_date, date_range)
    else:
        # Single date
        if not validate_date(date_input):
            return None
        
        return (date_input, None, date_input)

def format_date_for_display(date_string):
    """
    Convert yyyy-mm-dd to display format like "Oct 30, 2024".
    """
    try:
        dt = datetime.strptime(date_string, "%Y-%m-%d")
        return dt.strftime("%b %d, %Y")
    except:
        return date_string

def format_range_for_display(start_date, end_date):
    """
    Convert date range to display format.
    Same year: "Oct 30 – Nov 2"
    Different years: "Oct 30, 2023 – Nov 2, 2024"
    """
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        
        if start_dt.year == end_dt.year:
            # Same year: show year only on end date
            start_formatted = start_dt.strftime("%b %d")
            end_formatted = end_dt.strftime("%b %d")
            return f"{start_formatted} – {end_formatted}"
        else:
            # Different years: show year on both
            start_formatted = start_dt.strftime("%b %d, %Y")
            end_formatted = end_dt.strftime("%b %d, %Y")
            return f"{start_formatted} – {end_formatted}"
    except:
        return f"{start_date} – {end_date}"

def main():
    if len(sys.argv) < 3:
        print(json.dumps({
            "alfredworkflow": {
                "variables": {
                    "notification_title": "Error: Missing arguments",
                    "notification_subtitle": "Usage: edit_date.py <album_json> <date_input>"
                }
            }
        }))
        sys.exit(1)
    
    # Parse arguments
    try:
        album_data = json.loads(sys.argv[1])
        date_input = sys.argv[2]
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
    
    # Parse date input
    parsed_date = parse_date_input(date_input)
    if not parsed_date:
        print(json.dumps({
            "alfredworkflow": {
                "variables": {
                    "notification_title": "Error: Invalid date format",
                    "notification_subtitle": "Use yyyy-mm-dd or yyyy-mm-dd--yyyy-mm-dd"
                }
            }
        }))
        sys.exit(1)
    
    start_date, end_date, date_range = parsed_date
    
    # Get album URL
    album_url = album_data.get("url", "")
    if not album_url:
        print(json.dumps({
            "alfredworkflow": {
                "variables": {
                    "notification_title": "Error: Album URL not found",
                    "notification_subtitle": "Cannot identify album to edit"
                }
            }
        }))
        sys.exit(1)
    
    # Read database
    albums = read_database()
    
    # Find and update the album
    album_found = False
    for album in albums:
        if album.get("url") == album_url:
            album_found = True
            
            # Update date fields
            album["dateRange"] = date_range
            album["startDate"] = start_date
            if end_date:
                album["endDate"] = end_date
            elif "endDate" in album:
                # Remove endDate if switching from range to single date
                del album["endDate"]
            
            break
    
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
    
    # Write updated database
    if not write_database(albums):
        print(json.dumps({
            "alfredworkflow": {
                "variables": {
                    "notification_title": "Error: Failed to save",
                    "notification_subtitle": "Could not write to database"
                }
            }
        }))
        sys.exit(1)
    
    # Create success message with formatted dates
    if end_date:
        display_range = format_range_for_display(start_date, end_date)
        message = f"Date range updated to: {display_range}"
    else:
        display_date = format_date_for_display(start_date)
        message = f"Date updated to: {display_date}"
    
    # Output as environment variables for notification
    print(json.dumps({
        "alfredworkflow": {
            "variables": {
                "notification_title": "✓ Date updated successfully",
                "notification_subtitle": message
            }
        }
    }))

if __name__ == "__main__":
    main()

