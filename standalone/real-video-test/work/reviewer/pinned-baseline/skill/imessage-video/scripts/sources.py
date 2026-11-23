#!/usr/bin/env python3
"""Identify source films and remember explicitly verified work. Python 3.10+, FFmpeg."""
import argparse
import fcntl
import hashlib
import json
import math
from fractions import Fraction
import os
from pathlib import Path
import re
import subprocess
import tempfile

SEEDS = Path(__file__).resolve().parents[1] / "assets" / "known-films.json"
SAMPLE_RATE = 2
ID = re.compile(r"[a-z0-9][a-z0-9._-]{0,95}\Z")
HEX = re.compile(r"[a-f0-9]{64}\Z")


def sha256(path):
    with Path(path).open("rb") as stream:
        digest = hashlib.sha256()
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
        return digest.hexdigest()


def signature(frame):
    # Each 9-by-8 picture supplies two independent 64-bit descriptions.
    pixels = [value for i, value in enumerate(frame) if i % 9 != 8]
    level = sum(pixels) // 64
    if max(pixels) - min(pixels) < 23:
        return None
    shape = gradient = 0
    for y in range(8):
        for x in range(8):
            i = y * 9 + x
            shape = (shape << 1) | (frame[i] > level)
            gradient = (gradient << 1) | (frame[i] > frame[i + 1] + 2)
    return f"{shape:016x}{gradient:016x}{level:02x}"


def fingerprint(path):
    # The raw stream is only 144 bytes per second of footage. Normalize source PTS.
    command = ["ffmpeg", "-nostdin", "-v", "error", "-xerror", "-threads", "1",
               "-i", str(Path(path).resolve()), "-map", "0:v:0", "-an", "-sn", "-dn",
               "-vf", f"setpts=PTS-STARTPTS,fps={SAMPLE_RATE},scale=9:8:flags=area,format=gray",
               "-filter_threads", "1", "-threads", "1", "-f", "rawvideo", "pipe:1"]
    raw = subprocess.run(command, capture_output=True)
    if raw.returncode:
        raise ValueError(f"Cannot fingerprint {path}: {raw.stderr.decode(errors='replace').strip()}")
    if len(raw.stdout) % 72:
        raise ValueError("Incomplete decoded sample")
    return [signature(raw.stdout[i:i + 72]) for i in range(0, len(raw.stdout), 72)]


def decode(series):
    return [(int(s[:16], 16), int(s[16:32], 16), int(s[32:], 16)) if s else None for s in series]


def close(a, b, tolerance=5):
    return (a is not None and b is not None and abs(a[2] - b[2]) <= 10
            and (a[0] ^ b[0]).bit_count() <= tolerance
            and (a[1] ^ b[1]).bit_count() <= tolerance)


def visual_match(query, reference):
    # Votes for a constant time displacement. Repeated/flat shots alone cannot qualify.
    offsets = {}
    for qi, a in enumerate(query):
        if a is None:
            continue
        for ri, b in enumerate(reference):
            if close(a, b):
                offsets.setdefault(ri - qi, []).append(qi)
    best = None
    for offset, indices in offsets.items():
        if len(indices) < 5:
            continue
        # Split where a match disappears for over 1.5s, e.g. an inserted cut.
        segments = [[]]
        for index in indices:
            if segments[-1] and index - segments[-1][-1] > 3:
                segments.append([])
            segments[-1].append(index)
        for segment in segments:
            if len(segment) < 5 or segment[-1] - segment[0] < 4:
                continue
            window = segment[-1] - segment[0] + 1
            if len(segment) / window < .60:
                continue
            distinct = []
            for q in segment:
                if all(not close(query[q], seen, tolerance=9) for seen in distinct):
                    distinct.append(query[q])
                if len(distinct) == 3:
                    break
            if len(distinct) < 3 or sum(query[q][1].bit_count() >= 6 for q in segment) < 2:
                continue
            if best is None or len(segment) > best["matched_samples"]:
                best = {"kind": "visual-sequence", "matched_samples": len(segment),
                        "input_seconds": [segment[0] / SAMPLE_RATE, (segment[-1] + 1) / SAMPLE_RATE],
                        "catalog_seconds": [(segment[0] + offset) / SAMPLE_RATE,
                                            (segment[-1] + offset + 1) / SAMPLE_RATE],
                        "audio_compared": False}
    return best


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def records(library):
    indexed = {film["id"]: film for film in read_json(SEEDS)["films"]}
    for path in sorted((library / "films").glob("*.json")):
        saved = read_json(path)
        existing = indexed.get(saved["id"])
        if existing and saved["sha256"] != existing["sha256"]:
            raise ValueError(f"Conflicting identities for {saved['id']}")
        indexed[saved["id"]] = saved
    return list(indexed.values())


