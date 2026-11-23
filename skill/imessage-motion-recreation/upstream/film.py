#!/usr/bin/env python3
"""Run the pinned local reference-analysis and HyperFrames film routes."""
import argparse
from base64 import b64decode
from fractions import Fraction
from hashlib import sha256
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys


SKILL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL / "recreate"))
sys.path.insert(0, str(SKILL))
from analyze import analyze
from contracts.timeline import resolve
from media import MediaError, digest, video_clock, write_json
from ui.adapter import compile_conversation

RUNTIME = Path(os.environ.get("IMV_NODE_RUNTIME", SKILL / "upstream/runtime")).resolve()
HF = RUNTIME / "node_modules/.bin/hyperframes"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def run(argv, *, env=None, log=None):
    if log is None:
        subprocess.run(argv, check=True, env=env)
        return
    with log.open("w", encoding="utf-8") as handle:
        subprocess.run(argv, check=True, env=env, stdout=handle)


def hyperframes(*args, log=None):
    env = {
        **os.environ, "HYPERFRAMES_NO_TELEMETRY": "1",
        "HYPERFRAMES_SKIP_SKILLS": "1", "HYPERFRAMES_NO_UPDATE_CHECK": "1",
    }
    run([HF, *args], env=env, log=log)


def rea(output, *args):
    executable = os.environ.get("IMV_REA_VIDEO", "rea-video")
    env = {**os.environ, "REA_VIDEO_HOME": str(output / "rea-state")}
    run([executable, *args], env=env)


def clock_route(clock):
    grid = clock.rate and all(t == Fraction(i) / clock.rate for i, t in enumerate(clock.times))
    grid = grid and clock.end == Fraction(len(clock.pts)) / clock.rate
    geometry = (
        clock.sar == 1 and not any(clock.crop) and not clock.has_alpha
        and clock.display_matrix == (65536, 0, 0, 0, 65536, 0, 0, 0, 1073741824)
        and clock.width % 2 == 0 and clock.height % 2 == 0
        and clock.stream.get("color_transfer") not in ("smpte2084", "arib-std-b67")
    )
    if grid and geometry:
        return {"route": "hyperframes", "reason": "constant measured frame grid and opaque SDR geometry"}
    if geometry and clock.end is not None:
        return {"route": "measured-clock", "reason": "source presentation timestamps or ending are off-grid"}
    return {"route": "existing-renderer", "reason": "display or ending requires a renderer-specific probe"}


def refresh_ledger(source, output):
    analysis = read(output / "measurements/analysis.json")
    if digest(source) != analysis["source_sha256"]:
        raise MediaError("Use the reference bytes that produced the saved measurements")
    clock = video_clock(source)
    breakdown = read(output / "rea/breakdown.json")
    ledger_path = output / "shot-ledger.json"
    prior = read(ledger_path) if ledger_path.is_file() else {}
    retained = {shot["id"]: shot for shot in prior.get("shots", [])}
    if prior and prior["reference_sha256"] != analysis["source_sha256"]:
        raise MediaError("The existing shot ledger is for different source bytes")
    shots = []
    boundary = 0
    for shot in breakdown["shots"]:
        start, end = shot["start_frame"], shot["end_frame"]
        if start != boundary or not start < end <= len(clock.pts):
            raise MediaError(f"REA shot {shot['id']} does not partition the measured frames at {boundary}")
        boundary = end
        review = shot.get("review") or {}
        base = shot.get("base") or {}
        previous = retained.pop(shot["id"], {})
        if previous.get("layers") and previous["frames"] != [start, end - 1]:
            raise MediaError(f"Reconcile changed boundaries in {shot['id']} before replacing its authored layers")
        shots.append({
            "id": shot["id"], "frames": [start, end - 1],
            "source_pts": [clock.pts[start], clock.pts[end] if end < len(clock.pts) else clock.end_pts],
            "suggested_method": base.get("label"), "confidence": base.get("confidence"),
            "reviewed": bool(review),
            "boundary_review": previous.get("boundary_review", "inspect consecutive frames around the cut"),
            "transition": shot.get("transition_in"), "keyframes": [
                {**key, "source_pts": clock.pts[key["frame"]]}
                for key in shot.get("keyframes", []) if start <= key["frame"] < end
            ],
            "assessment": base, "observation": review.get("description"),
            "assets": review.get("embedded_assets") or shot.get("embedded_assets") or [],
            "layers": previous.get("layers", []),
        })
    if boundary != len(clock.pts):
        raise MediaError(f"REA breakdown ends at frame {boundary}, expected {len(clock.pts)}")
    if any(shot.get("layers") for shot in retained.values()):
        raise MediaError("Reconcile removed shots with authored layers before refreshing the ledger")
    write_json(ledger_path, {
        "reference_sha256": analysis["source_sha256"],
        "breakdown_sha256": digest(output / "rea/breakdown.json"),
        "clock": clock.summary(),
        "renderer": clock_route(clock),
        "shots": shots,
    })


