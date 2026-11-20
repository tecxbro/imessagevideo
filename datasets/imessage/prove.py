#!/usr/bin/env python3
"""Exercise the gate, intake, and restore from a clean Git worktree."""

import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

import archive
from capture import DATASET, ROOT, IntakeError, file_info, git, json_bytes, parse_json, probe
from intake import PIN, materialize_observer

REL_DATASET = DATASET.relative_to(ROOT)
REL_REVIEW = Path("review/imv-v3/dataset")
FIXTURE = "qa-state-markers"


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def run(*args, cwd=ROOT, expected=0):
    result = subprocess.run(args, cwd=cwd, capture_output=True)
    require(result.returncode == expected, f"expected exit {expected}, got {result.returncode}: "
            f"{result.stderr.decode(errors='replace').strip() or result.stdout.decode(errors='replace').strip()}")
    return result


def intake(root, *args, expected=0):
    return run(sys.executable, str(REL_DATASET / "intake.py"), *args, cwd=root, expected=expected)


def register(clip, record, registry, *flags, expected=0):
    return intake(ROOT, "register", clip, record, "--registry", registry, *flags, expected=expected)


def write_case(directory, label, record):
    path = directory / f"{label}.json"
    path.write_bytes(json_bytes(record))
    return path


def make_excluded(directory):
    source = directory / "control.mp4"
    transformed = directory / "transformed.mp4"
    policy = directory / "fixture-exclusions.json"
    materialize_observer(directory, "fingerprint.py", "test_fingerprint.py")
    # Use the pinned fixture authoring routine to reproduce Observer's control.
    spec = importlib.util.spec_from_file_location("observer_fixture", directory / "test_fingerprint.py")
    fixture = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fixture)
    fixture.generate_film(source)
    run(sys.executable, directory / "fingerprint.py", "fingerprint", source, "--output", policy)
    run("ffmpeg", "-v", "error", "-i", source, "-vf", "scale=192:288,fps=30", "-an",
        "-c:v", "libx264", "-threads", "1", "-crf", "31", "-pix_fmt", "yuv420p", transformed)
    require(file_info(source)["sha256"] != file_info(transformed)["sha256"], "control was not transformed")
    return transformed, policy


def rejection_controls(scratch, record, clip, record_file):
    blocked_registry = scratch / "blocked"
    candidate, extra = make_excluded(scratch)
    transformed = copy.deepcopy(record)
    metadata, pts = probe(candidate)
    transformed.update(id="qa-transformed-control", media_sha256=file_info(candidate)["sha256"],
                       clock=metadata["clock"])
    transformed["range"].update(end_frame=len(pts) - 1, start_pts=pts[0], end_pts=pts[-1])
    candidate_record = write_case(scratch, "transformed-record", transformed)
    result = register(candidate, candidate_record, blocked_registry, "--extra-exclusions", extra, expected=1)
    require(parse_json(result.stdout) == {"status": "excluded", "method": "visual"},
            "intake did not return a private visual exclusion")
    print("PASS transformed exclusion · visual match, exit 1")

    missing = copy.deepcopy(record)
    del missing["rights"]
    bad_hash = {**record, "media_sha256": "0" * 64}
    bad_time = copy.deepcopy(record)
    bad_time["range"]["start_pts"] += 1
    cases = [
        ("incomplete", missing, "record must contain exactly"),
        ("wrong-media", bad_hash, "candidate SHA-256 differs"),
        ("wrong-pts", bad_time, "start PTS does not match"),
        ("unreviewed", {**record, "id": "qa-unreviewed"}, "no committed source and rights approval"),
        ("stale-grant", {**record, "source": {**record["source"], "method": "Changed claim"}},
         "committed approval does not match"),
    ]
    for label, invalid, message in cases:
        result = register(clip, write_case(scratch, label, invalid), blocked_registry, expected=2)
        require(message.encode() in result.stderr, f"{label} was blocked for the wrong reason")
        print(f"PASS {label} · blocked, exit 2")
    malformed = scratch / "malformed-exclusions.json"
    malformed.write_text("{")
    result = register(clip, record_file, blocked_registry, "--extra-exclusions", malformed, expected=2)
    require(b"exclusion check could not clear" in result.stderr, "gate error was not fail-closed")
    require(not blocked_registry.exists(), "a blocked candidate created registry files")
    print("PASS malformed exclusion manifest · blocked without creating a registry")


