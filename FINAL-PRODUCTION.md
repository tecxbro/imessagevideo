# The final production code and videos

**Yes: all thirty completed method videos and all six accepted animation scenes are saved.** This is the normal working set. Older authoring scripts are optional history, not prerequisites for using the final scenes.

Start by running `python3 tools/sync_library.py` once after cloning. It restores oversized originals from verified pieces already in Git, including Daniel’s complete scene. Then open [catalog/index.html](catalog/index.html).

## Accepted scenes and complete timelines

| Example | Accepted scene/keyframe data | Output frames | Property tracks | Stored key entries | Required asset paths | Final MP4s |
|---|---|---:|---:|---:|---:|---|
| Photon 2.0 | [scene.json](projects/01-photonhq-complete-v1/imessage-recreations/scenes/01-photonhq/scene.json) | 655 | 1,677 | 27,238 | 1,227 | [five movies](projects/01-photonhq-complete-v1/imessage-recreations/deliverables/01-photonhq/) |
| Photon Agent to Agent | [scene.json](STORAGE.json) | 1,360 | 683 | 21,874 | 622 | [five movies](projects/02-danieltian-complete-v1/imessage-recreations/deliverables/02-danieltian/) |
| Photon Mini Apps | [scene.json](projects/03-photon-mini-complete-v1/imessage-recreations/scenes/03-photon-mini/scene.json) | 1,260 | 1,131 | 69,900 | 1,659 | [five movies](projects/03-photon-mini-complete-v1/imessage-recreations/deliverables/03-photon-mini/) |
| Poke Apple Messages | [scene.json](projects/04-poke-complete-v1/imessage-recreations/scenes/04-poke/scene.json) | 1,283 | 581 | 33,964 | 92 | [five movies](projects/04-poke-complete-v1/imessage-recreations/deliverables/04-poke/) |
| Linq iMessage Apps | [scene.json](projects/05-linq-complete-v1/imessage-recreations/scenes/05-linq/scene.json) | 1,458 | 4,643 | 48,379 | 368 | [five movies](projects/05-linq-complete-v1/imessage-recreations/deliverables/05-linq/) |
| Rene | [scene.json](projects/06-gallery-complete-v1/imessage-recreations/scenes/06-gallery/scene.json) | 1,483 | 7,247 | 35,761 | 664 | [five movies](projects/06-gallery-complete-v1/imessage-recreations/deliverables/06-gallery/) |

The totals are **15,962 nonempty animated property tracks, 237,116 literal stored key entries and 4,632 declared runtime paths**. The entries include measured transforms, opacity, material, glyph/path or UI-state changes. Explicit start/end lifecycles and sampled pose groups also preserve motion. These are data counts, not a claim of that many distinct creative effects.

Every accepted scene and referenced asset passed exact hashes against its immutable case pack. All thirty final movie dimensions, frame rates and frame counts match the accepted timelines. All originals and final movies fully decoded: 34 unique files cover 36 canonical paths, producing 43,037 decoded frames with no errors. The full evidence is in [the completeness audit](reports/completeness-audit/README.md).

Rene’s reconstructed timeline intentionally omits 181 live-action source frames, as permitted in the original brief. Its complete original remains stored. This is a source/output time mapping, not a lost source clip.

## The code to edit or run

Within **each** project root listed in [LOCAL-LIBRARY.json](LOCAL-LIBRARY.json):

| Purpose | Current relative path inside that project |
|---|---|
| Measured layers, keyframes, visible lifecycles and source mapping | `scenes/<example-id>/scene.json` |
| Declared artwork/font inputs | Paths referenced by that scene, usually `references/<example-id>/…` and `shared/…` |
| Main render entry and final encoding/mux orchestration | `tools/render_example.py` |
| Explicit per-method entrypoints | `examples/<example-id>/render-METHOD.py` |
| Remotion React implementation | `engines/remotion-entry.jsx` and `engines/render.mjs` |
| GSAP and HTML/SVG implementations | `engines/render.mjs` and `engines/web-runtime.mjs` |
| Native Motion Canvas implementation | `engines/render_motion_canvas.mjs` and `engines/motion-canvas-runtime.mjs` |
| Pillow implementation | `engines/render_pillow.py` |
| Shared evaluation, sampling and loading | `engines/common.mjs`, `engines/runtime-scene.mjs`, `engines/scene-loader.mjs` |
| Runtime dependency definitions | `engines/package.json`, `engines/package-lock.json`, `engines/requirements.txt` |
| Original source video | `references/<example-id>/source.mp4` |
| Completed reference-audio videos | `deliverables/<example-id>/<method>.mp4` |
| Source comparisons and retained frame evidence | `verification/` |

Example, from the repository root:

```bash
python3 tools/library.py where 04-poke
cd projects/04-poke-complete-v1/imessage-recreations
python3 tools/render_example.py --example 04-poke --method all --dry-run
```

Read that project’s `README-COMPLETE-EXAMPLE.md` and install its pinned dependencies before an actual rerender. The repository includes the renderer source and required project assets; third-party Node/Python installations and browser binaries are separate machine setup.

The architecture is one full measured scene per film with five real shared adapters. Per-method wrappers select those implementations. The final code is not a set of unrelated older builders that must be replayed, and it is not thirty independently authored standalone applications.

## Sound, explanations and lessons

- [Complete UI audio source and helpers](resources/complete-ui-audio-source-v1/imessage-recreations/) include cues, synthesis, sourced effects, music inputs, mixes, source/license records and twelve UI previews. Thirty silent masters are also retained separately.
- [Skill instructions](skill/imessage-motion-recreation/SKILL.md) cover research, direction, visuals, components, motion and validation.
- [Failures and accepted improvements](FAILURES-AND-FIXES.md) explain what went wrong, why, what changed and how it was checked.
- [Exact file inventory](inventory/index.html) and [all file paths](inventory/ALL-FILES.csv) locate every retained payload.

The saved selected frame images and the complete numeric comparison tables are useful evidence. An exhaustive PNG cache of every pre-encode frame is not needed for this final-code path and is not part of the completion claim. [The audit appendix](reports/completeness-audit/MEDIA-AND-FRAMES.md) explains that distinction. Figma is an unvalidated prototype; it is not included among the five completed production methods.
