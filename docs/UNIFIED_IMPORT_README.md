# Unified Album Import System

This unified system allows you to import albums from Google Photos into your local database, handling both **bulk imports** (from the albums list page) and **single album imports** (from individual album pages).

## Key Features

✨ **Automatic Detection**: The script automatically detects whether you're on:
- The albums list page (`https://photos.google.com/albums`)
- A single album page (`https://photos.google.com/album/...` or `https://photos.google.com/share/...`)

✨ **Date Extraction**: When importing a single album, the script extracts and stores:
- Date range (e.g., "Oct 30 – Nov 2")
- Start date
- End date

✨ **Unique IDs**: All albums now have unique IDs for easy reference and tracking

✨ **Smart Updates**: 
- Preserves existing titles
- Updates item counts intelligently
- Adds date information if missing
- Never overwrites existing data unnecessarily

✨ **Alfred Integration**: Returns a beautiful 3-row report showing:
1. Number of new albums imported
2. Number of albums updated
3. Number of albums unchanged

Each row is clickable and shows you the relevant albums!

## Files

### Main Scripts

- **`unified_import.sh`** - Main entry point that runs the scraper and import
- **`unified_add_albums.py`** - Python script that processes data and updates database
- **`fetch_albums_by_ids.py`** - Helper script to display albums by their IDs
- **`search_albums_by_ids.py`** - Wrapper to search within a subset of albums by IDs

### Database

- **`photoAlbums.json`** - Your album database (one JSON object per line)

## Usage

### Option 1: From Alfred (Recommended)

1. Navigate to Google Photos in your browser:
   - For bulk import: Go to `https://photos.google.com/albums`
   - For single album: Open any album page

2. Trigger the Alfred workflow that runs `unified_import.sh`

3. View the 3-row report:
   - ✅ **Added**: Shows newly imported albums
   - 🔄 **Updated**: Shows albums with updated information
   - ⚪ **Unchanged**: Shows albums that were already up to date

4. Click any row to see the list of albums in that category

**For single album imports:** When you import just one album, the row with count "1" will display the album title in parentheses (e.g., "✅ Added: 1 album (My Vacation Photos 2024)") and show "Shift+Cmd to copy markdown link". Press **⇧ Shift + ⌘ Cmd** to copy a markdown-formatted link like `[Photos: Album Title](url)`

### Option 2: From Terminal

```bash
cd "/Users/giovanni/gDrive/GitHub repos/alfred-gPhotos/gPhoto albums"
./unified_import.sh
```

## How It Works

### 1. Page Detection

The script first checks the current URL:
- If it contains `/albums`, it runs in **bulk mode**
- If it contains `/album/` or `/share/`, it runs in **single mode**

### 2. Data Extraction

**Bulk Mode** (albums list):
- Extracts all visible albums
- Gets title, URL, and item count for each
- Does NOT extract dates (not available on list page)
- **Important**: Bulk import is unreliable and may not capture all albums. Google Photos loads albums dynamically as you scroll, and the scraper can only see albums currently visible in the DOM. You may need to scroll down and run the import multiple times to capture all albums.

**Single Mode** (album page):
- Extracts title, URL, and item count
- Extracts date range (e.g., "Oct 30 – Nov 2")
- Extracts start date
- Extracts end date

### 3. Database Update

For each album:

**If URL already exists**:
- Preserves the title (never changes it)
- Updates item count if different (unless new value is 0)
- Adds date fields if they're missing and now available
- Returns as "updated" if anything changed, "unchanged" otherwise

**If URL is new**:
- Creates new entry with all available data
- Generates a unique ID
- Initializes empty tags array
- Returns as "added"

### 4. Report Generation

Outputs an Alfred-compatible JSON report with:
- Count of added albums (with their IDs)
- Count of updated albums (with their IDs)
- Count of unchanged albums (with their IDs)

Clicking a row runs `fetch_albums_by_ids.py` with the relevant IDs.

## Important Notes About Bulk Import

### Bulk Import Limitations

**Bulk import is unreliable** and will not capture all albums on the page. This is due to several factors:

1. **Dynamic Loading**: Google Photos uses infinite scroll and lazy loading. Albums are loaded dynamically as you scroll down the page.
2. **DOM Visibility**: The scraper can only see albums that are currently rendered in the DOM. Albums that haven't been scrolled into view won't be captured.
3. **Page State**: The number of albums captured depends on how far you've scrolled and how many albums Google Photos has loaded.

**What this means:**
- You may need to scroll down on the albums page to load more albums before running the import
- You may need to run bulk import multiple times to capture all albums
- Some albums may be missed even after multiple attempts

### Safe to Repeat Bulk Imports

**It's safe to run bulk import multiple times** - the workflow is designed to preserve your existing data:

- ✅ **New albums** will be added to the database
- ✅ **Existing albums are preserved** - your edited titles, tags, and customizations are never overwritten
- ✅ **Item counts** may be updated if they've changed (but only if the new value is different and not 0)
- ✅ **Date information** is preserved - bulk imports don't overwrite existing dates
- ✅ **Tags** are always preserved - bulk imports never modify tags

**Best Practice:**
Run bulk import periodically (e.g., weekly or monthly) to catch new albums. Don't worry about duplicates or overwriting - the system handles it safely.

