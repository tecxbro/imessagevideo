---
name: imessage-motion-recreation
description: Originate an iMessage product launch film from a brief, or recreate a supplied film using the local movies, editable UI, measured timing and five renderers.
---

# iMessage motion director

Version 3.1 local combines direction instructions, visual studies, component code and the complete example library stored in this checkout. It is not trained model weights or an autonomous video generator. For original direction, ground the product action, decide what is worth watching unfold, then build and review moving treatments. For recreation, preserve measured source evidence.

For an existing company or product, start with [RESEARCH-FIRST.md](library/RESEARCH-FIRST.md) and produce an evidence-backed profile using [company-profile.schema.json](library/company-profile.schema.json) **before choosing motion or writing the shot plan**. Use supplied/connected context, the official site, primary docs and real UI. Record citations, observed facts, inferences and unresolved gaps; do not invent product capabilities, transactions, integrations or results. Investigate ambiguous names before asking one focused clarification. For a fictional brief, implement or replay a clearly scoped fixture and tie the depicted actions and wording to it.

## Route the task

| User goal | Start here | Timing authority |
|---|---|---|
| Originate a film from a product brief | [Director workflow](director/directing.md) and [product evidence](library/RESEARCH-FIRST.md) | Observed product behavior or a tested prototype, and an authored edit |
| Recreate a supplied film | [Reconstruction playbook](references/reconstruction-playbook.md), actual movie and native-frame comparisons | Actual source with explicit output/source mapping |
| Adapt a studied technique to new footage | [Director workflow](director/directing.md), [visual explorer](director/index.html), [design grammar](director/design-grammar.md) | Authored choreography supported by the relevant source study |
| Extract or adapt a component | [Component contracts](director/component-contracts.md), [component code](director/components.mjs), chosen study | Declared editable boundary and actual source evidence |
| Add UI sound | [UI audio workflow](references/ui-audio-workflow.md) | Visible actions in the delivered picture |

For recreation, catalogue recipes help decompose the source; never replace its motion with a starter preset. For new direction, catalogue options carry tradeoffs; never claim a new starter is source-exact.

## Final working set and failure lessons

For the accepted code, keyframes, required assets and finished videos, read
[FINAL-PRODUCTION.md](../../FINAL-PRODUCTION.md) and
[the independent completeness audit](../../reports/completeness-audit/README.md).
Use the current scene plus current adapters; older builders and temporary frame
caches are not required to replay the final accepted animation. Before retrying
an observed defect, consult [FAILURES-AND-FIXES.md](../../FAILURES-AND-FIXES.md): it
records concrete causes, accepted changes, measured controls and unresolved
limits. Do not present a historical improvement as a fresh test or a remaining
issue as solved.

## Use the complete local library

The canonical local registry is [LOCAL-LIBRARY.json](../../LOCAL-LIBRARY.json), two directories above this skill folder. It resolves the six full projects and all supporting resources using portable paths relative to the checkout root. Open the [offline full-code/video viewer](../../catalog/index.html) and [every-file browser](../../inventory/index.html). The [location guide](../../LOCATIONS.md) and [exact skill/gap audit](../../reports/SKILL-CONTENTS-AND-GAPS.md) explain every layer. The original frozen skill/archive snapshots remain under `archives/`.

**Normal use requires no Drive, Notion, account or internet lookup for stored examples.** After cloning, run `python3 tools/sync_library.py` once from the checkout root: it assembles the tracked local archive pieces, verifies their hashes and restores the complete payloads. A clone alone does not include oversized raw scene data and archive binaries. Resolve existing local paths and inspect actual files before considering recovery. The original [Drive manifest](library/manifest.json) is retained as historical backup provenance, not the primary path. Do not download a file that already exists locally.

Run these from the checkout root:

```bash
python3 tools/library.py list
python3 tools/library.py where 04-poke
python3 tools/library.py find frames.csv
python3 tools/library.py verify
```

Each project is at `projects/ARCHIVE_ID/imessage-recreations/`. Read its `README-COMPLETE-EXAMPLE.md`. It contains the full measured `scenes/EXAMPLE/scene.json`, declared image/font assets, the original source clip, five completed films, all genuine shared adapters, per-method entry wrappers, authoring code, comparisons and analysis. Run `tools/render_example.py` **inside that materialized project**, after installing its pinned dependencies. Rendering is separate from opening stored films or reading source; the repository does not vendor third-party package installations or browser binaries.

The six examples use one complete scene plus genuine shared adapters for Remotion, GSAP, HTML/SVG, Pillow and native Motion Canvas. The per-method wrappers select that actual implementation; thirty independently rewritten standalone scene projects were not authored. Full scene data is not replaced by the neutral starters.

Supporting resources are under `resources/ARCHIVE_ID/`: frozen delivery, thirty silent masters, all retained authored source/fixtures, complete UI audio inputs, pinned font inputs/Linux fallbacks, and later workflow/review source. Their immutable ZIPs and all seventy-eight original transport parts are also retained in `archives/`. Use the inventory's relative paths if the checkout moves. Historical absolute paths inside scan reports remain provenance labels; `tools/library.py resolve-historical PATH` resolves retained canonical cases without rewriting their history.

