"""Extract bounded source motions as frame-addressed observations."""
import argparse
import csv
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "recreate"))
from analyze import inspect, measure_landmarks
from media import MediaError, digest, video_clock, write_json


def extract(source, plan, output, measurements=None):
    if output.exists():
        raise MediaError(f"Choose a new extraction folder: {output}")
    clock = video_clock(source)
    plan_sha = digest(plan)
    output.mkdir(parents=True)
    measure_landmarks(source, plan, output, measurements)
    if digest(plan) != plan_sha:
        raise MediaError("Landmark plan changed during extraction")
    landmark_report = json.loads((output / "landmarks.json").read_text(encoding="utf-8"))
    observations = {track["id"]: [] for track in landmark_report["tracks"]}
    with (output / "landmarks.csv").open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            frame = int(row["frame"])
            if int(row["pts"]) != clock.pts[frame]:
                raise MediaError(f"Source presentation timestamp changed at frame {frame}")
            sample = {"frame": frame, "pts": clock.pts[frame], "pixels": int(row["pixels"])}
            if sample["pixels"]:
                sample["centroid"] = [float(row["centroid_x"]), float(row["centroid_y"])]
                sample["bounds"] = [int(row[k]) for k in ("x", "y", "width", "height")]
            observations[row["id"]].append(sample)
    tracks = []
    for index, track in enumerate(landmark_report["tracks"], 1):
        samples = observations[track["id"]]
        if [item["frame"] for item in samples] != list(range(track["start"], track["end"] + 1)):
            raise MediaError(f"Incomplete decoded coverage for {track['id']}")
        evidence = f"track-{index:02d}"
        inspection = output / evidence
        inspect(source, inspection, [(track["start"], track["end"])], rect=track["rect"], measurements=measurements)
        record = json.loads((inspection / "inspect.json").read_text(encoding="utf-8"))
        if record["source_sha256"] != landmark_report["source_sha256"]:
            raise MediaError("Source changed between tracking and evidence extraction")
        for sample in samples:
            crop = inspection / f"frame-{sample['frame']:06d}.png"
            sample["evidence"] = {"path": str(crop.relative_to(output)), "sha256": digest(crop)}
        tracks.append({
            "actor": track["id"], "searchRect": track["rect"], "samples": samples,
            "unobservedFrames": [sample["frame"] for sample in samples if "bounds" not in sample],
        })
    result = {
        "version": 1, "sourceSHA256": landmark_report["source_sha256"],
        "clock": clock.summary(), "planSHA256": plan_sha,
        "method": "bounded decoded RGB landmark observations",
        "status": "needs-actor-review", "tracks": tracks,
    }
    write_json(output / "motion-observations.json", result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--measurements", type=Path)
    args = parser.parse_args()
    try:
        result = extract(args.source, args.plan, args.out, args.measurements)
        print(json.dumps({"motionObservations": str(args.out / "motion-observations.json"),
                          "tracks": len(result["tracks"]), "status": result["status"]}))
    except (MediaError, OSError, TypeError, KeyError, ValueError) as error:
        parser.exit(1, f"{error}\n")


if __name__ == "__main__":
    main()
