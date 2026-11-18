# D1 repair and opening-cue observer follow-up

## D1: delivery-only repair inputs

Delivered: `blind-damage/poke-review-D1-repaired.mp4`, with independent repaired UI PCM in `.flac` and `.repair.json` beside it.

The D1 input file SHA256 is `2851f9ccebf82ffbdc03ae4aa7ec469837a2109db6d594e7547c961cbe40e179`, byte-identical to the earlier damaged192k export. A fresh strict review was made from D1 itself:

```sh
.sound-survey-venv/bin/python trials/sound-editing/tools/check_cues.py \
  trials/sound-editing/blind-damage/poke-review-D1.mp4 \
  --receipt trials/sound-editing/references/receipt.json --tolerance-frames 0.5 \
  --json trials/sound-editing/results/D1-before.json
```

It reports34 scheduled cues,8 defective cues and1 extra. This is expected nonzero exit1, not a failed repair invocation. `tools/repair_cues.py` receives only damaged MP4, original receipt/reference waveforms and these findings. There is no key or clean-stem input. It hashes references, verifies video identity and span, and builds expected reference PCM. Only local repair regions are replaced:

- Scheduled and confidently detected wrong-time regions are restored, including all expected overlapping cues.
- A low-confidence missing-cue candidate elsewhere is not erased; the scheduled dropped cue is restored.
- Extra extent is found from decoded residual5ms blocks using the reviewer's.003 RMS floor and50ms grouping; it is replaced with expected PCM.
- Regions include20ms padding and5ms crossfades, and overlap is merged. Outside the10 repair regions, decoded damaged-delivery PCM is preserved.

```sh
.sound-survey-venv/bin/python trials/sound-editing/tools/repair_cues.py \
  trials/sound-editing/blind-damage/poke-review-D1.mp4 \
  --receipt trials/sound-editing/references/receipt.json \
  --findings trials/sound-editing/results/D1-before.json \
  --output trials/sound-editing/blind-damage/poke-review-D1-repaired.mp4
```

Printed result:

```text
Repaired 9 findings in 10 regions; video packets unchanged; no key or clean stem read
```

Video is stream-copied from D1. Original/D1/repaired encoded video packet-payload SHA256 remains `fef5481d8bbb13c16a14d05ad846cdb72112ca876913b9f0c27d871dc393d62b` (not a whole-file or decoded-frame hash).

Strict final-MP4 review, same command/receipt with repaired filename:

```text
pass: picture_match=True, cues=34, defective=0, extras=0
offsets [0] min_corr 0.893113698506744
```

All34 measured offsets are exactly0 samples with ±0.5-frame tolerance. Full evidence: `results/D1-{before,repaired}.{json,txt}`.

Only **after** repair did `tools/score_repairs.py` read the key and clean production UI stem. Its key-based result:

```json
{"key_defects":9,"before_detected":9,"remaining_key_defects":0,"resolved_key_defects":9,"new_or_unkeyed_findings":[]}
```

Decoded repaired FLAC versus clean production UI FLAC (`audio-recreation/ui-mixes/04-poke/no-music/ui.flac`):2,054,853 stereo samples, RMS difference0.0006589273 (**−63.623dBFS**), maximum absolute difference0.045882225 (**−26.767dBFS**), SNR21.234dB. **Not bit-identical.** Retaining undamaged decoded AAC regions retains codec error, and local fades can retain boundary error. Passing cue checks certifies the declared timing/similarity/level thresholds, not lossless restoration or an inaudible null. Full hashes/metrics: `results/D1-repair-score.json`.

Three repair-region tests passed (merged/overlapping replacement with untouched outside, empty findings preserving track, span mismatch error). Existing checker tests had already passed7/7 after its last code change; the checker was not modified for this addendum. No human listening audition was performed.

## T-V5 opening: is0.57 correlation a real defect?

**No defect is supported for the local delivered production/comparison files with their own pinned references. No audio or threshold was changed.** The reported observer template/window, file hash and definition of “gain span” were not supplied, so its exact0.57 and9.6dB cannot be reproduced verbatim or attributed with certainty. The following overlap explanation is verified for the actual local files, rather than assumed.

Reachable causal chain:

1. `blind/T-V5/receipts/production.json` schedules opening cue ordinal0 at native frame109, rational30000/1001 fps, impact174574 samples =3.636958s (rounded from native time3.636967s).3.633s differs by about4ms, not a full frame.
2. Its12000-sample reference starts172700 and ends184700 exclusive. Cue4/frame113 starts178228 and cue6/frame116 starts183912, so both references overlap the opening template window in the actual treatment receipt. The builder adds those references into the UI PCM; decoded delivery measurements show them present.
3. A raw single-template measurement at its correct scheduled window gives correlation**0.505732**, gain delta−0.139dB in production (comparison0.506383,−0.154dB). Broad raw search can even prefer the later same-key waveform at183912. This reproduces the *kind* of low raw correlation, not the exact observer value.
4. To try to **disprove** overlap and expose genuine corruption, subtract only the other cues at their **fixed expected gains and fixed scheduled times**, with no neighbor gain/time fitting, and measure the first cue again. Correlation becomes**0.998292**, gain delta**−0.0292dB** (comparison0.998240,−0.0440dB). A damaged first cue would remain damaged after this fixed subtraction; it does not.
5. `check_cues.review` first subtracts expected references and uses coordinate descent to isolate overlapping waveforms before `locate`. Its actual stored opening row passes the default.8 correlation and ±6dB per-cue level thresholds. The checker does **not** apply a global9.6dB uniformity target across different effect assets.

Across all25 cues, measured delivery-versus-own-reference level-delta span is only**0.317708dB production /0.294511dB comparison**, not9.6dB. Expected reference RMS levels themselves span15.940dB because different keys, notifications and attenuated transitions intentionally have different envelopes/gains. A raw cross-effect level span is not a per-cue gain-error metric. The default±6dB threshold would be too loose for some stricter loudness-consistency specifications, but loosening/tightening it is not implicated by these measured deltas. The observer's9.6dB could be a different raw level statistic; that interpretation remains unverified without its method.

Full expected-mix versus decoded correlation is0.995894 production /0.995634 comparison. `tools/investigate_opening.py` records input file/receipt hashes, raw and fixed-neighbor measurements, overlap bounds, stored checker rows and gain spans in `results/T-V5-opening-investigation.{json,txt}`. The meaningful corrected variable here is the **measurement model: isolated template versus overlapping scheduled mixture**, not an audio-edit or weakened threshold. No “first failure” was overwritten; raw low-correlation evidence remains in that report.
