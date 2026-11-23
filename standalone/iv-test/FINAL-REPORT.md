# iMessage Video skill — real-video test report

Skill under test: `skill/imessage-video` on branch `imessage-video-decision-layer`
Worktree: `/Users/darshan/Documents/video-analysis/imessagevideo-dl`
Test root: `/Users/darshan/Documents/video-analysis/iv-test`
Builder + independent reviewer on every case; all reviewer verdicts reproduced from artifacts.

## Results

| # | Request | Verdict | Playable output | Editable code | Comparison evidence | Review |
|---|---------|---------|-----------------|---------------|--------------------|--------|
| 1 | "Recreate this." | **PASS** | `jobs/t1/film.mp4` (960×720@30, 150f) | `library/entries/jelly-settle-arrive/scene.json`, `jobs/t1/project/scene.json`, `library/projects/unseen-doors/` | `jobs/t1/comparison/report.json` (150/150 paired, full MAE 2.37, doors 3.28, structure match); learned-motion evidence `library/entries/jelly-settle-arrive/evidence/` | `review/t1/REVIEW.md` PASS |
| 2 | "Learn this swipe." | **PASS** | `jobs/t2/replay-new.mp4` (new photos + "Osteria Bella" heading) | `jobs/t2/scene.json`, seed recipe `photos-under-fixed-heading` | source measure: rail ROI 68.06 vs heading ROI 0.59; rail trajectory = seed `photoOffsets`; generic-slide control `jobs/t2/generic-slide.mp4` fails as designed | `review/t2/REVIEW.md` PASS |
| 3 | "Make an iMessage video about two friends getting concert tickets." | **PASS** | `jobs/t3/film.mp4` (720×480@30, 288f, 9.6s) | `jobs/t3/v1-final.json` → `v2-final.json` plans, `pitch-v1.md`/`pitch-v2.md`, `approved.json` | goal change browse→`swipe-to-quote`, only that shot touched; quote proof shows "YES. Get us in!" + "Replying to Maya"; approval hash matched pitch revision | `review/t3/REVIEW.md` PASS |
| 4 | "Change this message to 'Meet at the doors' and replace this shot's motion with the swipe from this second clip." | **PASS** | `jobs/t4/film-v2.mp4` (720×480@30, 288f) | `jobs/t4/plan-v4.json`, `patch-*.json` diffs | text exact; donor resolved to `photos-under-fixed-heading`; heading ROI 0.001 (fixed) vs rail ROI 43 (moving); boundary frames inspected; unaffected shots byte-identical to reused previews (≤0.32 MAE re-encode noise vs prior film) | `review/t4/REVIEW.md` PASS |
| 5 | Audit all 77 motions | **PASS — 77/77** | `jobs/t5/renders/*.mp4` + fresh `renders-fix/` | `assets/seed/runtime/motion/packs/*.mjs` + `catalog.json` | `jobs/t5/audit-results.json`: all previews sha-verified, fresh renders match previews (max MAE ~0.5–1.2), motion present in all | `review/t5a`–`t5d`: 77/77 visual pass; `review/t5-fix` fix PASS |

### Restart/reuse check (T1 second session)
Resubmitting "Recreate this." in a fresh session → `status: known`, `verified-local-reconstruction`, `return_verified_editable_project_and_master`; no duplicate entry (library still has exactly `jelly-settle-arrive` + seed `toggle-thumb-then-tint`).

### Recognition check (T2 suite)
All six originals → `known` via sha256. Resized Linq swipe excerpt (35–38 s) → `candidate` mapped to the correct source window (35–37.5 s). Full 960→540 px resize → `candidate`, 82 matched samples. A near-static excerpt of a flat passage → `new` — documented behavior (anti-flat-shot guard needs ≥3 distinct signatures + 2 textured samples); not a defect.

### Comparison-sensitivity proof (sabotage)
Against the verified T1 source/master pair, using the same comparison config (`--max-mae 5`, `--require-structure-match`, `--max-pts-error-ms 0`, ROIs doors/chrome/anchor-bubble):

| Bad render | Result | Caught by |
|---|---|---|
| `sabotage/shifted2.mp4` (gesture +2f) | **FAIL**, exit 1 | doors ROI max MAE 12.54 > 5 (`sabotage/evidence-shifted2/report.json`) |
| `sabotage/cutshort.mp4` (135/150f) | **FAIL**, exit 1 | different frame_count, out-of-tolerance end timestamp, incomplete timeline, MAE (`sabotage/evidence-cutshort/report.json`) |

Contrast run without ROIs: the same shifted render **passes** full-frame-only (MAE 3.63 < 5) — `sabotage/evidence-shifted2-noroi/report.json`. The moving-ROI checks are the operative gate for local re-timing errors; the verified T1 comparison includes them.

## Failures found → fixed → re-verified

| Defect | Fix | Re-verification |
|---|---|---|
| `selection-confirm` + 22 other entries rendered the shared "Alpine field notes" heading bar but did not declare `heading` editable — `materialize` rejected it, so every replay carried frozen sample chrome | `heading` added to `editable`/`editableFields` for all 23 entries (`packs/inherited.mjs`, `packs/media.mjs`, `catalog.json`) | render with `{"heading":"Concert tickets"}` → bar shows new text; 23/23 fresh renders still match previews (defaults unchanged); pack↔catalog sync verified; reviewer `review/t5-fix` PASS |
| `bind-seed` cannot bind catalog intervals <1.6 s or pixel-verify stylized `measured-adaptation` seeds against real footage (docs presented it as the association path without limits) | documented both limits in `references/sources.md` | doc-only; recognition path (visual fingerprint `candidate`) verified as the working alternative |
| (disclosed, not fixed — literal scope) T4 film-v2 leaves the browse shot's quote context referencing the pre-edit text | disclosed in `review/t4/REVIEW.md`; the requested fields were changed exactly | reviewer confirmed the disclosure, not a hidden defect |
| flat-passage resized excerpt → `new` | none needed — documented anti-flat-shot behavior | reproduced with busier excerpt → `candidate` correctly |

## Inputs
Six originals (sha-verified) under `iv-test/inputs/`: 01-photonhq, 02-danieltian, 03-photon-mini, 04-poke, 05-linq, 06-gallery. Unseen test source `iv-test/unseen.mp4` (synthesized via the skill's own Pillow scene runtime: 960×720@30, 150f, novel damped squash-stretch "jelly settle" absent from all 77 entries).

## Regression
`python3 -m unittest discover -s skill/imessage-video/tests` → **6/6 PASS** after all fixes.

## Worktree diff (skill changes only)
`catalog.json` (+46), `packs/inherited.mjs` (+7/−7), `packs/media.mjs` (+4/−4), `references/sources.md` (+2). No commits made.
