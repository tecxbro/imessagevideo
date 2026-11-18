# Codex sound trial

The finished mix is [Pinch Hit](pinch/final/mix.mp4). The clean [PCM master](pinch/final/master.flac), [environment](pinch/final/environment.flac), [hands and UI](pinch/final/hands.flac), and [payoff](pinch/final/payoff.flac) stems are 48 kHz stereo FLAC, all starting at picture zero. The source MP4 is the director's 576-frame, 24 fps [revised silent cut](https://github.com/tecxbro/imessagevideo/blob/19d50dc26e4e8e2f2875affdb3b2c7b2ca6861be/trials/pinch-hit/films/final-picture.mp4), SHA-256 `b9c6d6a86fb34cbf5a7f6058dc3c96226a31d415d8e9a3bd54e571f9f61452db`.

## Poke. Two scores on the same edit

Source is the accepted GSAP v19 master at `c49482aec7b8ed0b840f97c61a5e5b860c4077b6`. Viewed full-master frames 540, 549, 574–575, 619, 644–645, 664, 687, 690, 702, 728, 732, 756 and 769. The excerpt uses frames [540, 770) at 30000/1001 fps, encoded once so both new mixes use the same 230 H.264 packets and timestamps. The blue restaurant check first appears at full-master f645. Maps begins to emerge at f728 and the orange marker is clear at f732. [Canonical cue evidence](https://github.com/tecxbro/imessagevideo/blob/c49482aec7b8ed0b840f97c61a5e5b860c4077b6/resources/complete-ui-audio-source-v1/imessage-recreations/audio-recreation/ui-cues/canonical-04-poke.json)

| Repository media at the trial base | Role |
| --- | --- |
| `resources/silent-picture-masters-v1/imessage-recreations/outputs/04-poke/gsap.mp4` | Silent H.264 master. SHA-256 `61286445805216b985028595c7e3f0f8dd01c2da44695b658a867145eef0d772`. |
| `projects/04-poke-complete-v1/imessage-recreations/deliverables/04-poke/gsap.mp4` | Historical picture with original reference AAC copied from `references/04-poke/source.mp4`. |
| `resources/complete-ui-audio-source-v1/imessage-recreations/audio-recreation/ui-previews/04-poke-ui.mp4` | Existing independent, boosted UI-only audition. |
| Same directory, `04-poke-recreated.mp4` | Existing independent UI and pinned music mix. |

All four share the same video stream. Their roles are supported by stream probes, the historical `gsap.audio.json`, and the two preview JSONs, which document `reference_audio_reused: false`. Only the silent master supplied picture to this trial. [Production map](https://github.com/tecxbro/imessagevideo/blob/c49482aec7b8ed0b840f97c61a5e5b860c4077b6/FINAL-PRODUCTION.md)

The independent reviewer received anonymous [V04](auditions/V04.mp4) and [V17](auditions/V17.mp4) at equal decode gain. The prompt asked whether the chooser, choice, result card and Maps read as separate actions or a continuous gesture, and where an apparent lift and landing occur.

### Blind interpretation

The reviewer inferred that V17 made the interface actions more discrete, especially by separating the intermediate result card from Maps. V04 gave Maps a stronger lift and settling motion. Both treatments preserved isolated action beats and a quiet decision gap. The reviewer used two local audio classifiers (Apple SoundAnalysis and YAMNet) with shared picture frames and signal analysis. The perceptual language is a model-assisted interpretation. Human listening remains unverified.

### Treatment and measurements

| Reveal | Cue file start | Design landmark | Decoded audio observation |
| --- | --- | --- | --- |
| V04, gesture | 6.124 s | 6.406 s, legible map marker | First sustained energy around 6.13 s. Largest window around 6.32 s, near first visible map. Holds energy through about 6.80 s. |
| V17, tactile | 6.374 s | 6.406 s, legible map marker | Shorter, brighter hit from about 6.37–6.52 s. Peak window near 6.40 s. |

V04 anticipates the camera and lets the picture settle into the next shot. It drops the found-spots and result-card transients. V17 scores both and uses a shorter pan to the result. The choice click is the same source and intended gain in both. V04 measures −23.3 LUFS and −9.5 dBTP. V17 measures −31.7 LUFS and −10.5 dBTP. The cues also differ in count, register and duration, so this is a treatment comparison at matched choice-cue gain. Both mixes preserve digital silence in the checked decision and distance-copy windows. [Gesture report](reports/poke-gesture.json) · [Tactile report](reports/poke-tactile.json)

A blind follow-up could combine V17's intermediate result click with a quieter V04-shaped map reveal. This trial keeps the two renders intact.

## Pinch Hit. Score, edit, score again

The [early mix](pinch/early/mix.mp4) scores picture commit [`3324065`](https://github.com/tecxbro/imessagevideo/blob/3324065c5386952c1db87a77925a5df9c1d81dff/trials/pinch-hit/films/early.mp4) as delivered. The [isolated hold test](pinch/hold-test/mix.mp4) scores the director's exact requested variant. At 24 fps, the chair shot loses 12 frames (3.542 → 3.042 s), and the completed mark gains those 12 frames before the title (1.208 → 1.708 s). Confirm, book cut and graphite all move 0.500 s earlier. Title f529 and total length stay fixed. The same foreground cues and gains apply to both cuts, with the ambience envelope moved to the new boundaries.

The observer's cold view of the early, silent picture caught the intended payoff in the mark and reported drifting late in the wait. The isolated timing change is designed to reduce that wait while leaving more time to register the consequence. The larger revised picture also introduces Maya's reply and the occupied-chair reveal. It has its own score, with a softer kitchen perspective, distinguishable coach and Maya sends, field sound carried into the book cut, and a dry graphite stroke. The title shares the remaining field air. The director asked for a level check. A +4 dB output trim moves the integrated reading from −31.1 to −27.1 LUFS, with −5.0 dBTP, −68.08 dBFS through the middle of the wait, and −43.62 dBFS through the closing hold. A +5 dB trim would put the closing hold near its ceiling. The gain decision is based on those measurements; normal-volume human playback remains unverified. [Independent cold-view report](https://github.com/tecxbro/imessagevideo/blob/262877b84fd153d8f6471a633ab71479cfe32d0d/OBSERVER.md) · [Director's edit and picture handoff](https://github.com/tecxbro/imessagevideo/blob/film-trials/codex-direction/HANDOFF.md)

| Revised picture event | Visible frame | Clip start | Intended impact landmark |
| --- | ---: | ---: | ---: |
| Coach sends | 170 | 7.090 s | 7.125 s |
| Maya sends | 352 | 14.681 s | 14.708 s |
| Coach confirmation | 392 first faint, 397 readable | 16.480 s | 16.542 s |
| Paper contact | 488 | 20.322 s | 20.333 s |
| Graphite stroke | 489–513 | 20.375 s | 20.875 s, strongest intended motion |

These are editorial landmarks and sample offsets. A source's largest sample can be elsewhere, and the felt moment in playback can move again. Per-cue sample and peak values are recorded in [final timing](pinch/final/timing.json).

## Provenance and reproducibility

[Asset manifest](assets.json) pins the tracked source paths and SHA-256 for the CC0 one-shots and the private library's procedural hits. Deterministic field air, room tone, scuff, softened ball/glove accents, motion foley and graphite are authored here in [soundscape.py](soundscape.py) and [mix.py](mix.py), with source seeds and design parameters in the plans. All trial music and reference soundtrack inputs are excluded. The comparison uses cue-matching and refines the correlation workflow with an absolute gain floor and a confidence floor. [HyperFrames sound direction](https://github.com/heygen-com/hyperframes/blob/main/skills/hyperframes/references/sound.md) · [Launch Video Clone checker](https://github.com/per-simmons/launch-video-clone/blob/main/scripts/soundcheck.py) · [Serena launch reference index](https://github.com/serenakeyitan/awesome-ai-clonable-launch-videos#poke-imessage-ai-assistant)

Use Python 3.12, NumPy/SciPy from `requirements.txt`, and FFmpeg with libx264, FLAC and AAC. From the repository root, `PICTURE` is the pinned director MP4 above. The plan refuses a picture with a different SHA-256 or frame count. Use the checked-in Poke excerpt to reproduce the two comparison mixes. To reconstruct the excerpt from a hydrated library, use `PYTHONPATH=sound-trial python3 sound-trial/poke/cut.py SILENT_POKE_MASTER /tmp/poke.mp4`. FFmpeg build changes can change that file's encoded SHA even with the same picture frames; the trial's plans pin the bundled excerpt bytes.

```sh
python3 sound-trial/mix.py "$PICTURE" sound-trial/pinch/final.json /tmp/pinch-clean
python3 sound-trial/mix.py "$PICTURE" sound-trial/pinch/final.json /tmp/pinch-faults --faults
python3 sound-trial/check_export.py /tmp/pinch-clean/mix.mp4 --picture "$PICTURE" \
  --manifest /tmp/pinch-clean/qc.json
python3 sound-trial/check_export.py /tmp/pinch-faults/mix.mp4 --picture "$PICTURE" \
  --manifest /tmp/pinch-clean/qc.json
```

The clean check must exit 0. The planted version must exit 1 with exactly `coach-send: late` and `pencil-contact: missing`. The negative control delays the coach send by five frames and removes the isolated pencil contact while leaving the graphite and picture intact. The checker verifies H.264 packet bytes, rational cadence, and timing; it decodes delivered AAC, measures true peak and protected quiet, and searches for the template with gain and confidence thresholds. It reports relevant missing or degraded cues within the tested search window. Use a distinct template or reduce the search range where near-identical cues repeat. AAC can change exact sample values and the analysis estimates timing at 8 kHz resolution. Export checks and evidence are in [reports](reports/).
