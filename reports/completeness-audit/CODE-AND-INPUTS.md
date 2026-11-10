# Final main code, keyframes and runtime inputs — independent audit

**The clarified final delivery is complete at the file/input level in this synchronized local repository.** All six full accepted scene files match their registered and immutable case-archive hashes; every one of 4,632 declared runtime asset paths exists and matches its archived SHA256; all five genuine shared adapters and all thirty per-example method wrappers are present. The six original reference clips and thirty final movie files also SHA-match their registered identities.

This is a verification of the actual final code/data, not a promise of 100% visual identity or a new full rerender. Older versions and caches are outside the user’s clarified requirement. Remote Git/tree proof is a separate part of the parent audit; this report checks the local files.

The full per-file findings, hashes and all 4,632 asset records are in [CODE-AND-INPUTS.json](../../reports/completeness-audit/CODE-AND-INPUTS.json). Use [inventory/ALL-FILES.csv](../../inventory/ALL-FILES.csv) for the whole-library location index.

## Full final scenes and motion data

| Final example | Scene bytes | Native output frames | Animated nodes | Nonempty property tracks | Literal key entries | Nodes with explicit lifecycle | Declared asset paths |
|---|---:|---:|---:|---:|---:|---:|---:|
| [01-photonhq](../../projects/01-photonhq-complete-v1/imessage-recreations/scenes/01-photonhq/scene.json) | 15,600,918 | 655 | 517 | 1,677 | 27,238 | 1,981 | 1,227 |
| [02-danieltian](../../projects/02-danieltian-complete-v1/imessage-recreations/scenes/02-danieltian/scene.json) | 414,006,429 | 1,360 | 210 | 683 | 21,874 | 4,866 | 622 |
| [03-photon-mini](../../projects/03-photon-mini-complete-v1/imessage-recreations/scenes/03-photon-mini/scene.json) | 35,753,408 | 1,260 | 406 | 1,131 | 69,900 | 1,308 | 1,659 |
| [04-poke](../../projects/04-poke-complete-v1/imessage-recreations/scenes/04-poke/scene.json) | 4,834,394 | 1,283 | 133 | 581 | 33,964 | 145 | 92 |
| [05-linq](../../projects/05-linq-complete-v1/imessage-recreations/scenes/05-linq/scene.json) | 15,225,907 | 1,458 | 1,156 | 4,643 | 48,379 | 1,385 | 368 |
| [06-gallery](../../projects/06-gallery-complete-v1/imessage-recreations/scenes/06-gallery/scene.json) | 39,145,282 | 1,483 | 1,259 | 7,247 | 35,761 | 2,199 | 664 |

Together these scenes contain **15,962 nonempty property tracks and 237,116 literal key entries**, plus 11,884 nodes with explicit start/end lifecycle data. These are counts of literal stored data, not counts of unique creative effects. Source-specific native pose groups can encode a change through lifecycle gates rather than an interpolated track. A body with thousands of static path nodes and a parent camera is still one coherent motion, not thousands of effects.

Every scene includes its complete accepted geometry/keyframe bytes, checked against both the local registry and the actual `PACK-CHECKSUMS.json` read from its immutable ZIP. Asset collection walks static image sources, animated `keyframes.src` values, child hierarchies and declared font sources; paths resolve relative to the actual scene. No declared remote/data-URI source was found. The 4,632 count is the sum of unique declared paths per case, including duplicated shared content across cases. This audit checked existence and SHA identity; it did not re-decode every image/font or reinterpret the artistic content.

The fourteen named teaching studies are therefore **not the quantity of motion data delivered**. They are selected explanations/filmstrips extracted from six complete scenes.

## Actual code and method entrypoints

The implementation is one complete measured scene per film plus real shared method adapters. It was not authored as thirty independently rewritten branded applications. All thirty wrapper files select their correct example and method and invoke the actual `tools/render_example.py`.

| Method | Concrete implementation in each project | Source constructs independently observed |
|---|---|---|
| Remotion | `engines/remotion-entry.jsx`, `engines/render.mjs` | Actual Remotion composition/current-frame/registerRoot and bundler/renderer calls |
| GSAP | `engines/web-runtime.mjs`, `engines/render.mjs` | Actual GSAP import, paused timeline, exact seek and Chromium capture |
| HTML/SVG | `engines/web-runtime.mjs`, `engines/common.mjs`, `engines/render.mjs` | Deterministic SVG state evaluation and browser screenshot/FFmpeg capture |
| Pillow + FFmpeg | `engines/render_pillow.py` | Actual PIL drawing and FFmpeg encode invocation |
| Native Motion Canvas | `engines/motion-canvas-runtime.mjs`, `engines/render_motion_canvas.mjs` | Actual Scene2D nodes/makeScene2D and native stage capture |

