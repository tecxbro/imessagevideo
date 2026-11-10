# What is actually in the skill, why there are fourteen studies, and what is missing

This is an audit of the restored v3 production/teaching package, not a claim that the model was trained or that every feature is finished. The current root is `/workspace/imessage-motion-local`. The exact original v3 snapshot remains in `archives/imessage-motion-complete-skill-v3.zip`; the working local entrypoint may now include the parent's local-first changes. The complete file-by-file location index is in [inventory/](../inventory/).

**The key distinction:** the six complete measured films and their full authored scenes are the production library. The fourteen studies are a smaller teaching catalogue extracted from that work. Nine reusable starters are a separate, newly authored design kit. A full film, a source study, a starter and a component are different things; adding their counts together would be misleading.

## What the agent is given

| Layer | Exact working file or directory | What it supplies |
|---|---|---|
| Instructions and routing | [SKILL.md](../skill/imessage-motion-recreation/SKILL.md) | When to research, recreate a source, direct a new film, port a component or design UI sound; what evidence to read; what to deliver |
| Company research | [RESEARCH-FIRST.md](../skill/imessage-motion-recreation/library/RESEARCH-FIRST.md), [company-profile.schema.json](../skill/imessage-motion-recreation/library/company-profile.schema.json) | Official domain, audience, promise, real user action, evidence of success, dated citations, observed/inferred/unresolved claims, brand assets and real UI states |
| Creative process | [directing.md](../skill/imessage-motion-recreation/director/directing.md) | Causal story, exact copy, named actors, attention, reading holds, sound, alternatives and three review stages |
| Decision helper | [decisions.mjs](../skill/imessage-motion-recreation/director/decisions.mjs) | Explicit keyword scoring, motif suggestions, matched words, choose/avoid rules, risks and editable parameters. This is a navigation aid, not an aesthetic AI or autonomous director |
| Shot-plan contract | [brief-schema.json](../skill/imessage-motion-recreation/director/brief-schema.json), [dinner-shot-plan.json](../skill/imessage-motion-recreation/director/examples/dinner-shot-plan.json) | Required shot fields, frame boundaries, evidence kind, components, reading holds, sound anchors and validation gates |
| Design instruction | [design-grammar.md](../skill/imessage-motion-recreation/director/design-grammar.md) | Typographic measurement, message grammar, hierarchy, masks, parent/local/camera transforms, materials, occlusion and continuity of identity |
| Named measured motions | [catalogue.json](../skill/imessage-motion-recreation/director/catalogue.json), [source-studies/](../skill/imessage-motion-recreation/director/source-studies/) | Fourteen selected source studies with actual frame windows, canonical scene hashes, layer identities, selected literal keys, anatomy, suitable uses, caveats and cue hooks |
| Visual reference | [atlas/](../skill/imessage-motion-recreation/director/atlas/), [component anatomy](../skill/imessage-motion-recreation/director/visuals/component-anatomy.png), [starter overview](../skill/imessage-motion-recreation/director/visuals/starter-overview.jpg) | Fourteen paired filmstrips: six source/rebuild phase pairs per study, giving eighty-four pairs (168 thumbnail panels). These are selected teaching images, not every frame of the films |
| Editable components | [components.mjs](../skill/imessage-motion-recreation/director/components.mjs), [component-contracts.md](../skill/imessage-motion-recreation/director/component-contracts.md) | Nine neutral parameterized builders; actual runnable code and explicit editability boundaries |
| New motion code | [motions.mjs](../skill/imessage-motion-recreation/director/motions.mjs), [example scenes and events](../skill/imessage-motion-recreation/director/examples/scenes/) | Nine adaptable starter functions plus nine sample scene JSON files and nine event JSON files. Timing and artwork are new defaults, not recovered source choreography |
| Exposed UI | [director/index.html](../skill/imessage-motion-recreation/director/index.html) | A local viewer/editor for starter play/pause, native-frame scrubbing, exposed copy/color/duration parameters, recommendations and scene/cue/SVG export. No model runs inside it |
| Actual renderer source | [scripts/engines/](../skill/imessage-motion-recreation/scripts/engines/) | Real shared Remotion React, GSAP, HTML/SVG, Pillow and native Motion Canvas adapters with pinned dependency manifests |
| Scene contract | [SCHEMA.md](../skill/imessage-motion-recreation/scripts/shared/SCHEMA.md), [scene-schema.json](../skill/imessage-motion-recreation/scripts/shared/scene-schema.json) | Geometry, stable IDs, lifecycles, keyframes, clips, camera hierarchy, assets and source mapping |
| Whole-film historical comparison | [analysis/index.json](../skill/imessage-motion-recreation/director/analysis/index.json), [analysis/](../skill/imessage-motion-recreation/director/analysis/) | Six scans and CSVs: 7,499 aligned native output frame rows with reference/candidate indices, times and residual errors |
| Reconstruction practice and corrections | [reconstruction-playbook.md](../skill/imessage-motion-recreation/references/reconstruction-playbook.md), [execution-ledger.md](../skill/imessage-motion-recreation/references/execution-ledger.md), [evidence/](../skill/imessage-motion-recreation/references/evidence/) | Measurement, extraction, glyph tracing, masks, actual method capability, renderer failures, source comparisons, and why accepted corrections worked |
| UI sound | [ui-audio-workflow.md](../skill/imessage-motion-recreation/references/ui-audio-workflow.md), [ui-audio/](../skill/imessage-motion-recreation/references/ui-audio/), full audio resource pack | Visible-action cue rules, schedules, licensed effects, prepared/generated inputs, stems, mixes, provenance, gain and codec validation |
| Production/resource registry | [manifest.json](../skill/imessage-motion-recreation/library/manifest.json), [file-inventory.json.gz](../skill/imessage-motion-recreation/library/file-inventory.json.gz) | Frozen archive/part identities and hashes; all 14,161 ZIP-member entries. This original Drive registry is backup provenance; the new local manifest resolves restored files without Drive |
| Integrity/reproduction | [verification/](../skill/imessage-motion-recreation/library/verification/), [materialize.py](../skill/imessage-motion-recreation/library/materialize.py), [RUNNING.md](../skill/imessage-motion-recreation/RUNNING.md) | Historical cold checks, source audits, safe archive assembly/extraction and dependency/runtime instructions |

