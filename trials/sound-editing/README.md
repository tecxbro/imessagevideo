# Sound and editing trials — reproducibility

Run all commands from the repository root on branch `film-trials/devin-bot-sound`. These are private research/review artifacts, not a release-clearance claim or a human listening verdict. Blind reviews are complete: intervention and assignment keys are committed. See `REVIEW-LOG.md`, `blind/README.md`, `checkin/README.md` and `REPAIR-AND-OBSERVER.md` for results and limitations.

## Storage decision

`AGENTS.md` preserves accepted exports and forbids dependencies, caches, credentials and session URLs. `STORAGE.json` specifies **ordinary Git, no LFS**, with existing library archives stored as hash-verified parts no larger than25,165,824 bytes. `tools/sync_library.py` is the offline verifier/assembler/extractor, not a generic trial packer: it checks part and assembled hashes against `LOCAL-LIBRARY.json`, refuses different existing files, and safely extracts registered archives. This trial does not modify those registrations or duplicate synchronized library payloads.

`.gitattributes` uses `* -text` for byte preservation; no LFS filters are configured. GitHub warns above50MiB per ordinary blob and rejects above100MiB; browser uploads cap at25MiB. Source: https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github . Repository totals should also remain small.

Generated review MP4/FLAC payloads collectively exceed the requested~50MB budget; NPY references are also large. They remain **uncommitted**, with byte counts, SHA256s and reproduction routes in `BINARY-MANIFEST.json`. Individual decoded PNG frames are omitted; contact/transition sheets are committed. The1.88MB original Check In silent MP4 **is committed** because it is an irreplaceable director input, not a generated review copy. Synchronized kit files are restored from the library, never committed a second time. Local `.gitignore` excludes generated media, NPYs, kit copies, caches, sync.log and first-failed-build binary products. `.sound-survey-venv/` is never staged.

Scripts, tests, schedules, receipt/report snapshots, manifests, result JSON/txt, docs, keys and contact sheets are committed. Binary hashes are environment-sensitive after encoding: reference NPY hashes must reproduce exactly; MP4/AAC byte identity also requires the original FFmpeg/tool versions. Video packet identity is checked independently. Historical failed attempts are inventoried as evidence, not promised as identical new successes.

## Environment and kit bootstrap

Requires Python3.12 and FFmpeg/FFprobe on PATH (on this Mac, Homebrew Python is `/opt/homebrew/bin/python3.12`). No secrets or network asset downloads are required.

```sh
/opt/homebrew/bin/python3.12 -m venv .sound-survey-venv
.sound-survey-venv/bin/python -m pip install numpy==2.5.5 scipy==1.18.1 Pillow==13.0.0
/opt/homebrew/bin/python3.12 tools/sync_library.py
T=trials/sound-editing
A=resources/complete-ui-audio-source-v1/imessage-recreations/audio-recreation
P=projects/04-poke-complete-v1/imessage-recreations/deliverables/04-poke/gsap.mp4
PY=.sound-survey-venv/bin/python
cp -R "$A/library" "$T/audio-recreation/"
cp -R "$A/synthesis" "$T/audio-recreation/"
```

Bootstrap copies are ignored, and are not new authored trial assets. Do not run random-label builders on top of committed keys: they deliberately refuse overwrite. Use the receipt-based rehydrator below to retain the recorded labels and gains.

## Render UI, restore exact references and named treatments

```sh
$PY "$T/audio-recreation/scripts/render_ui.py" --self-test
$PY "$T/audio-recreation/scripts/render_ui.py" --id 04-poke --plan
$PY "$T/audio-recreation/scripts/render_ui.py" --id 04-poke --no-music
$PY "$T/audio-recreation/scripts/render_ui.py" --id checkin --no-music
$PY "$T/tools/restore_outputs.py"
ffmpeg -v error -i "$P" -i "$T/audio-recreation/ui-mixes/04-poke/no-music/ui.m4a" \
  -map 0:v:0 -map 1:a:0 -c copy -movflags +faststart -movie_timescale 48000 \
  -n "$T/04-poke-ui-production.mp4"
```

`restore_outputs.py` recreates and SHA-checks304 pinned cue-reference uses, continuous music/texture references, named independent stems and production/comparison MP4s for all five treatment labels. It preserves existing files, and fails on a conflicting reference. `--references-only` avoids media rendering. It uses recorded receipts rather than randomizing assignments again. It does not open damage keys or re-score itself. On the original machine, output `Validated/restored 304 pinned cue references` established exact regenerated NPY hashes against all receipts.

## Check final decoded MP4s

```sh
$PY "$T/tools/check_cues.py" "$T/04-poke-ui-production.mp4" \
  --receipt "$T/references/receipt.json" --json "$T/results/clean-reproduced.json"
for label in T-K7 T-S6 T-V5; do
  for mode in production comparison; do
    $PY "$T/tools/check_cues.py" "$T/blind/$label/$mode.mp4" \
      --receipt "$T/blind/$label/receipts/$mode.json" \
      --json "$T/results/$label-$mode-reproduced.json"
  done
done
for label in T-M8 T-V2; do
  for mode in production comparison; do
    $PY "$T/tools/check_cues.py" "$T/checkin/blind/$label/$mode.mp4" \
      --receipt "$T/checkin/blind/$label/receipts/$mode.json" \
      --json "$T/checkin/results/$label-$mode-reproduced.json"
  done
done
```

