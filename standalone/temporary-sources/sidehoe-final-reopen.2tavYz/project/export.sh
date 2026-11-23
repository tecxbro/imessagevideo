#!/usr/bin/env bash
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
out="${1:?Usage: ./export.sh OUTPUT_DIR FRAME_CACHE [--reuse-cache]}"
cache="${2:?Usage: ./export.sh OUTPUT_DIR FRAME_CACHE [--reuse-cache]}"
python_exe="${PYTHON:-python3}"
mkdir -p "$out" "$cache"
if [[ "${3:-}" != "--reuse-cache" ]]; then
  "$python_exe" "$here/render.py" --cache "$cache" --frames 0:212 & first=$!
  "$python_exe" "$here/render.py" --cache "$cache" --frames 213:397 & second=$!
  "$python_exe" "$here/render.py" --cache "$cache" --frames 398:623 & third=$!
  "$python_exe" "$here/render.py" --cache "$cache" --frames 624:777 & fourth=$!
  wait "$first"
  wait "$second"
  wait "$third"
  wait "$fourth"
fi
"$python_exe" "$here/sound.py" --out "$out/sound"
ffmpeg -nostdin -hide_banner -loglevel error -y -framerate 25 -start_number 0 -i "$cache/%06d.png" \
  -vf 'scale=2000:2000:flags=lanczos,setsar=1' -frames:v 778 -an \
  -c:v libx264 -preset veryfast -crf 16 -pix_fmt yuv420p -video_track_timescale 60000 \
  -movflags +faststart "$out/picture.mp4"
ffmpeg -nostdin -hide_banner -loglevel error -y -i "$out/picture.mp4" -i "$out/sound/mix.wav" \
  -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -video_track_timescale 60000 \
  -movflags +faststart "$out/sidehoe.mp4"
