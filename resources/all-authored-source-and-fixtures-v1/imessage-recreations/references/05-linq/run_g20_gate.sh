#!/usr/bin/env bash
set -euo pipefail
cd /workspace/imessage-recreations
# Run only after final-v20 is frozen and the actual18 cache is verified.
node engines/render.mjs --method gsap --scene outputs/05-linq/final-v20/scene.json --out outputs/05-linq/gsap.mp4 --frames-dir outputs/05-linq/frames-gsap --ranges "$1"
python3 scripts/final_encode.py --only 05-linq --methods gsap
python3 verification/scan_timeline.py references/05-linq/source.mp4 outputs/05-linq/gsap.mp4 --out verification/timeline-scans/05-linq-v20-pc709
python3 verification/compare.py references/05-linq/source.mp4 outputs/05-linq/gsap.mp4 --segments verification/timeline-scans/05-linq-v20-pc709/peak-segments.json --times 0 --batch-native --out verification/final/05-linq/source-gsap-v20-pc709
