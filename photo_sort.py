#!/usr/bin/env python3
"""photo-sort: organize a folder of photos/videos into YYYY/MM-Month/ subfolders by capture date."""
import argparse
import hashlib
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

from PIL import Image, ExifTags

PHOTO_EXT = {".jpg", ".jpeg", ".png", ".heic", ".heif", ".tif", ".tiff", ".webp", ".gif", ".bmp"}
VIDEO_EXT = {".mp4", ".mov", ".m4v", ".avi", ".mkv", ".3gp", ".webm"}
ALL_EXT = PHOTO_EXT | VIDEO_EXT

DATETIME_TAGS = ("DateTimeOriginal", "DateTimeDigitized", "DateTime")


def exif_datetime(path: Path):
    try:
        with Image.open(path) as img:
            exif = img._getexif() or {}
        tag_map = {ExifTags.TAGS.get(k, k): v for k, v in exif.items()}
        for tag in DATETIME_TAGS:
            v = tag_map.get(tag)
            if v:
                try:
                    return datetime.strptime(v, "%Y:%m:%d %H:%M:%S")
                except ValueError:
                    pass
    except Exception:
        pass
    return None


def filename_datetime(path: Path):
    stem = path.stem
    for fmt in ("%Y%m%d_%H%M%S", "%Y-%m-%d_%H-%M-%S", "IMG_%Y%m%d_%H%M%S", "VID_%Y%m%d_%H%M%S"):
        try:
            cleaned = stem.replace("IMG_", "").replace("VID_", "")
            for try_fmt in ("%Y%m%d_%H%M%S", "%Y-%m-%d_%H-%M-%S"):
                try:
                    return datetime.strptime(cleaned[:17], try_fmt)
                except ValueError:
                    continue
        except Exception:
            continue
    return None


def best_datetime(path: Path):
    if path.suffix.lower() in PHOTO_EXT:
        dt = exif_datetime(path)
        if dt:
            return dt, "exif"
    dt = filename_datetime(path)
    if dt:
        return dt, "filename"
    ts = path.stat().st_mtime
    return datetime.fromtimestamp(ts), "mtime"


def file_hash(path: Path, chunk=1 << 20):
    h = hashlib.sha1()
    with path.open("rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def iter_media(src: Path, recursive: bool):
    it = src.rglob("*") if recursive else src.iterdir()
    for p in it:
        if p.is_file() and p.suffix.lower() in ALL_EXT:
            yield p


def target_path(dest: Path, dt: datetime, name: str, scheme: str):
    if scheme == "year-month":
        sub = Path(f"{dt.year:04d}") / f"{dt.month:02d}-{dt.strftime('%B')}"
    elif scheme == "year":
        sub = Path(f"{dt.year:04d}")
    elif scheme == "ymd":
        sub = Path(f"{dt.year:04d}") / f"{dt.month:02d}" / f"{dt.day:02d}"
    else:
        sub = Path(f"{dt.year:04d}") / f"{dt.month:02d}-{dt.strftime('%B')}"
    return dest / sub / name


def unique(path: Path):
    if not path.exists():
        return path
    stem, suf = path.stem, path.suffix
    i = 1
    while True:
        cand = path.with_name(f"{stem}_{i}{suf}")
        if not cand.exists():
            return cand
        i += 1


def run(args):
    src = Path(args.source).expanduser().resolve()
    dest = Path(args.dest).expanduser().resolve() if args.dest else src
    if not src.is_dir():
        sys.exit(f"source not a directory: {src}")

    seen_hashes = {} if args.dedupe else None
    actions = {"moved": 0, "copied": 0, "skipped_dupe": 0, "errors": 0}

    files = list(iter_media(src, args.recursive))
    total = len(files)
    if total == 0:
        print("no media files found")
        return

    for i, p in enumerate(files, 1):
        try:
            dt, source = best_datetime(p)
            tgt = target_path(dest, dt, p.name, args.scheme)

            if seen_hashes is not None:
                h = file_hash(p)
                if h in seen_hashes:
                    actions["skipped_dupe"] += 1
                    print(f"[{i}/{total}] DUPE  {p.name} == {seen_hashes[h].name}")
                    if args.delete_dupes and not args.dry_run:
                        p.unlink()
                    continue
                seen_hashes[h] = p

            tgt.parent.mkdir(parents=True, exist_ok=True)
            tgt = unique(tgt)
            verb = "COPY" if args.copy else "MOVE"
            print(f"[{i}/{total}] {verb}  {p.name} -> {tgt.relative_to(dest)}  ({source})")
            if args.dry_run:
                continue
            if args.copy:
                shutil.copy2(p, tgt)
                actions["copied"] += 1
            else:
                shutil.move(str(p), str(tgt))
                actions["moved"] += 1
        except Exception as e:
            actions["errors"] += 1
            print(f"[{i}/{total}] ERR   {p}: {e}")

    print("\n--- summary ---")
    for k, v in actions.items():
        print(f"{k:>14}: {v}")
    if args.dry_run:
        print("(dry run — no files changed)")


def main():
    ap = argparse.ArgumentParser(description="Organize photos/videos into dated folders by capture date.")
    ap.add_argument("source", help="folder containing photos/videos")
    ap.add_argument("-d", "--dest", help="destination folder (default: same as source)")
    ap.add_argument("-r", "--recursive", action="store_true", help="recurse into subfolders")
    ap.add_argument("-c", "--copy", action="store_true", help="copy instead of move")
    ap.add_argument("--scheme", choices=("year-month", "year", "ymd"), default="year-month",
                    help="folder structure (default: year-month)")
    ap.add_argument("--dedupe", action="store_true", help="skip duplicate files (by SHA1)")
    ap.add_argument("--delete-dupes", action="store_true", help="delete duplicates from source (implies --dedupe)")
    ap.add_argument("-n", "--dry-run", action="store_true", help="preview without changing files")
    args = ap.parse_args()
    if args.delete_dupes:
        args.dedupe = True
    run(args)


if __name__ == "__main__":
    main()
