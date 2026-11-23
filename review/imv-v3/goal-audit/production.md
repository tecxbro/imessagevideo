# Main-branch production audit

On November 21, 2026, `git ls-remote origin refs/heads/main` resolved to
`c49482aec7b8ed0b840f97c61a5e5b860c4077b6`. The clean
`codex-direction-library` checkout is pinned to that same revision.

## Media and source closure

The [verification record](production-verification.json) identifies all six
canonical scenes, their renderer wrappers, runtime files, source exports, and
five delivered variants per scene. All 36 media paths were hash-checked.
There are 34 unique files after deduplication. All 43,037 unique video frames
and all available audio streams decoded without errors. The six scene hashes
match `LOCAL-LIBRARY.json`, and declared relative image and font inputs
resolved from their respective scene directories.
The runtime inventory covers 150 paths, with 55 distinct file hashes.

Viewed seven decoded samples from each original and each of its five exports.
The sampled rows preserve the principal actions and composition across the five
renderer routes. A second Rene comparison aligned the source to the explicit
181-frame live-action omission. Uniform sampling alone paired unrelated Rene
states. The media verification record provides counts and dimensions. The
rendered samples do not certify exact visual parity.

The shared engine code provides actual implementations. The 30 short wrappers
choose the project and renderer. Each film owns an extensive frame-addressed
scene. Browser SVG/GSAP and Remotion share the same text and geometry evaluator.
Motion Canvas instantiates native scene nodes and separately corrects transformed
font shaping and blur/shadow compositing. Pillow evaluates the same layer
timeline and applies local transforms before raster effects. Both primary
browser and Motion Canvas transports prove frame appearance invariance when
pruning inactive branches. The pack's final encoder hashes its indexed PNG
cache before and after reproducible BT.709 encoding, then its muxer applies
explicit source-audio mapping.

I rerendered native PhotonHQ f535 from the frozen scene with all five adapters.
Pillow initially failed in CairoSVG because macOS could not locate the
already-installed Homebrew Cairo library. Setting
`DYLD_FALLBACK_LIBRARY_PATH` for that one process recovered the native
checkpoint with the same scene and renderer. This was a runtime dependency
location failure. It does not explain the Sidehoe title, pose, or glyph errors.

I also rerendered Poke at frame 633 in all five adapters. The source shows
Zareen's selected. Every fresh render lacks the blue checkbox. A separate scan
of the delivered exports finds the onset at frame 645 across all five. The
frozen scene starts the two checkbox layers at 21.5 seconds. [Poke audit](production-04.md)

## Editability

| Case | Frames | Live text nodes | Other layer types |
| --- | ---: | ---: | --- |
| PhotonHQ | 655 | 0 | Group, image, path, rect |
| Daniel Tian | 1,360 | 4 | Group, circle, path, image, rect |
| Photon Mini Apps | 1,260 | 428 | Group, image, path, rect, circle |
| Poke | 1,283 | 156 | Group, circle, rect, path, image |
| Linq | 1,458 | 1 | Group, image, circle, path, rect |
| Rene | 1,483 | 71 | Group, rect, path, image, circle |

Editing a measured pose, crop, mask or path is a supported reuse. Live
message text, typed drafts, semantic sender state and audio events need an
independent component contract. The packs retain historic isolated source
artwork and bounded material patches with their provenance. New Sidehoe shots
use the current independent-source requirements.

## Verification boundary

The production runtime closure and the archived authoring experiments are
distinct. The latter have per-path review and replay coverage in the
[PhotonHQ and Daniel Tian](production-01-02.md),
[Photon Mini Apps](production-03.md), [Poke](production-04.md),
[Linq](production-05.md) and [Rene](production-06.md) audits. The 30 complete
published exports were decoded and visually sampled. Fresh render evidence
covers ten native checkpoints across two scenes and the full Sidehoe rerenders.

```sh
python3 audit_production.py /path/to/imessage-video/codex-direction-library production-verification.json
```
