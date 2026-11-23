# Run a private film in a clean workspace

Observer selects one full-length reference and stages it in the approved private workspace. The analyst receives the skill, permitted UI and Motion pins, runtime dependencies, and the selected input with its SHA-256. Prior reconstructions and source-specific notes stay outside the assignment. Record package and runtime pins and a non-identifying run label. Keep the reference, decoded crops, source-bearing contact sheets and any revealing notes in the location Observer approves.

Use an approved model-capable workspace for analysis and authoring. Make a short neutral model call there before accepting the film. The local preflight below verifies tool execution and renderer isolation. Model connectivity needs its own check.

## Preflight on Train Options

From the root of an extracted skill, use the pinned Node lockfile and matching FFmpeg and ffprobe. The reference regression uses Python 3 with NumPy and Pillow, and Chromium and Bubblewrap on Linux. If the renderer uses a Chromium binary under a different runtime path, set `CHROME_PATH` within the system mounts listed in `isolated-render.sh`.

```bash
npm ci --prefix scripts/engines
bash recreate/verify-clean-runner.sh /tmp/recreate-clean-preflight
```

The wrapper runs the existing Train Options regression. Expect 120 passing final frames, the late seat selection at 74–77, and the missing final ten at 110–119. It then renders the editable final scene with only staged renderer inputs and the empty output directory mounted. It checks reference and analysis paths from inside the render namespace and verifies that the isolated MP4 matches the regression export byte for byte. Check `SHA256SUMS` in the chosen output directory. Preflight and model access results may be posted without revealing the selected film.

## Measure and author

Run from the extracted skill with `RUN` set to an approved, private run directory and `REFERENCE` and `REFERENCE_SHA256` supplied by Observer.

```bash
umask 077
printf '%s  %s\n' "$REFERENCE_SHA256" "$REFERENCE" | sha256sum -c --status
mkdir -p "$RUN"
python3 recreate/recreate.py analyze "$REFERENCE" --out "$RUN/measurements" --reuse
python3 recreate/recreate.py inspect "$REFERENCE" --measurements "$RUN/measurements" \
  --frames "$PASSAGE" --out "$RUN/reference-passage"
```

Before authoring, cover frames 0 through the final frame in an observation ledger. Record shot boundaries, the PTS time base and final end, fixed and moving layers, editable strings, interaction windows, camera and occlusion, and audio landmarks. Complete the [shot measurements and acceptance criteria](VISUAL-REVIEW.md#measure-before-building-a-shot). Keep every frame in a hold. Map source and output frame indices explicitly for every probe. Compile supported UI and Motion portions into the editable project with their pinned versions. List independent production assets and their provenance and hashes.

Choose a renderer and follow the [visual probe and export criteria](VISUAL-REVIEW.md#review-decoded-probes-before-the-first-full-render). For any audition or final render, stage only the editable project, authored assets and renderer dependencies under a separate input tree. Run the command through `recreate/isolated-render.sh INPUT EMPTY_OUTPUT COMMAND ...`. The command sees the staged tree at `/input` and writes to `/output`. It may read a separately staged, clock-only analysis JSON and timeline CSV for a measured VFR encode. Keep the source and its extracted pictures and audio outside the input tree.

## Verify and hand off

Set `$PICTURE` and `$SCORED` to the silent and scored outputs and supply checks for the interaction windows. Use `"audio": "silent"` for the first comparison and `"audio": "present"` with cue checks for the scored comparison when applicable.

```bash
python3 recreate/recreate.py compare "$REFERENCE" "$PICTURE" \
  --checks "$RUN/picture-checks.json" --out "$RUN/picture-comparison" --sheets
sha256sum "$PICTURE" "$RUN/picture.events.json"
python3 recreate/recreate.py compare "$REFERENCE" "$SCORED" \
  --checks "$RUN/scored-checks.json" --out "$RUN/scored-comparison" --sheets
```

Give Sound the exact silent picture SHA and frame-addressed event map through Observer’s approved handoff. For each encode, `frames.csv` records paired source and output frame indices and native start and exclusive-end ticks, including the final hold. The report gives each stream’s time base and full decode verdict. Review `regions.csv` and the paired crops against the ledger. Include the [visual verdict for every decoded shot](VISUAL-REVIEW.md#review-the-finished-export). Give reviewers the scored picture lock check as well as the source-to-output comparison.

Make one meaningful visible edit and rerender from the edited source. Keep the original evidence and edit result in different outputs. Report the exact workflow revision, runnable command, output hash and remaining differences in the build room. Share protected material and source-bearing evidence only through Observer’s approved location.

Run the [completion check](COMPLETION.md#lock-and-verify-the-review) on the final intended file. A benchmark's open checks remain the repair list for a full recreation.
