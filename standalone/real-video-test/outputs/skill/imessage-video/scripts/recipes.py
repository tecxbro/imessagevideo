#!/usr/bin/env python3
"""Find, inspect and adapt the bundled, read-only motion recipes."""
import argparse
import base64
from functools import lru_cache
import hashlib
import json
import mimetypes
import os
from pathlib import Path
import shutil
import subprocess
import sys

SEED = Path(__file__).resolve().parents[1] / "assets" / "seed"
RUNTIME = SEED / "runtime"
ENGINE = RUNTIME / "scripts" / "engines" / "render_pillow.py"
SVG_ENGINE = ENGINE.with_name("render_svg.mjs")


@lru_cache(maxsize=1)
def inventory():
    catalog = json.loads((SEED / "catalog.json").read_text(encoding="utf-8"))
    return {row["id"]: row for row in catalog["entries"]}


def info(recipe_id):
    """Return editable fields, timing evidence and installed preview/source paths."""
    row = inventory().get(recipe_id)
    if row is None:
        raise ValueError(f"Unknown bundled motion {recipe_id!r}. Run 'list' to see the IDs.")
    return {
        **row,
        "preview": str(SEED / row["preview"]),
        "implementation": str(SEED / row["implementation"]),
    }


def run_node(payload):
    result = subprocess.run(
        ["node", str(RUNTIME / "recipe.mjs")],
        input=json.dumps(payload), text=True, capture_output=True,
    )
    if result.returncode:
        raise ValueError(result.stderr.strip() or "Motion compilation failed.")
    return json.loads(result.stdout)


def suggest(request, limit=3):
    """Select by moving and fixed layers, supported technique and intended effect."""
    if not isinstance(request, str) or not request.strip():
        raise ValueError("Describe the action, what stays fixed and what the viewer should notice.")
    if limit < 1:
        raise ValueError("The suggestion limit must be positive.")
    match = run_node({"action": "suggest", "request": request})
    nearest = {item["id"]: item for item in match["candidates"]}
    ordered = list(dict.fromkeys([*match["matches"], *nearest]))
    candidates = []
    for key in ordered[:limit]:
        row = info(key)
        if key in nearest:
            row["selectionEvidence"] = nearest[key]
        candidates.append(row)
    return {**match, "candidates": candidates}


def write_json(destination, value):
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def portable_assets(value, asset_dir=None):
    """Inline editable image/font sources or collect local files for a project export."""
    if isinstance(value, list):
        return [portable_assets(item, asset_dir) for item in value]
    if not isinstance(value, dict):
        return value
    result = {}
    for key, item in value.items():
        if key == "src" and isinstance(item, str) and not item.startswith("data:"):
            asset = Path(item)
            raw = asset.read_bytes()
            if asset_dir:
                target = asset_dir / (hashlib.sha256(raw).hexdigest()[:16] + "-" + asset.name)
                asset_dir.mkdir(parents=True, exist_ok=True)
                if not target.exists():
                    target.write_bytes(raw)
                item = f"assets/{target.name}"
            else:
                mime = mimetypes.guess_type(asset.name)[0] or "application/octet-stream"
                item = f"data:{mime};base64," + base64.b64encode(raw).decode("ascii")
        result[key] = portable_assets(item, asset_dir)
    return result


def materialize(recipe_id, destination, content_file=None, fps=None, duration=None, asset_dir=None):
    row = info(recipe_id)
    content = {}
    if content_file:
        content = json.loads(content_file.read_text(encoding="utf-8"))
        if not isinstance(content, dict):
            raise ValueError("Content must be a JSON object.")
        unknown = set(content) - set(row["editable"])
        if unknown:
            raise ValueError(f"Unsupported fields {sorted(unknown)}. Editable fields: {', '.join(row['editable'])}")
        if "photos" in content:
            if not isinstance(content["photos"], list) or not all(isinstance(p, str) for p in content["photos"]):
                raise ValueError("photos must be an array of local image paths.")
            content["photos"] = [str((content_file.parent / photo).resolve()) for photo in content["photos"]]
    options = {key: value for key, value in {"fps": fps, "duration": duration}.items() if value is not None}
    scene = run_node({"action": "scene", "id": recipe_id, "content": content, "options": options})
    write_json(destination, portable_assets(scene, asset_dir))
    events_path = destination.with_name(destination.stem.removesuffix(".scene") + ".events.json")
    write_json(events_path, scene["timeline"])
    return {"id": recipe_id, "scene": str(destination), "events": str(events_path)}