All referenced implementation files, thirty wrappers and eighteen dependency-manifest copies hash-match their immutable case pack maps. Same-named shared renderer files have one distinct hash across all six complete cases. The actual code copies are browsable under each project and in [the skill engine folder](../../skill/imessage-motion-recreation/scripts/engines/). The JSON audit gives each exact file/hash.

The main render runner creates new outputs/caches, applies the measured Pillow overrides, encodes with the validated profile and muxes reference audio with Rene’s explicit source/output cut. Existing final movies remain immutable comparison targets. This supported final-scene route is separate from historical incremental-authoring programs.

## Assets, fonts, audio and environment records

| Supplemental content checked directly | Payload files checked | Result |
|---|---:|---|
| [all-authored-source-and-fixtures-v1](../../resources/all-authored-source-and-fixtures-v1/) | 1,476 | 0 hash errors |
| [font-inputs-and-linux-fallbacks-v1](../../resources/font-inputs-and-linux-fallbacks-v1/) | 98 | 0 hash errors |
| [complete-ui-audio-source-v1](../../resources/complete-ui-audio-source-v1/) | 496 | 0 hash errors |
| [later-workflow-and-review-source-v1](../../resources/later-workflow-and-review-source-v1/) | 180 | 0 hash errors |

For source/fixture, font and audio packs, those counts exclude each pack’s own checksum-map member. The later workflow pack uses a different prefix and has no internal checksum map; each of its 180 payloads was compared directly with SHA256 of its immutable ZIP member, and its whole ZIP hash also matches. The archive format difference was diagnosed before retrying that check.

The font pack includes eight original full SF font inputs, six pinned Linux fallback font files, source/repair records, source-specific subsets and original license files. All 98 mapped payload files match. This preserves the actual font bytes, not an installed target-machine Fontconfig setup. Primary declared font subsets are included in the 4,632 asset closure.

The complete audio pack’s 496 mapped payload files match. Its ten inputs previously identified as missing from an older supplement—two stock archives, two captured source/license pages and six original mix reports—are all now present and SHA-identical. Six pinned generated music files and their provenance, licensed raw/prepared effects, synthesis source, canonical cue schedules, stems/mixes and portable rebuild/mux helpers are present. No new generation is needed to reuse those pinned inputs. The main thirty method movies retain the supplied soundtracks; later UI-audio mixes are separately documented.

The engine lockfiles pin real Node packages and Python requirements. They do **not** bundle installed `node_modules`, Python virtual environments, browser binaries, native system libraries or a tested Mac runtime image. Reading/stored-film playback can be offline after the normal local assembly. Rerendering first requires a compatible runtime, browser/FFmpeg/fonts and method dependencies. No fresh six-film/full-thirty-movie render is claimed by this audit.

## What failed and how it improved

These are retained, evidence-backed corrections, not new reruns in this audit. Their proof scopes matter; a fixed infrastructure bug is not a proof that source motion became perfect.

