# Changelog

## v2.0.0 — 2026-04-28

- **Live-photo pairing** (`--pair-live`): iPhone `.HEIC` + `.MOV` siblings are
  filed together in the same destination folder.
- **Video creation date via ffprobe**: when `ffprobe` is on PATH, video files
  use real container `creation_time` instead of falling back to filename/mtime.
- **CSV manifest** (`--manifest path.csv`): writes a row per action for
  auditing — source, target, datetime, source-of-date, camera, action.
- **Group by camera** (`--by-camera`): nests output as
  `Camera Model/YYYY/MM-Month/...` when EXIF Make/Model is present.
- **More filename patterns**: `IMG_`, `VID_`, `MVI_`, `PXL_`, `DSC_`, `DSCN_`,
  `DSCF_`, `GOPR_`, `GH*_`, dashed and dotted variants.

## v1.0.0 — 2026-04-27

- Initial release: EXIF/filename/mtime-based sorting into `YYYY/MM-Month/`.
