#!/usr/bin/env python3
"""Stage an editable Poke project with the measured selection onset."""

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "projects/04-poke-complete-v1/imessage-recreations"
SCENE = PROJECT / "scenes/04-poke/scene.json"
SCENE_SHA256 = "bf46102ecdc578cdadac244ba85dec7e5ab19fe07b80277a2fdcdb4c2b191df1"
RATE = Fraction(30000, 1001)
SELECTION_FRAME = 633
SELECTION_LAYERS = {"p0249", "p0250"}


def walk(layers):
    for layer in layers:
        yield layer
        yield from walk(layer.get("children", []))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("work", type=Path, help="New output directory")
    args = parser.parse_args()
    raw = SCENE.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SCENE_SHA256:
        raise ValueError("The accepted Poke scene differs from the pinned input")
    scene = json.loads(raw)
    layers = [layer for layer in walk(scene["layers"]) if layer["id"] in SELECTION_LAYERS]
    if {layer["id"] for layer in layers} != SELECTION_LAYERS or len(layers) != 2:
        raise ValueError("Expected exactly one selected circle and one checkmark")
    for layer in layers:
        layer["start"] = float(SELECTION_FRAME / RATE)

    args.work.mkdir(parents=True)
    shutil.copytree(SCENE.parent, args.work, dirs_exist_ok=True, ignore=shutil.ignore_patterns("scene.json"))
    (args.work / "scene.json").write_text(json.dumps(scene, ensure_ascii=False, separators=(",", ":")) + "\n")


if __name__ == "__main__":
    main()
