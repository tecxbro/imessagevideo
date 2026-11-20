# iMessage video v3.2.2 release

- [Standalone skill ZIP](imessage-motion-recreation-v3.2.2.zip)
- [Media companion ZIP](imessage-motion-media-v3.2.1.zip)
- [Capability verdicts, commands and remaining work](VERDICT.md)
- [Shared frame and cue contract](../../../skill/imessage-motion-recreation/contracts/README.md)

The standalone skill includes a command to generate a Motion example after
runtime setup. In v3.2.2 the entry point routes ordinary requests about
moving headings, pinned photos and reading a count to Motion. The v3.2.1
media companion works with this skill. It contains the finished films,
images and editable project and audio archives, plus 90 ready-to-open
Motion previews and their event maps.

Download both ZIPs into one folder and run these commands there:

```sh
mkdir imessage-video-release
unzip -q imessage-motion-recreation-v3.2.2.zip -d imessage-video-release/skill
unzip -q imessage-motion-media-v3.2.1.zip -d imessage-video-release
cd imessage-video-release
sha256sum -c MEDIA-SHA256SUMS
python3 skill/imessage-motion-recreation/observer/package.py --verify ../imessage-motion-recreation-v3.2.2.zip
```

Then open `review/imv-v3/observer/PORTABLE.md` in the extracted release for
playback, pictures and the exact audio edit paths. Previous skill ZIPs
remain available. [v3.2.1](imessage-motion-recreation-v3.2.1.zip) · [v3.2.0](imessage-motion-recreation-v3.2.0.zip)

## Accepted films and editable projects

| Film | Deliverables |
| --- | --- |
| The Moon Cue | [Finished MP4](../direction/the-moon-cue.mp4), [standalone editable project with stems](the-moon-cue-editable-project.zip), [picture and sound measurements](evidence/direction-sound-measurements.json) |
| Train options | [Scored MP4](../recreate/train/scored.mp4), [standalone editable project with stems](train-options-editable-project.zip), [editable scene](../recreate/train/final.scene.json), [frame-addressed event map](../recreate/train/final.events.json), [render and edit instructions](../../../skill/imessage-motion-recreation/recreate/example/README.md), [editable audio](../sound/recreation/README.md) |
| Workshop interaction edit | [MP4](interaction-edit/interaction.mp4), [editable conversation](interaction-edit/conversation.json), [resolved events](interaction-edit/events.json), [consecutive frames](evidence/interaction-edit-strip.png) |
| Motion and conversation examples | [Motion review files](../motion/README.md), [editable Motion recipes](../../../skill/imessage-motion-recreation/motion/SKILL.md), [Interaction review films](../ui/README.md), [editable conversation adapter](../../../skill/imessage-motion-recreation/ui/SKILL.md) |

The Moon Cue archive includes the original adapter revision used for the
locked film. The reusable skill includes the current adapter for new work.
All links in this table are part of the private integration checkout.

From this directory, check the exact releases with `sha256sum -c SHA256SUMS`.
Verify the standalone skill with `observer/package.py --verify` from that
skill or the corresponding checkout.

To rebuild both archives from the repository root, run:

```sh
skill=skill/imessage-motion-recreation
release=review/imv-v3/observer
python3 "$skill/observer/package.py" --out "$release/imessage-motion-recreation-v3.2.2.zip"
python3 "$skill/observer/package_media.py" --out "$release/imessage-motion-media-v3.2.1.zip"
(cd "$release" && sha256sum -c SHA256SUMS)
```

This update ships from the Observer branch. The verdict lists the exact
specialist pins tested independently and the evidence still needed for the
seven-head integration.
