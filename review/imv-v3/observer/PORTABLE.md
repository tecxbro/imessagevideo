# Open the v3.3.0 release

Run the commands below from the directory where you extracted the two ZIPs.
The skill is in [skill/imessage-motion-recreation](../../../skill/imessage-motion-recreation/SKILL.md)
and the media checksums are in [MEDIA-SHA256SUMS](../../../MEDIA-SHA256SUMS).

## Motion previews

With Node available, copy the pre-rendered example to the path of your choice:

```sh
(cd skill/imessage-motion-recreation && node motion/cli.mjs preview --id heading-over-fixed-photos --out /tmp/heading-preview.mp4)
```

You can also open the [MP4](../motion/heading-over-fixed-photos.mp4) and read
its [event map](../motion/heading-over-fixed-photos.events.json). All 77 base
examples and the 13 conversation variants in the [catalog](../../../skill/imessage-motion-recreation/motion/catalog.json)
have a preview and event map here. Add `--ui` for an example with a
conversation variant. To make a new editable version, use the `render`
command in the [skill](../../../skill/imessage-motion-recreation/SKILL.md).

Two focused examples include edited numeric or conversation inputs.

| Example | Preview | Images | Edit |
| --- | --- | --- | --- |
| Count and reading hold | [MP4](../motion/v3.2/metric-hold.mp4) | [Frames](../motion/v3.2/metric-hold-frames.png) | [Content](../../../skill/imessage-motion-recreation/motion/examples/metric-hold.json), [scene](../motion/v3.2/metric-hold.scene.json) |
| In-thread swipe and return | [MP4](../motion/v3.2/photo-swipe.mp4) | [Frames](../motion/v3.2/photo-swipe-frames.png) | [Conversation](../../../skill/imessage-motion-recreation/motion/examples/photo-swipe.ui.json), [events](../motion/v3.2/photo-swipe.events.json) |

## Finished films, stills and editable projects

| Film | Playback | Images | Edit |
| --- | --- | --- | --- |
| The Moon Cue | [MP4](../direction/the-moon-cue.mp4) | [Picture-lock frames](evidence/direction-lock-strip.png) | [Editable project and audio ZIP](the-moon-cue-editable-project.zip) |
| Train options | [Scored MP4](../recreate/train/scored.mp4) | [Full-cut contact sheet](evidence/recreation-contact-sheet.png) | [Editable project and audio ZIP](train-options-editable-project.zip) |
| Workshop interaction | [MP4](interaction-edit/interaction.mp4) | [Consecutive frames](evidence/interaction-edit-strip.png) | [Conversation](interaction-edit/conversation.json), [events](interaction-edit/events.json), [Interaction skill](../../../skill/imessage-motion-recreation/ui/SKILL.md) |
| Station interaction example | [MP4](../ui/station-pillow.mp4) | [Consecutive frames](../ui/station-pillow-consecutive.jpg) | [Interaction skill](../../../skill/imessage-motion-recreation/ui/SKILL.md) |

The current Interaction adapter has a [keyboard-up send](../ui/sequences/send-keyboard.mp4),
[Tapback and scroll](../ui/sequences/tapback-scroll.mp4),
[fixed-header photo swipe](../ui/sequences/photos-fixed-header.mp4), and a
[payment test mock](../ui/sequences/payment-mock.mp4). Open the
[decoded frames](../ui/sequences/payment-mock-frames.jpg) and
[pixel and timing checks](../ui/sequences/proof.json), and edit the
[adapter inputs](../../../skill/imessage-motion-recreation/ui/SKILL.md).

Extract either editable project ZIP into a working directory to change its
timeline or sounds:

```sh
mkdir -p projects
unzip -q review/imv-v3/observer/the-moon-cue-editable-project.zip -d projects
unzip -q review/imv-v3/observer/train-options-editable-project.zip -d projects
(cd projects/the-moon-cue && sha256sum -c SHA256SUMS)
(cd projects/train-options && sha256sum -c SHA256SUMS)
```

Use each project's `README.md` for its renderer and reproduction commands.
The following paths are relative to its own extracted directory.

| Project | Editable audio plan | WAVs |
| --- | --- | --- |
| `projects/the-moon-cue` | `score/locked/a.json` | `score/locked/a/` contains atmosphere, dialogue, effects, music and mix. `score/assets/` holds the cue sources. |
| `projects/train-options` | `skill/imessage-motion-recreation/sound/recreation/train.plan.json` | `review/imv-v3/sound/recreation/final/` contains effects, mix and four separate WAVs in `cue-stems/`. The cue sources are in `review/imv-v3/sound/recreation/assets/`. |

The separate Train sound retime has a [remapped film](../sound/recreation/owner-retime/remapped/mix.mp4),
[seat-selection frames](../sound/recreation/owner-retime/seat-selection-frames.png),
and the same [editable plan](../../../skill/imessage-motion-recreation/sound/recreation/train.plan.json).
Its revised [PCM master](../sound/recreation/owner-retime/remapped/mix.wav),
[seat cue stem](../sound/recreation/owner-retime/remapped/cue-stems/seat-latch.wav),
and [pass](../sound/recreation/owner-retime/remapped/verify.json) and
[stale](../sound/recreation/owner-retime/stale.verify.json) reports are part of
the media companion. From the release root, reproduce the remapped plan with
the [Sound runtime](../../../skill/imessage-motion-recreation/sound/SKILL.md):

```sh
S=skill/imessage-motion-recreation/sound
D=review/imv-v3/sound/recreation/owner-retime
python3 "$S/sound.py" mix "$S/recreation/train.plan.json" "$D/revised-silent.mp4" /tmp/train-recut
```
