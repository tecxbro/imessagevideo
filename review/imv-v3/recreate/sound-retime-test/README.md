# Train Options sound retime

This neutral retime preserves the approved Train Options regression and exercises an independent Sound handoff. Recreation sent the silent MP4 and its hash at `3fa0021` with the frame and event map withheld. Sound resolved the seat selection at frame 84, ten frames after its approved anchor, and verified the other three anchors at frames 30, 56, and 89.

| Check | Result |
| --- | --- |
| Silent, remapped and stale picture | 120 identical decoded frames with matching picture timestamps |
| Revised selection cue | Frame 84, expected sample 134832, +432 samples after the visual event |
| Remapped cue error | +0.021 ms, all four cues pass |
| Stale cue error | −333.312 ms, seat cue rejected |

Sound supplies both muxes, cue stems, source plan and replay commands. Human audition is pending. [Sound evidence at 5e5a2a0](https://github.com/tecxbro/imessagevideo/tree/5e5a2a0/review/imv-v3/sound/recreation/owner-retime)

Rebuild the revised silent picture from the editable scene generator. The browser and FFmpeg versions used for the clean runner are recorded in the [preflight evidence](../clean-runner.json).

```bash
S=skill/imessage-motion-recreation
D=$(realpath review/imv-v3/recreate/sound-retime-test)
WORK=$(mktemp -d)
node "$S/recreate/example/scene.mjs" "$WORK/scene.json" \
  --config "$D/revised-config.json" --events "$WORK/revised.events.json"
node "$S/scripts/engines/render.mjs" --method html --scene "$WORK/scene.json" --out "$WORK/revised-silent.mp4"
(cd "$WORK" && sha256sum -c "$D/SHA256SUMS")
cmp "$D/revised.events.json" "$WORK/revised.events.json"
```