Keep this private repository's current visibility unless the user explicitly changes its audience. Prior rejection of a different public source-site upload is historical; it does not prohibit this explicitly authorized private GitHub migration. Figma remains an unvalidated prototype, not a completed sixth method. New-company research may need online primary sources unless sufficient local documents/UI evidence are supplied.

## Read the relevant knowledge

For an original film, prove the action and try the edit in the [director workflow](director/directing.md) before reaching for the catalogue. The catalogue and keyword router help find a component when a particular shot calls for it.

For recreation and technique adaptation, open the relevant source movie, native-frame atlas, study JSON, [design grammar](director/design-grammar.md) and component contract. Record the inspected frames, parent and clip structure, material and editability limits. Reconstruct source-specific artwork when the shot requires it. Use the brief schema and example as technical references for IDs, timing, clipping and evidence.

## Motion starters

| Starter | Show | Main constraint |
|---|---|---|
| `message-wall` | Breadth across conversations | Actor identity, row order and readable focus |
| `conversation-handoff` | A request, send and reply | Real composer changes; no fake AI typing |
| `mini-app-expand` | Work inside the conversation | Preserve context and readable controls |
| `app-drawer` | Where a tool is found | One clipped sheet and coherent children |
| `identity-morph` | One identity becoming an app icon | Separate outline, material and internal mark |
| `circle-to-panel` | An action becoming a working surface | New extension, not Poke's measured icon transition |
| `selection-confirm` | A decision and visible result | One control through press and confirmation |
| `camera-focus` | An important detail | Move the camera, preserve local UI geometry |
| `card-orbit` | Offerings converging into a promise | Independent paths, depth and readable settlement |

`director/motions.mjs` implements these nine adaptable scene builders. Keep capability/effect counts grounded in the actual catalogue. Starter timing is newly authored. The source studies contain measured motion and disclose when native poses, masks, source-specific paths or raster interiors prevent simple parameter replacement.

## Components and exposed UI

`director/components.mjs` provides nine editable builders: MessageBubble, Composer, AppIcon, AppCard, BottomSheet, PhoneFrame, ActionButton, Avatar and CameraRig. They emit the same scene contract used by the real renderers. Preserve stable child IDs, explicit copy/line breaks, independent camera/content groups and correct clipping. Replace the disclosed Arial fallback with verified production typography and remeasure it.

Open `director/index.html` for a standalone visual explorer. It works from the extracted folder without an account/server, displays the starters and component anatomy, scrubs by frame, suggests motifs from a brief and exports scene, cue and SVG files. It contains no AI model and does not automatically finish a film, export video or create a Figma file.

```bash
node director/cli.mjs plan --brief "Show booking inside a conversation"
node director/cli.mjs scene --motif mini-app-expand --out work/scene.json
node scripts/engines/render.mjs --method gsap --scene work/scene.json --out work/preview.mp4
```

Read [RUNNING.md](RUNNING.md) for dependencies. Remotion, GSAP, HTML/SVG, Pillow and native Motion Canvas were executed in the original project. Reprobe capabilities in each new environment. The Figma converter remains a prototype without a validated Motion API session; follow installed Figma skills before attempting it.

## Frame and sound discipline

Read `director/analysis/index.json`: bundled historical CSVs cover all 7,499 aligned native output frames across the six accepted GSAP comparisons, with source mapping and residual error. These are not a fresh all-five-method scan. Atlas images show selected teaching phases, not every frame. Canonical trajectory samples describe reconstructed states; pixel comparisons independently measure visual differences. Neither certifies perceptual perfection.

For exact work, scan every aligned frame numerically, rank separated error peaks and inspect source, reconstruction and foreground differences near those peaks. Verify dimensions, rational cadence, lifecycle boundaries, transform composition, blur, materials, masks and editability. Preserve canonical hashes and outside-range proofs. Use `scripts/shared/SCHEMA.md`, verification tools and the reconstruction playbook.

Sound follows actions. Prefer licensed provenance-pinned clicks/real single keys when suitable, procedural accents for gaps, actual pauses and intentional silence. Do not sound titles, AI text, caret blinks or composer clearing. Start with UI only; music is optional. Check attacks/onsets, sample span, headroom and encoded true peaks. Read complete sound inputs, sources, stems and license/provenance records locally under `resources/complete-ui-audio-source-v1/`; resolve the exact paths through the local registry/inventory. The skill carries the workflow and reference evidence.

## Diagnose and deliver

Before retrying, log the attempt, observed defect/error, evidence, cause or bounded hypothesis, changed variable and next check. Do not repeat unchanged failed operations. Prior corrections remain in [the reconstruction playbook](references/reconstruction-playbook.md), [execution ledger](references/execution-ledger.md) and [director upgrade log](director/upgrade-steps.md).

Deliver company research/evidence, brief/shot plan, component configuration, complete scene/assets/code, visual evidence, cue provenance, renders, comparisons, checks and known limits. Distinguish measured source evidence, authored choreography, inference, editable geometry/text and static imagery. Add accepted new examples to the local registry/inventory with hashes and rendered visual references; preserve frozen deliveries. Use `director/package_skill.py` with an explicit new output filename; the legacy packager predates this layer and can overwrite older archive names.
