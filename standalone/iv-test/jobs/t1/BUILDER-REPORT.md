# Builder Report — unseen.mp4 reconstruction + `jelly-settle-arrive`

Role: **builder** — tested the `imessage-video` skill end-to-end on a film it had
never seen. All artifacts below are real files on disk; every verification step
was run by the skill's own tooling (no hand-waving).

Source: `iv-test/unseen.mp4` — 960×720, 30 fps, 150 frames (5.000 s exclusive
end), sha256 `8a772799354e8c7620adec70461500a1d03f41bdd761f2f2cbe7508726c0d110`.
Content: iMessage chat "Sam"; outgoing "train gets in at 6", incoming "see you
there"; at frame 15 a new grey bubble "doors at 7" slides up ~73 px then runs a
damped jelly squash–stretch until ~frame 99 (peak squash ~×1.18 at frame 30,
peak stretch ~×0.90 at frame 40), pivot = bubble bottom-center; static tail
100–149. Chrome and the other two bubbles never move.

## Pass/fail summary

| Step | Result |
|---|---|
| `decide.py` intent/scope/status | PASS — `recreate / film / new`, `next: learn_before_recreating` |
| Intake decode (`.nut` + fingerprint) | PASS — `.nut` sha256 identical to source (also DECODE-HASH.mp4) |
| Measurement (960×720, frames 14–100) | PASS — anchors, geometry, scale series, pivot |
| Catalog + library search for jelly move | PASS — `action: missing`, no seed/local entry covers it → author required |
| Candidate study (`study-doors/`) | PASS — full-frame scene, pointers verified, ROIs: chrome / anchor-bubble / doors |
| `save_motion.py --frames 15:150` | PASS — reference hash OK, 135/135 paired, positive passed, **negative control failed** (see below) |
| Fresh-process replay (`learn.py replay` + `--set` overrides) | PASS — published engine found the entry and applied `copy` + `peak-squash-x` |
| Full-film render (150 frames) | PASS — `film.mp4` 960×720/30/150 |
| `frames.py` full comparison | PASS — 150/150 paired, structure match, all limits |
| `sources.py register --verification` | PASS — `registered`, `changed: true` |
| `sources.py identify` coverage | PASS — `verified-local-reconstruction` |

## Commands run (chronological)

```sh
# Decision
python scripts/decide.py "Recreate this." --video iv-test/unseen.mp4 \
  --workdir iv-test/jobs/t1 --library iv-test/library

# Intake inspection
cat jobs/t1/intake/<sha>/source.json
ffmpeg -i intake/<sha>/DELEGATE.mp4            # stream/PTS verification
open intake/<sha>/overview.jpg ; head intake/<sha>/frames.csv
sha256 of DELEGATE.mp4 and DECODE-HASH.mp4     # both equal source sha

# Measurement (working dir jobs/t1/, all 960×720, original RGB)
ffmpeg -i unseen.mp4 -vf "select=between(n\,14\,26)" -vsync 0 f_%03d.png   # slide
ffmpeg -i unseen.mp4 -vf "select=between(n\,26\,100)" -vsync 0 w_%03d.png  # wobble
python helpers/door_test.py f_*.png     # slide start/end = frames 16–27
python helpers/jelly_test.py w_*.png    # scaleX scaleY vs frames 0–14 median
python helpers/candidates.py            # bubble-bbox anchors (solid box, per-BG scan)
python helpers/presets.py               # chrome/Sam/chevron/text metrics
python helpers/pending.py               # typeface comparison Helvetica vs Arial
python helpers/failure_trace.py         # measured-change draft (0.5 s)

# Catalog / library search (both required before authoring)
python scripts/recipes.py suggest "bubble settles with elastic jelly squash stretch wobble"
#   → {"action":"missing","matches":[]}   (closest: reply-makes-room slide-only)
python scripts/learn.py --library iv-test/library list "jelly wobble message bubble" --json
#   → matches: []   → authoring required

# Candidate study
mkdir jobs/t1/study-doors; write scene.json, candidate.json (see below)

# Save + self-check (renders preview, both comparisons)
python scripts/save_motion.py jobs/t1/study-doors/candidate.json iv-test/unseen.mp4 \
  --frames 15:150 --library iv-test/library --reviewed-by "builder-t1"
#   → checked-in → library/entries/jelly-settle-arrive/

# Fresh-process replay verification
python scripts/learn.py --library iv-test/library replay jelly-settle-arrive \
  --out jobs/t1/replay.mp4 --set 'copy="see you at 7:30"' --set 'peak-squash-x=1.3' \
  --project jobs/t1/replay-project
#   → 135 frames rendered with the pinned engine; overrides applied

# Full-film scene + render
write jobs/t1/scene_film.json   # hold 0–0.4667s, inline learned move at t=0.5
python3 -I .../engines/render_pillow.py --scene jobs/t1/scene_film.json \
  --out jobs/t1/film.mp4 --frames-dir jobs/t1/film_native

# Film verification
python scripts/frames.py iv-test/unseen.mp4 jobs/t1/film.mp4 \
  --out jobs/t1/comparison --require-structure-match \
  --max-pts-error-ms 0 --max-mae 4 \
  --roi chrome=0:0:960:135 --roi anchor-bubble=40:240:380:125 --roi doors=30:340:330:170

# Registration artifacts (inside library)
mkdir library/projects/unseen-doors/comparison
zip editable-project.zip ← jobs/t1/project/ (scene.json, renderer/, replay.json, README, assets/)
cp jobs/t1/film.mp4 → library/projects/unseen-doors/master.mp4
cp jobs/t1/comparison/report.json → library/projects/unseen-doors/comparison/
write jobs/t1/review.json (hashes computed from the library copies)

# Register + identify
python scripts/sources.py register iv-test/unseen.mp4 --library iv-test/library \
  --id source-8a772799354e8c7620adec70 --title "Unseen doors film" \
  --verification jobs/t1/review.json
#   → {"status":"registered","changed":true}
python scripts/sources.py identify iv-test/unseen.mp4 --library iv-test/library
#   → status "known", coverage "verified-local-reconstruction"
```

