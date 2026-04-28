#!/usr/bin/env python3
"""photo-sort: organize a folder of photos/videos into dated folders by capture date.

Reads EXIF first, falls back to filename patterns, then file mtime. Optional:
- pairs iPhone live-photos (.HEIC + .MOV) so they stay together
- uses ffprobe for accurate video creation dates when available
- writes a CSV manifest of every action
- groups by camera model in addition to date
- SHA-1 dedupe with optional source deletion
"""
import argparse
import csv
import hashlib
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from PIL import Image, ExifTags

PHOTO_EXT = {".jpg", ".jpeg", ".png", ".heic", ".heif", ".tif", ".tiff", ".webp", ".gif", ".bmp"}
VIDEO_EXT = {".mp4", ".mov", ".m4v", ".avi", ".mkv", ".3gp", ".webm"}
ALL_EXT = PHOTO_EXT | VIDEO_EXT

DATETIME_TAGS = ("DateTimeOriginal", "DateTimeDigitized", "DateTime")

# Common phone/camera filename patterns. Each matches a YYYYMMDD_HHMMSS substring.
FILENAME_PATTERNS = [
    re.compile(r"(?:IMG|VID|MVI|PXL|DSC|DSCN|DSCF|GOPR|GH|P)[-_]?(\d{8})[-_](\d{6})"),
    re.compile(r"(\d{8})[-_](\d{6})"),
    re.compile(r"(\d{4}-\d{2}-\d{2})[-_ ](\d{2}-\d{2}-\d{2})"),
    re.compile(r"(\d{4}-\d{2}-\d{2})[-_T ](\d{2}\.\d{2}\.\d{2})"),
]


def exif_data(path: Path):
    """Return dict of named EXIF tags, or {}."""
    try:
        with Image.open(path) as img:
            exif = img._getexif() or {}
        return {ExifTags.TAGS.get(k, k): v for k, v in exif.items()}
    except Exception:
        return {}


def exif_datetime(tags: dict):
    for t in DATETIME_TAGS:
        v = tags.get(t)
        if v:
            try:
                return datetime.strptime(v, "%Y:%m:%d %H:%M:%S")
            except ValueError:
                pass
    return None


def exif_camera(tags: dict):
    make = (tags.get("Make") or "").strip()
    model = (tags.get("Model") or "").strip()
    if model:
        if make and not model.lower().startswith(make.lower()):
            return f"{make} {model}".strip()
        return model
    return None


def filename_datetime(path: Path):
    stem = path.stem
    for pat in FILENAME_PATTERNS:
        m = pat.search(stem)
        if not m:
            continue
        groups = m.groups()
        try:
            if len(groups[0]) == 8:
                ymd = groups[0]
                hms = groups[1].replace("-", "").replace(".", "")
                return datetime.strptime(f"{ymd}_{hms}", "%Y%m%d_%H%M%S")
            else:
                ymd = groups[0].replace("-", "")
                hms = groups[1].replace("-", "").replace(".", "")
                return datetime.strptime(f"{ymd}_{hms}", "%Y%m%d_%H%M%S")
        except ValueError:
            continue
    return None


_FFPROBE = shutil.which("ffprobe")


def ffprobe_datetime(path: Path):
    if not _FFPROBE:
        return None
    try:
        out = subprocess.run(
            [_FFPROBE, "-v", "quiet", "-print_format", "json", "-show_format", str(path)],
            capture_output=True, text=True, timeout=10,
        )
        data = json.loads(out.stdout or "{}")
        tags = (data.get("format", {}) or {}).get("tags", {}) or {}
        for key in ("creation_time", "com.apple.quicktime.creationdate", "date"):
            v = tags.get(key)
            if not v:
                continue
            for fmt in ("%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ",
                        "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%d %H:%M:%S"):
                try:
                    dt = datetime.strptime(v[:26] if "." in v else v[:19], fmt[:19] if "." not in fmt else fmt)
                    return dt.replace(tzinfo=None)
                except ValueError:
                    continue
    except Exception:
        return None
    return None


def best_datetime(path: Path):
    suf = path.suffix.lower()
    if suf in PHOTO_EXT:
        tags = exif_data(path)
        dt = exif_datetime(tags)
        if dt:
            return dt, "exif", tags
    elif suf in VIDEO_EXT:
        dt = ffprobe_datetime(path)
        if dt:
            return dt, "ffprobe", {}
    dt = filename_datetime(path)
    if dt:
        return dt, "filename", {}
    return datetime.fromtimestamp(path.stat().st_mtime), "mtime", {}


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


def safe(name: str):
    return re.sub(r"[^\w\-. ]+", "_", name).strip()[:64] or "unknown"


