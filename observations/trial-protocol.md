# Baseline-vs-revised recreation trial protocol

Observer-owned. Runnable by the observer (preferred) or by the lead under
this protocol. Target film: **`03-photon-mini`** (see
`observations/unfamiliar-choice.md`). Two fresh agent sessions recreate the
SAME film; the only intended difference is the skill revision.

## Legs

| Leg | Skill revision | Checkout |
|---|---|---|
| BASELINE | skill at base commit `c49482a` | clean checkout of `devin-bot` @ c49482a |
| REVISED | skill after this effort's improvements land | the merged/revised commit the lead designates |

Everything else identical: same agent harness/model, same machine, same
tools (ffmpeg, node, python3), same budgets.

## Environment provided to each leg

1. A copy of the target source at a NEUTRAL path outside any project dir,
   e.g. `trial-input/source-1080p30.mp4`. Do not hand them the path inside
   `projects/03-photon-mini-complete-v1/` (its location leaks the answer).
2. The full repo checkout minus all ground truth for the target film:
   - FORBIDDEN: `projects/03-photon-mini-complete-v1/**` — simply do not
     include it in the trial checkout (cleanest enforcement), plus
     `STORAGE.json`, `catalog/` and `inventory/` (they expose/render
     deliverables), and any `handoffs/` content describing accepted output.
   - ALLOWED: `skill/` as it ships for that leg — including the three
     `mini.*` source studies, atlas panels, and
     `director/analysis/03-photon-mini/` CSVs (legit shipped knowledge;
     identical availability in both legs) — plus `tools/`, `resources/`,
     all OTHER projects under `projects/` (accepted examples for other
     films are fair reference), and top-level docs.
3. A written task prompt, identical for both legs:

   > Recreate the supplied film as faithfully as you can within the budget.
   > Deliver: (a) a `scene.json` covering the film's full duration at its
   >   native fps and resolution; (b) a rendered MP4 through your primary
   >   adapter plus at least one secondary adapter proving scene-contract
   >   conformance; (c) a shot plan / attempt log noting defects observed,
   >   cause hypotheses and variables changed per retry; (d) a self-assessed
   >   list of remaining fidelity gaps.
   > You may use everything in this checkout except the explicitly
   > forbidden paths. Do not fetch the original film from the internet.

4. Budgets (defaults — record actuals; identical across legs):
   - Wall clock: **6 hours** from first tool call.
   - Tool calls: **≤ 500** total.
   - Renders: uncapped but every render invocation logged with timestamp
     and purpose; wasted/duplicate renders count in scoring.
   - No internet access to the film's origin or its existing recreations.
   - Single session, no human help. One clarification answer allowed,
     identical wording for both legs, if asked.

## What gets preserved (observer fills `observations/attempts/`)

Per leg, into `observations/attempts/<leg>/`:
- `session-log` — full tool-call trace / conversation export.
- `scene-first.json` — first scene that produced any render.
- `scene-final.json` — final submitted scene.
- `first-export.mp4` — FIRST render that played end-to-end, unretouched,
  preserved even if broken (blank segments count as found).
- `final-export-*.mp4` — all submitted final renders.
- `attempt-ledger.md` — timestamped renders: command, purpose, outcome,
  whether output was kept or discarded.
- `compliance-check.md` — grep of session log for forbidden paths
  (`03-photon-mini-complete-v1`, `deliverables/03-photon-mini`,
  `scenes/03-photon-mini`, catalog/inventory target-film URLs). Any hit →
  flag; material use → disqualify that leg, record, rerun fresh.
- `timing.json` — start/end, tool-call count, wall clock, retry count.

Large artifacts (> ~50 MB) may instead be preserved by absolute path +
SHA-256 + commit hash in `observations/preserved/` per `INDEX.md`
convention — but `first-export.mp4` is ALWAYS copied.

## Blind grading

Performed by the observer BEFORE the leg→version mapping is revealed.

