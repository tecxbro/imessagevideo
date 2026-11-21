---
name: imessage-film-recreation
description: Rebuild a complete supplied iMessage film as editable scene source. Measure its native picture clock and sound, reconstruct UI and camera, render the hardest passage, repair with local frame comparisons, and verify the complete encoded handoff.
---

# Recreate a complete iMessage film

Use the supplied movie as visual and timing evidence. Deliver editable scene data, authored assets, first and final complete picture exports, and an evidence directory with reproducible commands. Use the shared [scene format](../scripts/shared/SCHEMA.md) and, when present in your checkout, the Observer timeline contract and Clone iMessage UI adapter. Use the Motion library for a behavior only after measuring its local anchors in this film. Start with the [worked example](example/README.md). [Source studies and renderer probes](SOURCES.md) give tested commands.

For a private full-film assignment, use [the clean-run commands](CLEAN-RUN.md). They cover preflight on Train Options, the whole-film ledger, and the separate analysis and render workspaces.

Run from the repository root. The measurements and checker use Python 3.10+, NumPy, Pillow, and the matching FFmpeg and ffprobe executables (verified with FFmpeg 7.1). Tesseract is optional. Browser renderers also need the pinned Node dependencies and Chromium documented in the [engine setup](../RUNNING.md).

```bash
R=skill/imessage-motion-recreation/recreate
python3 "$R/recreate.py" analyze "$REFERENCE" --out work/measurements
python3 "$R/recreate.py" inspect "$REFERENCE" --measurements work/measurements --frames 42:49,75,118:119 --out work/inspect
```

## Read the complete reference

Read `analysis.json` and the contact sheets. `timeline.csv` has one row per decoded picture in presentation order, with integer PTS, sample span, a hash of decoded RGB, and a thumbnail motion estimate. Use decoded PTS and final end for timing. A filename marked 60 fps and an average frame rate can conceal irregular intervals. Reuse this folder when revising a scene. Use `analyze --reuse` for a SHA-checked cache hit. A different source SHA needs a separate measurement directory. Full-color comparison runs on the coded raster, so include display aspect ratio and display transform when interpreting positions.

Pass `--measurements work/measurements` to repeat an `inspect` or `landmarks` pass without another whole-film clock probe. It checks the source and timeline hashes, then matches the selected decoded RGB frames to the saved frame hashes. Put neighboring windows in a single call to share the decode through the last requested frame.

Thumbnail cuts, change boxes, exact-image holds and audio rises are hypotheses. Check both sides of suspected cuts, go back to native pixels for small controls, and inspect a consecutive run around every interaction. Split slow dissolves and freezes by observation. Compare first/last stills and check color, motion blur, and transparency where they affect a state. Use `inspect --crop X Y W H --ocr` to read difficult UI text; OCR TSV boxes use native crop coordinates. Crop tightly and use `--ocr-mode line` for one line or `--ocr-mode block` for a wrapped message. Confirm strings, line breaks, truncation, and system glyphs against the cited frames. Use `landmarks --plan PLAN --out DIR` to record a known flat-color object’s native bounding box, centroid and pixel count over a window. Each item under `tracks` supplies `id`, `start`, `end`, `rect`, `rgb` and a per-channel `tolerance`. Inspect frames for similarly colored objects and refine the crop before taking the trajectory as evidence.

Write an observation ledger with inclusive spans that cover the full film. For each shot, record visible objects and editable text, z-order and masks, camera versus local transforms, still and moving layers, and UI states before and after changes. Use source frame indices and stable IDs. Mark the first visible motion, first legible state, impact/selection, settlement, and final hold independently. Start with two tracked landmarks on each allegedly rigid camera layer and check their relative spacing across the move. Record residual local motion separately. Add measurements when something new matters, such as a rotated phone, animated text reflow, changing point of focus, keyboard preselection, or intersecting cards. Cite a frame run or measurement table for each conclusion; flag ambiguous frames.

The audio envelope CSVs cover each audio stream. Onset times are estimates from overlapping 20 ms windows, relative to the first picture, with nearest native frame indices for review. Record negatives if sound leads the picture. Tie cues to actions with stable IDs and signed offsets through the Observer/Sound contract. Keep source waveform and extracted stills in the measurement workspace. Give Sound the silent picture SHA and the event map. Use independently authored sound and verify the final mux again.

## Author, choose and render

Transfer measurements into one editable source: original layout/text, reusable components and geometry, frame-indexed timing, parent transforms, masks, and named assets. Use the UI adapter for Messages. Author card content, photographs, sounds and logos separately using the project's permitted assets. Keep editable text as text and editable motions as independent tracks. Do not import the film, its audio, a frame sequence, cropped reference patches, or effects that fetch those assets. Validate the renderer input paths. On Linux with Bubblewrap, [isolated-render.sh](isolated-render.sh) can bind a staged source and system runtime, hide the workspace and disable networking. Stage only declared render inputs and a vetted renderer/runtime. The reference file, measurement images and source audio should be outside the mounts. Record the isolated command and resulting file hash.

