# photo-sort

Stop staring at 12,000 unsorted phone photos. `photo-sort` reads each file's
capture date and drops it into `YYYY/MM-Month/` folders. Ten years of camera
roll, organized in seconds.

## Install

Requires Python 3.9+.

```bash
pip install Pillow
```

That's it. `photo_sort.py` is a single file — drop it anywhere on your PATH.

## Use

```bash
# preview what would happen (always do this first)
python3 photo_sort.py ~/Pictures/dump -d ~/Pictures/sorted -c -n

# do it (copy, keep originals)
python3 photo_sort.py ~/Pictures/dump -d ~/Pictures/sorted -c

# move files in place, dedupe, recurse into subfolders
python3 photo_sort.py ~/Pictures/dump -r --dedupe
```

### Options

| flag                 | what it does                                         |
| -------------------- | ---------------------------------------------------- |
| `-d, --dest DIR`     | output folder (default: same as source)              |
| `-r, --recursive`    | also process subfolders                              |
| `-c, --copy`         | copy instead of move (safer)                         |
| `--scheme`           | `year-month` (default), `year`, or `ymd`             |
| `--dedupe`           | skip duplicate files (SHA-1 match)                   |
| `--delete-dupes`     | also delete dupes from the source                    |
| `-n, --dry-run`      | preview without changing files                       |

### How dates are detected

1. **EXIF** `DateTimeOriginal` (real camera date)
2. **Filename** patterns like `IMG_20220815_120000.jpg`
3. **File modified time** (last resort)

Each file's report tells you which source was used.

### Supported formats

JPG, PNG, HEIC, TIFF, WEBP, GIF, BMP, MP4, MOV, M4V, AVI, MKV, 3GP, WEBM.

## License

MIT — do whatever, no warranty.