| Failure | Changed variable / improvement | Retained verification and status |
|---|---|---|
| **remotion-chunk-props** — Later transport chunks rendered blank after only inputProps changed. | Synchronize inputProps and resolved Composition.props for each chunk; prune only inactive lifecycles and prove SVG invariance. | Retained report compares 1360 decoded Remotion/GSAP frames after transport recovery; mean SSIM 0.999741755. Actual engine source is hash-checked in each final case. **fixed; historical bounded/multi-chunk evidence**. [reconstruction-playbook.md:109](../../skill/imessage-motion-recreation/references/reconstruction-playbook.md); [evidence](../../skill/imessage-motion-recreation/references/evidence/verification/remotion-v13-all-frames-parity.json). |
| **remotion-browser-reuse** — Repeated browser launches failed after earlier chunks succeeded with a 25-second startup timeout. | Own one browser via openBrowser/puppeteerInstance, reuse it across chunks and close in finally. | Four recorded control frames are pixel-identical with MAE 0. **fixed; bounded historical parity controls**. [reconstruction-playbook.md:110](../../skill/imessage-motion-recreation/references/reconstruction-playbook.md); [evidence](../../skill/imessage-motion-recreation/references/evidence/verification/remotion-browser-reuse-parity.json). |
| **pillow-coordinate-conditioning** — Mini frames 436–494 could display flat rectangles even in a fresh same-process capture. | Condition internal coordinates before rasterization; apply higher sampling only to audited affected ranges. | Release records 53 affectedframes; reported mean MAE 18.723788→0.600659, neutral pixel-exact controls and unchanged outside controls. **fixed; bounded released correction**. [reconstruction-playbook.md:119](../../skill/imessage-motion-recreation/references/reconstruction-playbook.md); [evidence](../../skill/imessage-motion-recreation/references/evidence/pillow-coordinate-conditioning/release-report.json). |
| **motion-canvas-text-rms** — Native text was 4–6 pixels too high, and transformed glyph shaping still differed after a baseline adjustment. | Measure actual inline geometry, shape Canvas glyphs at full-world RMS scale and compensate the paint transform; retain native editable Txt layout. | Retained all-six inventory/release binds glyph assay, controls and actual corrected capture history; source canonical unchanged. **fixed within audited text scope**. [reconstruction-playbook.md:120](../../skill/imessage-motion-recreation/references/reconstruction-playbook.md); [evidence](../../skill/imessage-motion-recreation/references/evidence/motion-canvas-text-inventory/rms-release-report.json). |
| **native-shadow-opacity** — Faded opaque components exposed shadow through ink, while a combined local Gaussian and world shadow could double-scale the kernel. | Paint an inner native shadow before outer opacity; when Gaussian and shadow coexist, apply both in the same component-local native-child canvas. | Release records combined fixture/near-plane 613 controls, all 16 dynamic-path states and all 11 Mini controls byte-identical where declared. **fixed; promoted corrected runtime with rejected iteration preserved**. [release-report.json:6](../../skill/imessage-motion-recreation/references/evidence/shadow-opacity/release-report.json); [evidence](../../skill/imessage-motion-recreation/references/evidence/shadow-opacity/release-report.json). |
| **linq-dark-control-plane** — A guessed fade produced a false backing halo; a continuous alpha fit regressed 24 held states. | Fit parent material and local control separately using measured quantized byte response; preserve original values on ties. | Release records 32 changed native states improving source MAE and 35 other controls exactly unchanged; mean MAE 1.562636→1.342749. **fixed; approved native-state source correction**. [reconstruction-playbook.md:122](../../skill/imessage-motion-recreation/references/reconstruction-playbook.md); [evidence](../../skill/imessage-motion-recreation/references/evidence/root-cash-plane-v20/release.json). |
| **linq-retained-frame625** — One retained Remotion frame had a white horizontal truncation despite a strong aggregate score. | Freshly capture the exact frozen scene; replace the bad retained state only after direct parity comparison. | Fresh capture has MAE 0/max-channel 0 to GSAP versus legacyMAE 2.185417/max 239. **artifact corrected; original cause unproven**. [reconstruction-playbook.md:118](../../skill/imessage-motion-recreation/references/reconstruction-playbook.md); [evidence](../../skill/imessage-motion-recreation/references/evidence/05-raster-parity-625/diagnostic.json). |
| **aac-overshoot** — Safe lossless music encoded at 112 kbps AAC reached+0.80 dBTP and clipped. | Run a codec-only bitrate comparison; use 256 kbps for music/full mix while keeping sparse effects gain separate. | Recorded 112 k:+0.80 dBTP;192 k:−0.98;256 k:−2.47, with no clipping in the latter two. Final-audit preserves actual source/config/execution hashes. **fixed for the measured listening-copy encoding**. [execution-steps.md:12](../../skill/imessage-motion-recreation/references/ui-audio/execution-steps.md); [evidence](../../resources/complete-ui-audio-source-v1/imessage-recreations/audio-recreation/mixes/01-photonhq/aac-headroom-diagnosis.json). |
| **poke-selection-timing** — Restaurant selection first appears at source 633 but accepted GSAP 645. | Preserve both indices; schedule new UI sound on 645 so it follows the delivered picture. | The execution log and canonical cue evidence retain the 12-frame discrepancy explicitly. **remaining visual mismatch; sound aligned to actual delivery**. [execution-steps.md:19](../../skill/imessage-motion-recreation/references/ui-audio/execution-steps.md); [evidence](../../resources/complete-ui-audio-source-v1/imessage-recreations/audio-recreation/ui-cues/04-poke.events.json). |

The original Linq frame 625 cause is explicitly unproven even though replacing the bad retained frame fixed that observed artifact. Poke’s twelve-frame graphics timing discrepancy is **not solved**: aligning its new sound to the delivered picture is correct audio scheduling, not a graphics repair. Current metrics and known limits must remain visible.

