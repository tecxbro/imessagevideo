#!/usr/bin/env bash
set -euo pipefail

if [[ $# != 1 ]]; then
  echo "Usage: bash reproduce.sh NEW_OUTPUT_DIRECTORY" >&2
  exit 2
fi

example="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
engine="$example/../../scripts/engines/render.mjs"
output="$1"
if [[ -d "$output" ]] && [[ -n "$(ls -A -- "$output")" ]]; then
  echo "Use a fresh output directory to preserve previous evidence." >&2
  exit 2
fi
mkdir -p -- "$output"
output="$(cd -- "$output" && pwd)"

render() {
  local scene="$1"
  local movie="$2"
  shift 2
  node "$engine" --method html --scene "$output/$scene.scene.json" --out "$output/$movie.mp4" "$@"
}

node "$example/scene.mjs" "$output/hardest.scene.json" --segment 70:83
render hardest hardest

node "$example/scene.mjs" "$output/first.scene.json" --config "$example/first.json" --events "$output/first.events.json"
render first first --frames-dir "$output/frames"
(
  cd -- "$output/frames"
  sha256sum -- ./*.png > "$output/native-before.sha256"
)

node "$example/scene.mjs" "$output/final.scene.json" --events "$output/final.events.json"
render final final --frames-dir "$output/frames" --ranges 74:77
(
  cd -- "$output/frames"
  sha256sum -- ./*.png > "$output/native-after.sha256"
)

node "$example/scene.mjs" "$output/edited.scene.json" --config "$example/edited.json" --events "$output/edited.events.json"
render edited edited

python3 "$example/verify.py" "$output"
(
  cd -- "$output"
  sha256sum -- hardest.mp4 first.mp4 final.mp4 edited.mp4 > exports.sha256
)
