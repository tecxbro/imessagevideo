# Original UI sound bank

Eight original procedural effects for the six motion-graphics films. No reference soundtrack, recorded sample, branded notification recording or external audio input is used. Oscillators, modal tones and seeded filtered Gaussian noise generate every sample locally. No paid generation is used.

Files are **48 kHz, stereo, signed 24-bit PCM WAV**. Use `bank/*.wav` for mixing; `bank/audition.mp3` is a quick sequential preview. `bank/index.csv` gives the preview timestamps. `bank/manifest.json` records synthesis parameters, source provenance, tool versions, duration, signal statistics and SHA256 for each asset.

| Effect ID | Default length | Design / typical cue |
| --- | ---: | --- |
| `bubble_pop` | 0.180 s | Descending resonant bubble; a message appearing |
| `touch_click` | 0.035 s | Dry high-band tick; a small selection |
| `key_tap` | 0.065 s | Short two-mode tap with a tiny return; sparse typing |
| `air_whoosh` | 0.280 s | Light rising noise/cavity pass; quick UI movement |
| `card_swoosh` | 0.620 s | Longer, rounder stereo pass; card or camera movement |
| `glass_confirm` | 0.720 s | Warm inharmonic modal bloom; completion |
| `low_impact` | 0.280 s | Muted descending low thump; landing/emphasis |
| `digital_sparkle` | 0.480 s | Five staggered stereo glints; a bright reveal |

## Python API

Requires Python 3.10+, NumPy and SciPy. FFmpeg is needed only for the audition MP3/its validation. Existing local versions are recorded in the bank manifest.

```python
import sys
sys.path.insert(0, "/workspace/imessage-recreations/audio-recreation")
from synthesis import SAMPLE_RATE, render, write_wav

audio = render(
    "bubble_pop", pitch=1.08, duration=0.16,
    energy=0.60, pan=-0.20, seed=42,
)
# audio: numpy float32 array [frames, 2], SAMPLE_RATE == 48000
write_wav("/path/to/my-pop.wav", audio)
```

- `pitch`: frequency multiplier, 0.25–4; `2` is one octave up. No recorded sound is resampled.
- `duration`: exact output duration in seconds, 0.01–4; omitted uses the table above. Envelopes and relative event timing stretch to fit. Length is rounded to the nearest 48 kHz sample.
- `energy`: 0–1. Joint stereo sample peak is normalized to `10**(-3/20) * energy`; `0` is silence. The default `0.75` peaks at **−5.50 dBFS**. Whoosh brightness also follows this value.
- `pan`: −1 left to +1 right. Equal-power balance is applied before joint peak normalization. Air and sparkle designs also have internal stereo motion.
- `seed`: nonnegative integer. Same parameters, seed and recorded toolchain produce the same samples. Seeds alter noise, slight tuning and sparkle timing without changing the output duration.

`analyze(audio)` returns signal statistics. `write_bank(path, seed=20261109, audition=True)` regenerates the eight WAVs, audition and manifest. Invalid/nonfinite parameters and clipped WAV input are rejected.

## CLI

Run from the project root:

```sh
python audio-recreation/synthesis/ui_synth.py list
python audio-recreation/synthesis/ui_synth.py render bubble_pop /tmp/pop.wav --semitones 2 --duration .16 --energy .6 --pan -.2 --seed 42
python audio-recreation/synthesis/ui_synth.py bank --out audio-recreation/synthesis/bank
python audio-recreation/synthesis/validate_bank.py audio-recreation/synthesis/bank --out audio-recreation/synthesis/validation.json
```

`--pitch` accepts a ratio; `--semitones` takes precedence when supplied. `bank --no-audition` omits FFmpeg. Import aliases include `pop`, `plop`, `click`, `key`, `whoosh`, `swoosh`, `bell`, `confirm`, `impact`, and `sparkle`.

## Mixing and verification

These are individual effects with headroom, ready for the parent cue mixer. Place at measured motion events; vary seed/pitch slightly for repeated taps rather than triggering one asset on every video frame. Start with restrained gain and allow extra headroom when sounds overlap. The bank contains no music or source-film audio.

The WAV endpoints are exactly zero, DC is removed with a smooth endpoint-preserving window, and releases are faded after filters and stereo delays. `validation.json` validates the actual PCM24 exports, hashes and decoded MP3. MP3 container padding makes its reported container length slightly longer; the decoded content is 6.27 seconds. Use WAV frame counts for timing.

Run the acceptance tests from this directory:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 python -m unittest -v test_ui_synth.py
```

Tests cover finite/peak-safe samples and clean tails for all designs, deterministic seeds, pitch-frequency behavior, short attacks, parameter/pan extremes, PCM24 round-trip integrity, and invalid input. `steps.md` records the envelope diagnosis and export checks.
