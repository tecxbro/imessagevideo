# Recreate a supplied film

## Establish the timeline

1. Keep the original movie in the analysis folder. Record its page or supplied origin, media identity and SHA-256. Capture the stream metadata and decoded presentation timeline before authoring.

   ```sh
   python3 scripts/verification/probe_source.py /absolute/source.mp4 --out /absolute/work/source-probe.json
   ```

   The probe uses the first video stream and records all audio streams. Zero-based frame indices are in presentation order. Source seconds are `PTS × time_base`. For zero-based elapsed time, subtract the first video PTS. The reported identical decoded tail is a lower bound on a visible hold. Annotate editorial holds by inspecting the last movement and recording its frame, duration and tolerance.
2. Keep a constant source rate as a fraction through encoding and decode the export to check PTS, frame count and final duration. For a frame-indexed scene, write key time as `frame × denominator / numerator`, retaining numeric precision. Pass the exact rational to the encoder where supported. For nonuniform cadence, use the original frame PTS and durations with a timestamp-aware export. If the requested editor requires CFR, record the conversion rule, target rational, per-frame mapping, duplicates/drops, maximum event displacement and audio drift. When a timestamp is estimated, retain that fact in the report. Avoid deriving VFR frame indices from seconds multiplied by an average rate.
3. Watch the whole film with audio where available. Record playback and inspection coverage separately from decode coverage. Use a cut detector for candidates, then inspect consecutive native frames around every cut, text change, gesture, reaction, authentication and other short event. Make one shot ledger row per shot and one row per event. Use inclusive in-frame and exclusive out-frame, source PTS, exact visible copy, actor, action, attention target, camera, before/after state, and audible cue or silence. Mark geometry, color, and timing as measured, inferred, or unknown.

## Build and prove the requested editor

Use the requested editor. When the brief leaves the choice open, explain the best verified backend for this footage. For code use the repo's normal renderer. For example, after [runtime setup](../RUNNING.md):

```sh
node scripts/engines/render.mjs --method gsap --scene /absolute/work/scene.json --out /absolute/work/picture.mp4
```

For native Figma or Paper, first test the hardest moving passage in an authorized working file. Keep text live, apply editable keyframes and a real mask, export, change the text and a keyframe, then export again. Inspect the decoded exports. Record results feature by feature for text, motion, masking, native cadence, sound, and final export. The rendered picture and sound can have different provenances or capabilities. Label a native design plus external video assembly as hybrid. If an editor blocks a requested feature, record the tool result and ask before substituting a materially different editor for the final.

1. Rebuild the hardest moving passage first and compare before, during and after action. Track stable IDs through press, swipe, expansion, and settlement. Keep camera transforms on a parent distinct from local layout and UI movement. Use held states only when observed. Match actual printed ink, row geometry, clipping, color and blur using native frames.
2. Keep an asset manifest with provenance and edit boundaries. Prefer independent or authorized artwork, fonts and sound. Reconstruct editable interfaces as layers. Keep full reference frames, reference UI crops, and extracted frame sequences in the analysis path. If independent artwork, typography or optics differ, report the substitution and visible consequence.
3. For every major event, record first and last relevant frames in both source and render, their signed difference and the check on neighboring UI. Anchor an independent cue to the intended visible action. Check the exported audio for offset, peaks and duration. Preserve stems and cue provenance. Where listening is unavailable, document which checks used decoded samples.
4. Preserve the first complete export before feedback. When a defect recurs, find the first divergent frame and test the causal variable (measurement, asset, layout, motion, export, or instructions). Keep the failed artifact. Rerender the interval and untouched controls, then decode the complete result. Check the transferable lesson on a second passage before promoting it.

## Deliver evidence

Deliver the editable scene or native file, render steps, final audiovisual export, source/rebuild side by side, difference views, per-event frame deltas and local findings. Use [compare.py](../scripts/verification/compare.py) for exact CFR frame comparisons and [scan_timeline.py](../scripts/verification/scan_timeline.py) for a full matched-frame scan after confirming the mapping. For nonuniform cadence, compare by the recorded PTS mapping. Review both complete films at speed and inspect at intended viewing size where available.

Grade decoded picture identity, interaction fidelity, independent sound and editability separately. Show the first complete and final grades per dimension. Track elapsed time, local renders, full renders, human interventions, reviewer minutes and defects per attempt. Use 1:1 only for measured dimensions that actually match.

[HyperFrames reverse-video workflow](https://github.com/heygen-com/hyperframes/tree/main/skills/reverse-any-video) and [review workflow](https://github.com/heygen-com/hyperframes/blob/main/skills/hyperframes/references/review.md) inform the native-frame strips, timing, and motion-review passes.
