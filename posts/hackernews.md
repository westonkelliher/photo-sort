# Hacker News — Show HN

**Title (≤80 chars, no emoji, no marketing):**
Show HN: Photo-sort – organize a folder of photos by EXIF date

**URL:** https://github.com/westonkelliher/photo-sort

**First comment (post immediately after submitting):**

I had 47GB of phone-export photos sitting in one folder going back a decade.
The existing tools either wanted to upload everything to a cloud service, or
were heavyweight GUIs, or had stopped being maintained. I wanted a single
Python file I could run on a folder.

It reads EXIF `DateTimeOriginal` first, falls back to filename patterns
(`IMG_20220815_120000.jpg`), then to file mtime as a last resort. Each output
line tells you which source it used so you can audit. SHA-1 dedupe is opt-in.
Dry-run before any move/copy.

Things I'd love feedback on:
- video metadata: I'm using mtime for video; happy to add ffprobe-based
  creation-date if anyone has run into format quirks
- HEIC live-photo paired files (.MOV alongside .HEIC) — currently treated
  independently, probably should be paired
- locale handling for the month folder name (currently English `%B`)

MIT, single file, ~150 lines. Pillow is the only dep.
