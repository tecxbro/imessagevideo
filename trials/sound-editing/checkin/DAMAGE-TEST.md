# Check In damage test — T-M8 production delivery

After the trial packaging commit was pushed, `tools/damage_checkin.py` read **T-M8's production MP4**, not its UI/full-mix stem. Seed420186. It subtracts expected reference cues from decoded delivery PCM to make interventions, retaining the continuous motion bed and AAC residual, then encodes192k AAC and copies the same video packets. No original production output is modified.

```sh
PY=.sound-survey-venv/bin/python
T=trials/sound-editing
$PY "$T/tools/damage_checkin.py" "$T/checkin/blind/T-M8/production.mp4" \
  --receipt "$T/checkin/blind/T-M8/receipts/production.json" --seed 420186 \
  --output "$T/checkin/checkin-damaged.mp4" --key "$T/checkin/keys/damage.json"
```

Result:

```text
Wrote trials/sound-editing/checkin/checkin-damaged.mp4; six interventions; original video packets preserved
```

The separate checker received only final damaged MP4 and the original T-M8 receipt/reference waveforms. It did not receive the key. Both checks were completed before the scorer opened the key:

```sh
$PY "$T/tools/check_cues.py" "$T/checkin/checkin-damaged.mp4" \
  --receipt "$T/checkin/blind/T-M8/receipts/production.json" \
  --json "$T/checkin/results/damage-default.json"
$PY "$T/tools/check_cues.py" "$T/checkin/checkin-damaged.mp4" \
  --receipt "$T/checkin/blind/T-M8/receipts/production.json" --tolerance-frames 0.5 \
  --json "$T/checkin/results/damage-strict.json"
# Each intentionally exits1. Only then:
$PY "$T/tools/score_cues.py" "$T/checkin/results/damage-default.json" \
  "$T/checkin/keys/damage.json" --json "$T/checkin/results/score-default.json"
$PY "$T/tools/score_cues.py" "$T/checkin/results/damage-strict.json" \
  "$T/checkin/keys/damage.json" --json "$T/checkin/results/score-strict.json"
```

Strict review, defective rows:

| Expected frame | Intervention | Measured offset | Correlation | Level delta | Finding |
|---:|---|---:|---:|---:|---|
|186|Send late3 frames|+4800 samples /100ms /3 frames|.984|−.29dB|late|
|445|Key late1 frame|+1600 samples /33.333ms /1 frame|.996|−.02dB|late|
|451|Key early2 frames|−3200 samples /−66.667ms /−2 frames|.996|−.09dB|early|
|529|Backspace attenuated12dB|0|.804|−12.31dB|damaged|
|542|Backspace dropped|No valid match|.201|−30.68dB|missing|
|—|Extra tap at10.250s|Detected10.250s|—|RMS.02123|extra|

The dropped cue's best low-confidence candidate offset is **not** a valid timing measurement. Other16 scheduled cues are unflagged.

```text
default ±1 frame:
fail: picture_match=True, cues=21, defective=4, extras=1
strict ±0.5 frame:
fail: picture_match=True, cues=21, defective=5, extras=1
```

Default scoring:5 true positives, one nominal miss (exactly1-frame delay is within the explicitly inclusive±1-frame tolerance), zero false positives. Strict scoring: **6 true positives, zero misses, zero false positives**. All three measured timing interventions have0-sample timing error against the independent key. No checker threshold was changed or algorithm adjusted in response to this test; the two runs exercise its existing configurable tolerance.

Motion-reference review also passes: measured bed gain delta−0.05865dB. Original and damaged video packet-payload SHA256 is `782119ce82a1cb231fa9d1ea0576174d36108d374cbefd40f3ab1d5fd4197799` (encoded video only, not whole-file/decoded-frame hash).

Retained: `checkin-damaged.{mp4,m4a,flac}` locally, hashed in `../BINARY-MANIFEST.json`; committed `keys/damage.json`, `results/damage-{default,strict}.{json,txt}`, `results/score-{default,strict}.json`. This is procedural separation, not a human blind listening review. No human audition or new visual playback was performed; video packets are unchanged.

New generator tests passed:

```text
Ran 3 tests in 0.012s
OK
```

They cover deterministic six interventions/mandatory delays/input preservation, empty receipt, and mismatched reference hashes. Existing checker tests were not rerun because checker code and their inputs were unchanged.
