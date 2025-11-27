# Unified Import - Quick Start Guide

## What is this?

A single script that automatically imports albums from Google Photos, whether you're on:
- **The albums list page** (bulk import multiple albums)
- **A single album page** (import one album with date information)

## Quick Start (3 Steps)

### 1. Navigate to Google Photos

Open your browser and go to one of these pages:

**For bulk import:**
```
https://photos.google.com/albums
```

**For single album:**
```
https://photos.google.com/album/YOUR_ALBUM_ID
https://photos.google.com/share/YOUR_ALBUM_ID
```

### 2. Run the Script

From terminal:
```bash
cd "/Users/giovanni/gDrive/GitHub repos/alfred-gPhotos/gPhoto albums"
./unified_import.sh
```

Or from Alfred: trigger your workflow

### 3. View Results

You'll see a 3-row report:

```
✅ Added: 5 albums         ← Click to see new albums
🔄 Updated: 2 albums       ← Click to see updated albums  
⚪ Unchanged: 10 albums    ← Click to see unchanged albums
```

**For single album imports:**
When importing just one album, the row with count "1" will display the album title in parentheses and show "Shift+Cmd to copy markdown link":
```
✅ Added: 1 album (My Vacation Photos 2024)
Shift+Cmd to copy markdown link
```
Press **⇧ Shift + ⌘ Cmd** to copy a markdown link like:
```
[Photos: My Vacation Photos 2024](https://photos.google.com/album/...)
```

## What Gets Imported?

### From Albums List Page (Bulk)
- ✅ Album title
- ✅ Album URL  
- ✅ Item count
- ❌ Dates (not available on list page)

**⚠️ Important**: Bulk import is unreliable and may not capture all albums. Google Photos loads albums dynamically as you scroll, so the scraper can only see albums currently visible. You may need to scroll down and run the import multiple times. **It's safe to repeat bulk imports** - your edited titles, tags, and customizations are preserved, and only new albums will be added.

### From Single Album Page
- ✅ Album title
- ✅ Album URL
- ✅ Item count
- ✅ Date range (e.g., "Oct 30 – Nov 2")
- ✅ Start date
- ✅ End date

## How It Updates Existing Albums

If an album URL already exists in your database:

1. **Title**: Preserved (never changed)
2. **Item count**: Updated if different
3. **Dates**: Added if missing (never overwritten)
4. **Tags**: Preserved (never changed)
5. **ID**: Preserved (never changed)

**This means it's safe to run bulk import multiple times** - your customizations (edited titles, tags, dates) are always preserved, and only new albums will be added.

## Database Structure

Your albums are stored in `photoAlbums.json` as line-delimited JSON:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "url": "https://photos.google.com/album/...",
  "title": "Trip to Pacific Palisades",
  "tags": ["vacation"],
  "itemCount": 24,
  "dateRange": "Oct 30 – Nov 2",
  "startDate": "Oct 30",
  "endDate": "Nov 2"
}
```

## Common Scenarios

### Scenario 1: First Time Bulk Import

```bash
# 1. Go to https://photos.google.com/albums
# 2. Run script
./unified_import.sh

# Result: All albums imported with unique IDs
✅ Added: 50 albums
```

### Scenario 2: Add Dates to Existing Album

```bash
# 1. Go to a specific album page
# 2. Run script
./unified_import.sh

# Result: Album updated with date information
🔄 Updated: 1 album
```

### Scenario 3: Import New Single Album

```bash
# 1. Go to a new album page
# 2. Run script
./unified_import.sh

# Result: New album added with all info including dates
✅ Added: 1 album
```

## Alfred Workflow Setup

Create a simple workflow:

1. **Script Filter** (keyword: `gpa` for "Google Photos Add")
   ```bash
   cd "/Users/giovanni/gDrive/GitHub repos/alfred-gPhotos/gPhoto albums"
   ./unified_import.sh
   ```

2. **Action** (passes the album IDs)
   ```bash
   cd "/Users/giovanni/gDrive/GitHub repos/alfred-gPhotos/gPhoto albums"
   python3 fetch_albums_by_ids.py "$1"
   ```

3. **Open URL** (opens the selected album)
   ```
   {query}
   ```

## Troubleshooting

### "Error: Not a Google Photos page"
**Solution**: Make sure you're on `photos.google.com` and on either:
- The albums list page (`/albums`)
- A single album page (`/album/...` or `/share/...`)

### "No albums found on this page"
**Solution**: 
- Wait for the page to fully load
- Scroll down to load more albums
- Try refreshing the page

### Dates not showing up
**Solution**: 
- Dates are only extracted from single album pages
- Some albums don't have dates visible on their pages
- The bulk import from the albums list cannot extract dates

### "Error: Failed to write to database"
**Solution**:
- Check that `photoAlbums.json` is writable
- Check disk space
- Try: `chmod 644 photoAlbums.json`

## Testing

Run the test suite to verify everything works:

```bash
cd "/Users/giovanni/gDrive/GitHub repos/alfred-gPhotos/gPhoto albums"
python3 test_unified_import.py
```

You should see:
```
🎉 All tests passed!
```

## What's New vs. Old System

| Feature | Old | New |
|---------|-----|-----|
| Single album import | ❌ | ✅ |
| Auto page detection | ❌ | ✅ |
| Date extraction | ❌ | ✅ |
| Unique IDs | ❌ | ✅ |
| Alfred report | Text | Interactive |

## Files in the System

- `unified_import.sh` - Main script (run this)
- `unified_add_albums.py` - Import logic
- `fetch_albums_by_ids.py` - Display albums by ID
- `test_unified_import.py` - Test suite
- `photoAlbums.json` - Your database
- `UNIFIED_IMPORT_README.md` - Full documentation

## Next Steps

After importing albums, you can:
- Add tags: `python3 toggle_tag.py`
- Search albums: `python3 search_albums.py`
- Edit titles: `python3 edit_album_title.py`
- List tags: `python3 list_tags.py`

## Support

For detailed documentation, see `UNIFIED_IMPORT_README.md`

For bulk import specifics, see `BULK_IMPORT_QUICKSTART.md`

---

**Enjoy your unified album management! 🎉**

