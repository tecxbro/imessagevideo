#!/usr/bin/env python3
"""Register a cleared iMessage capture, or restore its verified original bytes."""

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

import archive
from capture import (
    CONTAINERS, DATASET, IntakeError, approval, fields, file_info, git, json_bytes, parse_json,
    probe, record_digest, safe_id, sha256, validate_record, verify_span,
)

PIN = "f926ed417a128845a7912cc23edb632561f26cdd"
OBSERVER = "skill/imessage-motion-recreation/observer"
PINNED_FILES = {
    "fingerprint.py": "f53ff09567fa121b846d8fce645459a497f7a53f5a73f9b169804c71b54c5437",
    "exclusions.json": "a497a4c0e30b1bedbb31181bb4ed142a59ba9d3f693d3d7eaf4303f67cccc0f3",
    "test_fingerprint.py": "d3eaad1498e055827100b9020975f80089cc6068249f2fef107237cbb09f3870",
}
POLICY = {
    "observer_commit": PIN,
    "tool_sha256": PINNED_FILES["fingerprint.py"],
    "manifest_sha256": PINNED_FILES["exclusions.json"],
}
REGISTRY = DATASET / "registry"


class Excluded(IntakeError):
    """Observer returned a positive match."""

    def __init__(self, method):
        self.method = method


def materialize_observer(directory, *names):
    for name in names:
        result = git("show", f"{PIN}:{OBSERVER}/{name}", check=False)
        if result.returncode or hashlib.sha256(result.stdout).hexdigest() != PINNED_FILES[name]:
            raise IntakeError(f"pinned Observer files unavailable; run git fetch --no-tags origin {PIN}")
        (directory / name).write_bytes(result.stdout)


def gate(clip, digest, directory, extra=()):
    materialize_observer(directory, "fingerprint.py", "exclusions.json")
    args = [sys.executable, str(directory / "fingerprint.py"), "check", str(clip),
            "--exclusions", str(directory / "exclusions.json")]
    additions = []
    for index, path in enumerate(extra):
        copy = directory / f"extra-{index}.json"
        shutil.copyfile(path, copy)
        additions.append(file_info(copy)["sha256"])
        args.extend(("--exclusions", str(copy)))
    result = subprocess.run(args, capture_output=True)
    if result.returncode not in (0, 1):
        raise IntakeError("Observer exclusion check could not clear the candidate")
    decision = parse_json(result.stdout)
    if not isinstance(decision, dict) or decision.get("sha256") != digest:
        raise IntakeError("Observer did not verify the staged clip hash")
    if (result.returncode == 1 and decision.get("status") == "excluded"
            and decision.get("method") in ("visual", "sha256")):
        raise Excluded(decision["method"])
    count = decision.get("exclusions_checked")
    if (result.returncode or decision.get("status") != "clear"
            or type(count) is not int or count < 3 + len(additions)):
        raise IntakeError("Observer exclusion check could not clear the candidate")
    return {**POLICY, "status": "clear", "exclusions_checked": count, "extra_sha256": additions}


def register(args):
    record = parse_json(args.record.read_bytes())
    validate_record(record)
    suffix = args.clip.suffix.lower()
    if suffix not in CONTAINERS or not args.clip.is_file():
        raise IntakeError("candidate must be a local MP4, MOV, MKV or WebM file")
    # Verify and archive the same snapshot even if the submitter replaces the original.
    with tempfile.TemporaryDirectory(prefix="imessage-intake-") as temporary:
        scratch = Path(temporary)
        clip = scratch / f"clip{suffix}"
        shutil.copyfile(args.clip, clip)
        info = file_info(clip)
        if info["sha256"] != record["media_sha256"]:
            raise IntakeError("candidate SHA-256 differs from the record")
        decision = gate(clip, info["sha256"], scratch, args.extra_exclusions)
        media = verify_span(clip, record)
        grant = approval(record)
        manifest = {
            "schema_version": 1, "capture": record, "record_sha256": record_digest(record),
            "approval": grant, "exclusion_check": decision, "media": {"name": clip.name, **info, **media},
        }
        registry = args.registry.resolve()
        registry.mkdir(parents=True, exist_ok=True)
        target = registry / record["id"]
        with tempfile.TemporaryDirectory(prefix=".intake-", dir=registry) as transaction:
            staged = Path(transaction) / "entry"
            staged.mkdir()
            manifest["archive"] = archive.create(staged, clip, record)
            (staged / "manifest.json").write_bytes(json_bytes(manifest))
            try:
                if target.exists() or target.is_symlink():
                    raise FileExistsError(target)
                staged.rename(target)
            except OSError:
                if not target.is_dir() or archive.read_manifest(target) != manifest:
                    raise IntakeError("could not publish registry entry; the id may already be in use") from None
                verify_registry_files(target, manifest)
    print(json.dumps({"status": "registered", "id": record["id"], "media_sha256": info["sha256"],
                      "archive_sha256": manifest["archive"]["sha256"]}))


