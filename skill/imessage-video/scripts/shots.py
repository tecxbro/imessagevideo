#!/usr/bin/env python3
"""Create a shot pitch, record its approval, or revise one shot into a new plan."""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from fractions import Fraction
from pathlib import Path
from urllib.parse import quote, urlparse

ROOT = Path(__file__).resolve().parents[1]
MEDIA = ("board", "preview", "code", "review")
FIELDS = {"id", "frames", "purpose", "visual", "copy", "copy_key", "motion", "bindings", "assets", *MEDIA}


def digest(value):
    data = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    return hashlib.sha256(data.encode()).hexdigest()


def read(path):
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def write_new(path, content):
    """Publish a complete file without replacing an existing result, even on races."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as temp:
        tmp = Path(temp.name)
    try:
        tmp.write_text(content)
        os.link(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def validate(plan):
    if plan.get("mode") not in {"director", "edit", "recreate"} or not nonempty(plan.get("brief")):
        raise ValueError("Supply a brief and mode director, edit, or recreate")
    try:
        clock = Fraction(str(plan.get("fps", "")))
    except (ZeroDivisionError, ValueError) as exc:
        raise ValueError("fps must be a positive integer or rational number") from exc
    if clock <= 0 or not isinstance(plan.get("confirmation"), bool):
        raise ValueError("Specify a positive fps and boolean confirmation")
    if not isinstance(plan.get("shots"), list) or not plan["shots"]:
        raise ValueError("Supply a nonempty ordered shots list")
    ids = set()
    for shot in plan["shots"]:
        if not isinstance(shot, dict):
            raise ValueError("Every shot must be an object")
        sid = shot.get("id")
        if not isinstance(sid, str) or not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_.-]*", sid) or sid in ids:
            raise ValueError(f"Missing, invalid, or duplicate shot id: {sid}")
        ids.add(sid)
        if set(shot) - FIELDS or type(shot.get("frames")) is not int or shot["frames"] <= 0:
            raise ValueError(f"{sid}: unknown fields or invalid frame count")
        if not all(nonempty(shot.get(k)) for k in ("purpose", "visual")):
            raise ValueError(f"{sid}: describe the purpose and visible action")
        if not isinstance(shot.get("copy", ""), str) or not isinstance(shot.get("bindings", {}), dict):
            raise ValueError(f"{sid}: copy must be text and bindings must be an object")
        if "copy_key" in shot and not nonempty(shot["copy_key"]):
            raise ValueError(f"{sid}: copy_key must be an editable text field")
        if not isinstance(shot.get("assets", {}), dict) or not all(nonempty(v) for v in shot.get("assets", {}).values()):
            raise ValueError(f"{sid}: asset overrides must map names to local file paths")
        for key in MEDIA:
            if key in shot and not nonempty(shot[key]):
                raise ValueError(f"{sid}: {key} must be a file path or web URL")
        motion = shot.get("motion")
        if not isinstance(motion, dict) or motion.get("kind") not in {"seed", "learned", "reference", "original"}:
            raise ValueError(f"{sid}: choose seed, learned, reference, or original motion")
        kind = motion["kind"]
        required = ("id",) if kind in {"seed", "learned"} else ("intent",)
        if not all(nonempty(motion.get(k)) for k in required):
            raise ValueError(f"{sid}: supply motion {', '.join(required)}")
        if kind == "reference":
            span = motion.get("frames")
            if not nonempty(motion.get("source")) or not isinstance(span, list) or len(span) != 2 or not all(type(f) is int for f in span) or not 0 <= span[0] < span[1]:
                raise ValueError(f"{sid}: give the donor source and [start,end) frame range")


def asset(locator, base):
    if urlparse(locator).scheme in {"http", "https"}:
        return {"path": locator, "identity": "external link"}
    path = (base / Path(locator).expanduser()).resolve()
    if not path.is_file():
        return {"path": str(path), "identity": "missing"}
    with path.open("rb") as f:
        return {"path": str(path), "identity": hashlib.file_digest(f, "sha256").hexdigest()}


def evidence(shot, base, library):
    motion = shot["motion"]
    kind = motion["kind"]
    links = {k: asset(shot[k], base) for k in MEDIA if k in shot}
    for name, path in shot.get("assets", {}).items():
        links["asset " + name] = asset(path, base)
    photos = shot.get("bindings", {}).get("photos", [])
    if isinstance(photos, list):
        for index, photo in enumerate(photos):
            if isinstance(photo, str):
                links[f"photo {index + 1}"] = asset(photo, base)
    details = []
    issues = []
    if kind in {"seed", "learned"}:
        try:
            if kind == "seed":
                import recipes
                info = recipes.info(motion["id"])
                preview, code = info["preview"], info["implementation"]
                details = [info["title"], info["moves"], info["fixed"]]
            else:
                import learn
                info = learn.show(library, motion["id"])
                preview, code = info["preview"], info["scene"]
                details = [info["title"], "Moves: " + ", ".join(info["moving"]), "Fixed: " + ", ".join(info["fixed"])]
                links["comparison"] = asset(info["evidence"], base)
            links["motion example"] = asset(preview, base)
            links["implementation"] = asset(code, base)
            if kind == "seed" and links["motion example"]["identity"] != info["sha256"]:
                issues.append("Bundled motion preview does not match its catalog checksum.")
            editable = info["editable"] if kind == "seed" else info["parameters"]
            fields = set(shot.get("bindings", {}))
            if "copy_key" in shot:
                fields.add(shot["copy_key"])
            if fields - set(editable):
                issues.append("Unsupported content fields: " + ", ".join(sorted(fields - set(editable))))
        except (KeyError, ValueError, OSError, ImportError) as exc:
            issues.append(f"{kind} recipe unavailable: {motion['id']} ({exc})")
    elif kind == "reference":
        links["donor"] = asset(motion["source"], base)
        details = [f"{motion['intent']} (donor frames {motion['frames'][0]}–{motion['frames'][1]-1})"]
        if not ("preview" in links and "code" in links):
            issues.append("Donor selected; measure the passage and attach its working proof and code.")
    else:
        details = [motion["intent"]]
        if not ("preview" in links and "code" in links):
            issues.append("Original motion proposed; author a moving proof with editable source.")
    if kind in {"original", "reference"} and "preview" in links and "code" in links:
        review_link = links.get("review")
        observed = False
        if review_link and review_link["identity"] not in {"external link", "missing"}:
            try:
                report = read(Path(review_link["path"]))
                observed = (
                    report.get("preview_sha256") == links["preview"]["identity"]
                    and re.fullmatch(r"[0-9a-f]{64}", links["preview"]["identity"])
                    and nonempty(report.get("observation"))
                    and nonempty(report.get("reviewer"))
                )
                if observed and kind == "reference":
                    observed = report.get("donor_frames") == motion["frames"] and report.get("donor") == motion["source"]
            except (OSError, ValueError):
                observed = False
        if not observed:
            issues.append("Moving proof awaits a recorded visual check of this exact preview and donor window if used.")
    issues.extend(f"Missing {name}: {item['path']}" for name, item in links.items() if item["identity"] == "missing")
    return {"links": links, "details": details, "issues": issues}


def review(plan, base, library):
    results = {s["id"]: evidence(s, base, library) for s in plan["shots"]}
    # Stable across a checkout move. Bind approval to content and to local review assets.
    identities = {sid: {"details": r["details"], "issues": r["issues"],
                        "artifacts": {k: v["identity"] for k, v in r["links"].items()}}
                  for sid, r in results.items()}
    return digest({"plan": plan, "evidence": identities}), results


def link(path, directory):
    if urlparse(path).scheme in {"http", "https"}:
        return path.replace(" ", "%20").replace(")", "%29")
    return quote(os.path.relpath(path, directory), safe="/._-")


def pitch(doc, revision, results, directory):
    plan = doc["plan"]
    approved = doc.get("approval", {}).get("revision") == revision
    state = "approved" if approved else ("awaiting confirmation" if plan["confirmation"] else "confirmation optional")
    lines = ["# Shot pitch", "", plan["brief"], "", f"**{plan['mode'].title()}** · {plan['fps']} fps · {state}", ""]
    start = 0
    for shot in plan["shots"]:
        sid = shot["id"]
        stop = start + shot["frames"]
        result = results[sid]
        lines += [f"## {sid} · frames {start}–{stop-1}", "", shot["purpose"], "", shot["visual"]]
        if shot.get("copy"):
            lines += ["", *["> " + line for line in shot["copy"].splitlines()]]
        if result["details"]:
            lines += ["", " ".join(result["details"])]
        if shot.get("bindings"):
            lines += ["", "Content settings", "", "```json", json.dumps(shot["bindings"], ensure_ascii=False, indent=2), "```"]
        for label, item in result["links"].items():
            if item["identity"] != "missing":
                prefix = "!" if label == "board" else ""
                lines += ["", f"{prefix}[{label.capitalize()}]({link(item['path'], directory)})"]
        lines += ["", *("Open work — " + msg for msg in result["issues"])]
        start = stop
    lines += ["", f"Plan revision `{revision}`"]
    return "\n".join(lines) + "\n"


def render_shot(plan, shot, base, library, dest, issues):
    """Build one self-contained selected passage in a new directory."""
    kind = shot["motion"]["kind"]
    if kind not in {"seed", "learned"} or issues:
        raise ValueError("Select a working seed or learned recipe. " + " ".join(issues))
    fields = dict(shot.get("bindings", {}))
    if "copy" in shot:
        if "copy_key" not in shot:
            raise ValueError("Set copy_key to the editable recipe parameter that displays the shot's copy.")
        fields[shot["copy_key"]] = shot["copy"]
    clock = Fraction(str(plan["fps"]))
    duration = shot["frames"] / clock
    if dest.exists():
        raise ValueError("Use a new shot output directory")
    dest.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=dest.parent) as stage:
        bundle = Path(stage) / "bundle"
        bundle.mkdir()
        movie = bundle / "preview.mp4"
        recipe_id = shot["motion"]["id"]
        if kind == "seed":
            import recipes
            if shot.get("assets"):
                raise ValueError("Set this seed's editable fields in bindings; image arrays use bindings.photos")
            if clock not in {24, 25, 30, 60} or not 1.6 <= duration <= 12:
                raise ValueError("Bundled starter rendering supports 24, 25, 30 or 60 fps and 1.6–12 seconds. Author a custom shot for other clocks.")
            if "photos" in fields:
                if not isinstance(fields["photos"], list) or not all(isinstance(v, str) for v in fields["photos"]):
                    raise ValueError("Set photos to a list of project image paths")
                fields["photos"] = [str((base / name).resolve()) for name in fields["photos"]]
            content = bundle / "content.json"
            content.write_text(json.dumps(fields))
            scene = bundle / "scene.json"
            recipes.materialize(recipe_id, scene, content, int(clock), float(duration), bundle / "assets")
            recipes.render(scene, movie)
        else:
            command = [sys.executable, str(ROOT / "scripts/learn.py"), "--library", str(library),
                       "replay", recipe_id, "--out", str(movie), "--project", str(bundle / "editable")]
            for key, value in fields.items():
                command.extend(["--set", key + "=" + json.dumps(value)])
            for key, name in shot.get("assets", {}).items():
                command.extend(["--asset", key + "=" + str((base / name).resolve())])
            subprocess.run(command, check=True, stdout=sys.stderr)
        probe = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0",
            "-count_frames", "-show_entries", "stream=avg_frame_rate,nb_read_frames", "-of", "json", str(movie)])
        stream = json.loads(probe)["streams"][0]
        if Fraction(stream["avg_frame_rate"]) != clock or int(stream["nb_read_frames"]) != shot["frames"]:
            raise ValueError("Rendered passage uses a different frame count or clock than the selected shot")
        dest.mkdir()
        try:
            os.replace(bundle, dest)
        except OSError:
            dest.rmdir()
            raise


def production_state(doc, revision, results):
    issues = {sid: r["issues"] for sid, r in results.items() if r["issues"]}
    approved = doc.get("approval", {}).get("revision") == revision
    required = doc["plan"]["confirmation"]
    return {"revision": revision, "confirmation_required": required,
            "approved": approved, "open_work": issues}


def render_cut(doc, revision, results, destination):
    """Join the reviewed picture files without re-encoding unaffected shots."""
    from frames import inspect

    state = production_state(doc, revision, results)
    if state["confirmation_required"] and not state["approved"]:
        raise ValueError("The current pitch must be approved before rendering the full cut.")
    if state["open_work"]:
        raise ValueError("Resolve the open work before rendering the full cut.")
    if destination.exists() or destination.suffix.lower() != ".mp4":
        raise ValueError("Choose a new .mp4 destination for the cut.")

    plan = doc["plan"]
    clock = Fraction(str(plan["fps"]))
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=destination.parent) as stage:
        folder = Path(stage)
        lines = ["ffconcat version 1.0"]
        format_key = None
        total = 0
        for index, shot in enumerate(plan["shots"]):
            preview = results[shot["id"]]["links"].get("preview")
            if not preview or preview["identity"] in {"missing", "external link"}:
                raise ValueError(f"{shot['id']}: attach the local rendered shot preview to the pitch.")
            path = Path(preview["path"])
            info, pts, end = inspect(path)
            if info["sha256"] != preview["identity"]:
                raise ValueError(f"{shot['id']}: the approved shot preview changed.")
            if (len(pts) != shot["frames"] or end != shot["frames"] / clock
                    or any(t != i / clock for i, t in enumerate(pts))):
                raise ValueError(f"{shot['id']}: the reviewed picture must match the shot's frame clock.")
            raw = subprocess.check_output([
                "ffprobe", "-v", "error", "-show_entries",
                "stream=codec_type,codec_name,profile,width,height,pix_fmt,time_base,sample_aspect_ratio",
                "-of", "json", str(path),
            ])
            streams = json.loads(raw)["streams"]
            if len(streams) != 1 or streams[0].get("codec_type") != "video":
                raise ValueError(f"{shot['id']}: use a picture-only MP4 preview and mix sound against the assembled cut.")
            if format_key is not None and streams[0] != format_key:
                raise ValueError(f"{shot['id']}: render the reviewed shots with matching picture settings.")
            format_key = streams[0]
            name = f"shot-{index}.mp4"
            (folder / name).symlink_to(path)
            lines.append(f"file {name}")
            total += len(pts)

        manifest = folder / "shots.ffconcat"
        manifest.write_text("\n".join(lines) + "\n", encoding="utf-8")
        cut = folder / "cut.mp4"
        subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-xerror", "-f", "concat", "-i", str(manifest),
                        "-map", "0:v:0", "-c", "copy", "-movflags", "+faststart", str(cut)], check=True)
        _, pts, end = inspect(cut)
        if len(pts) != total or end != total / clock or any(t != i / clock for i, t in enumerate(pts)):
            raise ValueError("Full cut changed the approved shot clock or ending.")
        os.link(cut, destination)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--library", type=Path, default=os.environ.get("IMESSAGE_VIDEO_MOTION_LIBRARY") or ROOT/"assets/library")
    sub = parser.add_subparsers(dest="operation", required=True)
    for cmd in ("create", "pitch", "revise", "approve", "check", "render-shot", "render-cut"):
        p = sub.add_parser(cmd)
        p.add_argument("input", type=Path)
        if cmd in {"revise", "render-shot"}:
            p.add_argument("shot")
        if cmd == "revise":
            p.add_argument("patch", type=Path)
        if cmd == "approve":
            p.add_argument("revision")
            p.add_argument("--response", required=True, help="the user's actual confirmation")
        if cmd in {"create", "revise", "approve", "render-shot", "render-cut"}:
            p.add_argument("output", type=Path)
        if cmd == "pitch":
            p.add_argument("--out", type=Path)
        if cmd == "check":
            p.add_argument("--for-production", action="store_true", help="fail on open motion work or outstanding requested confirmation")
    args = parser.parse_args()
    cmd = args.operation
    raw = read(args.input)
    base = args.input.resolve().parent
    if cmd == "create":
        if set(raw) - {"mode", "brief", "fps", "confirmation", "shots"}:
            raise ValueError("Unknown plan fields; to change an existing plan use revise")
        plan = {"mode": "director", "fps": 30, **raw}
        plan.setdefault("confirmation", plan["mode"] == "director")
        doc = {"format": 1, "plan": plan}
    else:
        if raw.get("format") != 1 or not isinstance(raw.get("plan"), dict):
            raise ValueError("Expected a plan made by shots.py create")
        doc, plan = raw, raw["plan"]
        base = (base / doc["project_root"]).resolve()
    validate(plan)
    revision, results = review(plan, base, args.library.expanduser().resolve())
    if cmd == "pitch":
        directory = args.out.resolve().parent if args.out else Path.cwd()
        content = pitch(doc, revision, results, directory)
        if args.out:
            write_new(args.out, content)
        else:
            print(content, end="")
        return 0
    if cmd == "check":
        state = production_state(doc, revision, results)
        print(json.dumps(state, indent=2))
        return int(args.for_production and (bool(state["open_work"]) or
                                            (state["confirmation_required"] and not state["approved"])))
    if cmd == "render-cut":
        render_cut(doc, revision, results, args.output.resolve())
        print(args.output)
        return 0
    if cmd in {"revise", "render-shot"}:
        matches = [s for s in plan["shots"] if s["id"] == args.shot]
        if not matches:
            raise ValueError(f"Unknown shot {args.shot}")
        if cmd == "render-shot":
            render_shot(plan, matches[0], base, args.library.expanduser().resolve(),
                        args.output.resolve(), results[args.shot]["issues"])
            print(args.output / "preview.mp4")
            return 0
        patch = read(args.patch)
        if not patch or set(patch) - (FIELDS - {"id"}):
            raise ValueError("Patch must change fields within the selected shot; its ID is stable")
        shot = matches[0]
        if all(shot.get(k) == v for k, v in patch.items()):
            raise ValueError("No shot values changed")
        if set(patch) - set(MEDIA):
            for key in MEDIA:
                if key not in patch:
                    shot.pop(key, None)
        shot.update(patch)
        validate(plan)
        doc.pop("approval", None)
        doc["derived_from"] = {"revision": revision, "changed_shot": args.shot}
    elif cmd == "approve":
        if args.revision != revision:
            raise ValueError("The pitch or its local evidence has changed. Show the current pitch.")
        if not nonempty(args.response):
            raise ValueError("Record the user's confirmation")
        doc["approval"] = {"revision": revision, "response": args.response}
    doc["project_root"] = os.path.relpath(base, args.output.resolve().parent)
    write_new(args.output, json.dumps(doc, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
    print(args.output)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, OSError, TypeError, KeyError, subprocess.CalledProcessError) as error:
        sys.exit(str(error))
