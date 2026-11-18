#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../.." && pwd)"
PYTHON="${PYTHON:-$HOME/work/rw/.venv/bin/python}"
if [[ ! -x "$PYTHON" ]]; then PYTHON=python3; fi
export CHROME_PATH="${CHROME_PATH:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
"$PYTHON" "$HERE/export.py" --out "${1:-$HOME/work/rw/exports/readwise-first-export.mp4}"