def verify_registry_files(entry, manifest):
    for part in archive.part_layout(manifest["archive"]):
        path = entry / part["name"]
        if path.is_symlink() or not path.is_file() or file_info(path) != {
            "sha256": part["sha256"], "bytes": part["bytes"],
        }:
            raise IntakeError("existing registry archive differs from the registered hashes")


def restore(args):
    capture_id = safe_id(args.id)
    entry = args.registry.resolve() / capture_id
    manifest = archive.read_manifest(entry)
    fields(manifest, "schema_version capture record_sha256 approval exclusion_check media archive", "manifest")
    record = manifest["capture"]
    validate_record(record)
    if (type(manifest["schema_version"]) is not int or manifest["schema_version"] != 1
            or record["id"] != capture_id or record_digest(record) != manifest["record_sha256"]):
        raise IntakeError("registered capture identity or record hash mismatch")
    if approval(record) != manifest["approval"]:
        raise IntakeError("registered approval differs from the committed approval")

    receipt = manifest["exclusion_check"]
    fields(receipt, "observer_commit tool_sha256 manifest_sha256 status exclusions_checked extra_sha256", "gate receipt")
    if receipt["status"] != "clear" or any(receipt[key] != value for key, value in POLICY.items()):
        raise IntakeError("registration lacks a clear decision from the pinned gate")
    extras = receipt["extra_sha256"]
    count = receipt["exclusions_checked"]
    if not isinstance(extras, list) or type(count) is not int or count < 3 + len(extras):
        raise IntakeError("invalid exclusion check counts")
    for digest in extras:
        sha256(digest, "additional exclusion manifest hash")

    output = args.out.absolute()
    if output.exists() or output.is_symlink():
        raise IntakeError("restore output already exists")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".restore-", dir=output.parent) as temporary:
        scratch = Path(temporary)
        staged = scratch / "restored"
        staged.mkdir()
        clip = archive.restore(entry, manifest, staged)
        digest = file_info(clip)["sha256"]
        if digest != record["media_sha256"]:
            raise IntakeError("archived video differs from approved capture hash")
        media = verify_span(clip, record)
        if any(manifest["media"][name] != actual for name, actual in media.items()):
            raise IntakeError("archived video clock differs from the registered clock")
        gate(clip, digest, scratch)
        (staged / "manifest.json").write_bytes(json_bytes(manifest))
        staged.rename(output)
    print(json.dumps({"status": "restored", "id": capture_id, "media_sha256": digest,
                      "archive_sha256": manifest["archive"]["sha256"]}))


def inspect(args):
    metadata, pts = probe(args.clip)
    result = {**file_info(args.clip), **metadata}
    if args.frames is not None:
        start, end = args.frames
        if not 0 <= start <= end < len(pts):
            raise IntakeError("requested frames are outside the decoded video")
        result["range"] = {"start_frame": start, "end_frame": end, "start_pts": pts[start], "end_pts": pts[end]}
    print(json_bytes(result).decode(), end="")


def describe(args):
    record = parse_json(args.record.read_bytes())
    validate_record(record)
    print(record_digest(record))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(required=True)
    ingest = commands.add_parser("register", help="check and register a candidate")
    ingest.add_argument("clip", type=Path)
    ingest.add_argument("record", type=Path)
    ingest.add_argument("--registry", type=Path, default=REGISTRY)
    ingest.add_argument("--extra-exclusions", type=Path, action="append", default=[])
    ingest.set_defaults(run=register)
    recover = commands.add_parser("restore", help="verify and restore a registered capture")
    recover.add_argument("id")
    recover.add_argument("--out", type=Path, required=True)
    recover.add_argument("--registry", type=Path, default=REGISTRY)
    recover.set_defaults(run=restore)
    info = commands.add_parser("probe", help="print decoded media metadata and an optional frame range")
    info.add_argument("clip", type=Path)
    info.add_argument("--frames", nargs=2, type=int, metavar=("START", "END"))
    info.set_defaults(run=inspect)
    record_hash = commands.add_parser("record-sha256", help="validate a record and print its canonical digest")
    record_hash.add_argument("record", type=Path)
    record_hash.set_defaults(run=describe)
    args = parser.parse_args()
    try:
        args.run(args)
    except Excluded as error:
        print(json.dumps({"status": "excluded", "method": error.method}))
        return 1
    except (IntakeError, OSError, ValueError, zipfile.BadZipFile) as error:
        # Filesystem errors can contain private input paths.
        message = str(error) if isinstance(error, IntakeError) else "invalid or unavailable input, record or archive"
        print(f"blocked: {message}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
