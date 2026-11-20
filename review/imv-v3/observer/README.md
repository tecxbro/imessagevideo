# iMessage video v3 release

- [Standalone skill ZIP](imessage-motion-recreation-v3.2.0.zip)
- [Capability verdicts, commands and remaining work](VERDICT.md)
- [Shared frame and cue contract](../../../skill/imessage-motion-recreation/contracts/README.md)

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
