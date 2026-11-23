# Motion workflow audit

November 21, 2026. Motion code, catalog and published preview evidence at revision `587f030a7045df795ff02c5133ba33ffab6ed2d6`. The working skill had independent changes outside Motion. This audit added only files in this directory.

**Keep the motion recipes and repair the selection and composition boundary.** The catalog playback, local builders and visual mechanism examples work. The current default returns a complete generic demonstration shot. It can place a chart or metric heading directly after a conversation and report success. That path alone can produce the presentation-style result, without invoking HyperFrames. A film needs explicit approval of the motion's real actor, persistent Messages component and source or brief before it can use the recipe. [Motion stage](../../../../skill/imessage-motion-recreation/motion/scene.mjs#L76) · [Sequence compositor](../../../../skill/imessage-motion-recreation/motion/sequence.mjs#L45)

## What was verified

| Check | Result |
| --- | --- |
| Catalog identity | 77 unique IDs, 77 live code-backed builders and 77 archived default previews. The generator reports 75 by excluding the `conversation-handoff` composite and treating `app-drawer` as a variant of `inline-card-expand`. The former combines draft, send and reply. The latter uses the same sheet-rise family with a different target, content and underlay. |
| Distinct mechanisms | All 75 unflagged rows had distinct track signatures after removing actor names and replacing changing strings with a token. All 77 including the flagged two also had distinct signatures. This checks independent authored geometry and timing, which time variants can also produce. The visual sheet and per-row notes establish differences in actors and use, with overlap still possible at the motion-family level. |
| Published playback | All 90 films, including the 13 `--ui` alternatives, matched the catalog SHA-256, 72 native decoded frames, exact 30 fps cadence, and event map. Each had 22 to 72 distinct decoded images. I inspected frames from each film, including the start, action, stronger change and ending. |
| Current renderability | All 90 regenerated through the local CLI with pinned Pillow dependencies. Every rerender reproduced dimensions, native cadence and event map. Archived versus fresh outputs were 0/90 exact byte matches and 0/90 exact decoded-pixel matches in this environment. The result proves recoverability and stable event bookkeeping. Picture identity still requires locking render inputs and checking the exported pixels. |
| Editable code | All 257 documented default edit fields changed the generated layer tree in a one-field change probe. All default local asset references, layer IDs and event-to-layer references resolved. Of 41 supported-UI field probes, 40 changed the tree after using valid receipt statuses. `composer-type` accepts `reply` but ignores it in that variant. Edit testing checks that valid changes are wired, not arbitrary copy fit or exact decoded effect timing. |
| Tests and renderer scope | 68 Motion Node tests pass. I rechecked complete Pillow export and exact decoded cadence. The catalog's four alternative renderer claims are marked nine-frame probes and were not rerun for every entry. There is independent changed-content trial evidence for six entries. |
| Availability | The historical commit tracks 243 files and 100 MP4s in the Motion review directory, including earlier/reuse/probe evidence. The current sparse checkout excludes it, so all catalog URLs looked missing locally and the preview command pointed to rebuilding. I recovered the tracked review directory into scratch and verified each Git blob. The four default artwork PNGs work from the bundle. Generated scenes still point to absolute asset and font paths. UI variants also require configured DejaVu Sans, Pillow and the vendored adapter. |