def library_root(override):
    return Path(override or os.environ.get("IMESSAGE_VIDEO_MOTION_LIBRARY")
                or SEEDS.parent / "library").expanduser().resolve()


def identify(video_path, library_path=None):
    library = library_root(library_path)
    digest = sha256(video_path)
    films = records(library)
    matches = [(film, {"kind": "sha256", "sha256": digest}) for film in films if film["sha256"] == digest]
    status = "known" if len(matches) == 1 else "candidate"
    if not matches:
        query = decode(fingerprint(video_path))
        for film in films:
            evidence = visual_match(query, decode(film["fingerprint"]))
            if evidence:
                matches.append((film, evidence))
        matches.sort(key=lambda pair: -pair[1]["matched_samples"])
        status = "candidate" if matches else "new"
    result = []
    for film, evidence in matches:
        row = {k: film.get(k) for k in ("id", "title", "source", "editable_project", "reconstruction", "recipe_ids")}
        if film.get("archived"):
            row["archived"] = film["archived"]
        row["evidence"] = evidence
        row["seed_bindings"] = []
        for token in film.get("seed_bindings", []):
            try:
                binding = verified_binding(library, token, digest=film["sha256"])
                row["seed_bindings"].append({key: binding[key] for key in
                                            ("token", "recipe_id", "frames", "crop", "rois", "evidence")})
            except (ValueError, KeyError, OSError):
                row.setdefault("unavailable_seed_bindings", []).append(token)
        row["coverage"] = coverage(film, library, row["seed_bindings"])
        row["recipe_ids"] = sorted(set(row["recipe_ids"]) | {b["recipe_id"] for b in row["seed_bindings"]})
        if evidence["kind"] == "visual-sequence":
            row["next"] = "Align the input and catalog windows, compare adjacent frames, and check audio before reusing matched coverage."
        elif row["coverage"] == "archived-reconstruction":
            row["next"] = "Open the saved scene and master, restore large scene data if needed, then compare against this brief before rebuilding."
        elif row["coverage"] == "verified-local-reconstruction":
            row["next"] = "Inspect the verified local master and editable project for the requested changes."
        elif row["coverage"] == "verified-recipes-only":
            row["next"] = "Reuse the measured recipe spans and measure the rest of this film."
        else:
            row["next"] = "Recover or re-verify the associated artifacts before reuse."
        result.append(row)
    return {"status": status, "sha256": digest, "matches": result}


def library_file(library, name):
    if not isinstance(name, str) or not name or Path(name).is_absolute():
        raise ValueError("Artifact paths must be relative to the motion library")
    path = (library / name).resolve()
    if not path.is_relative_to(library) or not path.is_file():
        raise ValueError(f"Missing library artifact: {name}")
    return path


def checked_artifact(library, descriptor):
    if not isinstance(descriptor, dict):
        raise ValueError("An artifact needs a path and SHA-256")
    path = library_file(library, descriptor.get("path"))
    if not HEX.fullmatch(str(descriptor.get("sha256"))) or sha256(path) != descriptor["sha256"]:
        raise ValueError(f"Artifact hash mismatch: {path}")
    return {"path": str(path.relative_to(library)), "sha256": descriptor["sha256"]}


def verify_recipe(library, rid, digest):
    from learn import show
    recipe = show(library, rid)
    source = recipe["source"]
    if digest not in {source.get("original_sha256"), source.get("clip_sha256")}:
        raise ValueError(f"Recipe {rid} has no association with this source")
    report = read_json(recipe["evidence"])
    check_comparison(report, source["clip_sha256"], sha256(recipe["preview"]))


