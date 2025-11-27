# Alfred Google Photos Albums 📸 

Import and manage Google Photos albums in Alfred.
<a href="https://github.com/giovannicoppola/alfred-gphotos-albums/releases/latest/">
<img alt="Downloads"
src="https://img.shields.io/github/downloads/giovannicoppola/alfred-gphotos-albums/total?color=purple&label=Downloads"><br/>
</a>

![](images/gpa.png)

## Overview

This Alfred workflow helps you manage your Google Photos albums by creating a searchable database with metadata like dates, tags, and item counts. You can import albums from your browser and search/filter them with various options.

---

## 🚀 Quick Start

### Importing Albums

1. **Open your web browser** (Safari, Chrome, Opera, Vivaldi, Brave, or Edge)
2. **Navigate to Google Photos:**
   - For **bulk import**: Go to https://photos.google.com/albums (your albums list)
   - For **single album**: Go to a specific album page
3. **Make sure the browser window is the active/frontmost window**
4. **Trigger Alfred** and run your import command (e.g., `gpa_import`)

The script will automatically:
- Detect if you're on an album list or single album page
- Extract album titles, URLs, and item counts
- For single albums: extract date information (date ranges, start/end dates)
- Add new albums or update existing ones

**Important Note About Bulk Import:**
- **Bulk import is unreliable** and may not capture all albums on the page. This is due to how Google Photos loads albums dynamically as you scroll. The scraper can only see albums that are currently visible in the DOM.
- **It's safe to repeat bulk imports** - The workflow is designed to preserve your existing data. When you run a bulk import again:
  - New albums will be added
  - Existing albums will **not** be overwritten
  - Your edited titles, tags, and other customizations are preserved
  - Only item counts may be updated if they've changed
- **To get all albums**: You may need to scroll down on the albums page to load more albums, then run the import multiple times. Alternatively, import individual albums as you use them.

### Import Results

After importing, you'll see a 3-row summary:
- ✅ **Added**: Newly imported albums
- 🔄 **Updated**: Albums with new information added
- ⚪ **Unchanged**: Albums that were already in the database

**Click on any row** to view the specific albums in that category.

**For single album imports:**
When you import just one album, the row with a count of 1 will display the album title in parentheses and show "Shift+Cmd to copy markdown link" as the subtitle:
```
✅ Added: 1 album (My Vacation Photos 2024)
Shift+Cmd to copy markdown link
```
Press **⇧ Shift + ⌘ Cmd** to copy a markdown-formatted link like:
```
[Photos: My Vacation Photos 2024](https://photos.google.com/album/...)
```
This makes it easy to share album links in markdown documents, notes, or messages.

---

## 🔍 Searching Albums

### Basic Search

Type your search command followed by keywords:
```
gpa vacation
```

This searches album titles for "vacation".

### Year Filtering

Filter albums by year using the `y:` prefix:

**Single year:**
```
gpa y:2024
```
Shows only albums from 2024.

**Year range:**
```
gpa y:2023-2024
```
Shows albums from 2023 and 2024.

**Combine with keywords:**
```
gpa vacation y:2024
gpa family y:2022-2023
```
Filters by year AND searches for keywords.


**Note:** Year filtering only works for albums that have date information. Single album imports automatically extract dates, but bulk imports don't. You can manually set dates using the **⌃ Ctrl + ⌘ Cmd** modifier on any album.

### Search Results Display

Each result shows:
- **Title** with item count in parentheses (if available)
- **Subtitle** with:
  - 📅 Date range (if available)
  - 🏷️ Tags (if available)
  - URL (if no date or tags)
  - Position counter (e.g., "1/25")

**Tip:** Tap **⇧ Shift** on any result to preview the album page without leaving Alfred!

---

## ⌨️ Keyboard Modifiers

When viewing search results, you can use keyboard modifiers to perform actions:

### **⇧ Shift** - Quick Look Preview
Shows a quick preview of the album page using macOS QuickLook. This lets you see the album without leaving Alfred or opening your browser. Tap **⇧ Shift** again or press **Esc** to close the preview.

### **Return** (`↵`) - Open Album
Opens the album in your default web browser.

### **⇧ Shift + ⌘ Cmd** (`⌘-⇧-↵`) - Copy as Markdown Link
Copies the album as a markdown link:
```
[Photos: Album Title](https://photos.google.com/album/...)
```
**Tip:** When you import a single album, you can also use **⇧ Shift + ⌘ Cmd** directly from the import results report to copy the markdown link.

