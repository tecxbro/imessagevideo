# BUILDER REPORT — "Learn this swipe." (05-linq restaurant photo swipe)

Workdir: `/Users/darshan/Documents/video-analysis/iv-test/jobs/t2`
Library (persistent, untouched except failed-bind temp dirs that were auto-cleaned):
`/Users/darshan/Documents/video-analysis/iv-test/library`
Skill dir (read-only, unmodified):
`/Users/darshan/Documents/video-analysis/imessagevideo-dl/skill/imessage-video`

All numbers below come from scripts in this folder, not eyeballing:
`measure_source.py`, `measure_replay.py`, plus inline Pillow checks. Decoded
frames were produced with ffmpeg `select` filters (native frame indices).

---

## 1. Entry point + source verification

Command run from the skill dir (as SKILL.md prescribes):

```sh
python scripts/decide.py "Learn this swipe." \
  --video .../iv-test/inputs/05-linq.mp4 \
  --workdir .../iv-test/jobs/t2 \
  --library .../iv-test/library \
  --motion "restaurant photos slide horizontally under the fixed restaurant heading"
```

Full output: `decide-output.json`. Confirmed:

- `intent = "learn"`, `scope = "motion"`
- source `identity.status = "known"`, match id `05-linq` ("Linq iMessage Apps"),
  sha256 `86e22e69…bbf2eb`, coverage `archived-reconstruction`
- `documented_motions` contains bundled seed `photos-under-fixed-heading`,
  `source.ref = projects/05-linq-complete-v1/.../05-linq/source.mp4` (this film's
  repository path), `framesInclusive: [1091, 1111]`
- `motion_choices.seed[0].id = photos-under-fixed-heading` (seed_decision "retrieve"),
  editable fields `heading, detail, photos, direction`

### Decoded source frames

Extracted native frames 900–1300 (`src-wide/`, f0001.png = frame 900) and
1080–1125 (`src-frames/`). Contact sheet with green heading-ROI / red rail-ROI
boxes: **`source-contact-sheet.png`** — heading block ("Boqueria Soho" + rating +
Directions + tabs) is fixed while the photo rail translates left
(storefront → bar → paella → octopus → interior).

Measured bounds of the actual gesture (rail per-frame ROI MAE, threshold 1.0):
rail moves continuously from **frame ~1079 to ~1131**. The catalog's
1091–1111 is the core/high-velocity interval the seed sampled.
At ~1135 the whole card begins scrolling **vertically** (a different motion).

Cadence: content runs at 15 fps inside the 30 fps container — identical
odd/even frame pairs (per-frame rail MAE alternates ~0 / high).

## 2. Saved motion — `recipes.py info` / `preview`

`recipe-info.json` — full catalog record. `recipes.py preview` returned the
bundled preview; sha256 verified:
`adce3885b489d68f1b595c43d8dee4c5f4dbb1b02de8480ce351fe97b89a59dd` — **matches**
the catalog `sha256` field.

Decoded preview frames (`prev-frames/`, `prev-all/`): 720×480, 30 fps, 72
frames — "Alpine field notes" card, photos slide left under a fixed heading +
fixed "Field guide · Autumn" footer. Same Pillow measurement on the preview
(`preview-motion.json`):

| ROI | mean MAE | max MAE |
|---|---|---|
| heading band | 0.001 | 0.028 |
| photo rail | 3.263 | 21.547 |
| footer | 0.000 | 0.000 |

Rail active span = **frames 20–39**, exactly the declared events
`rail-start@20` / `rail-settle@39` (`scene.events.json`).

## 3. Justification — this swipe IS photos-under-fixed-heading

`source-motion-measurement.json` (from `measure_source.py`):

- Heading ROI (190,15,560,100) per-frame MAE inside 1091–1111:
  **mean 0.59, max 1.82**
- Rail ROI (190,295,780,640) per-frame MAE inside 1091–1111:
  **mean 68.06, max 83.27**  → ~115× the heading change
- Title dark-pixel bbox at frame 1080 vs 1130: identical left/right
  ([199,·,406,·]) — heading does not translate.
- Confound noted in JSON: the card's black chrome fades slightly during the
  swipe (Directions button black → dark grey); position is unchanged.

**Decisive evidence** — I measured the rail's per-frame horizontal translation
with a 1-D column-profile shift search (`rail_translation_measurement` in the
JSON). Source deltas for pairs 1091→1112:

`22, 0, 25, 29, 33, 39, 0, 47, 57, 72, 93, 0, 125, 156, 148, 110, 0, 79, 59, 46, [37]`

The seed's `photoOffsets` in
`assets/seed/runtime/motion/packs/core.mjs` is the cumulative array
`[0,22,22,47,76,109,148,148,195,252,324,417,417,542,698,846,956,956,1035,1094,1140]`
whose per-frame deltas are **exactly** the first 20 measured values
(`exact_match: true`). The bundled motion literally encodes this source
interval's measured trajectory — this is a measured adaptation of THIS swipe,
not a generic slide.

## 4. bind-seed attempt (per references/sources.md)

Two honest attempts; the seed remains the saved motion regardless.

Attempt A — catalog interval:
```sh
sources.py bind-seed 05-linq.mp4 --id linq-photos-swipe --title "..." \
  --recipe photos-under-fixed-heading --frames 1091:1112 \
  --crop 120,60,720,480 --roi rail:140,131,440,197 --max-mae 8 \
  --reviewed-by builder-t2 --library .../iv-test/library
```
Output (`bind-seed-attempt.txt`): **`Duration must be 1.6–12 seconds`** —
the seed renderer enforces a 1.6 s floor; the measured 21-frame window (0.7 s)
is rejected before any comparison.

