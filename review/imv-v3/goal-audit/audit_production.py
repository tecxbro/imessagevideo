#!/usr/bin/env python3
"""Verify the six main-branch reconstruction projects and their 30 exports."""
import argparse
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from hashlib import file_digest
import json
from pathlib import Path
import subprocess


def digest(file):
    with file.open("rb") as handle:
        return file_digest(handle, "sha256").hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def code_groups(root, examples):
    groups = defaultdict(list)
    for example in examples:
        project = root / example["project_root"]
        paths = {
            project / "README-COMPLETE-EXAMPLE.md", project / "tools/render_example.py",
            project / "scripts/final_encode.py", project / "scripts/add_reference_audio.py",
        }
        for movie in example["movies"]:
            paths.add(root / movie["entry_wrapper"])
            paths.update(root / path for path in movie["full_source_files"])
        paths.update(file for file in (project / "engines").rglob("*")
                     if file.is_file() and "node_modules" not in file.parts
                     and "__pycache__" not in file.parts)
        for file in sorted(paths):
            data = file.read_bytes()
            groups[digest(file)].append({
                "path": file.relative_to(root).as_posix(),
                "bytes": len(data), "lines": len(data.splitlines()),
            })
    return dict(groups)


def scene_summary(root, example):
    scene_file = root / example["scene"]["path"]
    require(digest(scene_file) == example["scene"]["sha256"], f"Scene bytes changed: {scene_file}")
    scene = json.loads(scene_file.read_text())
    kinds = Counter()
    properties = Counter()
    assets = set()
    keys = 0
    layers = list(scene["layers"])
    while layers:
        layer = layers.pop()
        kinds[layer["type"]] += 1
        layers.extend(layer.get("children", []))
        if layer.get("src") and not layer["src"].startswith("data:"):
            assets.add(layer["src"])
        for name, track in layer.get("keyframes", {}).items():
            if track:
                properties[name] += 1
                keys += len(track)
    assets.update(font["src"] for font in scene.get("fonts", []) if font.get("src"))
    require(all((scene_file.parent / asset).is_file() for asset in assets),
            f"Missing declared scene asset in {example['id']}")
    return {
        "id": example["id"], "scene_sha256": example["scene"]["sha256"],
        "dimensions": [scene["width"], scene["height"]], "scene_fps": scene["fps"],
        "scene_duration": scene["duration"], "source_mapping": scene.get("source"),
        "layer_types": dict(kinds), "keyframe_tracks": dict(properties),
        "key_entries": keys, "unique_image_and_font_paths": len(assets),
    }


def probe(file):
    result = subprocess.run([
        "ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0",
        "-show_entries", "stream=width,height,avg_frame_rate,nb_read_frames,duration",
        "-of", "json", str(file),
    ], check=True, capture_output=True, text=True)
    picture, = json.loads(result.stdout)["streams"]
    subprocess.run([
        "ffmpeg", "-v", "error", "-xerror", "-threads", "1", "-i", str(file),
        "-map", "0:v:0", "-map", "0:a?", "-f", "null", "-",
    ], check=True, capture_output=True, text=True)
    return {**picture, "full_decode": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("library", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    library = args.library.resolve()
    revision = subprocess.check_output(["git", "-C", str(library), "rev-parse", "HEAD"], text=True).strip()
    examples = json.loads((library / "LOCAL-LIBRARY.json").read_text())["examples"]
    require(len(examples) == 6, "Expected six declared production projects")
    code = code_groups(library, examples)
    media = defaultdict(list)
    for case in examples:
        require({movie["method"] for movie in case["movies"]}
                == {"pillow", "html", "gsap", "remotion", "motion-canvas"}, f"Incomplete matrix: {case['id']}")
        for item in [case["source"], *case["movies"]]:
            file = library / item["path"]
            checksum = digest(file)
            require(checksum == item["sha256"], f"Media bytes changed: {file}")
            media[checksum].append({**item, "case": case["id"]})
    with ThreadPoolExecutor(max_workers=4) as pool:
        jobs = {checksum: pool.submit(probe, library / matches[0]["path"])
                for checksum, matches in media.items()}
        scenes = [scene_summary(library, case) for case in examples]
        media_rows = [
            {"sha256": checksum, "paths": matches, **jobs[checksum].result()}
            for checksum, matches in media.items()
        ]
    for case in scenes:
        movies = [row for row in media_rows if any(
            item["case"] == case["id"] and "method" in item for item in row["paths"]
        )]
        require(len({(row["width"], row["height"], row["avg_frame_rate"], row["nb_read_frames"])
                     for row in movies}) == 1, f"Renderer clocks or dimensions disagree: {case['id']}")
        movie = movies[0]
        require([movie["width"], movie["height"]] == case["dimensions"],
                f"Encoded dimensions disagree with scene: {case['id']}")
        case["decoded_export_frames"] = int(movie["nb_read_frames"])
    result = {"local_revision": revision, "scenes": scenes, "runtime_code_groups": code, "media": media_rows}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(f"Six measured scenes, {sum(map(len, code.values()))} runtime paths, {len(code)} unique files")
    print(f"Decoded {len(media_rows)} unique source and final files across {sum(map(len, media.values()))} paths")


if __name__ == "__main__":
    main()