def target_path(dest: Path, dt: datetime, name: str, scheme: str, camera: str | None):
    if scheme == "year-month":
        sub = Path(f"{dt.year:04d}") / f"{dt.month:02d}-{dt.strftime('%B')}"
    elif scheme == "year":
        sub = Path(f"{dt.year:04d}")
    elif scheme == "ymd":
        sub = Path(f"{dt.year:04d}") / f"{dt.month:02d}" / f"{dt.day:02d}"
    else:
        sub = Path(f"{dt.year:04d}") / f"{dt.month:02d}-{dt.strftime('%B')}"
    if camera:
        sub = Path(safe(camera)) / sub
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


def find_live_pair(path: Path):
    """If path is a HEIC/JPG with a sibling .MOV of the same stem, return the .MOV (and vice versa)."""
    stem = path.stem
    parent = path.parent
    suf = path.suffix.lower()
    if suf in {".heic", ".heif", ".jpg", ".jpeg"}:
        for ext in (".MOV", ".mov", ".mp4", ".MP4"):
            cand = parent / f"{stem}{ext}"
            if cand.exists():
                return cand
    return None


def run(args):
    src = Path(args.source).expanduser().resolve()
    dest = Path(args.dest).expanduser().resolve() if args.dest else src
    if not src.is_dir():
        sys.exit(f"source not a directory: {src}")

    seen_hashes = {} if args.dedupe else None
    paired = set()
    actions = {"moved": 0, "copied": 0, "paired": 0, "skipped_dupe": 0, "errors": 0}

    files = list(iter_media(src, args.recursive))
    total = len(files)
    if total == 0:
        print("no media files found")
        return

    manifest = None
    if args.manifest:
        manifest = csv.writer(open(args.manifest, "w", newline=""))
        manifest.writerow(["source", "target", "datetime", "datetime_source", "camera", "action"])

    for i, p in enumerate(files, 1):
        if p in paired:
            continue
        try:
            dt, source, tags = best_datetime(p)
            camera = exif_camera(tags) if args.by_camera else None
            tgt = target_path(dest, dt, p.name, args.scheme, camera)

            if seen_hashes is not None:
                h = file_hash(p)
                if h in seen_hashes:
                    actions["skipped_dupe"] += 1
                    print(f"[{i}/{total}] DUPE  {p.name} == {seen_hashes[h].name}")
                    if manifest:
                        manifest.writerow([str(p), "", dt.isoformat(), source, camera or "", "dupe"])
                    if args.delete_dupes and not args.dry_run:
                        p.unlink()
                    continue
                seen_hashes[h] = p

            tgt.parent.mkdir(parents=True, exist_ok=True)
            tgt = unique(tgt)
            verb = "COPY" if args.copy else "MOVE"
            extra = f" [{camera}]" if camera else ""
            print(f"[{i}/{total}] {verb}  {p.name} -> {tgt.relative_to(dest)}  ({source}){extra}")
            if not args.dry_run:
                if args.copy:
                    shutil.copy2(p, tgt)
                    actions["copied"] += 1
                else:
                    shutil.move(str(p), str(tgt))
                    actions["moved"] += 1
            if manifest:
                manifest.writerow([str(p), str(tgt), dt.isoformat(), source, camera or "",
                                   "copy" if args.copy else "move"])

            if args.pair_live:
                mate = find_live_pair(p)
                if mate and mate.suffix.lower() in ALL_EXT:
                    mate_tgt = tgt.parent / mate.name
                    mate_tgt = unique(mate_tgt)
                    print(f"[{i}/{total}] PAIR  {mate.name} -> {mate_tgt.relative_to(dest)}")
                    if not args.dry_run:
                        if args.copy:
                            shutil.copy2(mate, mate_tgt)
                        else:
                            shutil.move(str(mate), str(mate_tgt))
                    actions["paired"] += 1
                    paired.add(mate)
                    if manifest:
                        manifest.writerow([str(mate), str(mate_tgt), dt.isoformat(),
                                           "pair", camera or "", "pair"])
        except Exception as e:
            actions["errors"] += 1
            print(f"[{i}/{total}] ERR   {p}: {e}")

    print("\n--- summary ---")
    for k, v in actions.items():
        print(f"{k:>14}: {v}")
    if args.manifest:
        print(f"      manifest: {args.manifest}")
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
    ap.add_argument("--by-camera", action="store_true",
                    help="group by camera model (Camera/YYYY/MM-Month/) when EXIF Make/Model is present")
    ap.add_argument("--pair-live", action="store_true",
                    help="keep iPhone live-photo .MOV next to its .HEIC counterpart")
    ap.add_argument("--dedupe", action="store_true", help="skip duplicate files (by SHA-1)")
    ap.add_argument("--delete-dupes", action="store_true", help="delete duplicates from source (implies --dedupe)")
    ap.add_argument("--manifest", help="write a CSV manifest of every action to this path")
    ap.add_argument("-n", "--dry-run", action="store_true", help="preview without changing files")
    args = ap.parse_args()
    if args.delete_dupes:
        args.dedupe = True
    run(args)


if __name__ == "__main__":
    main()
