#!/usr/bin/env python3
"""
Script to search through Google Photos albums database.
Returns Alfred JSON format with matching albums.

Usage:
  search_albums.py [search_query]

Search Query Filters:
  - y:2024         : Filter by year 2024
  - y:2023-2024    : Filter by year range (2023 to 2024)
  - Regular text   : Search album titles

Environment Variables:
  - ID_list: Filter by album IDs (comma-separated) - optional
  - searchTag: Filter by tag - optional
  - mySource: Source context (e.g., 'tagList') - optional

Examples:
  search_albums.py "vacation y:2024"     # Vacation albums from 2024
  search_albums.py "y:2023-2024"         # All albums from 2023-2024
  search_albums.py "family y:2022"       # Family albums from 2022
"""

import json
import sys
import os
import re
from pathlib import Path
from datetime import datetime

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

def normalize_text(text):
    """Normalize text for searching: lowercase and replace separators with spaces."""
    if not text:
        return ""
    # Replace common separators with spaces
    text = re.sub(r'[-_/\\|]', ' ', text)
    # Replace multiple spaces with single space
    text = re.sub(r'\s+', ' ', text)
    return text.lower().strip()

def matches_search(title, search_terms):
    """
    Check if all search terms are found in the title.
    Search is case-insensitive and treats separators as spaces.
    """
    if not search_terms:
        return True
    
    normalized_title = normalize_text(title)
    
    # Check if all search terms are present in the title
    for term in search_terms:
        if term not in normalized_title:
            return False
    
    return True

def clean_title(title):
    """Clean up the title by removing ' - Google Photos' suffix."""
    if title.endswith(" - Google Photos"):
        return title[:-16]
    return title

def parse_date_for_sorting(date_string):
    """
    Parse a date string for sorting.
    Handles: "Oct 30", "Oct 30, 2024", "2024-10-30"
    Returns a tuple (year, month, day) for comparison.
    Returns (0, 0, 0) for invalid/missing dates (sorts first).
    """
    if not date_string:
        return (0, 0, 0)
    
    try:
        # Try new format first: "2024-10-30"
        if '-' in date_string and len(date_string) >= 8:
            parts = date_string.split('-')
            if len(parts) == 3 and all(p.isdigit() for p in parts):
                year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
                return (year, month, day)
        
        # Try old format with year: "Oct 30, 2024"
        if ',' in date_string:
            dt = datetime.strptime(date_string.strip(), "%b %d, %Y")
            return (dt.year, dt.month, dt.day)
        
        # Try old format without year: "Oct 30"
        current_year = datetime.now().year
        # Parse with current year to avoid deprecation warning
        dt = datetime.strptime(f"{date_string.strip()}, {current_year}", "%b %d, %Y")
        return (dt.year, dt.month, dt.day)
    except:
        # If parsing fails, treat as no date
        return (0, 0, 0)

def extract_year_from_date(date_string):
    """
    Extract year from a date string.
    Handles both old format ("Oct 30, 2024") and new format ("2024-10-30").
    Returns year as int, or None if not found.
    """
    if not date_string:
        return None
    
    try:
        # Try new format first: "2024-10-30"
        if '-' in date_string and len(date_string) >= 4:
            # Format: yyyy-mm-dd
            year_str = date_string.split('-')[0]
            if year_str.isdigit() and len(year_str) == 4:
                return int(year_str)
        
        # Try old format: "Oct 30, 2024"
        if ',' in date_string:
            dt = datetime.strptime(date_string.strip(), "%b %d, %Y")
            return dt.year
    except:
        pass
    
    return None

def convert_date_to_edit_format(start_date, end_date):
    """
    Convert stored dates to yyyy-mm-dd or yyyy-mm-dd--yyyy-mm-dd format for editing.
    Handles both old format ("Nov 27, 2014") and new format ("2024-11-27").
    """
    if not start_date:
        return ""
    
    def convert_single_date(date_str):
        """Convert a single date to yyyy-mm-dd format."""
        if not date_str:
            return None
        
        # Already in yyyy-mm-dd format
        if re.match(r'\d{4}-\d{2}-\d{2}', date_str):
            return date_str
        
        # Try to parse old format: "Nov 27, 2014" or "Nov 27"
        try:
            if ',' in date_str:
                dt = datetime.strptime(date_str.strip(), "%b %d, %Y")
                return dt.strftime("%Y-%m-%d")
            else:
                # No year - use current year
                current_year = datetime.now().year
                # Parse with current year to avoid deprecation warning
                dt = datetime.strptime(f"{date_str.strip()}, {current_year}", "%b %d, %Y")
                return dt.strftime("%Y-%m-%d")
        except:
            return None
    
    start_converted = convert_single_date(start_date)
    if not start_converted:
        return ""
    
    if end_date:
        end_converted = convert_single_date(end_date)
        if end_converted:
            return f"{start_converted}--{end_converted}"
    
    return start_converted