Default tolerance is±1 frame. Use `--tolerance-frames 0.5` to flag exactly one-frame interventions. The checker reads delivery+receipt+references, not stems or intervention keys. It reports AAC skip metadata and measured alignment without hiding a global shift. Known limits: low-level extras and extras within150ms of scheduled cues can evade residual detection; matching is not human audition.

## Poke damage, blind review, independent score

Use fresh key/output names because historical keys are committed and generators refuse overwrites. The fixed seed reproduces the interventions, not necessarily encoded bytes across FFmpeg versions.

```sh
$PY "$T/tools/damage_cues.py" "$T/audio-recreation/ui-mixes/04-poke/no-music/ui.flac" \
  --receipt "$T/references/receipt.json" --seed 73129 \
  --output "$T/poke-reproduced-damaged.flac" --key "$T/keys/poke-reproduced.json"
ffmpeg -v error -i "$T/poke-reproduced-damaged.flac" -c:a aac -b:a 192k \
  -movie_timescale 48000 -n "$T/poke-reproduced-damaged.m4a"
ffmpeg -v error -i "$P" -i "$T/poke-reproduced-damaged.m4a" \
  -map 0:v:0 -map 1:a:0 -c copy -movflags +faststart -movie_timescale 48000 \
  -n "$T/poke-reproduced-damaged.mp4"
$PY "$T/tools/check_cues.py" "$T/poke-reproduced-damaged.mp4" \
  --receipt "$T/references/receipt.json" --tolerance-frames 0.5 \
  --json "$T/results/poke-reproduced-damaged.json"
# Expected checker exit1 (defects), then independently score:
$PY "$T/tools/score_cues.py" "$T/results/poke-reproduced-damaged.json" \
  "$T/keys/poke-reproduced.json" --json "$T/results/poke-reproduced-score.json"
```

Historical D1 is byte-identical to the original192k damaged output. For a fresh repair, use the newly generated damaged MP4 and corresponding findings:

```sh
$PY "$T/tools/repair_cues.py" "$T/poke-reproduced-damaged.mp4" \
  --receipt "$T/references/receipt.json" --findings "$T/results/poke-reproduced-damaged.json" \
  --output "$T/blind-damage/poke-reproduced-repaired.mp4"
$PY "$T/tools/check_cues.py" "$T/blind-damage/poke-reproduced-repaired.mp4" \
  --receipt "$T/references/receipt.json" --tolerance-frames 0.5 \
  --json "$T/results/poke-reproduced-repaired.json"
$PY "$T/tools/score_repairs.py" --before "$T/results/poke-reproduced-damaged.json" \
  --after "$T/results/poke-reproduced-repaired.json" --key "$T/keys/poke-reproduced.json" \
  --clean-stem "$T/audio-recreation/ui-mixes/04-poke/no-music/ui.flac" \
  --repair-stem "$T/blind-damage/poke-reproduced-repaired.flac" \
  --json "$T/results/poke-reproduced-repair-score.json"
```

The repair process never receives a key or clean stem. The separate evaluator may read both only afterward. For the historical filename, use `blind-damage/poke-review-D1-repaired.mp4` as output on a fresh checkout and historical D1 findings; a regenerated D1 input is made by the same Poke seed/mux recipe.

## Check In damage from T-M8 production MP4

This preserves its continuous motion texture; no clean production stem is used as the damaged input. Fresh names below avoid overwriting the retained test:

```sh
$PY "$T/tools/damage_checkin.py" "$T/checkin/blind/T-M8/production.mp4" \
  --receipt "$T/checkin/blind/T-M8/receipts/production.json" --seed 420186 \
  --output "$T/checkin/checkin-reproduced-damaged.mp4" \
  --key "$T/checkin/keys/damage-reproduced.json"
$PY "$T/tools/check_cues.py" "$T/checkin/checkin-reproduced-damaged.mp4" \
  --receipt "$T/checkin/blind/T-M8/receipts/production.json" --tolerance-frames 0.5 \
  --json "$T/checkin/results/damage-reproduced.json"
# Expected exit1, then:
$PY "$T/tools/score_cues.py" "$T/checkin/results/damage-reproduced.json" \
  "$T/checkin/keys/damage-reproduced.json" --json "$T/checkin/results/damage-reproduced-score.json"
```

## Evidence, investigation, tests, inventory

```sh
$PY "$T/checkin/tools/inspect_frames.py"
$PY "$T/checkin/tools/evidence_sheets.py"
$PY "$T/checkin/tools/transition_sheets.py"
$PY "$T/checkin/tools/author_schedule.py"
$PY "$T/tools/investigate_opening.py"
$PY "$T/tools/test_check_cues.py"
$PY "$T/tools/test_repair_cues.py"
$PY "$T/checkin/tools/test_motion_texture.py"
$PY "$T/tools/inventory_binaries.py"
```

Do not regenerate historical output metadata casually: its archived SHA/source snapshots describe the versions actually used. No source video is re-encoded by the mux helpers. No claim is made that repaired AAC is bit-identical to clean PCM.
