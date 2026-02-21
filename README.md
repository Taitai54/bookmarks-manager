# Bookmarks Manager

A lightweight desktop GUI for managing Google Chrome bookmarks. Search, filter, sort, and bulk-delete bookmarks without opening Chrome.

Built with Python and Tkinter -- no external dependencies required.

## Features

- **Search & Filter** -- Real-time text search across bookmark names, URLs, and folders. Filter by folder via dropdown.
- **Sortable Columns** -- Click any column header (Name, URL, Folder) to sort ascending/descending.
- **Multi-Select & Bulk Delete** -- Select multiple bookmarks and delete them in one go. Select All / Deselect All buttons included.
- **Automatic Backup** -- Creates a timestamped JSON backup of your bookmarks before any deletion, so you can always restore.
- **Manual Backup** -- One-click backup button to save your current bookmarks at any time.
- **Direct Chrome Integration** -- Reads and writes Chrome's native `Bookmarks` JSON file directly.

## Requirements

- Python 3.6+
- Google Chrome (Windows)
- No external packages needed (uses only Python standard library)

## Usage

```bash
python bookmarks.py
```

> **Note:** Close Chrome before running to avoid file lock conflicts.

## How It Works

The app reads Chrome's bookmarks from:

```
%LOCALAPPDATA%/Google/Chrome/User Data/Default/Bookmarks
```

It parses the JSON structure, displays bookmarks in a searchable/filterable table, and writes changes back to the same file when you delete bookmarks.

## Backups

Backup files are saved as `bookmarks_backup_YYYYMMDD_HHMMSS.json` in the working directory. You can restore by copying a backup file back to Chrome's Bookmarks path.

## License

MIT
