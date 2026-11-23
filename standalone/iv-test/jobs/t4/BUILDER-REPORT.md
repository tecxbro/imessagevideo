# BUILDER-REPORT — t4: "Change this message to 'Meet at the doors' and replace this shot's motion with the swipe from this second clip."

Skill under test: `/Users/darshan/Documents/video-analysis/imessagevideo-dl/skill/imessage-video` (read-only, unmodified by this run)
Python: `/Users/darshan/Documents/video-analysis/.venv/bin/python` (Pillow 13, numpy 2.5, fontTools, CairoSVG)
Library: `/Users/darshan/Documents/video-analysis/iv-test/library` (persistent; unchanged — donor motion is the bundled seed `photos-under-fixed-heading`, no new entries)
Workdir: `/Users/darshan/Documents/video-analysis/iv-test/jobs/t4`

## Request beat

User pointed at `t3/film.mp4` (the edit target) and `donor-swipe.mp4` ("this second clip") and asked for two edits: the outgoing blue message in shot `ask` → exactly **"Meet at the doors"**; the final `ticket` shot's motion → the swipe from the donor clip. Disambiguation (as supplied): "this message" = `ask`'s blue bubble; "this shot" = `ticket`.

## Entry point (exact user-style invocation)

```
cd SKILL_DIR
…/python scripts/decide.py "Change this message to 'Meet at the doors' and replace this shot's motion with the swipe from this second clip." \
  --video …/jobs/t3/film.mp4 --donor …/iv-test/donor-swipe.mp4 --project …/jobs/t3/approved.json \
  --workdir …/jobs/t4 --library …/iv-test/library
```

Recorded output (`decide-output.txt`):

- `intent: "edit"`, `scope: "changes"`, `next: "locate_target_shots"` ✔ expected
- Roles split correctly: `t3/film.mp4` → `edit-target`, `donor-swipe.mp4` → `motion-donor`.
- Target identity `new` (sha256 `9b2fc1fb…`) — the film was rendered locally in t3 and was never registered; correct.
- Donor identity `candidate` → **05-linq "Linq iMessage Apps"**, visual-sequence evidence, 6 matched samples, input 0.0–3.0 s ↔ catalog 35.0–38.0 s, coverage `archived-reconstruction`, `audio_compared: false`.
- Donor `documented_motions`: **`photos-under-fixed-heading`** — measured-adaptation of 05-linq source 36.367–37.067 s (frames 1091–1111), bundled preview + `core.mjs` implementation. This is the swipe the user pointed at.
- Workflow returned: `open_editable_target_or_recover_its_layers → identify_changed_copy_and_motion → retrieve_selected_donor_motion → patch_named_shots → render_changed_passage → check_changed_and_unchanged_regions → deliver_revised_film` — followed literally.
- Intake artifacts written per source under `intake/<sha>/{source.json,frames.csv,overview.jpg}`.

## Confirmation choice (documented per instruction)

The t3 baseline plan has `confirmation: true`. This user message is an **explicit literal revision** — per direction.md ("Ask for changes or confirmation before full production **unless the user has already delegated direct execution; set `confirmation:false` on that brief**") and SKILL.md ("For an explicitly requested literal reconstruction, proceed"), the copied derivative `plan-v0.json` sets **`confirmation: false`** and drops the stale baseline `approval` record (its revision hash could never match a new plan anyway; `revise` also auto-pops it). Result: `check --for-production` passes on merits — `confirmation_required:false, approved:false, open_work:{}`, exit 0 — with no fabricated approval.

## Commands run (order)

