"""Render a moving shape through all five engines and check the final sound exports."""
from concurrent.futures import ThreadPoolExecutor
from hashlib import file_digest
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
SKILL = HERE.parents[1]
REPO = SKILL.parents[1]
ENGINES = SKILL / "scripts/engines"
AUDIO = REPO / "review/imv-v3/sound/masters/assets/select-place.wav"


def run(command):
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode:
        raise ValueError(f"{subprocess.list2cmdline(command)}: {result.stdout}\n{result.stderr}")
    return result.stdout


def checksum(path):
    with path.open("rb") as data:
        return file_digest(data, "sha256").hexdigest()


def check(method, output, plan):
    picture = output / f"{method}.mp4"
    room = output / method
    if method == "pillow":
        renderer = [sys.executable, str(ENGINES / "render_pillow.py")]
    elif method == "motion-canvas":
        renderer = ["node", str(ENGINES / "render_motion_canvas.mjs")]
    else:
        renderer = ["node", str(ENGINES / "render.mjs"), "--method", method]
    run([*renderer, "--scene", str(HERE / "renderer-smoke.scene.json"), "--out", str(picture)])

    sound = [sys.executable, str(HERE.parent / "sound.py")]
    run([*sound, "mix", str(plan), str(picture), str(room)])
    report = json.loads(run([
        *sound, "verify", str(plan), str(picture), str(room / "mix.mp4"),
        str(room / "manifest.json"), "--report", str(room / "check.json"),
    ]))
    landmark = report["landmarks"]["demo.amber.enter"]
    if landmark["frame"] != 12 or landmark["sample"] != 24000:
        raise ValueError(f"{method} resolved the wrong frame or sample: {landmark}")
    cue = report["cues"][0]
    return {
        "renderer": method,
        "picture_sha256": checksum(picture),
        "export_sha256": checksum(room / "mix.mp4"),
        "picture_event": landmark,
        "cue": cue,
    }


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: python3 check_renderers.py OUTPUT_DIR")
    output = Path(sys.argv[1]).resolve()
    output.mkdir(parents=True, exist_ok=True)
    plan = output / "renderer-smoke.plan.json"
    plan.write_text(json.dumps({
        "landmarks": {"demo.amber.enter": {
            "roi": [282 / 320, 70 / 180, 4 / 320, 30 / 180],
            "color": [236, 134, 87], "tolerance": 25, "min_fraction": 0.75,
            "settle_frames": 2,
        }},
        "cues": [{
            "id": "settle", "event": "demo.amber.enter", "asset": str(AUDIO),
            "bus": "effects", "purpose": "Mark the amber shape entering the far right.",
            "source": "Original procedure in masters/synthesize.py.",
            "offset_ms": 12, "onset_ms": 5.3125, "impact_ms": 10.479166667,
            "gain_db": -14, "tolerance_ms": 20,
        }],
    }) + "\n")
    methods = ["pillow", "gsap", "html", "remotion", "motion-canvas"]
    with ThreadPoolExecutor(max_workers=3) as pool:
        results = list(pool.map(lambda method: check(method, output, plan), methods))
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