def coverage(film, library, bindings):
    rebuild = film.get("reconstruction")
    if rebuild and rebuild.get("verification") == "historical-archive":
        return "archived-reconstruction"
    try:
        if rebuild:
            for name in ("editable_project", "master", "comparison"):
                checked_artifact(library, rebuild[name])
            return "verified-local-reconstruction"
        if film["recipe_ids"] or bindings:
            for rid in film["recipe_ids"]:
                verify_recipe(library, rid, film["sha256"])
            return "verified-recipes-only"
    except (KeyError, OSError, ValueError):
        pass
    return "associated-artifacts-unavailable"


def check_comparison(report, source_hash, output_hash):
    thresholds = report.get("thresholds", {})
    count = report.get("compared_frames")
    if (thresholds.get("max_mae") is None or thresholds.get("max_pts_error_ms") is None
            or "full" not in report.get("metrics", {})
            or report.get("inputs", {}).get("source", {}).get("frame_count") != count
            or report.get("inputs", {}).get("output", {}).get("frame_count") != count
            or report.get("inputs", {}).get("source", {}).get("sha256") != source_hash
            or report.get("inputs", {}).get("output", {}).get("sha256") != output_hash
            or not report.get("structure_within_tolerance", report.get("structure_match")) or not count
            or report.get("source_only_tail_frames") or report.get("output_only_tail_frames")
            or report.get("limits_passed") is not True or report.get("failures")):
        raise ValueError("Comparison must cover the registered source/master pair and pass the specified limits")


def register(video_path, library_path=None, *, film_id, title, verification_path):
    if not isinstance(film_id, str) or not ID.fullmatch(film_id) or not isinstance(title, str) or not title.strip():
        raise ValueError("Provide a stable lowercase film ID and title")
    library = library_root(library_path)
    digest = sha256(video_path)
    receipt = read_json(verification_path)
    if (receipt.get("verdict") != "pass" or receipt.get("source_sha256") != digest
            or not isinstance(receipt.get("reviewed_by"), str) or not receipt["reviewed_by"].strip()):
        raise ValueError("Film registration requires a passing named review bound to this source SHA-256")
    recipe_ids = receipt.get("recipe_ids", [])
    if not isinstance(recipe_ids, list) or any(not isinstance(r, str) or not ID.fullmatch(r) for r in recipe_ids):
        raise ValueError("Invalid recipe IDs")
    for rid in recipe_ids:
        verify_recipe(library, rid, digest)
    tokens = receipt.get("seed_bindings", [])
    if not isinstance(tokens, list):
        raise ValueError("Expected seed binding tokens")
    for token in tokens:
        verified_binding(library, token, digest)
    reconstruction = receipt.get("reconstruction")
    project = None
    if reconstruction is not None:
        if not isinstance(reconstruction, dict):
            raise ValueError("Invalid reconstruction")
        project = checked_artifact(library, reconstruction.get("editable_project"))
        master = checked_artifact(library, reconstruction.get("master"))
        if project["sha256"] in {digest, master["sha256"]} or master["sha256"] == digest:
            raise ValueError("The source, editable project and reconstructed master must be distinct artifacts")
        comparison = checked_artifact(library, reconstruction.get("comparison"))
        report = read_json(library / comparison["path"])
        check_comparison(report, digest, master["sha256"])
        reconstruction = {"editable_project": project, "master": master, "comparison": comparison,
                          "verification": {"reviewed_by": receipt["reviewed_by"], "verdict": "pass"}}
    if not recipe_ids and not tokens and not reconstruction:
        raise ValueError("Register a verified recipe or an editable reconstruction and master")
    record = {"id": film_id, "title": title.strip(), "sha256": digest,
              "source": {"sha256": digest, "filename": Path(video_path).name},
              "editable_project": project, "reconstruction": reconstruction,
              "recipe_ids": sorted(set(recipe_ids)), "seed_bindings": sorted(set(tokens)), "reviewed_by": receipt["reviewed_by"].strip(),
              "fingerprint": fingerprint(video_path)}
    if sha256(video_path) != digest:
        raise ValueError("Source changed while registering")
    directory = library / "films"
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / ".register.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        for existing in records(library):
            if existing["id"] == film_id or existing["sha256"] == digest:
                if film_id != existing["id"] or digest != existing["sha256"]:
                    raise ValueError(f"Source or ID already registered as {existing['id']}")
                prior = existing.get("reconstruction")
                archived = prior and prior.get("verification") == "historical-archive"
                if prior and not archived and reconstruction:
                    if any(prior[k] != reconstruction[k] for k in ("editable_project", "master")):
                        raise ValueError("Conflicting verified reconstruction for this source")
                combined_ids = sorted(set(recipe_ids) | set(existing["recipe_ids"]))
                record = dict(existing, recipe_ids=combined_ids)
                if tokens:
                    record["seed_bindings"] = sorted(set(tokens) | set(existing.get("seed_bindings", [])))
                if reconstruction and (not prior or archived):
                    if archived:
                        record["archived"] = {"editable_project": existing["editable_project"], "reconstruction": prior}
                    record.update(reconstruction=reconstruction, editable_project=project)
                if record == existing:
                    return {"status": "registered", "id": film_id, "changed": False}
                break
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=directory,
                                         prefix=".film-", delete=False) as handle:
            temp = Path(handle.name)
        try:
            with temp.open("w", encoding="utf-8") as output:
                json.dump(record, output, indent=2, ensure_ascii=False)
                output.write("\n")
                output.flush()
                os.fsync(output.fileno())
            os.replace(temp, directory / (film_id + ".json"))
        finally:
            temp.unlink(missing_ok=True)
    return {"status": "registered", "id": film_id, "changed": True}


