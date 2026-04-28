# Gumroad listing copy

## Product name
photo-sort — organize 10 years of phone photos in 30 seconds

## Price
**$9** (impulse-buy band; bump to $14 after first 25 sales as social proof)

## Cover headline
**Stop scrolling through 12,000 unsorted photos.**
One command, every photo filed by year and month.

## Short description (under the title)
A tiny command-line tool that reads each photo's capture date and drops it into
clean `YYYY/MM-Month/` folders. Works on Mac, Windows, Linux. No cloud upload.
Your photos never leave your computer.

## Long description (body)

You exported your camera roll to a folder. It's 47 GB. The filenames are
`IMG_4831.HEIC`, `IMG_4832.HEIC`, `IMG_4833.HEIC` — useless. You meant to
organize them. That was three years ago.

**photo-sort** fixes it in one command:

```
photo-sort ~/Pictures/dump -d ~/Pictures/sorted -c
```

Result:

```
sorted/
  2019/
    07-July/
    08-August/
  2020/
    01-January/
  ...
```

### What it does
- Reads EXIF `DateTimeOriginal` from each photo (the real camera date)
- Falls back to filename patterns (`IMG_20220815_120000.jpg`)
- Falls back to file modified date as a last resort
- Detects and skips duplicates by SHA-1 hash
- Dry-run mode so you can preview before touching anything
- Handles JPG, PNG, HEIC, TIFF, WEBP, GIF, BMP, MP4, MOV, AVI, MKV, and more

### What it doesn't do
- Upload your photos anywhere. It's a local script. Your stuff stays yours.
- Re-encode or modify your files. It only moves or copies.
- Require a subscription. One purchase, yours forever.

### What you get
- `photo_sort.py` — single-file Python script (MIT licensed)
- README with examples
- Email support for setup questions

### Requirements
- Python 3.9 or newer (free, pre-installed on Mac/Linux)
- One `pip install Pillow` command

---

## FAQ

**Does this work on Windows?** Yes. Install Python from python.org, then run the
same command in PowerShell.

**Will it mess up my photos?** No. Default `--copy` mode keeps originals
untouched. Always run with `-n` (dry-run) first to preview.

**Does it support HEIC (iPhone)?** Yes, Pillow handles HEIC EXIF.

**What if a photo has no date?** It uses the filename, then file modified time.
The console output tells you which source was used for each file.

**Refund policy?** 7-day no-questions-asked refund.

---

## Tags
photo organizer, exif, camera roll, photo management, cli tool, python, mac,
windows, linux, automation, productivity, photography

## Cover image idea
Split-screen: left side a chaotic folder of `IMG_xxxx.JPG` files, right side a
tidy nested `2019/07-July/, 2019/08-August/` tree. Caption: "30 seconds."