The skill does not inject all these bytes into a model at once. It tells the agent which local code, JSON, images, video frames and evidence to open for the task. The full resources must exist beside the skill and the agent must actually inspect them. A link or image filename is not visual understanding.

## The actual source-code model

There is **one complete measured scene per accepted example**, with its full geometry, keyframes and assets. All five genuine renderer implementations consume that common scene contract. Per-example `render-METHOD.py` files are executable selectors/wrappers for those implementations, not five independently rewritten branded applications.

The source implementations include:

- `scripts/engines/render.mjs`, `remotion-entry.jsx`: Remotion composition and frame rendering; `render.mjs` also captures browser GSAP/HTML outputs.
- `scripts/engines/web-runtime.mjs`: a real paused GSAP timeline and an independently evaluated HTML/SVG path.
- `scripts/engines/common.mjs`, `runtime-scene.mjs`, `scene-loader.mjs`: shared state, scene and SVG machinery.
- `scripts/engines/render_pillow.py`: Python/Pillow drawing and FFmpeg assembly.
- `scripts/engines/render_motion_canvas.mjs`, `motion-canvas-runtime.mjs`: genuine native Scene2D nodes and deterministic canvas capture.

The complete case projects restored under `projects/<archive-id>/imessage-recreations/` contain `scenes/<example-id>/scene.json`, assets, `engines/`, five wrappers under `examples/<example-id>/`, original clips, finished movies, evidence, and retained historical authoring programs. Read their `README-COMPLETE-EXAMPLE.md`. Historical helper programs can depend on superseded measurements; the accepted full-scene plus adapter route is the supported cold-build path.

