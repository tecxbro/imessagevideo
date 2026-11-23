#!/usr/bin/env bash
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
reference="${1:?Usage: bash review.sh REFERENCE.mp4 CANDIDATE.mp4 REVIEW_DIR}"
candidate="${2:?Pass the encoded candidate MP4}"
out="${3:?Pass the review output directory}"
skill="${SIDEHOE_SKILL:-$here/../../codex-trial/skill/imessage-motion-recreation}"
python_exe="${PYTHON:-python3}"
hyperframes="${HYPERFRAMES:-hyperframes}"

mkdir -p "$out"
export HYPERFRAMES_NO_TELEMETRY=1 HYPERFRAMES_NO_UPDATE_CHECK=1 HYPERFRAMES_SKIP_SKILLS=1
"$hyperframes" --version > "$out/hyperframes-version.txt"

hf_status=0
"$hyperframes" diff "$reference" "$candidate" --worst 8 \
  --out "$out/hyperframes" --json > "$out/hyperframes.json" &
hf_pid=$!

exact_status=0
"$python_exe" "$skill/recreate/recreate.py" compare "$reference" "$candidate" \
  --exact --checks "$here/comparison-checks.json" --pairs --crops --sheets \
  --out "$out/native" > "$out/native.log" || exact_status=$?
wait "$hf_pid" || hf_status=$?

printf 'HyperFrames exit %d\nNative comparison exit %d\n' "$hf_status" "$exact_status" \
  | tee "$out/status.txt"
if (( hf_status != 0 || exact_status != 0 )); then
  exit 1
fi
