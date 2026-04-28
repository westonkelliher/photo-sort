# Product Hunt

**Tagline (≤60 chars):**
Sort 10 years of camera-roll photos by date in 30 seconds

**Description:**
photo-sort is a tiny CLI that reads each photo's EXIF capture date and files it
into clean year/month folders. Ten years of phone exports, organized in a
single command. No cloud upload, no subscription, no GUI. Single Python file,
MIT licensed. Free on GitHub. $9 packaged version with installer on Gumroad.

**First-comment maker post:**
Hi PH! I built this because I had a 47GB dump of camera-roll photos going back
to 2014 and got tired of paying monthly for cloud organizers.

It reads EXIF DateTimeOriginal first, falls back to filename patterns
(IMG_20220815_120000.jpg), then file mtime. SHA-1 dedupe is a flag. Dry-run is
a flag. Handles JPG, PNG, HEIC, TIFF, MP4, MOV, AVI, etc.

Free on GitHub: github.com/westonkelliher/photo-sort
$9 packaged on Gumroad if you'd rather not touch Python: [LINK]

Would love your feedback — especially on weird filename patterns from older
cameras and on HEIC live-photo pairing.

**Best launch day:** Tuesday, 12:01am PST.