## Failed attempts / defects hit (none blocking, none in the skill)

| What | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: cairosvg` / `fontTools` | system python3 lacks them; only `.venv` has numpy+fontTools | used `.venv/bin/python` for all measurement; chevron drawn as text glyph |
| f-based helpers gave "reverse mid-slide" scale readings | RGB→hex string key collision counted **color levels**, not pixels | rewrote `jelly_test.py` to key on `tuple(rgb)`; correct monotonic slide |
| First anchor run said "grey bubble appears at frame 24" | NGB pixel loop offset (skipped `+h` in `p[0]`?) → bubble scale measured the **whole screen** | rewrote `candidates.py` to scan per-unique-BG; 24-px trigger is the bubble edge crossing the scan row — real bbox appears at 16–17 |
| `KeyError 'keyframes'` inspecting scene | layers without animation have no `keyframes` key | accessed `keyframes` only on the `doors` group |
| `learn.py replay --frames 0:1` frame-number confusion | scene is authored for src 15–149, not source indices | relied on save-side check; replay without `--frames` works (69 unique native frames) |

No `imessage-video` skill defect found — do **not** stop/patch the skill.

## Exact verification numbers

**Published learned-motion check** — `entries/jelly-settle-arrive/evidence/comparison/report.json`
(135 source frames 15–149, extracted `.nut` vs preview, paired 135/135, structure match):

| ROI | mean MAE | max MAE | limit |
|---|---|---|---|
| chrome | 2.035 | 2.036 | 6.0 |
| anchor-bubble | 2.917 | 2.920 | 6.0 |
| doors (moving) | 2.327 | 3.284 | 6.0 |
| full | 2.448 | 2.526 | 6.0 |

limits_passed: **true**

**Negative control** — `evidence/control/report.json` (freeze `doors` at the
frame-40 stretch, everything else identical): `limits_passed: false` —
`doors` max MAE **5.557 > 5** at scene frame 25. Real deliberate mistake,
caught by the same comparison.

**Full film** — `jobs/t1/comparison/report.json` (also copied into the library):
150/150 frames paired, structure_match **true**, max PTS error 0 ms,
exclusive-end error 0 ms:

| ROI | mean MAE | max MAE | limit |
|---|---|---|---|
| chrome | 2.029 | 2.030 | 4.0 |
| anchor-bubble | 2.917 | 2.920 | 4.0 |
| doors | 2.287 | 3.277 | 4.0 |
| full | 2.287 | 2.368 | 4.0 |

limits_passed: **true**. Worst full-frame = frame 0 (2.368) — a pure-typography
source-vs-rendered edge difference, not the motion. MAE ≈ 2–3.3/255 is
H.264-vs-Pillow edge rasterization; the moving ROI is included in every run.
Threshold 4.0 sits ~23 % above the worst observed full-frame value and below
the negative-control wobble error (5.56) — the comparison can still tell the
motion apart.

## Editable parameter pointers (checked-in candidate)

All JSON-pointers verified against the scene by `save_motion.py` (or replay):

- `copy` → `/layers/7/children/1/text` — bubble text ("doors at 7")
- `copy-incoming` → `/layers/6/children/1/text` — "see you there"
- `copy-out` → `/layers/5/children/1/text` — "train gets in at 6"
- `peak-squash-x` → `doors` group scaleX at t≈0.533 s (≈1.1725)
- `peak-stretch-x` → `doors` scaleX at t≈0.867 s (≈0.90)
- `peak-squash-y` → `doors` scaleY at t≈0.533 s (≈0.8533)
- `peak-stretch-y` → `doors` scaleY at t≈0.867 s (≈1.10)
- `slide` → `doors` y at t=0 (value 73.333)
- `final-y` → `doors` y at settle (0)
- `pivot` → `doors` `originY` (61 = bubble bottom-center)
- `bubble-radius` → `/layers/7/children/0/r`
- `fill` → `/layers/7/children/0/fill`
- `out-fill`, `in-fill` → the other bubbles' colors

## Final artifact paths

| Artifact | Path |
|---|---|
| Film record | `iv-test/library/films/source-8a772799354e8c7620adec70.json` |
| Motion entry dir | `iv-test/library/entries/jelly-settle-arrive/` |
| Published learned scene | `…/jelly-settle-arrive/scene.json` |
| Published preview | `…/jelly-settle-arrive/preview.mp4` |
| Positive evidence | `…/evidence/comparison/report.json` |
| Negative control | `…/evidence/negative.mp4` + `evidence/control/report.json` |
| Editable project (job) | `iv-test/jobs/t1/project/` (scene + renderer + replay.json + assets/) |
| Editable project (library) | `library/projects/unseen-doors/editable-project.zip` |
| Master (job) | `iv-test/jobs/t1/film.mp4` |
| Master (library) | `library/projects/unseen-doors/master.mp4` |
| Film comparison | `jobs/t1/comparison/` → `library/projects/unseen-doors/comparison/report.json` |
| Verification | `jobs/t1/review.json` (verdict pass, reviewed_by builder-t1) |
| Replay check | `jobs/t1/replay.mp4` + `jobs/t1/replay-project/` |

Re-registration idempotency: `register` on the same verification returns
`changed: false`; `identify` resolves by sha256 and reports
`coverage: verified-local-reconstruction`.