### **⌘ Cmd** (`⌘-↵`) - Edit Album Title
Change the album title in your database (doesn't affect Google Photos).

### **⌃ Ctrl** (`⌃-↵`) - Add/Remove Tags
Opens a tag management interface where you can:
- Add new tags to the album
- Remove existing tags
- View all available tags in your database

### **⌥ Option/Alt** (`⌥-↵`) - Edit Item Count
Manually update the number of items in the album.

### **⌃ Ctrl + ⌘ Cmd** (`⌃-⌘-↵`) - Edit Date
Manually set or update the date or date range for an album.

**Date formats:**
- Single date: `2025-11-10` (yyyy-mm-dd)
- Date range: `2020-11-10--2025-11-10` (yyyy-mm-dd--yyyy-mm-dd)

Note: Use a **double dash** (`--`) to separate start and end dates in a range.

### **⌘ Cmd + ⌥ Option** - Go Back
When viewing filtered results (from tag list or album stats), press this to return to the previous view.

### **⌘ Cmd + ⌥ Option + ⌃ Ctrl** - Delete Album
**⚠️ Warning:** Permanently removes the album from your database. This does not delete the album from Google Photos, only from your local workflow database.

---

## 🏷️ Working with Tags

### Adding Tags to Albums

1. Search for an album
2. Press **⌃ Ctrl** on the album you want to tag
3. Type a tag name and press Return
4. Repeat to add multiple tags

### Searching by Tags

You can filter albums by tags:

1. **List all available tags:**
   ```
   gpa_tags
   ```

2. **Click on a tag** to see all albums with that tag

3. **Combine with search:**
   After selecting a tag, you can further filter by typing keywords

### Tag Examples

Common tag categories:
- **Events**: `wedding`, `birthday`, `graduation`
- **People**: `family`, `friends`, `kids`
- **Places**: `beach`, `mountains`, `paris`, `home`
- **Activities**: `vacation`, `sports`, `hiking`, `cooking`
- **Time**: `summer2024`, `holiday`, `weekend`

### Advanced Search Examples

Combine filters and keywords for powerful searches:

```
gpa y:2024                    # All albums from 2024
gpa vacation y:2023-2024      # Vacation albums from 2023-2024
gpa family y:2022             # Family albums from 2022
gpa beach y:2024              # Beach albums from 2024
gpa y:2020-2025 wedding       # Wedding albums between 2020-2025
```

**Filters are cumulative:**
- Year filter + tag filter + keyword search all work together
- Albums must match ALL criteria to appear in results

---

## 📅 Date Information

When importing a **single album**, the script automatically extracts date information:

### Date Formats Recognized
- **Date range**: `Oct 30 – Nov 2`
- **Single date with year**: `Oct 30, 2024`
- **Single date**: `Oct 30`

### Date Display
Dates appear in the subtitle with a 📅 icon:
```
Paris Trip (245)
1/10 • 📅 Jun 15 – Jun 22 • 🏷️ vacation, europe
```

### Updating Dates

**Automatic extraction (from browser):**
1. Navigate to the album page in your browser
2. Run the import command
3. The script will extract and add date information automatically

**Manual entry:**
1. Search for an album
2. Press **⌃ Ctrl + ⌘ Cmd** on the album
3. Enter date in format: `2025-11-10` or `2020-11-10--2025-11-10`
4. Press Return to save

### Date Storage Format
Dates are stored internally in `yyyy-mm-dd` format for consistency and sorting:
- **Single date**: `2025-11-10`
- **Date range**: `2020-11-10--2025-11-10` (double dash separator)

When displayed in Alfred, dates are formatted for readability:
- Same year: `Oct 30 – Nov 2`
- Different years: `Oct 30, 2023 – Nov 2, 2024`
- Single date: `Oct 30, 2024`

---

## 🔄 Updating Albums

### When to Re-import

Re-import an album to:
- Add date information (first imports from bulk don't have dates)
- Update item counts if the album has changed
- Refresh album metadata

### How to Update

1. **Single album**: Navigate to the album page and run import
2. **Bulk update**: Go to the albums list page and run import

The script will:
- **Preserve** existing title and tags
- **Add** missing date information
- **Update** item counts if they've changed

---

## 📊 Album Statistics

### Overview

The album statistics feature provides a comprehensive overview of your album database, helping you understand what's complete, what's missing, and how your albums are organized.

### How to Access Statistics

Run the album stats command (set up in your Alfred workflow):

**Typical keyword**: `gpa_stats`

### Statistics Categories

The stats view shows all of the following categories:

#### 🔍 Incomplete Albums
Albums missing item count or date information. Click to view and fix them.

#### 🏷️ With Tags
Albums that have at least one tag. Useful for finding tagged vs. untagged albums.

#### 📋 Without Tags
Albums that have no tags. Click to add tags to these albums.

#### 📊 Missing Item Count
Albums without item count information. Visit these albums and use **⇧ Shift + ⌘ Cmd** to add counts.

#### 📅 Missing Date
Albums without date information. Visit the album pages and re-import to capture dates automatically.

#### ⚠️ Missing Both Item Count and Date
Albums missing both pieces of information. These need the most attention.

#### 📚 Total Albums
View all albums in your database.

#### ✅ Complete Albums
Albums that have both item count and date information. These are fully documented.

### Example Stats Display

```
🔍 Incomplete: 94 albums
🏷️ With tags: 12 albums
📋 Without tags: 91 albums
📊 Missing item count: 13 albums
📅 Missing date: 90 albums
⚠️ Missing both item count and date: 9 albums
📚 Total: 103 albums
✅ Complete: 9 albums
📈 Summary: 9 complete, 94 incomplete • 12 tagged, 91 untagged
```

---

## ⌨️ Quick Reference - Keyboard Shortcuts

When viewing album search results:

| Shortcut | Action |
|----------|--------|
| **⇧ Shift** (`⇧`) | QuickLook preview of album |
| **Return** (`↵`) | Open album in browser |
| **⇧ Shift + ⌘ Cmd** (`⌘-⇧-↵`) | Copy as markdown link |
| **⌘ Cmd** (`⌘-↵`) | Edit album title |
| **⌃ Ctrl** (`⌃-↵`) | Add/remove tags |
| **⌥ Option/Alt** (`⌥-↵`) | Edit item count |
| **⌃ Ctrl + ⌘ Cmd** (`⌃-⌘-↵`) | Edit date/date range |
| **⌘ Cmd + ⌥ Option** | Go back to tag list or stats (when viewing filtered results) |
| **⌘ Cmd + ⌥ Option + ⌃ Ctrl** | Delete album from database |

---

## 📞 Support

If you encounter issues:
1. Check that your browser is supported and frontmost
2. Verify you're on a Google Photos page
3. Try refreshing the page and importing again
4. Check the Alfred debugger for detailed error messages

---

## Acknowledgements
- Cursor for help with coding and documentation.
- Icon from Google Gemini
- Thanks to the Alfred community for inspiration and feedback.
