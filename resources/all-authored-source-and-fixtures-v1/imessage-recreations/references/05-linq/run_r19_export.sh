#!/usr/bin/env bash
set -euo pipefail
cd /workspace/imessage-recreations
# Run after the G19 visual/source gate; cache is still the actual17 baseline.
node engines/render.mjs --method remotion --scene outputs/05-linq/final-v19/scene.json --out outputs/05-linq/remotion.mp4 --frames-dir outputs/05-linq/frames-remotion --ranges "$1"
python3 scripts/final_encode.py --only 05-linq --methods remotion
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 references/05-linq/verify_primary_v19.py
