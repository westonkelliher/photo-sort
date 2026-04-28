# r/DataHoarder

**Title:** I had 47GB of unsorted phone photo exports going back to 2014. Wrote a tiny tool that filed them all by EXIF date in 30 seconds. Sharing it.

**Body:**

For years I'd been telling myself I'd "get around to" organizing my camera roll
exports. Folders full of `IMG_4831.HEIC`, `IMG_4832.HEIC`. 47 GB. I finally
just wrote the thing.

It reads each photo's EXIF `DateTimeOriginal`, falls back to filename patterns,
falls back to mtime, and drops everything into `YYYY/MM-Month/`. SHA-1 dedupe
is a flag. Dry-run is a flag. Move or copy. Single Python file, MIT license.

GitHub: https://github.com/westonkelliher/photo-sort

Example:

```
photo-sort ~/Pictures/dump -d ~/Pictures/sorted -c --dedupe
```

→

```
sorted/
  2014/07-July/
  2014/08-August/
  2015/01-January/
  ...
```

Handles HEIC, JPG, PNG, TIFF, WEBP, MP4, MOV, AVI, MKV, etc.

Selling a $9 packaged version on Gumroad if you'd rather not touch Python:
[GUMROAD LINK]

Free version on GitHub does the same job; pay if you want to support it or get
a one-click installer instead of `pip install Pillow`.

What I want from this thread: tell me what's broken on your dataset. Especially
interested in weird filenames from old phones, GoPro patterns, scanner output.
