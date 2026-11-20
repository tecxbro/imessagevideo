"""Store verified capture bytes in a deterministic ZIP and verify each restore."""

import shutil
import stat
import tempfile
import zipfile
from pathlib import Path

from capture import BUFFER, CONTAINERS, IntakeError, file_info, fields, json_bytes, parse_json, sha256

PART_SIZE = 24 * 1024 * 1024


def create(directory, clip, record):
    whole = directory / "archive.zip"
    member = zipfile.ZipInfo(clip.name)
    member.file_size = clip.stat().st_size
    with zipfile.ZipFile(whole, "w") as archive:
        with clip.open("rb") as source, archive.open(member, "w", force_zip64=True) as output:
            shutil.copyfileobj(source, output, BUFFER)
        archive.writestr(zipfile.ZipInfo("capture.json"), json_bytes(record))

    info = file_info(whole)
    parts = []
    if info["bytes"] <= PART_SIZE:
        parts.append({"name": whole.name, **info})
    else:
        with whole.open("rb") as source:
            for index in range(1, (info["bytes"] + PART_SIZE - 1) // PART_SIZE + 1):
                part = directory / f"archive.zip.part{index:03d}"
                part.write_bytes(source.read(PART_SIZE))
                parts.append({"name": part.name, **file_info(part)})
        whole.unlink()
    return {**info, "parts": parts}


def part_layout(archive):
    fields(archive, "bytes sha256 parts", "archive")
    sha256(archive["sha256"], "archive.sha256")
    total = archive["bytes"]
    parts = archive["parts"]
    if type(total) is not int or total < 1 or not isinstance(parts, list):
        raise IntakeError("invalid archive size or parts")
    count = (total + PART_SIZE - 1) // PART_SIZE
    if len(parts) != count:
        raise IntakeError("incorrect number of archive parts")
    for index, part in enumerate(parts, start=1):
        fields(part, "name bytes sha256", "archive part")
        expected_name = "archive.zip" if count == 1 else f"archive.zip.part{index:03d}"
        if part["name"] != expected_name or type(part["bytes"]) is not int:
            raise IntakeError("invalid archive part name or size")
        if part["bytes"] != min(PART_SIZE, total - (index - 1) * PART_SIZE):
            raise IntakeError("invalid archive part size")
        sha256(part["sha256"], "part.sha256")
    return parts


def restore(directory, manifest, target):
    archive = manifest["archive"]
    parts = part_layout(archive)
    media = manifest["media"]
    fields(media, "name bytes sha256 clock frame_count width height landmark_pts", "media")
    if media["name"] not in {f"clip{suffix}" for suffix in CONTAINERS}:
        raise IntakeError("invalid archived clip name")

    with tempfile.TemporaryDirectory(prefix="join-", dir=target.parent) as temporary:
        joined = Path(temporary) / "archive.zip"
        with joined.open("wb") as output:
            for part in parts:
                source = directory / part["name"]
                expected = {"bytes": part["bytes"], "sha256": part["sha256"]}
                if source.is_symlink() or not source.is_file() or file_info(source) != expected:
                    raise IntakeError("archive part is missing or has a size or hash mismatch")
                with source.open("rb") as handle:
                    shutil.copyfileobj(handle, output, BUFFER)
        if file_info(joined) != {"bytes": archive["bytes"], "sha256": archive["sha256"]}:
            raise IntakeError("joined archive size or hash mismatch")

        with zipfile.ZipFile(joined) as bundle:
            names = sorted(bundle.namelist())
            if names != ["capture.json", media["name"]]:
                raise IntakeError("archive must contain exactly the clip and capture record")
            for item in bundle.infolist():
                if stat.S_ISLNK(item.external_attr >> 16):
                    raise IntakeError("archive contains a symlink")
            record_bytes = json_bytes(manifest["capture"])
            if bundle.getinfo("capture.json").file_size != len(record_bytes):
                raise IntakeError("archived capture record size mismatch")
            if bundle.read("capture.json") != record_bytes:
                raise IntakeError("archived capture record differs from the registered record")
            if bundle.getinfo(media["name"]).file_size != media["bytes"]:
                raise IntakeError("archived clip size mismatch")
            clip = target / media["name"]
            with bundle.open(media["name"]) as source, clip.open("wb") as output:
                shutil.copyfileobj(source, output, BUFFER)
            if file_info(clip) != {"bytes": media["bytes"], "sha256": media["sha256"]}:
                raise IntakeError("archived clip size or hash mismatch")
            (target / "capture.json").write_bytes(record_bytes)
    return clip


def read_manifest(directory):
    path = directory / "manifest.json"
    if directory.is_symlink() or path.is_symlink():
        raise IntakeError("registry entry must use ordinary files")
    return parse_json(path.read_bytes())