def verified_binding(library, token, digest):
    if not isinstance(token, str) or not HEX.fullmatch(token):
        raise ValueError("Invalid seed binding token")
    folder = library / "film-bindings" / token
    binding = read_json(folder / "binding.json")
    raw = json.dumps(binding["identity"], sort_keys=True).encode()
    if hashlib.sha256(raw).hexdigest() != token or binding["identity"]["source_sha256"] != digest:
        raise ValueError("Seed binding belongs to another source or recipe")
    for name, checksum in binding["files"].items():
        if sha256(library_file(folder, name)) != checksum:
            raise ValueError("Seed comparison evidence changed")
    report = read_json(folder / "comparison/report.json")
    ident = binding["identity"]
    check_comparison(report, ident["clip_sha256"], ident["preview_sha256"])
    expected_regions = {k: [x, y, x + w, y + h] for k, (x, y, w, h) in ident["rois"].items()}
    if (binding["files"].get("reference.nut") != ident["clip_sha256"]
            or binding["files"].get("preview.mp4") != ident["preview_sha256"]
            or binding["files"].get("scene.json") != ident["scene_sha256"]
            or report.get("roi_xyxy") != expected_regions or not expected_regions
            or report["thresholds"]["max_mae"] != ident["max_mae"]
            or report["thresholds"]["max_pts_error_ms"] != ident["max_pts_error_ms"]
            or report["compared_frames"] != ident["frames"][1] - ident["frames"][0]):
        raise ValueError("Incomplete seed comparison")
    return {**ident, "token": token, "evidence": str(folder / "comparison/report.json")}