1. Leg anonymization: a coin flip (committed hash of `mapping-sealed.txt`
   in `observations/attempts/` BEFORE exports arrive; plaintext sealed with
   the lead or committed as a `git notes`/separate late commit) assigns
   exports to neutral names `EXPORT-A` / `EXPORT-B`. File mtimes stripped
   in copies; graders see only the two MP4s + neutral attempt ledgers
   (timestamps kept, skill-version mentions redacted).
2. Known limit: skill-version fingerprints (e.g., new catalog entries the
   revised leg cites) may de-anonymize. Mitigations: grade objective metrics
   first; score blind on the rubric; record any de-anonymizing tell in the
   verdict so the margin can be sanity-checked.
3. Objective metrics (computed identically for both exports):
   - Decode `first-export.mp4` and `final-export.mp4`; align to
     `source-1080p30.mp4` frame-for-frame (both 30fps/1260f; flag duration
     mismatch as a defect, don't re-time to forgive it).
   - Per-frame RGB MAE vs source → mean / p90 / max; same pipeline for both.
   - Shot-boundary alignment: detect the ~12 major beats (title, agent
     chat, email draft, doc card, group chat, UE card, UE sheet, game card,
     world-release, mosaic, taglines, logo); each within ±15 frames of the
     source boundary counts as aligned.
4. Rubric (100 pts, applied to FINAL export; first-export gets the
   accept/reject + defect count only):
   - Completeness (20): full duration, 1920x1080@30, no blank/frozen run
     >30 frames, all 12 beats present.
   - Layout & UI fidelity (25): iPhone chrome, header, bubbles, composer,
     cards, menus match source composition (not just "a chat").
   - Motion & timing (25): shot boundaries, pacing, easings, sheet/world
     choreography; no slide-show feel inside motion sections.
   - Content fidelity (15): copy/text matches, plausible assets
     (food photos may be placeholders — judged on believability, not
     pixel identity), Memoji/avatars present where source has them.
   - Polish/sound-readiness (5): end card, brand marks, no obvious glitches.
   - Process quality (10, from ledger): retries bounded, hypotheses logged,
     no unchanged-repeat failures, compliance clean.
5. First-pass accept/reject: on `first-export.mp4`, verdict `ACCEPT`,
   `ACCEPT-WITH-NOTES`, or `REJECT` with a defect list (each defect tagged
   major/minor). >2 major or 1 fatal defect (blank render, wrong duration
   ±3 s, unplayable) ⇒ REJECT.
6. Reviewer effort recorded: grading wall time per leg, defect count,
   unresolved-defect count after discussion would hypothetically end.

## Pass bars

- Per-leg "skill adequate": rubric ≥ 60/100 AND first-export not REJECT.
- "Improvement demonstrated": REVISED composite ≥ BASELINE + 15 pts, OR
  REVISED accepts where BASELINE rejects, OR equal composite with ≥30%
  fewer tool calls/renders and a shorter elapsed time. A tie or regression
  is a reportable verdict — do not spin it.
- Context anchor: accepted-scene mean MAE 1.5265 is the production bar;
  a fresh-leg mean MAE under ~8.0 vs source is strong; report the number
  regardless.

## Execution checklist (when the revised skill lands)

1. Build both trial checkouts; strip target-film ground truth; copy
   source.mp4 to `trial-input/`.
2. Extend observer sparse-checkout with `projects/03-photon-mini-complete-v1/`
   for ground truth (scene, deliverables, analysis CSV) — observer only.
3. Commit `mapping-sealed.txt` sha; run legs (parallel OK if machine allows;
   sequential otherwise, BASELINE first if order must be chosen — order is
   moot since sessions are independent).
4. Preserve artifacts per above; run compliance grep; decode+score; blind
   grade; reveal; write `observations/verdict-<date>.md` and hand a copy to
   `handoffs/out/observer/`.
