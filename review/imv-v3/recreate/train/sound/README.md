# Independent soundtrack

The Sound work at `d3fc101` supplied four original, synthesized cue effects, with separate PCM stems. The scored MP4s preserve every decoded picture of the corresponding silent exports. The locked scored MP4 passes all six picture regions against the reference. Its four-second picture and audio clocks start together. The Recreation check observes all four audio cues inside their planned windows. The Sound check measures individual impact timing to within 0.021 ms, at an estimated true peak of −13.02 dBTP. Human audition is pending. [Sound handoff and source recipe](https://github.com/tecxbro/imessagevideo/tree/d3fc101/review/imv-v3/sound/recreation)

The edited score keeps the intended +9 ms seat-latch lag when the picture event moves from frame 74 to 69. The stale control places the old cue on the edited picture and fails by +166.688 ms. The other three event anchors stay in place. [Locked check](sound-final.json) · [Edited check](sound-edited.json) · [Stale control](sound-stale-control.json)

```sh
R=skill/imessage-motion-recreation/recreate
D=review/imv-v3/recreate/train
python3 "$R/recreate.py" compare "$D/reference.mp4" "$D/scored.mp4" --checks "$D/sound/scored.checks.json" --out /tmp/train-scored
python3 "$R/recreate.py" compare "$D/edited.mp4" "$D/edited-scored.mp4" --checks "$D/sound/edited-scored.checks.json" --out /tmp/train-edited-scored
```