The six project roots are:

| Example | Full local project root relative to this report |
|---|---|
| PhotonHQ | [01-photonhq-complete-v1](../projects/01-photonhq-complete-v1/imessage-recreations/) |
| Daniel Tian's Photon | [02-danieltian-complete-v1](../projects/02-danieltian-complete-v1/imessage-recreations/) |
| Photon Mini App | [03-photon-mini-complete-v1](../projects/03-photon-mini-complete-v1/imessage-recreations/) |
| Poke | [04-poke-complete-v1](../projects/04-poke-complete-v1/imessage-recreations/) |
| Linq | [05-linq-complete-v1](../projects/05-linq-complete-v1/imessage-recreations/) |
| Launch gallery / Rene | [06-gallery-complete-v1](../projects/06-gallery-complete-v1/imessage-recreations/) |

## Why fourteen studies, and the complete list

Fourteen is the number of curated motion breakdowns actually authored, not a technical limit, a count of every animation, or proof that the full videos only contain fourteen ideas. They were selected to teach representative recurring problems. The curation is not exhaustive. More of the existing full scenes can be turned into studies; that editorial/parameterization work has not all been done.

The current allocation is two studies for PhotonHQ, three for Daniel Tian, three for Mini, two for Poke, two for Linq and two for Rene. All frame ranges below are inclusive output-native windows. Atlas links show the actual paired visual; the recipe link leads to the detailed measured JSON. A starter association is a conceptual adaptation, not an exact preset replay of the study.

