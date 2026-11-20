# Sound for The Moon Cue

The finished film uses Sound's treatment A. The quiet room carries the wait.
The tin and paper establish the operator's physical action. The audience's
exhale follows the lean beginning at f270. Direction chose this treatment
after both rough muxes passed the export checks. Their integrated loudness
differed by 0.2 LU. [Rough treatments](https://github.com/tecxbro/imessagevideo/blob/5745cad/review/imv-v3/sound/direction/rough/README.md)

The [selected plan](locked/a.json), nine original synthesized source WAVs
under `assets/`, landmark crops, and four 48 kHz stereo stems are all editable.
The dialogue and music stems are silent in this treatment. The PCM mix
and eight verified cue placements are in [the report folder](locked/a/).
Sound's original synth and arrangement code is pinned in its handoff.
[Sound's source and mix measurements](https://github.com/tecxbro/imessagevideo/blob/1ba37bb/review/imv-v3/sound/direction/locked/README.md)

The chosen mux carries exactly the locked H.264 picture and its presentation
timestamps. FFmpeg decoded it in full with video and 48 kHz stereo AAC each
running 15 seconds. Sound's checker returned eight of eight cues within their
intended offsets, each measured at 0.0 ms error. It reported −4.14 dBTP,
zero audio-clock discontinuity and no energy dropout. Sound measured
−29.7 LUFS integrated. Human listening remains pending.

Re-run the encoder or decoded-export check from the repository root using
the integrated Sound runtime.

```sh
S=${S:-skill/imessage-motion-recreation/sound}
R=review/imv-v3/direction
python3 "$S/sound.py" mix "$R/sound/locked/a.json" "$R/locked.mp4" /tmp/moon-mix
python3 "$S/sound.py" verify "$R/sound/locked/a.json" "$R/locked.mp4" \
  "$R/the-moon-cue.mp4" "$R/sound/locked/a/manifest.json"
(cd "$R" && sha256sum -c final.sha256)
```

On the standalone Direction branch, run this setup and use its `S` value in
the commands above.

```sh
git fetch origin refs/heads/codex-video-v3/sound:refs/remotes/origin/codex-video-v3/sound
sound_runtime=$(mktemp -d)
git archive 1ba37bb skill/imessage-motion-recreation/sound | tar -x -C "$sound_runtime"
S="$sound_runtime/skill/imessage-motion-recreation/sound"
python3 -m pip install -r "$S/requirements.txt"
```
