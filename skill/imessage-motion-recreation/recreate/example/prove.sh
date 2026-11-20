#!/usr/bin/env bash
set -euo pipefail
if [[ $# != 1 ]]; then
  echo "Usage: bash prove.sh NEW_OUTPUT_DIRECTORY" >&2
  exit 2
fi
example="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
recreate="$example/.."
output="$1"
if [[ -e "$output" ]]; then
  echo "Use a new output directory to preserve evidence." >&2
  exit 2
fi
mkdir -p "$output"
output="$(realpath "$output")"
check="$example/checks.json"

node "$example/reference/render.mjs" "$output/reference.mp4"
bash "$example/reproduce.sh" "$output/render"
python3 "$recreate/recreate.py" analyze "$output/reference.mp4" --out "$output/measurements"

expect_gate_failure() {
  local status=0
  python3 "$recreate/recreate.py" compare "$@" || status=$?
  if (( status != 1 )); then
    echo "Expected a comparison gate failure, received status $status." >&2
    return 1
  fi
}
expect_gate_failure "$output/reference.mp4" "$output/render/first.mp4" \
  --checks "$check" --out "$output/check-first" --sheets
python3 "$recreate/recreate.py" compare "$output/reference.mp4" "$output/render/final.mp4" \
  --checks "$check" --out "$output/check-final" --sheets
ffmpeg -nostdin -v error -i "$output/render/final.mp4" -map 0:v:0 -frames:v 110 \
  -c:v libx264 -preset ultrafast -crf 0 -color_range tv -colorspace bt709 -color_primaries bt709 \
  -color_trc bt709 "$output/truncated.mp4"
expect_gate_failure "$output/render/final.mp4" "$output/truncated.mp4" \
  --checks "$check" --out "$output/check-truncated"
python3 - "$output" <<'PY'
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
first, final, truncated = (
    json.loads((root / name / "report.json").read_text())
    for name in ("check-first", "check-final", "check-truncated")
)
assert first["failures"] == [{"check": "region", "id": "seat-selection", "spans": [[74, 77]]}], first
assert final["verdict"] == "PASS" and final["compared_frames"] == 120, final
assert truncated["mean_abs_rgb"] == 0 and truncated["compared_frames"] == 110, truncated
assert {"check": "missing_candidate_frames", "spans": [[110, 119]]} in truncated["failures"], truncated
print("Train picture, late-selection, truncation and source edit proofs passed.")
PY
