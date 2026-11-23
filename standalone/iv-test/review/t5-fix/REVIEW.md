# Independent review — heading-editability fix (t5)

Reviewer: independent verification agent
Date: checked live in working tree (uncommitted changes)
Repo: `/Users/darshan/Documents/video-analysis/imessagevideo-dl`

## Verdict: PASS

The fix is correct, complete, and minimal. All 23 previously-missing entries now
declare `heading` editable in both the runtime packs and `catalog.json`, the
enforcement in `recipes.py materialize` still rejects unknown fields, fresh
renders show a custom heading in the shared top bar, and default renders still
match bundled previews within encode noise.

One non-blocking flag: the working tree also contains an unrelated docs edit to
`references/sources.md` (see "Scope").

## Evidence per claim

### 1. Pack `editable` lists include 'heading' for all 23 entries — CONFIRMED

- `assets/seed/runtime/motion/packs/media.mjs:8` — shared `entry()` helper now
  emits `editable: ['heading', 'photos']`; all 16 media entries use it.
  Explicit overrides gained 'heading' at lines 195 (`photo-album-deal`),
  376 (`media-caption-disclosure`), 518 (`attachment-download-progress`).
- `assets/seed/runtime/motion/packs/inherited.mjs` — 'heading' prepended in all
  7 `baseEntry` calls: `message-wall` (l159), `app-drawer` (l167),
  `identity-morph` (l175), `circle-to-panel` (l183), `mini-app-expand` (l191),
  `selection-confirm` (l199), `card-orbit` (l207). Other entries in the file
  already declared heading (e.g. `messages-attachment-stack` l216).
- 7 inherited + 16 media = 23. Independent node check importing
  `runtime/motion/catalog.mjs` and comparing each entry's `editable` against
  `assets/seed/catalog.json`:
  `runtime entries: 77, catalog entries: 77, mismatches: [], missingHeading: [],
   notSubset: [], catalog-only ids: []` — every pack list exactly matches the
  catalog (including order), every entry declares 'heading', and every
  `editable` item is a key of `editableFields`.
- `catalog.json` diff: 23 hunks, 46 added lines, 0 deletions — each hunk adds
  `"heading",` to `editable` and `"heading": "text",` to `editableFields`.
  Hunk-to-entry mapping confirms exactly the 23 expected IDs.

### 2. `configuration()`/`scene.mjs` accepts and renders `heading` — CONFIRMED

- `scene.mjs:16-20` — `defaults` includes `heading: 'Alpine field notes'`, so
  `configuration()` (l43, `Object.hasOwn(defaults, key)`) accepts `heading`
  and validates it as a ≤250-char string (l44).
- `scene.mjs:77-84` — the shared heading chrome group `heading` is drawn at
  (110,44), 500×54, with `text('heading-copy', data.heading, …)` and is added
  to every scene's `layers`. `buildMotion` merges
  `{...entry.defaults, ...content}` (l62), so supplied `heading` wins.
- Enforcement lives only in `recipes.py:102-104`
  (`unknown = set(content) - set(row["editable"])` → `ValueError`), where
  `row["editable"]` comes from `catalog.json` via `inventory()`/`info()`. The
  node runtime (`recipe.mjs` → `buildMotion`) does not re-filter by `editable`;
  its only use is the unrelated `direction` special-case at `scene.mjs:70`.
  So adding 'heading' to `catalog.json` `editable` is the necessary and
  sufficient gate change, and the pack lists stay in sync (verified above).

### 3. `recipes.py info` shows heading — CONFIRMED

`/Users/darshan/Documents/video-analysis/.venv/bin/python scripts/recipes.py info <id>`:
- `selection-confirm` → `editable: ['heading','title','detail']`,
  `editableFields: {heading: 'text', title: 'text', detail: 'text'}`
- `photo-iris-reveal` → `editable: ['heading','photos']`,
  `editableFields: {heading: 'text', photos: 'array of local PNG, JPEG or WebP paths…'}`

### 4. Custom heading renders in the top bar — CONFIRMED (own renders)

Content file `review/t5-fix/heading-content.json` = `{"heading":"Reviewer check"}`:
- `recipes.py render selection-confirm --out renders/selection-confirm-heading.mp4
  --content heading-content.json` → rendered 72f/30fps OK.
- `recipes.py render photo-iris-reveal --out renders/photo-iris-reveal-heading.mp4
  --content heading-content.json` → rendered OK (default bundled sample photos).
- Frame-60 crops `crop=500:54:110:44` (frames/sc-heading-f60.png,
  frames/iris-heading-f60.png) were opened and visually show **"Reviewer check"**
  in the heading bar for BOTH renders.
- Compiled scene JSON confirms `heading-copy` layer `text: "Reviewer check"`.
- Builder's own evidence (`/tmp/heading-check/heading-f60.png`) shows
  "Concert tickets" — consistent. Note: `--content` takes a JSON **file path**
  (`type=Path`, `content_file.read_text()`); the builder's claim text shows the
  JSON inline but they actually passed `/tmp/heading-check/content.json`. The
  claim's substance is verified.

### 5. Unknown-field enforcement still works — CONFIRMED

`recipes.py render selection-confirm --out renders/should-fail.mp4 --content
bogus-content.json` (`{"bogus":1}`) → exit 1,
`Unsupported fields ['bogus']. Editable fields: heading, title, detail`.
No output file created.

### 6. Defaults unchanged (spot check) — CONFIRMED

Own fresh default renders compared to bundled previews via `scripts/frames.py`:
- `selection-confirm` default vs `previews/selection-confirm.mp4`:
  compared 72 frames, max frame MAE **0.547**, limits passed.
- `photo-iris-reveal` default vs `previews/photo-iris-reveal.mp4`:
  compared 72 frames, max frame MAE **0.712**, limits passed.

Within the builder's claimed ~0.93 encode-noise bound. The builder's
`/Users/darshan/Documents/video-analysis/iv-test/jobs/t5/renders-fix/` contains
exactly the 23 expected mp4s. (I re-verified 2 of 23 independently rather than
re-running all MAE comparisons.)

## Scope check (`git diff --stat`)

4 modified files, all expected except one flag:
- `skill/imessage-video/assets/seed/catalog.json` — 23 hunks, +46/−0. In scope.
- `.../packs/inherited.mjs` — 7 editable-line changes only. In scope.
- `.../packs/media.mjs` — helper + 3 overrides only. In scope.
- `skill/imessage-video/references/sources.md` — **UNRELATED**: adds a
  "Binding limits." paragraph about bind-seed interval/style constraints.
  Docs-only, no functional impact, but not part of this fix; recommend
  confirming it is intentional or splitting it out.

No other working-tree modifications (`git status --short` shows only these 4).

## Defects found

None in the fix itself. Minor claim wording nit: `--content` accepts a file
path, not an inline JSON string as written in the builder's claim (their actual
invocation used a file — harmless shorthand).

## Review artifacts

- `/Users/darshan/Documents/video-analysis/iv-test/review/t5-fix/heading-content.json`,
  `bogus-content.json`
- `renders/selection-confirm-heading.mp4`, `photo-iris-reveal-heading.mp4`,
  `selection-confirm-default.mp4`, `photo-iris-reveal-default.mp4` (+ scene/events)
- `frames/sc-heading-f60.png`, `iris-heading-f60.png` (heading-bar crops)
- `frames/sc-default-compare/`, `iris-default-compare/` (frames.py reports)