| # | Study / visual | Film and inclusive output frames | Measured evidence | Adaptable starter association |
|---|---|---|---|---|
| 1 | [Cursor press, compression, release and reflow](../skill/imessage-motion-recreation/director/atlas/photon-press-release.jpg)<br>`photon-press-release` | `01-photonhq` 45–119 | [press-release](../skill/imessage-motion-recreation/director/source-studies/photon-recipes.json) | `selection-confirm` |
| 2 | [Staggered message field with overlapping channel handoffs](../skill/imessage-motion-recreation/director/atlas/photon-channel-walls.jpg)<br>`photon-channel-walls` | `01-photonhq` 336–464 | [channel-walls](../skill/imessage-motion-recreation/director/source-studies/photon-recipes.json) | `message-wall` |
| 3 | [Visible draft, thought pause and send flight](../skill/imessage-motion-recreation/director/atlas/photon-compose-send.jpg)<br>`photon-compose-send` | `02-danieltian` 95–179 | [compose-send](../skill/imessage-motion-recreation/director/source-studies/photon-recipes.json) | `conversation-handoff` |
| 4 | [Independent service trajectories become a group header](../skill/imessage-motion-recreation/director/atlas/photon-agent-convergence.jpg)<br>`photon-agent-convergence` | `02-danieltian` 548–629 | [agent-convergence](../skill/imessage-motion-recreation/director/source-studies/photon-recipes.json) | `card-orbit` |
| 5 | [Conversation growth with an independent header and overlapping avatars](../skill/imessage-motion-recreation/director/atlas/photon-thread-camera-overlap.jpg)<br>`photon-thread-camera-overlap` | `02-danieltian` 621–1029 | [thread-camera-overlap](../skill/imessage-motion-recreation/director/source-studies/photon-recipes.json) | `camera-focus`, `conversation-handoff` |
| 6 | [Circle identity becomes a verified app](../skill/imessage-motion-recreation/director/atlas/poke-identity_circle_to_app.jpg)<br>`poke-identity_circle_to_app` | `04-poke` 40–81 | [poke.identity_circle_to_app](../skill/imessage-motion-recreation/director/source-studies/mini-poke-recipes.json) | `identity-morph` |
| 7 | [Message result springs into an anchored rich card](../skill/imessage-motion-recreation/director/atlas/mini-rich_card_arrival.jpg)<br>`mini-rich_card_arrival` | `03-photon-mini` 546–617 | [mini.rich_card_arrival](../skill/imessage-motion-recreation/director/source-studies/mini-poke-recipes.json) | `mini-app-expand`, `selection-confirm` |
| 8 | [Mini App opens above a receding Messages page](../skill/imessage-motion-recreation/director/atlas/mini-sheet_depth.jpg)<br>`mini-sheet_depth` | `03-photon-mini` 618–734 | [mini.sheet_depth](../skill/imessage-motion-recreation/director/source-studies/mini-poke-recipes.json) | `mini-app-expand`, `app-drawer` |
| 9 | [Food and message fragments detach into the world while phone retreats](../skill/imessage-motion-recreation/director/atlas/mini-world_release.jpg)<br>`mini-world_release` | `03-photon-mini` 730–799 | [mini.world_release](../skill/imessage-motion-recreation/director/source-studies/mini-poke-recipes.json) | `card-orbit`, `camera-focus` |
| 10 | [A pressed option becomes an outgoing conversation result](../skill/imessage-motion-recreation/director/atlas/poke-choice_to_message.jpg)<br>`poke-choice_to_message` | `04-poke` 330–375 | [poke.choice_to_message](../skill/imessage-motion-recreation/director/source-studies/mini-poke-recipes.json) | `selection-confirm`, `conversation-handoff` |
| 11 | [Chat card expands into a clipped mini-app document](../skill/imessage-motion-recreation/director/atlas/linq-chat-to-mini-app.jpg)<br>`linq-chat-to-mini-app` | `05-linq` 351–510 | [linq-chat-to-mini-app](../skill/imessage-motion-recreation/director/source-studies/linq-rene-recipes.json) | `mini-app-expand`, `camera-focus` |
| 12 | [A control pulse drives an independent rolling amount](../skill/imessage-motion-recreation/director/atlas/linq-native-control-and-amount.jpg)<br>`linq-native-control-and-amount` | `05-linq` 768–837 | [linq-native-control-and-amount](../skill/imessage-motion-recreation/director/source-studies/linq-rene-recipes.json) | `selection-confirm` |
| 13 | [A centered device carries consent and completion](../skill/imessage-motion-recreation/director/atlas/rene-message-to-action-cascade.jpg)<br>`rene-message-to-action-cascade` | `06-gallery` 680–830 | [rene-message-to-action-cascade](../skill/imessage-motion-recreation/director/source-studies/linq-rene-recipes.json) | `conversation-handoff`, `selection-confirm` |
| 14 | [A letter-slot prop leaves the word and leads into messages](../skill/imessage-motion-recreation/director/atlas/rene-word-prop-message-bridge.jpg)<br>`rene-word-prop-message-bridge` | `06-gallery` 846–1048 | [rene-word-prop-message-bridge](../skill/imessage-motion-recreation/director/source-studies/linq-rene-recipes.json) | `identity-morph`, `camera-focus` |

Each study supplies intent, choose/avoid advice, anatomy, editability caveats, source window, six selected phase pairs and scene identity. Its detailed JSON supplies relevant canonical nodes/keys or sampled poses. Some catalogue entries delegate the detailed bindings to their rich-study JSON; an empty short `bindings` list is not a full-source omission.

## Exactly how much is curated versus analyzed

| Film | Curated studies | Frames inside the union of study windows | Native analyzed output frames | Frames outside named study windows |
|---|---:|---:|---:|---:|
| `01-photonhq` | 2 | 204 | 655 | 451 |
| `02-danieltian` | 3 | 567 | 1,360 | 793 |
| `03-photon-mini` | 3 | 254 | 1,260 | 1,006 |
| `04-poke` | 2 | 88 | 1,283 | 1,195 |
| `05-linq` | 2 | 230 | 1,458 | 1,228 |
| `06-gallery` | 2 | 354 | 1,483 | 1,129 |
| Total | 14 | 1,697 | 7,499 | 5,802 |