Attempt B — whole observed gesture (49 frames = 1.633 s):
`--frames 1079:1128` (same crop/roi/max-mae). The pipeline ran end-to-end:
clip extracted, scene materialized (keyframes rescaled to duration), 49-frame
preview rendered, comparison executed → **`limits_passed: false`**
(`bind-seed-attempt2.txt`, exit 1, "Seed replay failed …").

I replicated that comparison durably in `bind-evidence/` (reference.nut,
preview.mp4, `comparison/report.json`, `worst.png`):

- `structure_match: true`, 49 frames compared
- full-frame MAE **mean 82.2 / max 86.0**; rail ROI **mean 79.2 / max 90.6** vs
  `--max-mae 8` — off by an order of magnitude.
- `worst.png` shows why: source is the real Boqueria UI (storefront/bar
  photos, Directions button, tabs); the seed renders stylized "Alpine field
  notes" artwork at a different layout. The catalog says so itself:
  `"kind": "measured-adaptation" … "Reproduced at a new size with authored
  artwork and a held header."` A pixel bind cannot pass by construction.
  Conclusion: binding not feasible; recorded, not forced.
- Library check: no `film-bindings/` or `.bind-seed-*` residue; existing
  `entries/jelly-settle-arrive` and `films/source-8a77…json` untouched.

## 5. Replay with different content

Created `photos/osteria-1..4.png` (384×256: red/circle, teal/triangle,
mustard/stripes, violet/grid — all synthetic, authored by me) and
`content.json` = `{heading:"Osteria Bella", detail:"Trattoria · West Village",
direction:"left", photos:[…4 paths…]}`.

```sh
scripts/recipes.py render photos-under-fixed-heading \
  --out jobs/t2/replay-new.mp4 --content jobs/t2/content.json --fps 30
```

Rendered 72 frames (`replay-frames/`). `replay-measurement.json`:

| check | result |
|---|---|
| heading band mean/max MAE | 0.0002 / 0.013 — fixed |
| heading MAE-from-first max | 0.016 |
| title text present | 72/72 frames, left-edge drift 0 px |
| rail mean/max MAE | 12.27 / 78.94 — moving |
| rail active span | frames 20–39 (= declared events) |
| footer mean/max | 0.0007 / 0.007 — fixed |

Heading crop artifact `replay-heading-crop.png` reads **"Osteria Bella"**.
Contact sheet `replay-contact.png`. → PASS.

## 6. Negative check — generic slide that moves the heading

`generic-slide.scene.json` = the replay scene with the photo-rail's exact
`x` keyframes copied onto the `heading` and `footer` groups, so heading + rail
+ footer translate together. Rendered with the same engine →
`generic-slide.mp4` (72 frames). Same measurement →
`generic-slide-measurement.json`:

| metric | replay (correct) | generic slide (wrong) |
|---|---|---|
| heading max per-frame MAE | 0.013 | **3.87** |
| heading MAE-from-first max | 0.016 | **9.87** |
| footer MAE-from-first max | 0.021 | **8.22** |
| title text present | 72/72 frames | **23/72 — departs at frame 23** |
| `heading_fixed` flag | true | **false** |

`generic-slide-contact.png` shows the heading band + footer sliding off the
card leftward. The same check that passed the replay **flags the wrong
motion**. → PASS (the check catches it).

## 7. Skill defects / observations

1. **`bind-seed` cannot bind the catalog's own measured interval.** The seed
   renderer enforces duration ∈ [1.6 s, 12 s] (`Duration must be 1.6–12
   seconds`), but `photos-under-fixed-heading`'s measured source span is 21
   frames = 0.7 s. `references/sources.md` gives no guidance about a minimum
   binding length. This is a doc/tool gap, hit on the very film the seed was
   measured from.
2. **`bind-seed` is structurally unable to verify "measured-adaptation"
   seeds.** The tool pixel-compares a fresh recipe render against source
   frames; adaptation seeds are "reproduced at a new size with authored
   artwork", so no crop/ROI/max-mae can pass. Either `sources.md` should state
   that adaptation seeds bind by trajectory/structure rather than pixels, or
   `bind-seed` needs a non-pixel (e.g. translation-trajectory) mode.
3. Minor/UX: `recipes.py render` writes undocumented sidecars
   `<out>.scene.json`, `<out>.events.json`, `<out>.mp4.render.json` next to the
   output (useful — I used `.scene.json` for the negative control).
4. No defect: `decide.py` returned `inspect_candidates` (seed + unrelated
   learned `jelly-settle-arrive`) for the `--motion` query, leaving final
   selection to the agent; documented_motions already named the right seed.

## Pass/fail summary

| task | status | evidence |
|---|---|---|
| decide.py intent/scope/source/seed | PASS | `decide-output.json` |
| source contact sheet photos-move/heading-fixed | PASS | `source-contact-sheet.png` |
| preview exists + sha256 match + motion verified | PASS | `recipe-preview.txt`, `preview-motion.json` |
| numeric justification vs generic slide | PASS (115× ROI ratio; exact trajectory match) | `source-motion-measurement.json` |
| bind-seed | ATTEMPTED, correctly FAILED — infeasible by design | `bind-seed-attempt{,2}.txt`, `bind-evidence/` |
| replay new content, heading fixed + rail moves | PASS | `replay-new.mp4`, `replay-measurement.json` |
| generic-slide negative control flagged | PASS | `generic-slide.mp4`, `generic-slide-measurement.json` |
| skill/library/input dirs unmodified | PASS | only `jobs/t2/` written; library verified clean |
