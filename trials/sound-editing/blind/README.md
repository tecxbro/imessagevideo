# Anonymous comparison set

Listen to each `T-*/comparison.mp4`. Neutral labels are random; the assignment
key is stored only in `../keys/treatments.json`. Do not consult that key before
review. For a perceptual anonymous comparison, do not inspect stems, cue counts,
receipts or provenance until after choosing: these necessarily reveal what can
also be heard in the audio. There is no assertion of cryptographic blinding.

Each folder contains independent 48 kHz stereo PCM24 `ui.flac`, `music.flac` and
`full_mix.flac`; `production.mp4` preserves production gain. `comparison.mp4`
uses only common scalar attenuation of the full mix, never peak-raising,
compression or separate UI normalization. `levels.json` contains measured final
MP4 levels. The matched copies span 0.04 LUFS; their quiet level is intentional
because sparse production effects were not raised to a program loudness target.

`cue-impacts.json` records native frame, sample, source asset/effect and alignment.
`provenance.json` pins sources, license evidence/limits, gain, code and exports.
`receipts/{production,comparison}.json` pin individual reference waveforms for
the decoded checker. `*.check.json` and `*.check.txt` retain its full output.

The existing music input is byte-pinned to the project's earlier provider-
generated asset. No new AI generation was requested. Its archive contains
provider/job/input provenance, but not a standalone music license or account
entitlement certificate. It is not CC0; external release clearance remains
unverified. Stock UI effects and keyboard recordings retain their CC0 evidence;
custom movement effects retain their original project source provenance.

## Hash identity

Original accepted `gsap.mp4` **whole-file** SHA-256:
`1004ce2e9ab70da7f5a1e0d7a849156cf06b89902ee0aadb8d2bddb2e416e176`.
This hashes container metadata, audio and video together.

**Video packet payload** SHA-256:
`fef5481d8bbb13c16a14d05ad846cdb72112ca876913b9f0c27d871dc393d62b`.
Measured with `ffmpeg -map 0:v:0 -c copy -f hash -hash sha256`.
This excludes container metadata and audio and matches all six exports.
Neither value is a decoded-frame hash; no decoded-frame identity claim is made.
Receipts/manifests now name hash methods explicitly. Older trial receipts retain
their original values with added `hash_methods` annotations.

## Review correction retained

The first continuous-reference runs found all UI cues but reported residual
extras (5 production, 4 comparison). The old fixed 0.003 RMS threshold mistook
AAC error from subtracting an uncompressed continuous reference for extra hits.
Initial JSON evidence is retained under `../results/*-first.json`.

Changed only the continuous-reference residual noise model: independently encode
the pinned reference at the declared AAC 192 kbps, measure its codec residual,
then use `max(0.003, 2 * local_105ms_max_reference_codec_RMS + 0.001)` for extra
detection. This derives no noise floor from the delivery being checked and
does not fit away its residual. The expected reference itself is still subtracted
at unity gain, not fitted gain. All six final checks pass. Music-free reviews
retain the original fixed threshold. A unit test verifies an extra transient
survives background subtraction and is still flagged.

This codec floor reduces sensitivity to quiet extras during dense music. It is
not a substitute for audition; no human listening or visual playback is claimed.

Example command, replacing LABEL with a folder name:

```sh
.sound-survey-venv/bin/python trials/sound-editing/tools/check_cues.py \
  trials/sound-editing/blind/LABEL/comparison.mp4 \
  --receipt trials/sound-editing/blind/LABEL/receipts/comparison.json \
  --json trials/sound-editing/blind/LABEL/comparison.check.json
```