The union of named study windows is 1,697 of 7,499 aligned output frames (about 22.6%). That ratio is **teaching-window coverage**, not a quality percentage or missing-code percentage. Outside those windows can be holds, repetitions, title motion, other transitions or other graphic scenes. A shot-by-shot audit is needed before labeling each interval as a new unique effect.

All 7,499 frames have historical numeric source/candidate comparisons. They do not all have a written shot breakdown, annotated phase image, editable parameter API, standalone starter or narrated design rationale. The fourteen JPEGs do not replace the full video or per-frame data.

## All nine editable components

All are actual functions in `director/components.mjs`. All support stable IDs and explicit position. Their current appearance is neutral, using disclosed Arial fallback and generic artwork rather than every original source asset.

| Component | Exposed design controls | Important boundary |
|---|---|---|
| `MessageBubble` | side, copy, width/height, tail, fill, font size | Explicit dimensions/line breaks; no arbitrary-text auto-fit |
| `Composer` | width, copy, active state | A composed scene element, not an operating-system text field |
| `AppIcon` | size, roundness, color, label | A neutral mark; not the measured Poke palm/material pose sequence |
| `AppCard` | width/height, title, detail, action, artwork color | Generic editable field, not recovered source photography or screenshot interiors |
| `BottomSheet` | width/height, title, children and owned rounded clip | Child motion and viewport must remain coherent |
| `PhoneFrame` | width/height, title, children | Conversation viewport/chrome, not an exact hardware/reflection model |
| `ActionButton` | width/height, copy, fill | Preserve one stable control through press/result states |
| `Avatar` | size, initials, fill | Neutral initials, not source portraits/Memoji |
| `CameraRig` | children, keyframes, position, origin/pivot | Moves a parent hierarchy without rewriting local UI |

## All nine motion starters

| Starter | What it demonstrates | What still must be directed |
|---|---|---|
| `message-wall` | Independent bubbles with stagger and parent camera | Real participants/copy, hierarchy, paths, density and readability |
| `conversation-handoff` | Visible human draft, send, reply | Product-specific interaction, realistic pauses, reading holds and layout |
| `mini-app-expand` | A useful card expands within a conversation | Real embedded product state, expansion anchor, controls and proof |
| `app-drawer` | A clipped tool sheet opens | Actual available tools, icon/label art, grouping and context |
| `identity-morph` | A neutral identity changes outline/material/mark | Source-specific shapes and measured pose sequence for exact Poke |
| `circle-to-panel` | Compact surface becomes content | A new composition; explicitly not the measured Poke transition |
| `selection-confirm` | One control press and visible confirmation | Real capability, correct selected state and confirmation copy |
| `camera-focus` | Parent camera emphasizes a detail | Attention target, context, travel and reading hold |
| `card-orbit` | Distinct cards converge | Independent authored paths and settlement; no claim that the reference used an analytic circular orbit |

`motions.mjs` currently accepts duration 2–12 seconds, fps 24/25/30/60, copy/title/color and motif-specific options. Those are authoring constraints, not the limits of the underlying scene engines or full source films. Source typography and arbitrary string fitting are not solved by changing a preset name.

## What is measured, authored, heuristic or unverified