## Database Structure

Each album in `photoAlbums.json` is a JSON object with these fields:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "url": "https://photos.google.com/album/...",
  "title": "Trip to Pacific Palisades",
  "tags": ["vacation", "california"],
  "itemCount": 24,
  "dateRange": "Oct 30 – Nov 2",
  "startDate": "Oct 30",
  "endDate": "Nov 2"
}
```

### Fields

- **`id`** (string, required): Unique identifier (UUID format)
- **`url`** (string, required): Full URL to the album
- **`title`** (string, required): Album title
- **`tags`** (array, required): Array of tag strings
- **`itemCount`** (number, optional): Number of photos/videos
- **`dateRange`** (string, optional): Full date range display
- **`startDate`** (string, optional): Start date of album
- **`endDate`** (string, optional): End date of album

## Migration

If you have an existing `photoAlbums.json` without IDs, don't worry! The system will automatically add unique IDs to all albums the first time it reads the database.

## Workflow Integration

### Alfred Workflow Setup

**Option 1: Simple View (no search)**

1. **Script Filter**: Use `unified_import.sh` as your main import trigger
2. **Action**: Pass the `{query}` (which contains album IDs) to `fetch_albums_by_ids.py`

```
[Keyword Trigger] → [Run Script: ./unified_import.sh] → [Script Filter: ./fetch_albums_by_ids.py "$1"]
```

**Option 2: With Search (recommended)**

1. **Script Filter**: Use `unified_import.sh` as your main import trigger
2. **Script Filter**: Search within the selected subset

**Script configuration:**
```bash
python3 ./search_albums.py "$1"
```

**That's it!** No need to manually set environment variables.

**How it works:**
1. Run unified_import.sh → See 3-row report
2. Click a row (e.g., "Added: 5") → Alfred automatically sets `ID_list` env var
3. Type search query → passed as `$1`
4. Results filtered by BOTH ID list AND search query

The unified_import script now outputs the IDs as `variables` in the Alfred JSON, so Alfred automatically passes them as environment variables to the next Script Filter. You don't need to configure anything manually!

## Examples

### Example 1: Bulk Import

**Action**: Navigate to `https://photos.google.com/albums` and run the script

**Result**:
```
✅ Added: 5 album(s)
🔄 Updated: 3 album(s)
⚪ Unchanged: 47 album(s)
```

### Example 2: Single Album Import (New)

**Action**: Navigate to a new album at `https://photos.google.com/album/ABC123` and run the script

**Result**:
```
✅ Added: 1 album(s)
🔄 Updated: 0 album(s)
⚪ Unchanged: 0 album(s)
```

The new album includes date information extracted from the page.

### Example 3: Single Album Import (Update)

**Action**: Navigate to an existing album that now has date information

**Result**:
```
✅ Added: 0 album(s)
🔄 Updated: 1 album(s)
⚪ Unchanged: 0 album(s)
```

The existing album now has the date fields added without changing anything else.

## Troubleshooting

### "Error: Not a Google Photos page"
- Make sure you're on `photos.google.com`
- Supported pages: `/albums`, `/album/...`, `/share/...`

### "No albums found on this page"
- The page may still be loading
- Try scrolling down to load more albums
- Some pages may not have the expected structure

### "Error: Failed to write to database"
- Check file permissions on `photoAlbums.json`
- Make sure the directory is writable

### Dates not extracted
- Some albums don't have date information visible on the page
- The script only extracts dates that are present in the page text

## Advanced Usage

### Fetching Albums Directly

You can fetch albums by ID programmatically:

```bash
python3 fetch_albums_by_ids.py "id1,id2,id3"
```

This returns Alfred JSON format with the album details.

### Searching Within a Subset

You can search within a specific set of albums:

```bash
python3 search_albums_by_ids.py "id1,id2,id3" "search query"
```

This is particularly useful after importing - you can search only within the newly added or updated albums. See `SEARCH_BY_IDS_README.md` for complete documentation.

### Checking for Duplicates

Since each album has a unique ID, you can easily check for duplicate URLs:

```bash
# Count unique URLs vs total lines
wc -l photoAlbums.json
cat photoAlbums.json | jq -r '.url' | sort | uniq | wc -l
```

## Benefits Over Old System

| Feature | Old System | New System |
|---------|-----------|------------|
| Single album import | ❌ Not supported | ✅ Fully supported |
| Date extraction | ❌ Never | ✅ Yes (single albums) |
| Unique IDs | ❌ No | ✅ UUID for all |
| Page type detection | ❌ Manual | ✅ Automatic |
| Alfred report | ⚠️ Text only | ✅ Interactive JSON |
| Update tracking | ⚠️ Basic | ✅ Detailed by type |

## Future Enhancements

Possible improvements:
- Support for extracting location information
- Support for extracting contributor information
- Batch date extraction for multiple albums
- Duplicate URL detection and merging
- Export to other formats (CSV, etc.)

## Questions?

Refer to the other documentation files:
- `BULK_IMPORT_QUICKSTART.md` - Quick start guide for bulk imports
- `SINGLE_ALBUM_IMPORT.md` - Single album import guide
- `single_script.md` - Original requirements document


