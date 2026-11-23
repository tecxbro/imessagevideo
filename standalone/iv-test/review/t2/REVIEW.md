# INDEPENDENT REVIEW — t2 "Learn this swipe." (05-linq)

Reviewer artifacts in `/Users/darshan/Documents/video-analysis/iv-test/review/t2/`:
`src-frames/` (frames 1070–1145 decoded by reviewer), `verify_source.py`,
`verify_renders.py`, `source-check.json`, `render-check.json`, `decide-rerun.json`,
`prev-frames/`, `replay-frames/`, `generic-frames/`.

All numbers below are from the reviewer's own Pillow/numpy scripts (different ROIs,
different matching implementation), not the builder's.

## Verdict per claim

### 1. decide.py — PASS (rerun independently)
Reran with the venv python (system python3 lacks PIL → ImportError in intake.py,
a minor env note). Output `decide-rerun.json`: `intent=learn`, `scope=motion`,
identity `status=known` → `05-linq` ("Linq iMessage Apps", sha256
`86e22e69…bbf2eb` — I did not re-hash the input but the match record is
internally consistent), `documented_motions=[photos-under-fixed-heading]` with
`framesInclusive [1091,1111]`, `motion_choices.seed[0].id=photos-under-fixed-heading`,
`decision=inspect_candidates`, editable `heading, detail, photos, direction`. PASS.

### 2. Source evidence — PASS
Own decode of frames 1070–1145 (`src-frames/`). Visual: "Boqueria Soho" heading
static at [199,~24]…[406,~52]; photo rail sweeps left (storefront → octopus →
interior). Own ROI MAE (heading 195,15–660,110; rail 195,300–775,640):
- In the catalog window (pairs ending 1091–1112): heading mean **0.295 / max 1.72**;
  rail mean **51.25 / max 80.04** → rail ≈ 170× heading. Builder reported
  0.59/68.06 with slightly different ROIs — same conclusion.
