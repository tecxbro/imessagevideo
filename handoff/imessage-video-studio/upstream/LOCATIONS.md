# Every production file: local locations

All paths below are relative to this repository. After Git LFS finishes, these are real local files. The current cloud checkout is `/workspace/imessagevideo`; your Mac checkout path will be wherever you clone it. No files have been remotely installed on your Mac.

For every individual filename, byte count, role and SHA256, use [ALL-FILES.csv](inventory/ALL-FILES.csv), [the searchable offline inventory](inventory/index.html), or [the code-only list](inventory/CODE.csv). All archive copies and transport parts are retained and labelled, so duplicate paths do not imply different authored works.

## Fast entry points

| Need | Exact location |
|---|---|
| Watch originals and all thirty method results; read full renderer code | [catalog/index.html](catalog/index.html) |
| Read the skill instructions | [skill/imessage-motion-recreation/SKILL.md](skill/imessage-motion-recreation/SKILL.md) |
| Inspect every file | [inventory/index.html](inventory/index.html) and [ALL-FILES.csv](inventory/ALL-FILES.csv) |
| Find only code/full scene data | [CODE.csv](inventory/CODE.csv) |
| Find every video, including duplicate archival copies | [VIDEOS.csv](inventory/VIDEOS.csv) |
| Find frame studies, comparisons and evidence | [ANALYSIS.csv](inventory/ANALYSIS.csv) |
| Find effects, music, mixes and stems | [AUDIO.csv](inventory/AUDIO.csv) |
| Find images, vectors and fonts | [ASSETS.csv](inventory/ASSETS.csv) |
| Understand exactly what is taught and missing | [SKILL-CONTENTS-AND-GAPS.md](reports/SKILL-CONTENTS-AND-GAPS.md) |
| Install/read on your Mac | [MAC-SETUP.md](MAC-SETUP.md) |

## Six full projects

| Film | Full scene code/data | Original | Five finished reference-audio films | Frame analysis |
|---|---|---|---|---|
| Photon 2.0 | [scene.json](projects/01-photonhq-complete-v1/imessage-recreations/scenes/01-photonhq/scene.json) | [source.mp4](projects/01-photonhq-complete-v1/imessage-recreations/references/01-photonhq/source.mp4) | [deliverables](projects/01-photonhq-complete-v1/imessage-recreations/deliverables/01-photonhq/) | [scan.json](projects/01-photonhq-complete-v1/imessage-recreations/verification/timeline-scans/01-photonhq-v10/scan.json) |
| Photon Agent to Agent | [scene.json — assemble locally](STORAGE.json) | [source.mp4](projects/02-danieltian-complete-v1/imessage-recreations/references/02-danieltian/source.mp4) | [deliverables](projects/02-danieltian-complete-v1/imessage-recreations/deliverables/02-danieltian/) | [scan.json](projects/02-danieltian-complete-v1/imessage-recreations/verification/timeline-scans/02-danieltian-v19/scan.json) |
| Photon Mini Apps | [scene.json](projects/03-photon-mini-complete-v1/imessage-recreations/scenes/03-photon-mini/scene.json) | [source.mp4](projects/03-photon-mini-complete-v1/imessage-recreations/references/03-photon-mini/source.mp4) | [deliverables](projects/03-photon-mini-complete-v1/imessage-recreations/deliverables/03-photon-mini/) | [scan.json](projects/03-photon-mini-complete-v1/imessage-recreations/verification/timeline-scans/03-photon-mini-v18-pc709/scan.json) |
| Poke Apple Messages | [scene.json](projects/04-poke-complete-v1/imessage-recreations/scenes/04-poke/scene.json) | [source.mp4](projects/04-poke-complete-v1/imessage-recreations/references/04-poke/source.mp4) | [deliverables](projects/04-poke-complete-v1/imessage-recreations/deliverables/04-poke/) | [scan.json](projects/04-poke-complete-v1/imessage-recreations/verification/timeline-scans/04-poke-v19/scan.json) |
| Linq iMessage Apps | [scene.json](projects/05-linq-complete-v1/imessage-recreations/scenes/05-linq/scene.json) | [source.mp4](projects/05-linq-complete-v1/imessage-recreations/references/05-linq/source.mp4) | [deliverables](projects/05-linq-complete-v1/imessage-recreations/deliverables/05-linq/) | [scan.json](projects/05-linq-complete-v1/imessage-recreations/verification/timeline-scans/05-linq-v20-pc709/scan.json) |
| Rene | [scene.json](projects/06-gallery-complete-v1/imessage-recreations/scenes/06-gallery/scene.json) | [source.mp4](projects/06-gallery-complete-v1/imessage-recreations/references/06-gallery/source.mp4) | [deliverables](projects/06-gallery-complete-v1/imessage-recreations/deliverables/06-gallery/) | [scan.json](projects/06-gallery-complete-v1/imessage-recreations/verification/timeline-scans/06-gallery-v23/scan.json) |

