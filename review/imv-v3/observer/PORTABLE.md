# Open the v3.2.1 release

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

## Finished films, stills and editable projects

| Film | Playback | Images | Edit |
| --- | --- | --- | --- |
| The Moon Cue | [MP4](../direction/the-moon-cue.mp4) | [Picture-lock frames](evidence/direction-lock-strip.png) | [Editable project and audio ZIP](the-moon-cue-editable-project.zip) |
| Train options | [Scored MP4](../recreate/train/scored.mp4) | [Full-cut contact sheet](evidence/recreation-contact-sheet.png) | [Editable project and audio ZIP](train-options-editable-project.zip) |
| Workshop interaction | [MP4](interaction-edit/interaction.mp4) | [Consecutive frames](evidence/interaction-edit-strip.png) | [Conversation](interaction-edit/conversation.json), [events](interaction-edit/events.json), [Interaction skill](../../../skill/imessage-motion-recreation/ui/SKILL.md) |
| Station interaction example | [MP4](../ui/station-pillow.mp4) | [Consecutive frames](../ui/station-pillow-consecutive.jpg) | [Interaction skill](../../../skill/imessage-motion-recreation/ui/SKILL.md) |

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