- Title dark-pixel bbox constant `[199,24,406,52]` across 1080–1130 in my
  measurement (identical to builder's). At 1140 the whole card scrolls
  vertically (bbox changes) — confirms the swipe ends before the scroll.
- Rail motion span: my column-profile shift search shows leftward rail motion
  begins ~**1074–1078** (small −3…−8 px pairs, builder said ~1079 — within a
  few frames, threshold-sensitive), peak fling 1091–1111, deceleration tail
  1113–1129 (−30 → −1 px), stop ~1130–31, vertical scroll ~1135. Cadence
  confirmed: alternating ~0/high MAE pairs (15 fps content in 30 fps).

### 3. Exact trajectory match — PASS (independently re-derived)
`assets/seed/runtime/motion/packs/core.mjs:3`:
`photoOffsets = [0,22,22,47,76,109,148,148,195,252,324,417,417,542,698,846,956,956,1035,1094,1140]` (cumulative).
My own column-profile SAD shift search (band 195,310–775,630, ±220 px) measured
per-pair leftward shifts whose magnitudes are **exactly** the seed deltas:
22,0,25,29,33,39,0,47,57,72,93,0,125,156,148,110,0,79,59,46 for pairs
(1091→1092)…(1110→1111); sign negative = leftward = `direction:'left'`.
Cumulative 1140 px = last seed offset. Pair 1111→1112 = 37 px continues past the
catalog window, as builder noted. The seed literally encodes this film's measured
fling. Caveat: it covers only the 1091–1111 fling core; the ~1074–1090 lead-in
drag and 1113–1129 deceleration tail are not in the seed (builder disclosed this:
"catalog interval is the core/high-velocity interval"; the pack note says
"Normalized Linq rail shift"). PASS with nuance noted.

### 4. Saved-motion preview — PASS
`shasum -a 256` of `assets/seed/previews/photos-under-fixed-heading.mp4` =
`adce3885b489d68f1b595c43d8dee4c5f4dbb1b02de8480ce351fe97b89a59dd` = catalog/
recipe-info.json sha256. Own decode (72 frames, 720×480): heading band per-frame
MAE mean 0.0008/max 0.037, drift-vs-first max 0.044 — fixed; rail max 22.57 —
moving, active pairs 20–40 (declared events rail-start@20/rail-settle@39);
footer fixed. Title pixels at x137–326, zero drift, 72/72 frames. PASS.

### 5. bind-seed — PASS (failure is real, correctly not claimed as pass)
- Attempt A (`bind-seed-attempt.txt`): `Duration must be 1.6–12 seconds` — real.
- Attempt B: full pipeline ran; `bind-evidence/comparison/report.json`:
  `structure_match: true`, 49 compared frames, full-frame MAE
  **mean 82.22 / max 86.00**, rail ROI **mean 79.23 / max 90.63** vs
  `--max-mae 8` → `limits_passed: false`, worst frame 0/45. `worst.png` shows
  the real Boqueria UI vs stylized "Alpine field notes" art — a pixel bind is
  indeed infeasible for a "measured-adaptation" seed; builder recorded it as a
  limitation, not a pass. Library is clean: no `.bind-seed-*` temp dirs, no
  `film-bindings/`. PASS.

### 6. Replay with new content — PASS
Decoded `replay-new.mp4` (72 frames): heading reads **"Osteria Bella"** +
footer "Trattoria · West Village"; 4 authored photos (red/circle, teal/triangle,
mustard/stripes, violet/grid) sweep left frames ~20–39 while heading + footer
stay put. Own measurement: heading per-frame MAE mean **0.0002 / max 0.014**,
drift-from-first max **0.0168**; title left edge constant x=137, 0 px drift,
present 72/72; rail mean **10.14 / max 65.22**, active pairs 20–40; footer
drift max 0.022. Matches builder's 0.0002/0.016/0-drift claim. PASS.

### 7. Negative control — PASS
`generic-slide.scene.json` is a legit variant: the rail's x-keyframes were
copied onto `heading` and `footer` groups (verified by diffing scene JSONs —
only those keyframes differ). Decoded `generic-slide.mp4`: at frame 35 the
title and footer have slid off the card with the photos. Own measurement:
heading drift-from-first max **10.04** (builder 9.87), per-frame max **4.16**
(builder 3.87), footer drift **8.29** (builder 8.22), title dark pixels only in
first **24** frames (builder: 23; off-by-one from ROI/threshold — same
conclusion: heading departs ~frame 23–25). Builder's `heading_fixed=false`
flag is genuine. PASS.

## DEFECTS / notes (skill issues observed, none fabricated)

1. `scripts/decide.py` requires Pillow; fails under bare `python3` — works with
   the project venv. Doc/env nit, not a builder error.
2. `bind-seed` cannot bind the seed's own measured interval (0.7 s < 1.6 s
   minimum) and can never pixel-verify "measured-adaptation" seeds by
   construction — builder correctly flagged both as tool/doc gaps rather than
   hiding them.
3. Nuance, not a defect: actual rail drag begins ~frame 1074–1078 (builder said
   ~1079) and decelerates through ~1130; the seed encodes only the 1091–1111
   fling core, time-normalized onto 20 render frames. Honest, disclosed.
4. Builder's "title present 23/72" vs my 24/72 — threshold/ROI-level difference,
   conclusion identical.

## Overall

**PASS on every claim.** The seed `photos-under-fixed-heading` is provably a
measured adaptation of THIS exact Linq swipe — my independent column-profile
measurement reproduces the seed's `photoOffsets` deltas exactly (20/20 deltas,
1140 px total, leftward). Heading is positionally fixed during the gesture
(title bbox constant), the replay with new photos/heading keeps the heading
fixed while the rail moves, the negative control that moves the heading is
genuinely flagged, and the bind failure is real and honestly reported.
