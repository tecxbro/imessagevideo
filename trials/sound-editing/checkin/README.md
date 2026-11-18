# Check In — actual director rough cut

Start with the two anonymous `blind/T-*/comparison.mp4` files, not their metadata/stems. Both use the untouched24-second first-export picture. Assignment is only in `keys/treatments.json` (0600). Provenance necessarily exposes structural differences; read it after comparison.

## Deliverables

- `EVENT-VERIFICATION.md`: director list versus observed native frames and explicit omissions.
- `canonical-cues.json`: 30/1 fps,720 frames,1,152,000 samples;21 audible events,3 silent states; exact frame×1600 sample offsets. Renderer copy: `../audio-recreation/ui-cues/canonical-checkin.json`.
- `evidence/contact-sheet-verified.png`: inspected key states, with all native PNGs and detailed transition sheets alongside.
- `EDITORIAL.md`: slide-presentation risks, seven-second gap, and exactly one unimplemented retiming proposal.
- Each neutral folder: `ui.flac`, silent `music.flac`, `motion.flac` (silent when unused), `full_mix.flac`; production/comparison MP4s,192 kbps AAC inputs, cue impacts, hashed per-cue NPY references, production/comparison receipts, provenance, check JSON and tables.
- `blind/levels.json`: encoded-MP4 loudness/true-peak measurements. Matching uses scalar **attenuation only**, not normalization of sparse UI to a full-program target. Programs are intentionally quiet; matching at this level is for relative comparison, not an asserted platform delivery specification.

The UI stem was rendered **first, with no music**, by the existing copied renderer and sound kit. It uses CC0-pinned stock UI samples plus declared original procedural effects; source/prepared hashes, licenses, gain/pan/pitch and synthesis hashes are retained in each manifest and cue receipt. No reference-film audio was sampled. No new AI generation or unpinned music asset was used. The optional seven-second texture is seeded procedural filtered noise, not real-location recording or asserted Apple sound. `music.flac` remains silent; the independent `motion.flac` makes the nonmusical role explicit. All four lossless stems add exactly at decoded precision in these outputs.

## Hash domains

Original whole-file SHA256:
`47a3cd6678980f33788726fd5784d23d20317ce8df7b75c0a28a7f0642e49c81`

Original and all four muxed MP4 **video packet-payload** SHA256:
`782119ce82a1cb231fa9d1ea0576174d36108d374cbefd40f3ab1d5fd4197799`

Packet method: `ffmpeg -map 0:v:0 -c copy -f hash -hash sha256`. This excludes audio/container metadata and is not a decoded-frame hash. Original/production/comparison whole-file hashes differ as expected. Every receipt explicitly labels its hash domains. No decoded-frame hash is claimed. Muxing uses video copy and explicit stream mapping, never picture re-encode.

## Reproduction and review

First follow the parent README's environment, library sync and kit bootstrap. From repo root, using that isolated NumPy/SciPy/Pillow environment:

```sh
.sound-survey-venv/bin/python trials/sound-editing/checkin/tools/inspect_frames.py
.sound-survey-venv/bin/python trials/sound-editing/checkin/tools/evidence_sheets.py
.sound-survey-venv/bin/python trials/sound-editing/checkin/tools/transition_sheets.py
.sound-survey-venv/bin/python trials/sound-editing/checkin/tools/author_schedule.py
.sound-survey-venv/bin/python trials/sound-editing/audio-recreation/scripts/render_ui.py --id checkin --no-music
.sound-survey-venv/bin/python trials/sound-editing/tools/restore_outputs.py
```

The receipt-based restorer preserves committed labels and keys and recreates missing media. The original random-label `build_scores.py` deliberately refuses committed keys and is not a fresh-checkout reproduction route. Existing render result and snapshots: `../audio-recreation/ui-mixes/checkin/no-music/`; production render output: `results/ui-render.txt`. The boosted renderer preview was **not** used for these deliveries.

For either label and either `production` or `comparison`:

```sh
.sound-survey-venv/bin/python trials/sound-editing/tools/check_cues.py \
  trials/sound-editing/checkin/blind/LABEL/production.mp4 \
  --receipt trials/sound-editing/checkin/blind/LABEL/receipts/production.json \
  --json trials/sound-editing/checkin/blind/LABEL/check-production.json
```

The checker reads final MP4 plus reference receipts/waveforms, not production stems or label keys. Expected continuous texture is generated independently from the pinned algorithm/seed, not recovered from a delivery. All21 cue offsets measured0 samples in all four MP4s, no defects/extras; minimum correlation exceeds.973. AAC first packet PTS=-1024 with skip_samples=1024; decoder honors this metadata and measured common offset is0, with no additional alignment shift. The continuous-reference case is also checked, with independent AAC codec-floor estimation. Known limitation remains: extras below the fixed/codec floor or within150ms of fitted cue hits can be missed. This clean check is not a new Check In damage test.

Tests: `checkin/tools/test_motion_texture.py` (3) and `../tools/test_check_cues.py` (7). No changes were required to the existing renderer or checker.

## Build issue retained

First packaging attempt stopped with `KeyError: 'skipped_events'`: the renderer stores silent rows inside `report['events']` with `rendered=false`, not a separate list. The new builder now selects those rows. Partial first-attempt products are under `results/build-first/`; their abandoned key remains only in `keys/build-first.json`. They are not comparison deliverables. No accepted export was overwritten. Successful build log: `results/build.txt`.

Native frame evidence was visually inspected. No human listening audition or real-time audiovisual playback was performed; decoded measurements are not a claim that either treatment has been heard or preferred. The director revision is proposed, not applied. Nothing staged or committed; `.sound-survey-venv/` stays out of git.