def parse_search_filters(search_query):
    """
    Parse search query for special filters.
    Returns (year_filter, date_filter, remaining_query)
    
    Year filter: y:2024 or y:2023-2024
    Date filter: d:Oct 30 or d:Oct 30-Nov 2
    """
    year_filter = None
    date_filter = None
    remaining_terms = []
    
    if not search_query:
        return year_filter, date_filter, ""
    
    # Split into terms
    terms = search_query.split()
    
    for term in terms:
        # Check for year filter: y:2024 or y:2023-2024
        year_match = re.match(r'y:(\d{4})(?:-(\d{4}))?', term, re.IGNORECASE)
        if year_match:
            start_year = int(year_match.group(1))
            end_year = int(year_match.group(2)) if year_match.group(2) else start_year
            year_filter = (start_year, end_year)
            continue
        
        # Check for date filter: d:Oct 30 or d:Oct 30-Nov 2
        # This is more complex as dates can have spaces
        if term.lower().startswith('d:'):
            # Collect this and potentially next terms for date parsing
            date_part = term[2:]  # Remove "d:" prefix
            # For now, add back to remaining terms and handle later
            # This is a simplified implementation
            remaining_terms.append(term)
        else:
            remaining_terms.append(term)
    
    remaining_query = ' '.join(remaining_terms)
    
    return year_filter, date_filter, remaining_query

def matches_year_filter(album, year_filter):
    """
    Check if album matches year filter.
    year_filter is a tuple (search_start_year, search_end_year)
    
    An album matches if:
    1. It's a single-date album and its year falls within the search range, OR
    2. It's a date-range album and the date ranges overlap
    
    For example:
    - Album: 2020-2025, Search: y:2023 -> MATCH (2023 is within album range)
    - Album: 2020-2025, Search: y:2023-2024 -> MATCH (ranges overlap)
    - Album: 2024, Search: y:2020-2025 -> MATCH (2024 is within search range)
    """
    if not year_filter:
        return True
    
    search_start_year, search_end_year = year_filter
    
    start_date = album.get("startDate", "")
    end_date = album.get("endDate", "")
    
    album_start_year = extract_year_from_date(start_date)
    
    if album_start_year is None:
        return False
    
    # Check if album has a date range
    if end_date:
        album_end_year = extract_year_from_date(end_date)
        if album_end_year is None:
            album_end_year = album_start_year
        
        # Check if ranges overlap
        # Ranges overlap if: album_start <= search_end AND album_end >= search_start
        return album_start_year <= search_end_year and album_end_year >= search_start_year
    else:
        # Single date - check if it falls within search range
        return search_start_year <= album_start_year <= search_end_year

def alfred_response(items, variables=None):
    """Create an Alfred JSON response with multiple items and optional variables."""
    response = {"items": items}
    if variables:
        response["variables"] = variables
    return json.dumps(response, ensure_ascii=False)

