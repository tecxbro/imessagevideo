#!/usr/bin/env python3
"""Build and verify a reproducible skill ZIP and its SHA-256 manifest."""
import argparse
from hashlib import file_digest
import hmac
import json
import os
from pathlib import Path, PurePosixPath
import tempfile
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[1]
SKILL = "imessage-motion-recreation"
CHECKSUMS = "checksums.json"
SKIP_DIRS = {".cache", ".git", ".pytest_cache", ".venv", "__pycache__", "node_modules", "venv"}
SKIP_FILES = {".DS_Store", CHECKSUMS}
LOCAL_ONLY = {"observer/exclusions.json"}
EXTERNAL_SUFFIXES = {".mp4", ".mov", ".mp3", ".m4a", ".wav", ".flac", ".ogg", ".ttf", ".otf", ".woff", ".woff2"}
SYNTHETIC_PICTURE_FIXTURES = {"sound/fixtures/picture.mp4", "sound/fixtures/revised.mp4"}
FROZEN = {
    "imessage-motion-recreation-skill.zip",
    "imessage-motion-recreation-skill-public-update.zip",
    "imessage-motion-recreation-with-ui-audio-skill.zip",
    "imessage-motion-recreation-ui-audio-final-skill.zip",
}


def skill_files(root):
    files = {}
    for directory, subdirs, names in os.walk(root):
        subdirs[:] = sorted(set(subdirs) - SKIP_DIRS)
        current = Path(directory)
        for name in subdirs:
            if (current / name).is_symlink():
                raise ValueError(f"symlink in skill: {(current / name).relative_to(root)}")
        for name in names:
            if name in SKIP_FILES or name.endswith((".pyc", ".tmp")):
                continue
            path = current / name
            relative = path.relative_to(root).as_posix()
            if path.is_symlink() or not path.is_file():
                raise ValueError(f"invalid mounted file in skill: {relative}")
            if relative in LOCAL_ONLY:
                continue
            if path.suffix.lower() in EXTERNAL_SUFFIXES and relative not in SYNTHETIC_PICTURE_FIXTURES:
                raise ValueError(f"put media and fonts in the editable project bundle: {relative}")
            files[relative] = path
    return dict(sorted(files.items()))


def file_hash(path):
    with path.open("rb") as descriptor:
        return file_digest(descriptor, "sha256").hexdigest()


def safe_name(name):
    path = PurePosixPath(name)
    return (not path.is_absolute() and path.as_posix() == name and len(path.parts) >= 2
            and path.parts[0] == SKILL and ".." not in path.parts and "\\" not in name)


def verify(out):
    with ZipFile(out) as archive:
        names = archive.namelist()
        manifest = f"{SKILL}/{CHECKSUMS}"
        if len(set(names)) != len(names) or not all(map(safe_name, names)):
            raise ValueError("unexpected duplicate or nonportable ZIP path")
        if bad := archive.testzip():
            raise ValueError(f"corrupt ZIP member: {bad}")
        hashes = json.loads(archive.read(manifest))
        if set(names) != {f"{SKILL}/{name}" for name in hashes} | {manifest}:
            raise ValueError("ZIP contents differ from the checksum manifest")
        for name, expected in hashes.items():
            with archive.open(f"{SKILL}/{name}") as member:
                digest = file_digest(member, "sha256").hexdigest()
            if not hmac.compare_digest(digest, expected):
                raise ValueError(f"checksum mismatch: {name}")
    return {"path": str(out), "sha256": file_hash(out), "files": len(names), "bytes": out.stat().st_size}


def make_zip(out):
    if out.name in FROZEN or out.suffix != ".zip" or out.is_relative_to(ROOT):
        raise ValueError("choose a new .zip file outside the skill directory")
    files = skill_files(ROOT)
    checksums = json.dumps({name: file_hash(path) for name, path in files.items()}, indent=2) + "\n"
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=out.parent, suffix=".zip", delete=False) as handle:
        temp = Path(handle.name)
    staged_manifest = ROOT / f".checksums-{os.getpid()}.tmp"
    try:
        with ZipFile(temp, "w", ZIP_DEFLATED, compresslevel=6) as archive:
            for name, path in {**files, CHECKSUMS: None}.items():
                info = ZipInfo(f"{SKILL}/{name}", (2020, 1, 1, 0, 0, 0))
                info.create_system = 3
                info.external_attr = (0o100755 if path and path.stat().st_mode & 0o111 else 0o100644) << 16
                data = path.read_bytes() if path else checksums.encode()
                archive.writestr(info, data, compress_type=ZIP_DEFLATED, compresslevel=6)
        result = verify(temp)
        staged_manifest.write_text(checksums, encoding="utf-8")
        staged_manifest.replace(ROOT / CHECKSUMS)
        temp.replace(out)
        return {**result, "path": str(out)}
    finally:
        temp.unlink(missing_ok=True)
        staged_manifest.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--out", type=Path, help="build a new archive and refresh the loose checksums")
    mode.add_argument("--verify", type=Path, help="check the full contents of an existing archive")
    args = parser.parse_args()
    try:
        result = make_zip(args.out.resolve()) if args.out else verify(args.verify.resolve())
    except (ValueError, OSError, KeyError) as exc:
        parser.exit(1, f"{exc}\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
