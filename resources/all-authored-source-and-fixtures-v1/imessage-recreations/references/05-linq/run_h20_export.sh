#!/usr/bin/env bash
set -euo pipefail
cd /workspace/imessage-recreations
# Run sequentially after R20; this cache's actual baseline is immutable18.
node engines/render.mjs --method html --scene outputs/05-linq/final-v20/scene.json --out outputs/05-linq/html.mp4 --frames-dir outputs/05-linq/frames-html --ranges "$1"
python3 scripts/final_encode.py --only 05-linq --methods html
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 references/05-linq/verify_html_v20.py