def reference(source, output):
    output.mkdir(parents=True, exist_ok=False)
    analyze(source, output / "measurements")
    rea(output, "decompose", source, "-o", output / "rea", "--lang", "en",
        "--no-vlm", "--no-asr", "--no-stems", "--workers", "2")
    rea(output, "review", output / "rea")
    refresh_ledger(source, output)


def init_project(output):
    if output.exists():
        raise MediaError(f"Choose a new project directory: {output}")
    hyperframes("init", output, "--non-interactive", "--example", "blank", "--skip-skills")
    assets = output / "assets"
    assets.mkdir(exist_ok=True)
    for name in ("package.json", "package-lock.json"):
        shutil.copyfile(SKILL / "upstream/runtime" / name, output / name)
    shutil.copyfile(RUNTIME / "node_modules/gsap/dist/gsap.min.js", assets / "gsap.min.js")
    shutil.copyfile(RUNTIME / "node_modules/gsap/README.md", assets / "GSAP-README.md")
    index = output / "index.html"
    index.write_text(index.read_text().replace(
        "https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js", "assets/gsap.min.js"
    ), encoding="utf-8")


def messages(source, project):
    assets, compositions = project / "assets", project / "compositions"
    compositions.mkdir(exist_ok=True)
    scene = compile_conversation(read(source), input_dir=source.parent, output_dir=project)
    prior_scene = project / "messages.scene.json"
    if prior_scene.is_file():
        prior = read(prior_scene)
        if (scene["width"], scene["height"], scene["timeline"]["picture"]) != (
            prior["width"], prior["height"], prior["timeline"]["picture"]
        ):
            raise MediaError("Build a new Messages project when changing its mounted canvas or clock")
    # The contract resolves references before packaging so visual and event
    # names travel together. Stage every declared input as a project file.
    events = resolve(scene)
    for font in scene.get("fonts", []):
        file = (project / font["src"]).resolve()
        target = assets / file.name
        if not target.exists():
            shutil.copyfile(file, target)
        elif digest(target) != digest(file):
            raise MediaError(f"Asset collision with a different file: {target.name}")
        font["src"] = f"assets/{file.name}"

    def local_images(layers):
        for layer in layers:
            if layer["type"] == "image":
                src = layer["src"]
                if src.startswith("data:image/png;base64,"):
                    payload = b64decode(src.partition(",")[2], validate=True)
                    filename = f"{sha256(payload).hexdigest()}-oriented.png"
                    (assets / filename).write_bytes(payload)
                    layer["src"] = f"assets/{filename}"
                    continue
                file = (project / src).resolve()
                filename = f"{digest(file)[:16]}-{file.name}"
                target = assets / filename
                if not target.exists():
                    shutil.copyfile(file, target)
                elif digest(target) != digest(file):
                    raise MediaError(f"Asset collision with a different file: {filename}")
                layer["src"] = f"assets/{filename}"
            local_images(layer.get("children", []))

    local_images(scene["layers"])
    write_json(project / "messages.scene.json", scene)
    write_json(project / "messages.events.json", events)
    shutil.copyfile(SKILL / "scripts/engines/common.mjs", assets / "scene-runtime.mjs")
    run(["node", SKILL / "upstream/messages.mjs", project / "messages.scene.json",
         compositions / "messages.html"])
    return scene