[Visual notes for each entry](visual-review.tsv) · [Builder, edit, asset and event evidence](scenes.json) · [Full archive and fresh-render verification](previews.json) · [Catalog generator](../../../../skill/imessage-motion-recreation/motion/build-catalog.mjs#L37)

## How the existing source work holds up

The catalog distinguishes seven measured adaptations, one observed pose, one adaptation from an earlier Direction film, nine authored adaptations and 59 newly authored examples. It also explicitly records seven observed effects with gaps and excludes those from the playable lineup. I decoded all eight claimed moving source windows by presentation frame and visually inspected all frames of those windows and the one timestamp still. The five local source or locked-film ranges agree with decoded half-open timestamps within the published decimal precision. [Provenance](../../../../skill/imessage-motion-recreation/motion/SOURCES.md) · [Observed-only inventory](../../../../skill/imessage-motion-recreation/motion/observed.json) · [Decoded source ranges and SHA-256](source-windows.json)

| Entry | What the source shows and what the recipe carries |
| --- | --- |
| Linq rail, f1091–1111 | The same photos translate left inside a crop while title, top controls and supporting row stay in place. The neutral recipe applies the historical normalized curve to independently drawn demo assets. Inline Messages paging is a separate adapter treatment. |
| Simulator send flight, f73–114 | The draft shape collapses, rises and settles as a green outgoing bubble. The default uses fitted geometry ratios in a blue demo. Adapter uses its own send entrance while preserving the action and separate settle marker. |
| Simulator delivery, f134–147 | The latest bubble lifts slightly while the preceding bubble holds. The recipe carries the relative lift and authors receipt fades. Adapter has a separate discrete status action. |
| Simulator long press, f85–114 | Dimming, context menu and reaction rail arrive independently, with the rail following the menu. Default responds over the calibrated 380 ms at authored staging. The adapter opens one anchored simplified popup. |
| Simulator timestamp still | Timestamp alignment beside the displaced transcript is visible. One still proves the pose only. Opening, hold and return are authored. |
| Photon Mini Apps, f211–240 | An independent detail sheet enters above a still-recognizable conversation. Recipe carries sampled grabber y and authors the scrim, card and layout. The authored `mini-app-expand` has a different inline parent. |
| Gallery converge, f603–653 | Portraits approach from different depths and occlude the central text. Recipe carries measured center text scale. Portrait paths, artwork and depth treatment are authored. |
| Poke location, f413–519 | Question reads first, keyboard brings up current location, then the keyboard clears before the rising map and pin. Recipe carries order and pin trajectory over compressed authored timing. |
| Previous Direction lock, f140–168 | Phone remains visible through f152, the prop cut is f153, and lid starts rising around f165. Recipe changes clearance and cut size and holds closed prop, while retaining the authored source's handoff pattern. |

The simulator encoded display clock is variable despite the nominal 60 fps. Send has a 33.333 ms interval at f6→7 and long press has a 33.334 ms interval at f28→29. The frame windows are valid. Catalog seconds computed from nominal fps are one 60 Hz frame early in all three measured simulator windows, including send f73 at **1.233333 s** on the decoded clock versus **1.216667 s** in the catalog. Keep the decoded source ticks when measuring or extracting. [Source clock data](source-windows.json)

This work shows substantive historical extraction, especially the ownership of the Linq rail and the Poke keyboard-to-map sequence. Motion has no callable command that ingests an arbitrary supplied source, measures its actors, records uncertainty, and installs an evidence-backed recipe. The CLI's inputs are prose, IDs and editable scene content. The catalog has historical links, but no standard binding of each normalized curve to its source frame/PTS, crop or actor graph. A usable intake can receive native windows from Recreation, then accept measured transform observations and explicit authored substitutions. Sidehoe's handset/cursor and calendar material requests correctly returned `Missing` instead of `Retrieve` in two probes. Turning those into reusable motions still requires a native source attachment and tracked actor proof. [Motion CLI](../../../../skill/imessage-motion-recreation/motion/cli.mjs#L71) · [Sidehoe frame evidence](../../../../../sidehoe-skill-trial/repair/reviewer-audit/AUDIT.md#L16)

## Failure paths and smallest repair

1. **Inspection and authoring share the same wording.** `Scrub through this motion preview` returns `Retrieve media-video-scrub`. `preview --id …` supports returning or copying a path. It supplies no native frame seek or trim affordance. The lab recipe is four ordered stills switched under an authored playhead. Keep an explicit preview/seek route that operates on an existing clip, and an authoring route only for depicting a seek inside the work. Accept an actual video/timebase if a continuous playback result is required. [Preview command](../../../../skill/imessage-motion-recreation/motion/cli.mjs#L80) · [Scrub recipe](../../../../skill/imessage-motion-recreation/motion/packs/media.mjs#L213)
2. **A requested fixed actor can be absent.** `Scrub through a video attachment in the Messages conversation without moving the composer` selects the generic recipe even though it contains no Messages composer. Fixed-role checking only rejects an actor when metadata says it moves. Prose `fits` and `avoid` already give useful intent, but they cannot prove a required component exists. Require explicit actor presence, movement, parent and fixed-relation fields based on the selected real component graph. Preserve the working distinction between a moving photo rail and a moving heading, which the current selector retrieved correctly on both opposing prompts. [Fixed-role filter](../../../../skill/imessage-motion-recreation/motion/select.mjs#L259) · [Photo test pair](../../../../skill/imessage-motion-recreation/motion/PHOTO-SWIPE.md)
3. **`--ui` accepts a mixed sequence and tears down state.** `scene --ids composer-type,metric-count --ui` compiled `beat-1` with editable conversation state and a second shot with `uiState: null` and independent chart packaging. `--ui` only checks that one of the parts has an adapter. Wrapping each recipe in a full shot is appropriate for preview compilation. Attach selected tracks and cues to stable actor IDs for a film that must keep the conversation. Require permission for each actual cut and purpose, and reject unsupported UI traits instead of quietly returning a demo shell. [Mixed adapter check](../../../../skill/imessage-motion-recreation/motion/cli.mjs#L124) · [Intentional cut reset](../../../../skill/imessage-motion-recreation/motion/tests/sequence.test.mjs#L8)
4. **A Messages-themed picture can mask missing iMessage components.** Twenty editorial pack entries render as standalone presentation cards. Most default conversation samples have demo typography and hand-built rows. Only two default stories initialize semantic conversation state, and only 13 IDs have adapter clips. Adapter treatment uses a themed frame-free pane. Its receipt status is constrained, its typing indicator is a static label, and its reaction badge uses generic text. PhoneFrame is a neutral viewport. Avatar defaults to initials. Nothing in these results proves real iPhone bezel, screen corner mask, Bubble/iOS typography, emoji/Tapback, avatar placement or group chrome. Production should bind each required actor to the specific native or authorized reference style already chosen and verify the actual output at legible size. Keep camera, timing, masks and charts as optional primitives, with non-Messages standalone output confined to the preview route. [Neutral component boundaries](../../../../skill/imessage-motion-recreation/director/component-contracts.md) · [Adapter scope notes](../../../../skill/imessage-motion-recreation/motion/ui-bridge.mjs#L58)
5. **Presence and integrity need to precede discovery.** Catalog previews are published evidence with useful hashes. The current sparse skill pickup received broken preview routes. Make a selected preview inspectable in a clean checkout through explicit hydration or a generated preview with its own evidence, and rebundle local assets and font-resolution instructions beside a portable scene. Require full-candidate frame review for first visible action or preservation claims. Verify title, composer, keyboard, actor registration, reply and ending on the relevant intermediate frames, with reference-specific crop or pixel evidence where applicable. [Runtime packaging](../../../../skill/imessage-motion-recreation/RUNNING.md) · [Published preview path and fallback](../../../../skill/imessage-motion-recreation/motion/cli.mjs#L80)

These are repairable interface and evidence gaps around a working library. Keep discovery and its 77 mechanism previews, mark the two catalog count conventions explicitly, and use the per-row conditions here to seed a machine-checkable Motion decision layer. The part worth rebuilding is the production bridge that turns a chosen mechanism into constrained tracks inside an existing Messages scene. Fresh Director construction then remains responsible for choosing a Messages-native scene and proving what changed in it.

## Reproducing these checks

Start in the tagged skill directory. Use the pinned Python requirements, FFmpeg, Node, DejaVu Sans and a Fontconfig configuration that finds the fonts. CairoSVG may need the installed Cairo library on the dynamic library path. The Linux/macOS environment can change the picture without changing the event map. This run used Python 3.12 plus the lockfile package versions, locally installed Cairo and DejaVu.

```sh
node --test motion/tests/*.test.mjs
node motion/cli.mjs select --brief 'Scrub through this motion preview'
node motion/cli.mjs select --brief 'Scrub through a video attachment in the Messages conversation without moving the composer'
node motion/cli.mjs scene --ids composer-type,metric-count --ui --out /tmp/motion-mixed-ui.json
```

Recover `review/imv-v3/motion` from the recorded revision into a scratch checkout or archive with the root-relative layout intact. If using the sparse partial clone, acquire the missing Git blobs through the authenticated repository and verify the Git object IDs before reading the package. It is possible to reproduce all published assets without changing the working checkout.

The scene verifier expects freshly generated filenames `$FRESH/ID.scene.json`, `$FRESH/ID.events.json` and `$FRESH/ID.mp4`, and `ui.ID` stems for adapter clips. Each generation starts from the same tagged skill.

```sh
mkdir -p "$FRESH"
jq -r '.entries[].id' motion/catalog.json | while IFS= read -r id; do
  node motion/cli.mjs render --id "$id" --method pillow --out "$FRESH/$id.mp4"
done
jq -r '.entries[] | select(.ui) | .id' motion/catalog.json | while IFS= read -r id; do
  node motion/cli.mjs render --id "$id" --method pillow --ui --out "$FRESH/ui.$id.mp4"
done
node "$AUDIT/audit_scenes.mjs" "$PWD" "$FRESH" "$OUT/scenes.json"
"$MOTION_PYTHON" "$AUDIT/verify_previews.py" --catalog motion/catalog.json \
  --snapshot "$SNAPSHOT" --fresh "$FRESH" --out "$OUT"
```

The source script additionally expects the sibling private source bundle and four staged files named `send-60fps.mp4`, `longpress-60fps.mp4`, `swipe-timestamps-light.png` and `locked.mp4`. Their immutable source URLs and verified SHA-256 values are recorded in `source-windows.json`. It generates one square-safe annotated thumbnail sheet per source window in scratch.

```sh
"$MOTION_PYTHON" "$AUDIT/audit_source_windows.py" --catalog motion/catalog.json \
  --source-root "$SOURCE_BUNDLE" --supplemental "$PINNED_SOURCE_MEDIA" --out "$OUT/source"
```