```
# baseline derivative + evidence layout (paths in shots are relative to plan dir)
cp ../t3/approved.json plan-v0.json          # then: confirmation→false, approval removed
cp -R ../t3/assets assets; cp -R ../t3/proof-quote ../t3/proof-celebrate .   # unchanged shots' evidence
cp -R ../t3/proof-ask baseline-proof-ask; cp -R ../t3/proof-ticket baseline-proof-ticket
cp -R ../t3/final-shots baseline-final-shots; cp ../t3/board-*.png .

shots.py --library LIB revise plan-v0.json ask    patch-ask-copy.json    plan-v1.json
shots.py --library LIB revise plan-v1.json ticket patch-ticket-motion.json plan-v2.json
shots.py --library LIB render-shot plan-v2.json ask    final-v2/ask
shots.py --library LIB render-shot plan-v2.json ticket final-v2/ticket
ffmpeg -i final-v2/ask/preview.mp4    -vf select=eq(n,60) -frames:v 1 board-ask-v2.png
ffmpeg -i final-v2/ticket/preview.mp4 -vf select=eq(n,30) -frames:v 1 board-ticket-v2.png
shots.py --library LIB revise plan-v2.json ask    patch-ask-media.json    plan-v3.json
shots.py --library LIB revise plan-v3.json ticket patch-ticket-media.json plan-v4.json
shots.py --library LIB pitch  plan-v4.json --out pitch-v2.md
shots.py --library LIB check  plan-v4.json --for-production     # exit 0
ffmpeg -f concat -safe 0 -i concat-v2.txt -c copy film-v2.mp4   # lossless splice
```

## Patches applied