def main():
    # Get search query from argv (like original workflow)
    search_query = sys.argv[1].strip() if len(sys.argv) > 1 else ""
    
    # Parse special filters from search query
    year_filter, date_filter, remaining_query = parse_search_filters(search_query)
    
    # Check if we're filtering by tag and where we came from
    tag_filter = os.environ.get("searchTag", "").strip()
    my_source = os.environ.get("mySource", "").strip()
    
    # Check if we're filtering by album IDs (comma-separated) - from env var only
    filter_ids = os.environ.get("ID_list", "").strip()
    id_set = None
    if filter_ids:
        id_set = set(id.strip() for id in filter_ids.split(',') if id.strip())
    
    # Normalize and split search query into terms (using remaining query after filter extraction)
    search_terms = normalize_text(remaining_query).split() if remaining_query else []
    
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
    
    # Filter albums based on search terms and optional tag/ID filters
    matching_albums = []
    for album in albums:
        title = album.get("title", "Untitled")
        url = album.get("url", "")
        tags = album.get("tags", [])
        item_count = album.get("itemCount")
        album_id = album.get("id", "")
        
        # Skip if ID filter is set and album's ID is not in the set
        if id_set and album_id not in id_set:
            continue
        
        # Skip if tag filter is set and album doesn't have that tag
        if tag_filter and tag_filter not in tags:
            continue
        
        # Skip if year filter is set and album doesn't match
        if not matches_year_filter(album, year_filter):
            continue
        
        if matches_search(title, search_terms):
            clean = clean_title(title)
            
            # Add item count to title if available
            if item_count is not None and item_count > 0:
                display_title = f"{clean} ({format_number(item_count)})"
            else:
                display_title = clean
            
            # Get date information
            date_range_display = album.get("dateRange", "")
            start_date = album.get("startDate", "")
            end_date = album.get("endDate", "")
            
            # Convert to edit format (yyyy-mm-dd or yyyy-mm-dd--yyyy-mm-dd)
            date_range_edit = convert_date_to_edit_format(start_date, end_date)
            
            # Create subtitle: show date and tags if available, otherwise URL
            subtitle_parts = []
            if date_range_display:
                subtitle_parts.append(f"📅 {date_range_display}")
            if tags:
                subtitle_parts.append(f"🏷️ {', '.join(tags)}")
            
            if subtitle_parts:
                subtitle_string = " • ".join(subtitle_parts)
            else:
                subtitle_string = url
            
            matching_albums.append({
                "title": display_title,
                "clean_title": clean,
                "url": url,
                "tags": tags,
                "subtitle_string": subtitle_string,
                "item_count": item_count,
                "date_range_edit": date_range_edit,
                "start_date": start_date,
                "end_date": end_date,
                "sort_date": parse_date_for_sorting(start_date)
            })
    
    # Sort albums: by date descending (most recent first), then no date albums last
    matching_albums.sort(key=lambda x: (
        1 if x['sort_date'] == (0, 0, 0) else 0,  # No date albums last
        -x['sort_date'][0],  # Year descending (most recent first)
        -x['sort_date'][1],  # Month descending
        -x['sort_date'][2]   # Day descending
    ))
    
    # Create Alfred items with position counters
    total_count = len(matching_albums)
    matching_items = []
    for idx, album_data in enumerate(matching_albums, 1):
        subtitle = f"{format_number(idx)}/{format_number(total_count)} • {album_data['subtitle_string']}"
        
        # Create full album JSON for editing
        album_json = json.dumps({
            "url": album_data["url"],
            "title": album_data.get("clean_title", album_data["title"]),
            "tags": album_data["tags"],
            "itemCount": album_data.get("item_count")
        })
        
        # Build mods dictionary
        mods = {
            "ctrl": {
                "subtitle": "Add/remove tags",
                "arg": json.dumps({"url": album_data["url"], "title": album_data.get("clean_title", album_data["title"]), "tags": album_data["tags"]}),
                "valid": True
            },
            "alt": {
                "subtitle": "Edit item count",
                "arg": str(album_data.get("item_count", 0)),
                "valid": True,
                "variables": {
                    "albumToEdit": album_json,
                    "albumTitle": album_data.get("clean_title", album_data["title"])
                }
            },
            "cmd": {
                "subtitle": "Edit album title",
                "arg": album_data.get("clean_title", album_data["title"]),
                "valid": True,
                "variables": {
                    "albumToEdit": album_json
                }
            },
            "shift+cmd": {
                "subtitle": "Copy as markdown link",
                "arg": f"[Photos: {album_data.get('clean_title', album_data['title'])}]({album_data['url']})",
                "valid": True
            },
            "cmd+ctrl": {
                "subtitle": "Edit date (yyyy-mm-dd or yyyy-mm-dd--yyyy-mm-dd)",
                "arg": album_data.get("date_range_edit", ""),
                "valid": True,
                "variables": {
                    "albumToEdit": album_json,
                    "albumTitle": album_data.get("clean_title", album_data["title"])
                }
            },
            "cmd+alt+ctrl": {
                "subtitle": "⚠️ Delete album from database",
                "arg": album_data.get("clean_title", album_data["title"]),
                "valid": True,
                "variables": {
                    "albumToDelete": album_json,
                    "albumTitle": album_data.get("clean_title", album_data["title"])
                }
            }
        }
        
        # Add cmd+opt modifier if coming from tag list or album stats
        if my_source == "tagList":
            mods["cmd+alt"] = {
                "subtitle": "Go back to tag list",
                "arg": "",
                "valid": True
            }
        elif my_source == "album_stats":
            mods["cmd+alt"] = {
                "subtitle": "Go back to album stats",
                "arg": "",
                "valid": True
            }
        
        matching_items.append({
            "title": album_data["title"],
            "subtitle": subtitle,
            "arg": album_data["url"],
            "valid": True,
            "mods": mods,
            "icon": {
                "path": "icon.png" if Path(__file__).parent.joinpath("icon.png").exists() else ""
            }
        })
    
    # If no matches, show a helpful message
    if not matching_items:
        if id_set:
            if search_query:
                subtitle = f"No albums in the filtered set matching: {search_query}"
            else:
                subtitle = f"No albums found in the filtered set"
        elif tag_filter:
            if search_query:
                subtitle = f"No albums with tag '{tag_filter}' matching: {search_query}"
            else:
                subtitle = f"No albums found with tag: {tag_filter}"
        else:
            subtitle = f"No results for: {search_query}" if search_query else "No albums found"
        
        matching_items.append({
            "title": "No albums match your search",
            "subtitle": subtitle,
            "valid": False
        })
    
    # Output with environment variables (preserve searchTag, ID_list, and mySource if they were set)
    variables = {"userInputString": search_query}
    if tag_filter:
        variables["searchTag"] = tag_filter
    if filter_ids:
        variables["ID_list"] = filter_ids
    if my_source:
        variables["mySource"] = my_source
    
    print(alfred_response(matching_items, variables=variables))

if __name__ == "__main__":
    main()