| Kind | Examples | What it means |
|---|---|---|
| Measured/historical evidence | Full scene geometry and native keys; source hashes; atlas phases; 7,499 comparison rows | Tied to particular source/output files and frame clocks; not recovered original project physics |
| Newly authored design | Neutral components, starter curves/default timings, dinner sample shot plan | Runnable reusable examples; not a claim of exact source appearance or choreography |
| Written guidance | Design grammar, research order, shot review, sound rules | Instructions for an agent to follow and judge using its actual tools |
| Heuristic code | `decisions.mjs` word matching and scores | Explainable suggestions; cannot evaluate beauty, story truth or a rendered frame |
| Actual rendered methods | Remotion, GSAP, HTML/SVG, Pillow, native Motion Canvas | Real completed adapters/films from the earlier project; fresh dependencies/runtime must be checked here |
| Prototype only | `scripts/figma/prepare-figma.mjs` | No validated Figma Motion/export session; not a completed sixth format |
| Prior integrity checks | Pack and dependency-source audits; five cold sample frames; audio/font checks | Defined scopes, not a new clean-machine rerender of all thirty final movies |
| Viewer QA | Historical static syntax/local-link checks | Earlier interactive browser access was blocked; do not silently promote that to a playback pass |

## Known visual and audio limits

The source/candidate scans are against the accepted **GSAP** picture, with all aligned output frames represented. They are not an independent source comparison for every method. Their recorded pixel errors are nonzero:

| Film | CSV rows | Historical mean native MAE | Maximum native MAE |
|---|---:|---:|---:|
| [01-photonhq](../skill/imessage-motion-recreation/director/analysis/01-photonhq/frames.csv) | 655 | 1.0235 | 5.2943 |
| [02-danieltian](../skill/imessage-motion-recreation/director/analysis/02-danieltian/frames.csv) | 1,360 | 0.7569 | 3.0583 |
| [03-photon-mini](../skill/imessage-motion-recreation/director/analysis/03-photon-mini/frames.csv) | 1,260 | 1.5265 | 4.4732 |
| [04-poke](../skill/imessage-motion-recreation/director/analysis/04-poke/frames.csv) | 1,283 | 2.6103 | 6.0337 |
| [05-linq](../skill/imessage-motion-recreation/director/analysis/05-linq/frames.csv) | 1,458 | 1.3110 | 5.2130 |
| [06-gallery](../skill/imessage-motion-recreation/director/analysis/06-gallery/frames.csv) | 1,483 | 0.9304 | 4.7878 |

MAE is a pixel-difference statistic on native frames, not a perceptual percentage. Neither low MAE nor byte-identical renderer parity establishes 100% identity with the original. The new source-check audit did not rerender these films.

A concrete known discrepancy is retained in `references/ui-audio-workflow.md`: Poke's restaurant selection is visible at source frame633 and accepted GSAP frame645, a twelve-frame mismatch. The new cue follows the picture actually delivered at645. That is honest synchronization to the reconstruction, not a fix of the source timing discrepancy.

Rene omits the permitted live-action interval: output0–1048 maps identically; output1049–1482 maps to source1230–1663. Frame paths in historical scan JSON can name the old `/workspace/imessage-recreations/outputs/...` locations. Those are provenance labels, not promises that those old absolute directories still exist. Use the local project/manifest mapping.

Some exact source lettering is vector outline geometry with semantic copy recorded beside it, not live-font editable text. Some rich-card interiors, portraits, hardware or material details are bounded static imagery. Native outer motion does not make a bitmap's internal words editable. New copy can require rebuilding or re-typesetting that element.

The compact skill does not itself generate/mix audio. It supplies schedules, source code and rules; the full audio pack supplies the binaries. UI effect cues are based on visible actions and documented inferences, not proof of the original film's isolated sounds. Licensed CC0 library effects and declared custom synthesis are distinguished from the original soundtrack. Music is optional and pinned generated music is an input, not a reproducible generation promise.

## What is still missing, in a useful order

