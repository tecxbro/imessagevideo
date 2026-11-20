#!/usr/bin/env bash
# Run Train Options from an extracted skill, then repeat its final render in isolation.
set -euo pipefail
if (( $# != 1 )); then
  echo "Usage: bash verify-clean-runner.sh NEW_OUTPUT_DIRECTORY" >&2
  exit 2
fi
recreate="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
skill="$(dirname "$recreate")"
output="$1"
if [[ -e "$output" ]]; then
  echo "Choose a new output directory." >&2
  exit 2
fi
command -v bwrap >/dev/null
mkdir -p -- "$output"
output="$(realpath -e -- "$output")"

bash "$recreate/example/prove.sh" "$output/train"
mkdir -p -- "$output/render-input/engine"
cp -- "$output/train/render/final.scene.json" "$output/render-input/scene.json"
cp -a -- "$skill/scripts/engines/." "$output/render-input/engine"

bash "$recreate/isolated-render.sh" "$output/render-input" "$output/isolated" \
  bash -euc '
    test ! -e "$1"
    test ! -e "$2"
    test ! -e "/proc/1/root$1"
    test ! -e "/proc/1/root$2"
    exec node /input/engine/render.mjs --method html --scene /input/scene.json --out /output/final.mp4
  ' _ "$output/train/reference.mp4" "$output/train/measurements"

cmp -- "$output/train/render/final.mp4" "$output/isolated/final.mp4"
python3 - "$output/train" <<'PY'
import csv
import json
from pathlib import Path
import sys

root = Path(sys.argv[1])
for check, paired in (("check-final", 120), ("check-truncated", 110)):
    evidence = root / check
    report = json.loads((evidence / "report.json").read_text())
    with (evidence / "frames.csv").open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert [row["reference_frame"] for row in rows] == [str(i) for i in range(120)]
    assert [row["candidate_frame"] for row in rows] == [str(i) for i in range(paired)] + [""] * (120 - paired)
    assert rows[-1]["reference_end_pts_exclusive"] == str(report["reference"]["clock"]["end_pts_exclusive"])
    assert rows[paired - 1]["candidate_end_pts_exclusive"] == str(report["candidate"]["clock"]["end_pts_exclusive"])
PY
(
  cd -- "$output"
  sha256sum -- train/reference.mp4 train/render/final.mp4 isolated/final.mp4 > SHA256SUMS
  sha256sum -c SHA256SUMS
)