Inside **each** project root, `engines/` contains the actual renderer implementation; `examples/<example-id>/render-METHOD.py` contains explicit run entrypoints; `tools/render_example.py` provides the supported cold-build route. `references/<example-id>/` contains retained authoring programs, assets and source input. `scenes/<example-id>/scene.json` is the full accepted measured geometry/keyframe data, not a small neutral starter. `verification/timeline-scans/` includes native per-frame CSVs; `verification/final/` includes comparison reports and retained comparison images.

The six projects share genuine adapters; the same adapter code is intentionally preserved in each portable case. To read one full representative implementation directly:

- [remotion-entry.jsx](projects/01-photonhq-complete-v1/imessage-recreations/engines/remotion-entry.jsx)
- [render.mjs](projects/01-photonhq-complete-v1/imessage-recreations/engines/render.mjs)
- [web-runtime.mjs](projects/01-photonhq-complete-v1/imessage-recreations/engines/web-runtime.mjs)
- [runtime-scene.mjs](projects/01-photonhq-complete-v1/imessage-recreations/engines/runtime-scene.mjs)
- [scene-loader.mjs](projects/01-photonhq-complete-v1/imessage-recreations/engines/scene-loader.mjs)
- [common.mjs](projects/01-photonhq-complete-v1/imessage-recreations/engines/common.mjs)
- [render_motion_canvas.mjs](projects/01-photonhq-complete-v1/imessage-recreations/engines/render_motion_canvas.mjs)
- [motion-canvas-runtime.mjs](projects/01-photonhq-complete-v1/imessage-recreations/engines/motion-canvas-runtime.mjs)
- [render_pillow.py](projects/01-photonhq-complete-v1/imessage-recreations/engines/render_pillow.py)
- [package.json](projects/01-photonhq-complete-v1/imessage-recreations/engines/package.json)
- [package-lock.json](projects/01-photonhq-complete-v1/imessage-recreations/engines/package-lock.json)
- [requirements.txt](projects/01-photonhq-complete-v1/imessage-recreations/engines/requirements.txt)

## Shared production resources

| Resource | Exact local root |
|---|---|
| frozen-visual-delivery-v1 | [resources/frozen-visual-delivery-v1/](resources/frozen-visual-delivery-v1/) |
| silent-picture-masters-v1 | [resources/silent-picture-masters-v1/](resources/silent-picture-masters-v1/) |
| all-authored-source-and-fixtures-v1 | [resources/all-authored-source-and-fixtures-v1/](resources/all-authored-source-and-fixtures-v1/) |
| complete-ui-audio-source-v1 | [resources/complete-ui-audio-source-v1/](resources/complete-ui-audio-source-v1/) |
| font-inputs-and-linux-fallbacks-v1 | [resources/font-inputs-and-linux-fallbacks-v1/](resources/font-inputs-and-linux-fallbacks-v1/) |
| later-workflow-and-review-source-v1 | [resources/later-workflow-and-review-source-v1/](resources/later-workflow-and-review-source-v1/) |

The first five resource packs use an `imessage-recreations/` prefix. `later-workflow-and-review-source-v1` uses its own named prefix. Exact starting points:

