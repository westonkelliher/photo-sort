# photo-sort

Stop staring at 12,000 unsorted phone photos. `photo-sort` reads each file's
capture date and drops it into `YYYY/MM-Month/` folders. Ten years of camera
roll, organized in seconds.

![demo](assets/demo.svg)

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
| `--by-camera`        | also group by camera model (e.g. `iPhone 13/2023/...`)|
| `--pair-live`        | keep iPhone live-photo `.MOV` next to its `.HEIC`    |
| `--dedupe`           | skip duplicate files (SHA-1 match)                   |
| `--delete-dupes`     | also delete dupes from the source                    |
| `--manifest FILE`    | write a CSV log of every action for auditing         |
| `-n, --dry-run`      | preview without changing files                       |

### How dates are detected

1. **EXIF** `DateTimeOriginal` (photos)
2. **ffprobe** `creation_time` (videos, when ffmpeg is installed)
3. **Filename** patterns: `IMG_`, `VID_`, `MVI_`, `PXL_`, `DSC_`, `DSCN_`, `DSCF_`, `GOPR_`, `GH*_`, plain `YYYYMMDD_HHMMSS`, dashed `YYYY-MM-DD_HH-MM-SS`
4. **File modified time** (last resort)

Each file's report tells you which source was used.

### Supported formats

JPG, PNG, HEIC, TIFF, WEBP, GIF, BMP, MP4, MOV, M4V, AVI, MKV, 3GP, WEBM.

## License

MIT — do whatever, no warranty.
