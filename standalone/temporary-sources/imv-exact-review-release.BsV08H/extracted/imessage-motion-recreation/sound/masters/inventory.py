"""Probe the library media used to prepare the independent sound comparison."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import subprocess


REPO = Path(__file__).resolve().parents[4]
METHODS = ("pillow", "gsap", "remotion", "html", "motion-canvas")


def inspect(item):
    path, role, expected = item
    if not path.is_file():
        raise ValueError(f"{path} is absent. Restore the archive with tools/sync_library.py.")
    command = [
        "ffprobe", "-v", "error", "-of", "json", "-show_entries",
        "stream=codec_type,codec_name,sample_rate,channels,avg_frame_rate,nb_frames,start_time,duration",
        str(path),
    ]
    streams = json.loads(subprocess.check_output(command))["streams"]
    types = sorted(stream["codec_type"] for stream in streams if stream["codec_type"] in {"video", "audio"})
    if types != sorted(expected):
        raise ValueError(f"{path} has {types}, expected {expected}")
    with path.open("rb") as data:
        digest = hashlib.file_digest(data, "sha256").hexdigest()
    return {"path": path.relative_to(REPO).as_posix(), "role": role, "sha256": digest, "streams": streams}


def inputs():
    outputs = REPO / "resources/silent-picture-masters-v1/imessage-recreations/outputs"
    projects = sorted((REPO / "projects").glob("*-complete-v1"))
    if len(projects) != 6:
        raise ValueError("Six restored complete projects are required. Run tools/sync_library.py.")
    for project in projects:
        film = project.name.removesuffix("-complete-v1")
        base = project / "imessage-recreations"
        yield base / "references" / film / "source.mp4", "original picture with reference soundtrack", ("video", "audio")
        for method in METHODS:
            yield outputs / film / f"{method}.mp4", "silent picture master", ("video",)
            yield (
                base / "deliverables" / film / f"{method}.mp4",
                "accepted reconstructed picture with historical reference-audio mux",
                ("video", "audio"),
            )

    archive = REPO / "resources/complete-ui-audio-source-v1/imessage-recreations/audio-recreation"
    for sample in sorted((archive / "library/prepared").glob("*.wav")):
        yield sample, "prepared independent effect (historical CC0 library)", ("audio",)
    yield archive / "ai/04-poke/music.mp3", "historical generated music source", ("audio",)
    for name, role in [
        ("ui", "historical constructed UI effects stem"),
        ("music", "historical prepared music stem"),
        ("full_mix", "historical finished mix"),
        ("ui_preview", "historical effects-only review mix"),
    ]:
        yield archive / "ui-mixes/04-poke" / f"{name}.m4a", role, ("audio",)


if __name__ == "__main__":
    with ThreadPoolExecutor(max_workers=4) as pool:
        print(json.dumps(list(pool.map(inspect, inputs())), indent=2))