- [All retained authored programs and fixtures](resources/all-authored-source-and-fixtures-v1/imessage-recreations/)
- [Full UI-audio working tree](resources/complete-ui-audio-source-v1/imessage-recreations/audio-recreation/)
- [Portable audio rebuild/mux helpers](resources/complete-ui-audio-source-v1/imessage-recreations/tools/)
- [Silent masters](resources/silent-picture-masters-v1/imessage-recreations/outputs/)
- [Pinned font inputs and fallback environment](resources/font-inputs-and-linux-fallbacks-v1/imessage-recreations/)
- [Later site/review and workflow source](resources/later-workflow-and-review-source-v1/later-workflow-and-review-source-v1/)
- [Original frozen delivery](resources/frozen-visual-delivery-v1/imessage-recreations/)

## Skill, visual direction and analysis

- [Main direction/research instructions](skill/imessage-motion-recreation/SKILL.md)
- [Research-first workflow](skill/imessage-motion-recreation/library/RESEARCH-FIRST.md) and [company profile schema](skill/imessage-motion-recreation/library/company-profile.schema.json)
- [Visual starter/component explorer](skill/imessage-motion-recreation/director/index.html)
- [Fourteen-study catalogue](skill/imessage-motion-recreation/director/catalogue.json), [study recipes](skill/imessage-motion-recreation/director/source-studies/), and [paired visual atlases](skill/imessage-motion-recreation/director/atlas/)
- [Nine component builders](skill/imessage-motion-recreation/director/components.mjs) and [component contracts](skill/imessage-motion-recreation/director/component-contracts.md)
- [Nine motion starter builders](skill/imessage-motion-recreation/director/motions.mjs)
- [Motion-selection heuristic](skill/imessage-motion-recreation/director/decisions.mjs), [design grammar](skill/imessage-motion-recreation/director/design-grammar.md), and [direction workflow](skill/imessage-motion-recreation/director/directing.md)
- [Historical native-frame analysis and all six CSV copies](skill/imessage-motion-recreation/director/analysis/)
- [UI-sound workflow](skill/imessage-motion-recreation/references/ui-audio-workflow.md)
- [Execution history](skill/imessage-motion-recreation/references/execution-ledger.md), [complete-library steps](skill/imessage-motion-recreation/library/execution-steps.md), and [director upgrade log](skill/imessage-motion-recreation/director/upgrade-steps.md)
- [Earlier release evidence](release-evidence/), [current reports](reports/), and [exact skill contents/gaps](reports/SKILL-CONTENTS-AND-GAPS.md)

Fourteen is the number of curated source teaching studies. Their union covers 1,697 of 7,499 aligned frames; historical numeric comparison data covers the full 7,499 frames for accepted GSAP results. This is not an all-method pixel-perfect certificate. The full scene code covers the entire films. See the audit for nonzero errors, source-specific/raster content and the documented Poke timing mismatch.

## Archives and recovery

[archives/](archives/) contains every assembled ZIP after local synchronization, the frozen compact v3 skill ZIP and release-verification ZIP. [archives/resource-parts/](archives/resource-parts/) preserves all 78 original transport fragments. These duplicate data already extracted into projects/resources; they are retained because this migration requested every file. [inventory/restore-receipts/](inventory/restore-receipts/) and [inventory/extractions/](inventory/extractions/) record actual hash-verified local restoration.

Historical reports may contain old absolute paths under `/workspace/imessage-recreations` or superseded `outputs/...` labels. They remain unchanged as evidence. Resolve retained core examples with `python3 tools/library.py resolve-historical PATH`; use current relative paths in the inventory for everything else.

Git internals, installed third-party dependencies, caches, credentials and unfinished temporary writes are excluded. The inventory documents every observed exclusion. Those are not authored project source. Font/source licenses remain attached; storing a font does not create a redistribution license. The repository remains private.

Git stores the seventy-eight original pieces and both small snapshot ZIPs directly. The twelve large complete ZIPs and two oversized Daniel scene copies are losslessly derived locally by `python3 tools/sync_library.py`; see [STORAGE.json](STORAGE.json). All bytes are on GitHub without LFS or release downloads.