def verify_fixture_picture(path):
    frames = (0, 47, 48, 95, 96, 191)
    expression = "+".join(f"eq(n\\,{frame})" for frame in frames)
    raw = run("ffmpeg", "-v", "error", "-xerror", "-i", path, "-vf", f"select={expression}",
              "-fps_mode", "passthrough", "-pix_fmt", "rgb24", "-threads", "1", "-f", "rawvideo", "-").stdout
    size = (320, 480)
    stride = size[0] * size[1] * 3
    require(len(raw) == len(frames) * stride, "fixture landmark frame decode failed")
    for index, frame in enumerate(frames):
        pixels = Image.frombytes("RGB", size, raw[index * stride:(index + 1) * stride])
        x, y, expected = (
            (120, 160, (112, 134, 145)) if frame < 48 else
            (120, 220, (199, 101, 63)) if frame < 96 else
            (120, 285, (66, 120, 84))
        )
        actual = pixels.getpixel((x, y))
        require(max(abs(a - b) for a, b in zip(actual, expected)) <= 5, f"wrong marker at frame {frame}")


def prove_split(scratch, clip, manifest):
    # Exercise the exact multipart path with a small limit so CI can run it every week.
    previous_limit = archive.PART_SIZE
    archive.PART_SIZE = 2048
    try:
        store = scratch / "split"
        store.mkdir()
        candidate = store / manifest["media"]["name"]
        candidate.write_bytes(clip.read_bytes())
        meta = {**manifest, "archive": archive.create(store, candidate, manifest["capture"])}
        parts = meta["archive"]["parts"]
        require(len(parts) > 1, "multipart control did not split")
        target = scratch / "split-restore"
        target.mkdir()
        require(file_info(archive.restore(store, meta, target)) == file_info(clip), "split restore changed the bytes")
        part = store / parts[0]["name"]
        part.write_bytes(b"X" + part.read_bytes()[1:])
        try:
            archive.restore(store, meta, target)
        except IntakeError as error:
            require("archive part" in str(error), "corrupt part was blocked for the wrong reason")
        else:
            raise RuntimeError("corrupt part was accepted")
        print("PASS multipart archive reassembly and corrupt-part rejection")
    finally:
        archive.PART_SIZE = previous_limit


def restore_in_clean_worktree(scratch, expected):
    clean = scratch / "checkout"
    git("worktree", "add", "--detach", "--no-checkout", str(clean), "HEAD")
    try:
        run("git", "sparse-checkout", "set", str(REL_DATASET), str(REL_REVIEW), cwd=clean)
        run("git", "reset", "--hard", "HEAD", cwd=clean)
        require(not run("git", "status", "--porcelain", cwd=clean).stdout, "restore checkout is dirty")
        registry = clean / REL_DATASET / "registry"
        entries = sorted(path for path in registry.iterdir() if path.is_dir())
        require(any(path.name == FIXTURE for path in entries), "committed fixture archive is missing")
        for entry in entries:
            out = scratch / f"restore-{entry.name}"
            result = intake(clean, "restore", entry.name, "--out", out)
            receipt = parse_json(result.stdout)
            require(receipt["status"] == "restored", "unexpected restore result")
            if entry.name == FIXTURE:
                require(receipt == {**expected, "status": "restored"}, "clean restore differs from new registration")
                clip = out / "clip.mp4"
                require(file_info(clip) == file_info(clean / REL_REVIEW / f"{FIXTURE}.mp4"),
                        "restored clip differs from the authorized fixture")
                verify_fixture_picture(clip)
                intake(clean, "restore", entry.name, "--out", out, expected=2)
            print(f"PASS clean restore · {entry.name} · {receipt['media_sha256']}")
        require(not run("git", "status", "--porcelain", cwd=clean).stdout, "restore modified the clean checkout")
    finally:
        git("worktree", "remove", "--force", str(clean))


def main():
    if git("cat-file", "-e", f"{PIN}^{{commit}}", check=False).returncode:
        git("fetch", "--depth=1", "--no-tags", "origin", PIN)
    fixture = ROOT / REL_REVIEW / FIXTURE
    clip, record_file = fixture.with_suffix(".mp4"), fixture.with_suffix(".json")
    record = parse_json(record_file.read_bytes())

    with tempfile.TemporaryDirectory(prefix="imessage-intake-proof-") as temp:
        scratch = Path(temp)
        rejection_controls(scratch, record, clip, record_file)
        registry = scratch / "new-registry"
        first = register(clip, record_file, registry)
        second = register(clip, record_file, registry)
        require(first.stdout == second.stdout, "retry changed the registration")
        receipt = parse_json(first.stdout)
        require(receipt["status"] == "registered", "authorized sample did not register")
        manifest_path = registry / FIXTURE / "manifest.json"
        committed = DATASET / "registry" / FIXTURE / "manifest.json"
        require(manifest_path.read_bytes() == committed.read_bytes(), "registration differs from committed manifest")
        print(f"PASS authorized registration and retry · archive {receipt['archive_sha256']}")
        prove_split(scratch, clip, parse_json(manifest_path.read_bytes()))
        restore_in_clean_worktree(scratch, receipt)


if __name__ == "__main__":
    try:
        main()
    except (IntakeError, OSError, RuntimeError, subprocess.CalledProcessError) as error:
        sys.exit(f"FAIL intake proof: {error}")
