# Decoded cue review experiment

No accepted export or tracked production source is modified. The checker reads
only the final MP4, a frozen receipt and individual reference waveforms, never
the clean UI stem, damage key or intervention generator. The scorer alone opens
the key after review completes. This is procedural separation, not an independent
human blind review: one agent authored the generator and checker.

## Reference preparation

`tools/prepare_review.py` reproduces each canonical event using the copied current
renderer and actual prepared library, with its seeded pitch/pan, production gain,
and recorded alignment offset. It freezes 34 individual float64 stereo reference
arrays with SHA256 hashes, canonical event frames and the accepted picture video
packet SHA256 into `references/receipt.json`. The intentionally silent control
is excluded. Reference waveforms are allowed inputs; no full stem is provided to
the checker. The schedule and production report remain in `audio-recreation/`.

## Development failure and correction

The first clean run falsely selected silence as a match: FFT sliding-energy
roundoff allowed enormous normalized correlations in near-zero-energy windows.
Evidence is retained in `results/clean-first.{json,txt}`. Changed only energy
measurement/normalization: cumulative sum energy, bounded correlations and a
reference-relative minimum-energy gate. The next clean run found all 34 cues
with exactly zero sample offsets and no defects. Its overlapping key correlations
were 0.858 or higher; no claim of perceptual equivalence follows.

## Damage test and boundary correction

There are nine interventions, rather than approximately 6–8, to cover every
enumerated requested category: delays of 1/2/4/8 frames, an early cue, attenuation,
lowpass distortion, a drop and an extra click. Eight randomly selected distinct
non-typing cues are modified with seed 73129. The private key is a separate 0600
JSON under `keys/`; the extra is at 33.25 seconds. Waveform subtraction/addition
retains every other clean-stem sample apart from FLAC quantization.

First damaged outputs and scorer remain in `results/damaged-first.*` and
`results/score-first.json`. That MP4 used 256 kbps AAC rather than the original
UI's 192 kbps. It detected all nine interventions, but inspection found a timing
boundary bug: one NTSC frame rounds to 1602 samples, slightly beyond the floating
1601.6-sample threshold, so the nominal one-frame delay was incorrectly flagged
under a ±1-frame policy. Changed the threshold to the nearest integer sample and
added a regression test. This is the sole post-damage checker correction.

Final MP4 `04-poke-damaged-192k.mp4` uses the same 192 kbps AAC codec setting as
the clean production UI. `damaged-default` results use the corrected ±1-frame
default: the one-frame intervention is properly within tolerance (a scored miss,
not an undetected onset). `damaged-strict` uses the existing configurable ±0.5-frame
tolerance to deliberately test all timing interventions. No key is passed to
either checker run. Both results, thresholds, tables and scores are preserved.

## Algorithm and limits

The checker validates video packet SHA256 before decoding audio. FFmpeg applies
the actual MP4 edit list and Skip Samples metadata. The clean file's first AAC
packet has PTS -1024 and skip_samples 1024; measured common post-decode offset is
zero samples. No assumed 1024-sample shift or median subtraction is performed;
a globally shifted soundtrack is not silently corrected away.

Four coordinate-descent passes perform stereo normalized cross-correlation in a
±12-frame window, subtracting other fitted cues to isolate overlapping keys.
Reports include correlation, fitted gain delta and sample/ms/frame offset.
Missing means correlation <0.25 or fitted gain below -35 dB; damage means
correlation <0.8 or level deviation >6 dB. Residual 5-ms block RMS >0.003 identifies
extras, merging gaps up to 50 ms; residuals within 150 ms of fitted cue impacts
are excluded to avoid double-counting damage as an extra. These thresholds are
exposed in JSON (timing, search, correlation and level are CLI configurable).

Limits: not certified for music beds, dense ambiguous repeated effects, quiet
extras below the fixed threshold, or extras within the cue exclusion window.
Missing-cue offset is just the best low-confidence candidate, not a valid timing
estimate. Correlation/level can identify lowpass damage without claiming a
separate spectral classifier. No human audition or visual playback performed.

## Reproduction from repository root

Use `.sound-survey-venv/bin/python` (NumPy/SciPy installed; never stage this venv).

```sh
.sound-survey-venv/bin/python trials/sound-editing/tools/check_cues.py \
  trials/sound-editing/04-poke-ui-production.mp4 \
  --receipt trials/sound-editing/references/receipt.json \
  --json trials/sound-editing/results/clean.json

.sound-survey-venv/bin/python trials/sound-editing/tools/check_cues.py \
  trials/sound-editing/04-poke-damaged-192k.mp4 \
  --receipt trials/sound-editing/references/receipt.json \
  --tolerance-frames 0.5 --json trials/sound-editing/results/damaged-strict.json

.sound-survey-venv/bin/python trials/sound-editing/tools/score_cues.py \
  trials/sound-editing/results/damaged-strict.json \
  trials/sound-editing/keys/04-poke.json \
  --json trials/sound-editing/results/score-strict.json

.sound-survey-venv/bin/python -m unittest discover \
  -s trials/sound-editing/tools -p 'test_*.py' -v
```

The generator refuses to overwrite its output/key. To reproduce a new trial,
run `tools/damage_cues.py CLEAN_FLAC --receipt RECEIPT --output NEW_FLAC
--key NEW_KEY --seed 73129`, encode AAC at 192k, then explicitly mux `0:v:0`
from the original picture and `1:a:0` from the new AAC with `-c copy`, faststart
and movie timescale 48000. Keep the key out of review inputs.