def bind_seed(video_path, library_path, *, film_id, title, recipe_id, frames, rois, max_mae,
              reviewed_by, content_file=None, crop=None, max_pts_error_ms=.05):
    import learn
    import recipes
    from frames import parse_roi
    if not reviewed_by.strip() or not ID.fullmatch(film_id) or not title.strip():
        raise ValueError("Provide film ID, title and reviewer")
    if not re.fullmatch(r"\d+:\d+", frames):
        raise ValueError("Use a native-frame interval FIRST:EXCLUSIVE_END")
    first, end = map(int, frames.split(":"))
    if end - first < 2 or not rois or not (0 <= max_mae < 255 and math.isfinite(max_pts_error_ms) and max_pts_error_ms >= 0):
        raise ValueError("Provide at least two frames, a moving ROI and finite comparison tolerances")
    region_map = {}
    for region in rois:
        name, (x, y, right, bottom) = parse_roi(region)
        if name in region_map:
            raise ValueError("Duplicate comparison ROI")
        region_map[name] = [x, y, right - x, bottom - y]
    library = library_root(library_path)
    video = Path(video_path).resolve()
    library.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=library, prefix=".bind-seed-") as tmp:
        temp = Path(tmp)
        folder = temp / "proof"
        folder.mkdir()
        subject = {"source": {"start_frame": first}}
        clip = learn.prepare_clip(video, folder, subject, frames, crop)
        fps = Fraction(subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0",
                       "-show_entries", "stream=avg_frame_rate", "-of", "csv=p=0", str(video)], text=True).strip())
        if fps.denominator != 1 or fps not in (24, 25, 30, 60):
            raise ValueError("This seed renderer supports 24, 25, 30 and 60 fps; retain the source cadence")
        recipes.materialize(recipe_id, folder / "scene.json", Path(content_file) if content_file else None,
                            int(fps), float((end - first) / fps))
        recipes.render(folder / "scene.json", folder / "preview.mp4")
        checks = {"checks": {"rois": region_map, "max_mae": max_mae, "max_pts_error_ms": max_pts_error_ms}}
        code, report = learn.compare(clip, folder / "preview.mp4", folder / "comparison", checks)
        if code or report["compared_frames"] != end - first:
            raise ValueError("Seed replay failed the requested frame interval, ROI, or full-frame comparison")
        fingerprint_source = subject["source"]["original_sha256"]
        clip_hash, preview_hash = sha256(clip), sha256(folder / "preview.mp4")
        check_comparison(report, clip_hash, preview_hash)
        ident = {"recipe_id": recipe_id, "source_sha256": fingerprint_source, "frames": [first, end],
                 "crop": subject["source"].get("crop_xywh"), "rois": region_map,
                 "max_mae": max_mae, "max_pts_error_ms": max_pts_error_ms,
                 "clip_sha256": clip_hash, "preview_sha256": preview_hash, "scene_sha256": sha256(folder / "scene.json")}
        token = hashlib.sha256(json.dumps(ident, sort_keys=True).encode()).hexdigest()
        # Store comparisons plus their exact inputs; source checksums and bounds bind them to this film.
        files = {q.relative_to(folder).as_posix(): sha256(q) for q in folder.rglob("*") if q.is_file()}
        (folder / "binding.json").write_text(json.dumps({"identity": ident, "files": files}, indent=2))
        target = library / "film-bindings" / token
        with learn.locked(library):
            if not target.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                folder.rename(target)
        checked = verified_binding(library, token, fingerprint_source)
        review = temp / "review.json"
        review.write_text(json.dumps({"verdict": "pass", "reviewed_by": reviewed_by,
                                     "source_sha256": fingerprint_source, "seed_bindings": [token]}))
        result = register(video, library, film_id=film_id, title=title, verification_path=review)
        return {**result, "seed_binding": checked}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest="action", required=True)
    for action in ("identify", "register", "bind-seed"):
        p = subs.add_parser(action)
        p.add_argument("video")
        p.add_argument("--library", help="Motion library (overrides IMESSAGE_VIDEO_MOTION_LIBRARY)")
        if action != "identify":
            p.add_argument("--id", required=True)
            p.add_argument("--title", required=True)
        if action == "register":
            p.add_argument("--verification", required=True)
        if action == "bind-seed":
            p.add_argument("--recipe", required=True)
            p.add_argument("--frames", required=True, help="FIRST:EXCLUSIVE_END")
            p.add_argument("--roi", action="append", required=True, help="NAME:X,Y,W,H")
            p.add_argument("--crop", help="Optional X,Y,W,H crop of the source before comparison")
            p.add_argument("--content", type=Path, help="Editable fields for this seed")
            p.add_argument("--max-mae", type=float, required=True)
            p.add_argument("--max-pts-error-ms", type=float, default=.05)
            p.add_argument("--reviewed-by", required=True)
    args = parser.parse_args()
    try:
        if args.action == "identify":
            result = identify(args.video, args.library)
        elif args.action == "bind-seed":
            result = bind_seed(args.video, args.library, film_id=args.id, title=args.title, recipe_id=args.recipe,
                               frames=args.frames, rois=args.roi, content_file=args.content, crop=args.crop,
                               max_mae=args.max_mae, max_pts_error_ms=args.max_pts_error_ms, reviewed_by=args.reviewed_by)
        else:
            result = register(args.video, args.library, film_id=args.id, title=args.title, verification_path=args.verification)
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError, argparse.ArgumentTypeError) as exc:
        parser.exit(1, f"{exc}\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