def messages_project(source, output):
    init_project(output)
    # Preserve the relative paths used by the editable conversation.
    description = read(source)
    for asset in description.get("assets", {}).values():
        relative = Path(asset)
        if relative.is_absolute() or ".." in relative.parts:
            raise MediaError("Portable conversation assets must use paths inside the conversation folder")
        destination = output / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists() and digest(destination) != digest(source.parent / relative):
            raise MediaError(f"Conversation asset conflicts with named project file: {relative}")
        if not destination.exists():
            shutil.copyfile(source.parent / relative, destination)
    write_json(output / "conversation.json", description)
    scene = messages(output / "conversation.json", output)
    width, height = scene["width"], scene["height"]
    picture = scene["timeline"]["picture"]
    rate = f"{picture['fpsNum']}/{picture['fpsDen']}"
    duration = scene["duration"]
    (output / "index.html").write_text(f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>Messages composition</title>
<script src="assets/gsap.min.js"></script>
<style>html, body {{margin: 0; overflow: hidden;}}</style></head>
<body>
<main id="root" data-composition-id="main" data-start="0" data-duration="{duration}"
  data-width="{width}" data-height="{height}" data-fps="{rate}">
  <div id="messages" class="clip" data-composition-id="messages"
    data-composition-src="compositions/messages.html" data-start="0"
    data-duration="{duration}" data-track-index="0" data-track-kind="graphics"
    data-width="{width}" data-height="{height}"></div>
</main>
<script>window.__timelines.main = gsap.timeline({{paused:true}});</script>
</body></html>
""", encoding="utf-8")


def review(project, output, reference_file, candidate):
    output.mkdir(parents=True, exist_ok=False)
    hyperframes("check", project, "--json", log=output / "check.json")
    hyperframes("snapshot", project, "--review", "--output", output / "snapshots",
                "--json", log=output / "snapshots.json")
    if reference_file is not None:
        hyperframes("diff", reference_file, candidate or project, "--out", output / "diff",
                    "--json", log=output / "diff.json")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_subparsers(dest="action", required=True)
    for name in ("reference", "apply-reference-review", "messages"):
        command = actions.add_parser(name)
        command.add_argument("source", type=Path)
        command.add_argument("output", type=Path)
    for name in ("recompile-messages", "render", "review"):
        command = actions.add_parser(name)
        command.add_argument("project", type=Path)
        if name in ("review", "render"):
            command.add_argument("output", type=Path)
        if name == "review":
            command.add_argument("--reference", type=Path)
            command.add_argument("--candidate", type=Path)
    args = parser.parse_args()
    for key, value in vars(args).items():
        if isinstance(value, Path):
            setattr(args, key, value.resolve())
    try:
        if args.action == "reference":
            reference(args.source, args.output)
        elif args.action == "apply-reference-review":
            saved = read(args.output / "measurements/analysis.json")
            if digest(args.source) != saved["source_sha256"]:
                raise MediaError("Use the reference bytes that produced the saved measurements")
            rea(args.output, "apply-review", args.output / "rea", "--lang", "en")
            refresh_ledger(args.source, args.output)
        elif args.action == "messages":
            messages_project(args.source, args.output)
        elif args.action == "recompile-messages":
            messages(args.project / "conversation.json", args.project)
        elif args.action == "review":
            review(args.project, args.output, args.reference, args.candidate)
        else:
            if args.output.exists():
                raise MediaError(f"Choose a new export path: {args.output}")
            hyperframes("render", args.project, "--output", args.output, "--quality", "high")
    except (OSError, KeyError, TypeError, ValueError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"{error}\n")


if __name__ == "__main__":
    main()