def render(scene, out, engine="pillow"):
    command = ["node", str(SVG_ENGINE)] if engine == "svg" else [sys.executable, str(ENGINE)]
    subprocess.run(
        [*command, "--scene", str(scene), "--out", str(out)],
        env={**os.environ, "IMESSAGE_VIDEO_PYTHON": sys.executable}, stdout=sys.stderr, check=True,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    listing = commands.add_parser("list", help="List all playable bundled entries")
    listing.add_argument("--json", action="store_true")
    selector = commands.add_parser("suggest", help="Find motions that fit a described shot")
    selector.add_argument("request")
    selector.add_argument("--limit", type=int, default=3)
    commands.add_parser("info", help="Inspect a recipe, preview, constraints and frame anchors").add_argument("id")
    preview = commands.add_parser("preview", help="Locate or copy the verified reference preview")
    preview.add_argument("id")
    preview.add_argument("--out", type=Path)
    for name in ("scene", "render", "export"):
        command = commands.add_parser(name)
        command.add_argument("id")
        command.add_argument("--out", type=Path, required=True)
        command.add_argument("--content", type=Path, help="JSON containing this recipe's editable fields")
        command.add_argument("--fps", type=int, choices=(24, 25, 30, 60))
        command.add_argument("--duration", type=float, help="Desired duration in seconds (1.6–12)")
        if name in ("render", "export"):
            command.add_argument("--engine", choices=("pillow", "svg"), default="pillow")
    args = parser.parse_args()

    if args.command == "list":
        if not args.json:
            for row in inventory().values():
                print(f"{row['id']}\t{row['title']}")
            return
        result = [info(recipe_id) for recipe_id in inventory()]
    elif args.command == "suggest":
        result = suggest(args.request, args.limit)
    elif args.command == "info":
        result = info(args.id)
    elif args.command == "preview":
        row = info(args.id)
        preview_path = Path(row["preview"])
        if hashlib.sha256(preview_path.read_bytes()).hexdigest() != row["sha256"]:
            raise ValueError(f"Bundled preview failed its checksum: {args.id}")
        if args.out:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(preview_path, args.out)
        result = {"id": args.id, "preview": str(args.out.resolve() if args.out else preview_path)}
    else:
        out = args.out.resolve()
        asset_dir = None
        if args.command == "export":
            if out.exists() and (not out.is_dir() or any(out.iterdir())):
                raise ValueError("Choose a new or empty directory for the editable export.")
            scene = out / "scene.json"
            asset_dir = out / "assets"
        elif args.command == "render":
            if out.suffix.lower() != ".mp4":
                raise ValueError("The render output must end in .mp4.")
            scene = out.with_suffix(".scene.json")
        else:
            if out.suffix.lower() != ".json":
                raise ValueError("The scene output must end in .json.")
            scene = out
        result = materialize(args.id, scene, args.content, args.fps, args.duration, asset_dir)
        if args.command == "render":
            render(scene, out, args.engine)
            result["video"] = str(out)
            result["engine"] = args.engine
        elif args.command == "export":
            if args.engine == "svg":
                for file in (SVG_ENGINE, SVG_ENGINE.with_name("common.mjs")):
                    shutil.copyfile(file, out / file.name)
                runner = "node render_svg.mjs"
            else:
                shutil.copyfile(ENGINE, out / "render_pillow.py")
                shutil.copyfile(ENGINE.with_name("requirements.txt"), out / "requirements.txt")
                runner = "python3 render_pillow.py"
            result["engine"] = args.engine
            result["renderCommand"] = runner + " --scene scene.json --out film.mp4"
            (out / "render.txt").write_text(result["renderCommand"] + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        raise SystemExit(str(error))