1. **An exhaustive shot and motion inventory of the six films.** First label every retained graphic shot and transition, including holds/repeats, then identify unique motifs. Cross-reference full scene layer IDs, source/output frame mapping and asset boundaries. This fills the present gap between full production scenes and fourteen selected lessons. Do not choose an inflated target count such as seventy before the audit.
2. **More complete visual teaching cards for the motions that audit finds.** For each unique study: purpose, when to choose/avoid, actor hierarchy, start/end states, all phases, native frames, trajectories, camera/clip/material rules, component boundaries, sound hooks, actual source/rebuild images, exact code location and a rendered example. Include failure examples and why they fail. Six teaching phases are useful but not mandatory evidence of every transition.
3. **Semantic reusable implementations beyond the nine neutral starters.** Extract robust layout and editable fields from accepted scenes, replace required bitmap/glyph-only copy with measured live text or explicit asset slots, support variable message counts/copy lengths, and verify representative brand/size/fps cases. This is substantive code/design work, not just more Markdown descriptions.
4. **A second layer of exact measured snippet replay.** The full scene already contains source-specific timing/poses. A reusable extraction tool could copy an explicitly bounded actor/camera/asset subgraph and rebase its clock while retaining exact editability caveats. The generic starters currently do not promise that.
5. **A richer decision layer with evaluated examples.** Current keyword matching is shallow. Author example briefs, explain competing story choices and score real output against product truth, readability, hierarchy, rhythm and sound. Keep agent judgment and user taste explicit; do not call a bigger keyword table an aesthetic evaluator.
6. **Actual end-to-end tests for new-company direction.** Research several real products, create evidence-backed films through the local workflow and verify the outputs. Existing sample shot plans and starter tests do not establish an autonomous prompt-to-polished-film pipeline.
7. **A validated local runtime installation and offline dependency cache for the target computer.** Reading code, images, stored video, CSVs and JSON can be fully offline after restoration. Rendering needs compatible Node/Python packages, Chromium, FFmpeg and fonts. Pinned manifests alone are not installed dependencies; a cross-platform offline installer/container/runtime was not supplied in v3.
8. **Real viewer/playback/audition QA on the target device.** A valid HTML file and MP4 link are not evidence that that device decodes, seeks, switches soundtrack modes and preserves volume correctly. Run desktop/mobile interaction checks and listen to the UI-only mix. Earlier managed-browser restrictions remain a scope limit unless a new successful test replaces it.
9. **The Figma method, only if useful.** Validate actual account/file access, editable component import, keyframe/easing/clip mapping and a successful Motion export. The present converter is source for a prototype, not the result of that validation.
10. **Resolve remaining source fidelity differences and document accepted tradeoffs.** Review independent native-frame error peaks and event timing discrepancies, then correct with scoped before/after proofs. Preserve the historical metrics rather than relabeling current accepted work “100% perfect.”

None of those gaps means the full completed scene code or stored movies are absent. They describe what separates a complete archive of excellent reference work from an exhaustive, semantically editable, target-machine-tested directing system.

## What should be local, and what might still use the internet

A portable local folder is the correct primary home for the skill, actual projects, original/final films, assets, motion studies, audio, analyses and history. Drive can remain a backup. Notion can hold a human-facing table of contents or notes, but a database page is not a substitute for preserving scene paths, versioned source, binary assets and executable dependency contracts.

After the folder is copied to the user's computer, the agent can inspect the stored reference library without Drive, Notion or a media-generation service. New-company research may still need the internet unless the user supplies a complete local evidence pack. Rendering can avoid external services once the necessary local runtime is installed. The currently selected `/workspace` is the managed cloud execution machine, not proof that the files are already on the user's laptop.

## Checks performed for this report

Read the restored entry instructions, research schema/workflow, director/design/component contracts, catalogue and all three rich-study JSON files, router/components/starters source, renderer entrypoints, native-frame index/CSVs, running and verification instructions, and UI-audio limitations. Opened the Poke identity atlas and the component anatomy board for direct visual inspection. Independently checked all fourteen atlas SHA256 values, six teaching pairs per atlas, all six CSV SHA256 values and row counts totaling7,499. No new full-film render, current-machine renderer installation, human sound audition or interactive viewer pass is claimed by this report.
