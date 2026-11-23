# Frame review

Use the first video stream from each file. Run from the skill directory or invoke the script by its absolute path. Requires Python 3.11+, NumPy, Pillow, FFmpeg and ffprobe.

```bash
python scripts/frames.py source.mp4 render.mp4 --out evidence
python scripts/frames.py source.mp4 render.mp4 --out evidence-keyboard \
  --roi keyboard:240,1072,960,8 --require-structure-match
```

**Read the outputs.** `report.json` records SHA-256 hashes, native geometry, display rotation, raw and effective pixel aspect ratios, original time bases, first and last presentation timestamps, exclusive ends, unpaired tails, metrics and any explicit threshold violations. `frames.csv` contains every frame index from either input, PTS in ticks and seconds, timing error and mean absolute RGB error (MAE) for each comparable pair. `worst.png` shows a side-by-side pair with the highest single-frame MAE across the full frame and selected regions. Read the CSV around the discrepancy to see its onset, peak and recovery. Recheck the full-size frames whenever the relevant detail is too small in the preview.

**Set limits intentionally.** `--max-mae N` limits the largest RGB MAE on a 0–255 scale for every frame, both full image and each requested ROI. An identical lossless baseline should achieve 0. A new encode or independently authored artwork may change RGB values. `--max-pts-error-ms N` checks absolute paired timestamps and the exclusive end. Both options require all frames to have partners. `--require-structure-match` asks for equal frame count, size, orientation, pixel aspect, PTS and known exclusive end. The checker uses the tagged sample aspect, derives it from tagged display aspect when available, and otherwise interprets untagged pixels as square. `structure_match` reports exact native timing. When combined with an explicit timing tolerance, `--require-structure-match` checks `structure_within_tolerance`; raw deltas stay visible. Without explicit limits, `limits_passed` is null. Exit codes are 0 for a completed diagnostic or satisfied limits, 1 for a violated limit, and 2 for an input, option or execution error.

**Check synchronization.** The script respects presentation order, disables automatic frame-rate conversion and display rotation, and compares matching indices without resizing. Unmatched frames have `source_only` or `output_only` rows. Different image dimensions produce a diagnostic pair with zero pixel-comparable frames. Split a stream that changes native dimensions midstream before comparing its sections. Unknown final-frame timing is recorded as unknown.

`possible_frame_shift` compares low-resolution RGB signatures on the same interior frames at each candidate offset. For example, +2 means source frame N most closely resembles output frame N+2. `--shift-window 12` checks offsets through 12 frames in either direction. `--reject-detected-shift` makes an indicated offset or unavailable offset check fail. Still footage, near-identical frames, isolated timing errors and edits at boundaries can make a whole-film offset inconclusive. Review event-specific ROIs or individual frame pairs in those cases.

**Verify the event.** For a learned move, compare a same-content reference fixture and reconstruction when available. For a new story, inspect the brief's intended event, which layer moved, which layer held, what the viewer can read and when. Assess controlled triggers and settling in successive frames. Numeric agreement alone cannot establish intent, interaction accuracy, sound independence or acceptable visual quality.
