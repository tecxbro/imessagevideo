"""Recreate, guard, register and reopen the benchmark's independent short."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
from zipfile import ZIP_DEFLATED, ZipFile

from direction_and_edit import SKILL, decide, run, write
from measure_tether import author
from tether_sound import make_sound

sys.path.insert(0, str(SKILL / "scripts"))
from frames import sha256


def ffmpeg(*args):
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", *map(str, args)], check=True)


def verification(source, movie, folder, recipe, expect=0, *, audio=True):
    checks = recipe["checks"]
    rois = []
    for key, box in checks["rois"].items():
        rois += ["--roi", key + ":" + ",".join(map(str, box))]
    run("frames.py", source, movie, "--out", folder, "--require-structure-match",
        "--max-pts-error-ms", 0, "--max-mae", checks["max_mae"], *rois,
        *(["--check-audio"] if audio else []), expected=expect)
    report = json.loads((folder / "report.json").read_text())
    assert report["limits_passed"] is (expect == 0)
    return report


def snapshot(folder):
    return {file.relative_to(folder).as_posix(): sha256(file)
            for file in folder.rglob("*") if file.is_file() and not file.name.startswith(".")}


def portable_replay(project, destination, *, late=False):
    work = destination.parent
    command = json.loads((project / "replay.json").read_text())["command"]
    scene = project / "scene.json"
    if late:
        shifted = json.loads(scene.read_text())
        for layer in shifted["layers"]:
            for keys in layer.get("keyframes", {}).values():
                for key in keys:
                    key["t"] += 2 / 30
        scene = write(work / "two-frame-delay.scene.json", shifted)
    subprocess.run([
        sys.executable, "-I", str(project / command[2]), "--scene", str(scene),
        "--out", str(destination), *command[7:],
    ], cwd=work, check=True, stdout=subprocess.DEVNULL)


def recreate(source, output, library, reviewer):
    initial = decide(output / "initial.json", library, "Recreate this.", "--video", source)
    assert initial["next"] == "learn_before_recreating" and initial["sources"][0]["identity"]["status"] == "new"
    assert initial["intent"] == "recreate"
    candidate = output / "candidate"
    author(source, candidate)
    recipe = json.loads((candidate / "candidate.json").read_text())
    mid = recipe["id"]
    receipt = json.loads(run("save_motion.py", candidate / "candidate.json", source, "--frames", "0:90",
                             "--library", library, "--reviewed-by", reviewer))
    write(output / "learned.json", receipt)
    film = receipt["film"]["id"]
    assert receipt["film"]["changed"] and receipt["motion"] == mid
    project = output / "editable"
    picture = output / "picture.mp4"
    run("learn.py", "--library", library, "replay", mid, "--out", picture, "--project", project)
    saved = library / "entries" / mid / "preview.mp4"
    assert sha256(saved) == sha256(picture)
    shutil.copyfile(Path(__file__).with_name("tether_sound.py"), project / "tether_sound.py")
    stem = project / "sound.wav"
    make_sound(stem)
    master = output / "recreated.mp4"
    ffmpeg("-i", picture, "-i", stem, "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy",
           "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", master)
    comparison = output / "comparison"
    positive = verification(source, master, comparison, recipe)
    assert positive["compared_frames"] == 90 and positive["audio"]["tracks"][0]["decoded_samples"] == [144000, 144000]

    reopened = output / "reopened"
    shutil.copytree(project, reopened)
    from_code = reopened / "fresh-render.mp4"
    portable_replay(reopened, from_code)
    assert sha256(from_code) == sha256(picture)

    delayed_picture = output / "two-frame-delay-picture.mp4"
    portable_replay(reopened, delayed_picture, late=True)
    delay = output / "two-frame-delay.mp4"
    ffmpeg("-i", delayed_picture, "-i", master, "-map", "0:v:0", "-map", "1:a:0",
           "-c", "copy", delay)
    delayed_report = verification(source, delay, output / "rejected-delay", recipe, 1)
    assert delayed_report["compared_frames"] == 90
    assert delayed_report["structure_match"] and delayed_report["audio"]["limits_passed"]
    assert any("MAE" in error for error in delayed_report["failures"])

    cutoff = output / "short-ending.mp4"
    ffmpeg("-i", master, "-map", "0:v:0", "-map", "0:a:0", "-t", "2.8", "-c:v", "libx264",
           "-crf", "16", "-pix_fmt", "yuv420p", "-c:a", "aac", cutoff)
    short_report = verification(source, cutoff, output / "rejected-short-end", recipe, 1)
    assert short_report["source_only_tail_frames"] == 6

    silent = output / "missing-audio.mp4"
    ffmpeg("-i", master, "-map", "0:v:0", "-c:v", "copy", "-an", silent)
    silent_report = verification(source, silent, output / "rejected-missing-audio", recipe, 1)
    assert silent_report["audio"]["failures"] == ["different audio stream counts"]
    verification(source, silent, output / "picture-only-control", recipe, audio=False)

    storage = library / "projects" / film
    storage.mkdir(parents=True)
    archive = storage / "editable.zip"
    with ZipFile(archive, "w", compression=ZIP_DEFLATED) as bundle:
        for path in sorted(project.rglob("*")):
            if path.is_file():
                bundle.write(path, path.relative_to(project))
    shutil.copyfile(archive, output / "editable.zip")
    registered_master = storage / "recreated.mp4"
    shutil.copyfile(master, registered_master)
    for name in ("report.json", "frames.csv", "worst.png"):
        shutil.copyfile(comparison / name, storage / name)
    reconstruction = {}
    for label, path in (("editable_project", archive), ("master", registered_master),
                        ("comparison", storage / "report.json")):
        reconstruction[label] = {"path": path.relative_to(library).as_posix(), "sha256": sha256(path)}
    review = write(output / "film-review.json", {
        "verdict": "pass", "reviewed_by": reviewer, "source_sha256": sha256(source),
        "recipe_ids": [mid], "reconstruction": reconstruction,
    })
    registration = json.loads(run("sources.py", "register", source, "--library", library, "--id",
                                  film, "--title", source.stem, "--verification", review))
    assert registration["changed"]
    files = snapshot(library)
    restart = output / "restart"
    restart.mkdir()
    second = decide(restart / "receipt.json", library, "Recreate this.", "--video", source)
    assert second["next"] == "return_verified_editable_project_and_master"
    known = second["sources"][0]["identity"]["matches"]
    assert len(known) == 1 and known[0]["recipe_ids"] == [mid]
    assert sha256(library / known[0]["reconstruction"]["master"]["path"]) == sha256(master)
    assert snapshot(library) == files
    write(output / "reuse.json", {"fresh_process": True, "same_request": second["request"] == initial["request"],
                                  "artifacts_unchanged": True, "library_files_checked": len(files),
                                  "library_recipe_count": len(list((library / "entries").iterdir())),
                                  "verified_project": reconstruction})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("library", type=Path)
    parser.add_argument("--reviewer", required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    recreate(args.source.resolve(), args.output.resolve(), args.library.resolve(), args.reviewer)