- `patch-ask-copy.json`: `{"copy": "Meet at the doors"}` — copy still binds via `copy_key:"copy"` to the outgoing bubble; content patch auto-cleared stale preview/code/board.
- `patch-ticket-motion.json`: `motion → {kind:"seed", id:"photos-under-fixed-heading"}` (the donor's documented motion), `copy → "The Neon Pines - GA Floor - 2 tickets - Fri Jun 12"` via `copy_key:"detail"` (the ticket info), `bindings {heading:"Maya", direction:"left", photos:[4 × assets/ticket-*.png]}`, refreshed `purpose`/`visual`. `frames:72` and shot ids untouched throughout; every `revise` wrote a new plan file.

## Plan chain / revisions

`plan-v0` (rev `ae60a900…`) → `plan-v1` (changed_shot `ask`) → `plan-v2` (rev `1f6b45e7…`, changed_shot `ticket`) → `plan-v3` → `plan-v4` (rev `e30eeb2e65a4fd633f96a70344de9479a7fa04f9ef8c8ca5d20d2ef8880ae82e`, printed in `pitch-v2.md`, state "confirmation optional"). Unchanged `browse`/`celebrate` records are carried through verbatim; their evidence still resolves (sha-verified below).

## Renders

| shot | output | spec | notes |
|---|---|---|---|
| ask | `final-v2/ask/` | 720×480 @30 fps, 72 f | conversation-handoff; receipt `preview.mp4.render.json`, scene sha `bca371a1…` |
| ticket | `final-v2/ticket/` | 720×480 @30 fps, 72 f | photos-under-fixed-heading; render receipt cites 05-linq source 36.366667–37.066667 s; scene sha `bb97a1c6…` |
| browse, celebrate | reused `baseline-final-shots/{browse,celebrate}/preview.mp4` | identical spec | **sha256 byte-identical** to `../t3/final-shots/*` AND to the plan-attached `proof-quote`/`proof-celebrate` previews (`943911a2…`, `42782622…`) — reuse verified against recorded evidence |

Assembly: `ffmpeg -f concat -safe 0 -i concat-v2.txt -c copy film-v2.mp4` → h264 720×480, 30 fps, **288 frames**, 9.6 s, sha256 `c8457d89ce5b1d5326a910a64af1536b9ec6ee01098152acdf1092dc7bf4be2a`. Stream-copy splice → **no re-encode anywhere** (differs from t3's libx264 concat; quantified below).

## Self-verification (numbers in `ticket-motion-check.json`, script `verify_motion.py`)

**a. Copy check** — decoded `film-v2.mp4` frame 60 (`verify/film-frame60.png`): outgoing blue bubble literally reads **"Meet at the doors"**; reply/header unchanged. Diff vs t3 frame 60 → 519 px >30 delta localized to the bubble's glyphs (`verify/ask-diff-x4.png`, 4× amplified).

**b. Ticket motion (frames 216–287), per-frame ROI MAE vs segment first frame:**
- heading ROI (110,45,500,60): **max 0.0008** — static (encode noise only)
- footer ROI (110,390,500,50): max 0.0053 — static
- rail ROI (110,125,500,215): **max 41.33**, mean 27.32 — moves then settles at new state
- consecutive-frame MAE shows motion on film frames **236–255 = local frames 20–39**, exactly the recipe's `rail-start@20` / `rail-settle@39` events — the donor swipe's timing.

**c. Boundaries** (`verify/boundary/f*.png`, all inspected): 70–71 ask settled (new copy) → 72–73 browse start; 142–143 browse end ("Replying to Maya" quote draft) → 144–145 celebrate; 214–215 celebrate settled (Love badge) → 216–217 ticket rail start (GA FLOOR card); 286–287 VIP PIT settled. Clean cuts at all three joins; no donor-motion bleed into `celebrate`; first/last frames correct.

**d. Unaffected segments vs `t3/film.mp4`** (per-frame whole-frame MAE):
- `browse` 72–143: max **0.3197**, mean 0.2367 (worst f119)
- `celebrate` 144–215: max **0.2534**, mean 0.2134 (worst f172)
- vs their own source previews: **0.0 / 0.0** — v2's segments decode bit-identically to the reused renders. The residual vs `t3/film.mp4` is entirely t3's own re-encode generation loss; v2 itself re-encoded nothing.
- Changed segments vs v1 (sanity): `ticket` mean 22.11 (new scene); `ask` mean 0.26 — same layout, difference is only bubble glyphs (verified visually + localized diff).

## Integrity

- `donor-swipe.mp4` sha256 `befaf0d9…` — byte-identical ✔ (never opened for writing; donor used only via decide intake + seed replay)
- `t3/film.mp4` `9b2fc1fb…`, `t3/approved.json` `6efe03f2…` — untouched; all t3 artifacts only read/copied
- Library: no files newer than job start; no registrations/bindings/entries added
- Skill dir: no writes from this run

## Observation (out of scope, flagged for user)

`browse`'s `bindings.reply` still contains the pre-edit outgoing text "Neon Pines tickets drop at 10 - grab us two?", so the quote card in shot 2 references a message that no longer matches shot 1's new copy. Left intact per the user's literal scope ("this message" = shot 1 only); a one-field follow-up `revise` on `browse` would align it if wanted.

## Skill defects / issues found

1. **Pre-existing dirty file (not caused by this run):** `git status` inside `imessagevideo-dl` shows `M skill/imessage-video/references/sources.md` — 2 added lines (blank + the "Binding limits" paragraph); file mtime Nov 21 13:39, the same state t3's report documented. This builder issued no writes under the skill dir.
2. **No new functional defects.** decide.py parsed the two-clause edit + donor roles correctly on the literal phrasing; `revise` enforced stable ids and auto-cleared stale media on content patches; `render-shot` verified frame count/clock and produced receipts; `check --for-production` correctly gated on `confirmation` + open work.
3. Minor note (by design): `revise` rejects output over an existing file and `render-shot` requires a fresh dir — artifacts are immutable; new names (`final-v2/*`, `board-*-v2.png`) are the intended pattern.

## Artifacts

- Deliverable: `film-v2.mp4` (288 f, sha `c8457d89…`); concat list `concat-v2.txt`
- Plans: `plan-v0…v4.json`; patches `patch-{ask-copy,ticket-motion,ask-media,ticket-media}.json`; pitch `pitch-v2.md` (rev `e30eeb2e…`)
- Changed-shot evidence: `final-v2/{ask,ticket}/` (preview.mp4, scene.json, content.json, scene.events.json, render receipt; ticket also `assets/`), boards `board-{ask,ticket}-v2.png`
- Verification: `ticket-motion-check.json`, `verify_motion.py`, `verify/film-frame60.png`, `verify/ask-diff-x4.png`, `verify/boundary/f070–f287.png`, `verify/v1-frame60.png`, `inspect-*.png`
- Decide record: `decide-output.txt`; intake inventories `intake/`
- Baseline copies: `baseline-final-shots/`, `baseline-proof-{ask,ticket}/`, `proof-{quote,celebrate}/`, `board-{ask,quote,celebrate,ticket}.png`, `assets/ticket-*.png`
