# Separate v3 web delivery master

`master.mp4` is a separate delivery product. The production `../final.mp4` and all four independent stems remain unchanged; their before/after hashes are in `measurements.json`. Input is only `../full_mix.flac`. No new cue, music or picture edit is introduced.

## Recipe and readouts

First pass: FFmpeg9.0.2 `loudnorm` measurement of the lossless full mix:−39.75LUFS,−16.74dBTP,15.6LU LRA. Second-pass delivery chain uses **static linear volume**,192kHz(4×) oversampling, linked lookahead `alimiter`, then48kHz downsampling and192kbps AAC. This is not `loudnorm`'s dynamic normalization fallback. The exact limiter is:

`alimiter=limit=0.794328234724:attack=5:release=50:level=false:latency=true`

The−2dB limiter ceiling leaves headroom for downsampling/AAC overshoot. Initial static gain+23.75dB yields−18.59LUFS after limiting. Six offline loudness calibrations converge to **+28.69dB static gain**,−16.06LUFS PCM; final decoded AAC measures **−16.13LUFS /−1.29dBTP /20.7LU LRA**. All calibration readouts are retained; there is no running loudness gain controller. The first implementation's five-calibration cap was insufficient; it was increased to15 without changing the target or verification thresholds.

Maximum measured limiter reduction is **13.9497dB**;99th percentile over non-negligible input samples is10.7791dB. Measurement compares the latency-compensated192kHz limiter output/input sample amplitudes before downsampling. The final extra gain beyond the initial+23.75dB compensates limiting loss; unrestricted peak at that final gain would be about+11.95dBTP, not the initial roughly+7dBTP. This is substantial peak shaping, not a claim of perceptual transparency. No human audition is claimed.

Final whole-file SHA256: `467aa6447505a7521335831f2ceb0e1e0b68dbe406bb4c007810b3fd7082f2c5`.

Video packet-payload SHA256: `3bc70fbb7856ef3e8c988509caa5f90e8377316845367f54842322417c9d3fd6`, unchanged via video stream copy. Not a decoded-frame hash.

## Strict cue review

The delivery receipt declares an explicit `delivery_transform`: static gain, limiter, oversampling and reference derivation. **Production references are not reused at the wrong level.** Each independently pinned cue reference passes through the same declared delivery chain, with100ms zero padding at both edges; motion reference is independently transformed too. No reference is extracted from the master or the full-mix stem. Cue sample positions stay fixed. Nonlinear neighboring-cue interactions are not modeled by these independent templates, and are still subject to the unchanged similarity/level tests.

Original checker thresholds remain±0.5frame,.8 correlation and±6dB level. No checker code or thresholds were loosened:

```text
pass: picture_match=True, cues=35, defective=0, extras=0
```

All offsets0 samples; minimum correlation.961556. See `check.{json,txt}` and `receipts/master.json`.

## Fresh reproduction

First execute the parent v3 README, including the root environment/library bootstrap. Then, from repository root:

```sh
.sound-survey-venv/bin/python trials/sound-editing/checkin-v3/tools/build_delivery.py
.sound-survey-venv/bin/python trials/sound-editing/tools/check_cues.py \
  trials/sound-editing/checkin-v3/delivery/master.mp4 \
  --receipt trials/sound-editing/checkin-v3/delivery/receipts/master.json \
  --tolerance-frames 0.5 --json trials/sound-editing/checkin-v3/delivery/check.json
.sound-survey-venv/bin/python trials/sound-editing/checkin-v3/tools/test_delivery.py
```

The builder refuses an existing master, creates its own missing output directories, records input-integrity hashes and asserts the final encoded loudness/true-peak specification. Media and NPY references are omitted from Git and recorded in `../../BINARY-MANIFEST.json`; recipe, measurements and receipt/check snapshots are committed.
