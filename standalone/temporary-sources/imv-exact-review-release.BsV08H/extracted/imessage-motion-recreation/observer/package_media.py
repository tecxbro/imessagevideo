#!/usr/bin/env python3
"""Build the portable media companion from verified release files."""
import argparse
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
from tempfile import TemporaryDirectory
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

from package import ROOT, file_hash

REPO = ROOT.parents[1]
REVIEW = PurePosixPath("review/imv-v3")
MOTION = REVIEW / "motion"
MANIFEST = "MEDIA-SHA256SUMS"
MEDIA_FILES = (
    "direction/the-moon-cue.mp4",
    "recreate/train/scored.mp4",
    "observer/PORTABLE.md",
    "observer/the-moon-cue-editable-project.zip",
    "observer/train-options-editable-project.zip",
    "observer/evidence/direction-lock-strip.png",
    "observer/evidence/recreation-contact-sheet.png",
    "observer/evidence/interaction-edit-strip.png",
    "observer/interaction-edit/interaction.mp4",
    "observer/interaction-edit/conversation.json",
    "observer/interaction-edit/events.json",
    "ui/station-pillow.mp4",
    "ui/station-pillow-consecutive.jpg",
    "sound/recreation/assets/drawer-glide.wav",
    "sound/recreation/assets/drawer.png",
    "sound/recreation/assets/receipt-resolve.wav",
    "sound/recreation/assets/receipt.png",
    "sound/recreation/assets/seat-latch.wav",
    "sound/recreation/assets/send-flick.wav",
)
PROOF_BUNDLES = ("motion/v3.2", "ui/sequences", "sound/recreation/owner-retime")


def media_path(name, parent):
    relative = PurePosixPath(name)
    if (relative.as_posix() != name or "\\" in name or ".." in relative.parts
            or not relative.is_relative_to(parent)):
        raise ValueError(f"unexpected media path: {name}")
    path = REPO / relative
    if not path.is_file() or path.resolve() != path:
        raise ValueError(f"missing or linked media file: {name}")
    return path


def collect():
    files = {}
    for name in MEDIA_FILES:
        relative = (REVIEW / name).as_posix()
        files[relative] = media_path(relative, REVIEW)
    for name in PROOF_BUNDLES:
        bundle = REVIEW / name
        ledger = media_path((bundle / "SHA256SUMS").as_posix(), bundle)
        for line in ledger.read_text().splitlines():
            expected, member = line.split("  ", 1)
            relative = (bundle / member).as_posix()
            path = media_path(relative, bundle)
            if file_hash(path) != expected:
                raise ValueError(f"proof checksum differs: {relative}")
            if path.suffix != ".md":
                files[relative] = path
    catalog = json.loads((ROOT / "motion/catalog.json").read_text())
    for entry in catalog["entries"]:
        for example in (entry, entry.get("ui")):
            if example is None:
                continue
            preview = media_path(example["preview"], MOTION)
            event_map = media_path(example["eventMap"], MOTION)
            if file_hash(preview) != example["sha256"]:
                raise ValueError(f"preview checksum differs from catalog: {preview.name}")
            resolved = json.loads(event_map.read_text())
            if any(resolved["picture"][key] != value for key, value in example["picture"].items()):
                raise ValueError(f"picture clock differs from catalog: {event_map.name}")
            events = [{key: event[key] for key in ("id", "kind", "frame")} for event in resolved["events"]]
            if events != example["events"]:
                raise ValueError(f"events differ from catalog: {event_map.name}")
            files[example["preview"]] = preview
            files[example["eventMap"]] = event_map
    return dict(sorted(files.items()))


def add(archive, name, data):
    entry = ZipInfo(name, (2020, 1, 1, 0, 0, 0))
    entry.create_system = 3
    entry.external_attr = 0o100644 << 16
    archive.writestr(entry, data, compress_type=ZIP_DEFLATED, compresslevel=6)


def build(out):
    if out.suffix != ".zip" or out.is_relative_to(ROOT):
        raise ValueError("choose a .zip file outside the skill directory")
    files = collect()
    out.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=out.parent) as staging:
        staged = Path(staging) / out.name
        with ZipFile(staged, "w") as archive:
            checksums = []
            for name, path in files.items():
                data = path.read_bytes()
                add(archive, name, data)
                checksums.append(f"{sha256(data).hexdigest()}  {name}\n")
            add(archive, MANIFEST, "".join(checksums).encode())
        with ZipFile(staged) as archive:
            if bad := archive.testzip():
                raise ValueError(f"corrupt ZIP member: {bad}")
        staged.replace(out)
    return {"path": str(out), "sha256": file_hash(out), "files": len(files) + 1, "bytes": out.stat().st_size}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = build(args.out.resolve())
    except (KeyError, OSError, ValueError) as exc:
        parser.exit(1, f"{exc}\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