Choose the requested editor first. If the user leaves it open, pick the one renderer that fits the hardest passage. Run its real export on that passage and inspect it for the capabilities the film requires.

| Renderer | When to use it |
| --- | --- |
| HTML/CSS/SVG | Precise 2D browser geometry, type and clipping, or an editable browser project |
| GSAP | Browser vector project with a GSAP timeline and independently animated proxies |
| Remotion | React composition and an editing workflow in Remotion |
| Motion Canvas | Editable native Scene2D components and timeline signals |
| Pillow/FFmpeg | Headless deterministic drawing and integer frame work with supported effects |

The five entries have actual export probes linked in [SOURCES.md](SOURCES.md). Probe the target passage for its own font, color treatment and lens effects. If the chosen engine cannot represent a required operation, record the failed probe before choosing another. Make one requested full render. Keep a lossless native render cache where the engine supports it.

Render the passage with the most interacting constraints first. Retain absolute native frame indices for animated properties and equivalence at the endpoints. Check consecutive frames against the same source indices, then render the complete first export. Prefer controls, text and keyframes built for the destination editor over a flattened workaround. For a variable clock, render one PNG for each original frame index and apply the measured timestamps on encode. With a square-pixel SDR source, native dimensions and an opaque PNG cache named from `000000.png`, use the command below. Author the PNGs in the intended SDR primaries and transfer. Stage only the analysis JSON and timeline CSV from measurements if encoding in isolation. The encoder verifies every resulting PTS and the final sample end. Run the complete comparison after encoding.

```bash
python3 "$R/recreate.py" encode-clock work/candidate-frames --measurements work/measurements --out work/final.mp4
```

Record any editor-timeline limits and keep its editable source on the same frame-index mapping. Mark deliberate rate conversions as a separate delivery with their time mapping.

## Compare, repair and verify

Create a check file before declaring the result. Start from [example/checks.json](example/checks.json). Include first/last states, every interaction, and a window starting before and ending after each expected change. Use tight coded raster `[x,y,width,height]` rectangles, or supply an array of `rects` with one per frame for a moving target. Add a local MAE limit, a changed pixel count limit with a per-pixel channel floor, or both. Set thresholds against static and settled frames in the same scene. Optional overlapping `tile` checks can flag differences outside the chosen windows. They are especially useful to find missing observations. Use the frame CSV's tile location to inspect a new window. Avoid raising limits merely to pass a known error.

```bash
python3 "$R/recreate.py" compare "$REFERENCE" "$FIRST" --checks work/checks.json --out work/first-check --sheets
python3 "$R/recreate.py" compare "$REFERENCE" "$FINAL" --checks work/checks.json --out work/final-check --sheets
```

The checker drains both streams through EOF and verifies decoded counts, independent normalized PTS, display geometry and final end. A clock tolerance defaults to zero; any explicit tolerance needs a reason such as documented container tick quantization. FFmpeg passes through the decoded pictures at their measured timestamps. Each paired frame contributes an RGB error row, and each declared ROI is independently checked on every frame in its window. Missing and extra rows remain visible. Exit 0 means the declared gates passed, 1 means a gate failed, and 2 means the check could not be completed. A default run without regions covers picture-level checks only. Without audio checks it reports stream metadata. Use `audio: "silent"` for the picture handoff or `audio: "present"` plus `audio_checks` for a mux. Supply decoded-start tolerance against reference audio when applicable or author cue peak checks with event ID, frame, signed offset in milliseconds, an inspection window and a minimum linear amplitude. [Checker inputs](CHECKS.md)

Prioritize structural and clock errors, then first wrong states, then layout and raster characteristics. Triage by the paired native crops, including every interaction and the final hold. Keep a repair log with the first wrong frame and region, measured value, changed scene property and the inclusive affected ranges. Render those ranges only. Update dependent tracks and capture every affected frame if a camera, font or component change propagates. Re-encode the whole cache and run the complete check on the encoded file. Compare lossless frame hashes outside the repaired intervals. Check the actual encoded output even when unaffected source PNGs match. For an editability proof, change real visible text and a frame anchor in source, rerender and show both changes in decoded frames.

Hand over the original reference provenance and hash, shot/interaction/audio observations, independently renderable editable project, silent picture and optional independent mux/stems, first and final exports, edit proof, commands and measurements. Include the full last frame and event windows. State precisely what the numbers cover, the unresolved differences and whether anyone actually watched or listened. A fresh-agent blind run must use a reserved film and the skill in a separate workspace. Correct workflow failures in the skill, then test on a different film. Preserve previously valid render data and measurements to avoid repeating work.
