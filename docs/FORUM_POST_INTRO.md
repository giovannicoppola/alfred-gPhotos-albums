# Forum Post Introduction

# Motivation
Have you ever tried to find quickly a Google Photos album, or wished you could search by tag or year? `Google Photos Albums` creates a searchable, local database of all your Google Photos albums, that you can access through Alfred.

# Setting up
The workflow lets you import albums directly from your browser—just navigate to your Google Photos albums page or a specific album, trigger the workflow, and it will try to extract album titles, URLs, item counts (bulk import only), and dates (single-album import only). Import is not perfect (parsing errors are common, if you have a better solution, feel free to reach out!), I recommend you try it multiple times, as it does not overwrite your edits.  Everything is stored locally in a JSON database.

# Usage
## Searching albums
Once imported, you can search albums by keywords, filter by year (e.g., `y:2024`, or `y:2020-2023`), assign and browse by tags, and view statistics about your collection.
Once you find the album you want, you can:
- quicklook it (`⇧`)
- open it in your browser (`↵`)
- edit its title (`⌘-↵`)
- edit its tags (`⌃-↵`)
- edit its item count (`⌥-↵`)
- edit its date or date range (`⌃-⌘-↵`)
- copy its URL to the clipboard in Markdown format (`⌘-⇧-↵`)
- edit its item count (`⇧-↵)`

## Searching by tag
`gpa_tags` will show you a list of all tags you have assigned to albums. Selecting a tag will show you all albums with that tag.

## Album stats
You can view statistics about your album collection via the `gpa stats` keyword.