## Analysis, explanations and decision records

This audit independently checked the six current historical native-frame CSV hashes and row counts: **7,499 aligned output rows**, using the accepted GSAP picture as the comparison candidate. It also rechecked fourteen atlas hashes and six phase pairs per study, giving 84 source/rebuild teaching pairs. Named study windows cover a 1,697-frame union (22.6% of 7,499); this is teaching-window coverage, not missing final animation code or a quality percentage.

The current repository contains 298 Markdown documents outside this audit directory, including 132 step/ledger/playbook/handoff records. Their exact paths and hashes, plus state/scope JSON paths, are listed in this audit’s JSON. Important entrypoints include [PROJECT-HANDOFF.md](../../PROJECT-HANDOFF.md), [SKILL.md](../../skill/imessage-motion-recreation/SKILL.md), [reconstruction playbook](../../skill/imessage-motion-recreation/references/reconstruction-playbook.md), [execution ledger](../../skill/imessage-motion-recreation/references/execution-ledger.md), [director upgrade log](../../skill/imessage-motion-recreation/director/upgrade-steps.md), [audio execution steps](../../skill/imessage-motion-recreation/references/ui-audio/execution-steps.md) and each case’s `references/<id>/steps*.md`. Counts are from the audit timestamp, not an assertion that every historical conversation/tool action was transcribed.

## Remaining boundaries of the final work

- Source/candidate visual residuals are nonzero. Renderer agreement and successful files do not certify perceptual perfection.
- Poke’s source 633/delivered 645 selection remains a known timing mismatch.
- Static raster card interiors, portraits, materials/hardware and outlined glyphs preserve declared semantic editability limits. Outer motion does not make bitmap words editable text.
- Figma Motion/export remains an unvalidated prototype.
- Fourteen curated studies, nine neutral components, nine authored starters and a keyword motion router provide direction aids; they are not an exhaustive motion taxonomy or autonomous aesthetic judge.
- Target-machine dependency setup, actual browser interaction/playback and human audio audition are separate checks.

None of these boundaries is evidence of a missing final scene, final keyframe array or declared asset path.

## Secondary appendix: retained history and current staging

The current restored staging folder `/workspace/imessage-motion-local` was compared independently with this repository. **14,829 files match byte-for-byte**. The only staging-only path is generated Python bytecode `tools/__pycache__/build_inventory.cpython-312.pyc`. Eleven differing paths are ten regenerated inventory files and one generated `.pyc`. No staging-only authored production source was found. This compares the available restored staging, not the unavailable original pre-reset workspace.

The six previously installed-only legacy helpers are present in the complete authored-source archive tree: `retain_running_mc.py`, `render_pillow.before-alternatives.py`, `motion-canvas-runtime.before-alternatives.mjs`, `mux_reference_audio.py`, `run_alternative_batch.py`, and `transparent_image_ranges.py`. Exact locations/hashes are in the JSON. The six per-case source areas contain 784 retained authored program files in addition to shared engine code and fixture/source packs.

Historical authoring tools are preserved as reference, not promised as complete standalone pipelines for every old version. Examples of unavailable/superseded historical inputs include HQ’s `early-walls-v7-measure/observations-all.json`, Daniel’s old `outputs/02-danieltian/final-v18/scene.json`, and Mini’s `mail-edit-v17-elements.json`; exact reading scripts/lines are recorded in the JSON. Forty-six historical Python import occurrences use `cv2`, which is not pinned in the canonical rendering requirements. Those observations concern old measurement/authoring routes, not the complete accepted final scene/render route.

The original pre-reset workspace is unavailable, so this audit cannot certify every file/version ever written there. Scratch/intermediate exports, installed packages, browser/compiler/frame caches and every verbatim tool/agent conversation were not universally archived. The user clarified those previous versions/caches are not required. The final main-code/keyframe/asset closure above remains the relevant passing result.

## Reproduction of this audit’s claims

Read actual current scene JSONs and registry records; hash each full scene; recursively enumerate static/animated image and font sources; resolve relative paths; compare every local runtime hash to its actual case ZIP checksum map; verify all referenced engine, wrapper and lockfile hashes; directly hash supplemental pack payloads; re-count literal motion tracks/keys/lifecycles; verify reference/final file hashes, teaching atlas/CSV identities, documented failure evidence and current staging content. No production file was changed, no remote service was accessed and no dependency or new render was created.
