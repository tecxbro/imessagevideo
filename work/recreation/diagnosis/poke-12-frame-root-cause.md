# Poke restaurant-selection 12-frame defect — root cause and catch-check

Defect recorded in FAILURES-AND-FIXES.md: the blue selection check on the
restaurant sheet ("Anything catching your eye?" → Zareen's row) appears at
source frame 633 but at accepted GSAP frame 645.

## Root cause

- The two painted layers are `p0249` (56px circle, fill #0b9ae9) and `p0250`
  (white "✓" glyph), children of sheet group `p0255` in
  `projects/04-poke-complete-v1/imessage-recreations/scenes/04-poke/scene.json`.
- Both carry a hardcoded `start: 21.5` written by hand in the original builder
  `references/04-poke/build_scene.py` line ~170
  (`node('circle',...,fill='#0b9ae9',start=21.5)`). The value was an authored
  estimate — every later revision (v8–v19) re-measured sheet trajectories,
  glyph ink and camera poses but never re-measured this pop-in time, so the
  estimate survived into the frozen scene.
- Measured ground truth (saturated-blue pixel detection on the row region):
  source first paints the circle at frame 633 (t=21.121s), held while the
  sheet is stationary (bbox y 476-531 constant frames 633-645). The GSAP
  deliverable first paints it at frame 645 (t=21.521s), by which time the
  sheet has started moving. Exact Δ = +12 frames = +0.40s.
- Corrected scene (`work/recreation/poke-check/scene-corrected.json`) sets
  `start = 633*1001/30000 = 21.1211` on both layers. Rendered frames prove:
  original 633 = no blue, corrected 633 = blue circle 2323px at the same
  location (see `poke-check/corr-633.png` vs `orig-633.png`).

## Why the aggregate metrics missed it

- The check is ~2,377 px of a 1,555,200 px frame (~0.15%). A 12-frame pop-time
  error contributes ≲0.3 to whole-frame MAE — invisible under the existing
  ~2.4-2.5 MAE noise floor in that window (film grain, artwork, compression).
- The every-frame timeline scan (verification/timeline-scans/04-poke-v19)
  shows MAE 2.52-2.54 at frames 633-644, *below* the film mean of 2.61 — the
  error literally sits under the average.
- The sparse "peak segments" review sampled ~24 frames, none inside 633-644.
- Conclusion: whole-frame averages and sparse peak review cannot catch
  small-region discrete-event timing errors. Event *times* must be compared
  directly.

## The check that catches it — `work/recreation/event_check.py`

Builds a per-film event map on a 24px spatial grid and matches events by
mutual-best-match (kind + hue + location):

- Tier 1 color onsets: saturated-ink pixel counts per hue-bin per cell;
  appear/disappear onsets must persist ≥5 frames (rejects codec flicker).
- Tier 2 change onsets: |F(t)-F(t-1)| hot-cell clusters (≥3 cells) that are
  quiet before AND after — a pop to a new stable state, not a motion streak.
- Report: matched events with frame offset (|offset|>2 → FAIL flag),
  unmatched reference events → warnings (independent artwork legitimately
  differs).

### Proof

- Accepted GSAP vs source, full film:
  `FLAG color/appear ref=633 cand=645 offset=12 bbox=[1080,480,1152,552]`
  — exact defect caught (52 total flags ≈4% of detected events, all
  reviewable by bbox+frame; report `diagnosis/event-check-gsap-v19.json`).
- Windowed re-run frames 600-700: same flag at ref-offset 33 (=633) +12.
- Corrected scene frames 600-700 rendered with the real GSAP engine
  (`poke-check/corr-frames/`): the 633-appear flag is GONE. Remaining flags
  are unrelated small residuals (offset 4 at frame 614 artwork edge; one
  ambiguous change-match at 688 during sheet dismissal) — the same class of
  residual error the project already documents.

### Usage in the pipeline

Run before accepting any export:
`python3 event_check.py --ref source.mp4 --cand candidate.mp4`
Any FLAG row names the frame, offset and bbox — eyeball the 2-3 frames
around it. The agent then re-measures that event in the source (as done
above) and patches the exact layer start/keyframe, not a global shift.
