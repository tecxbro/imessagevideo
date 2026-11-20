# Photo swipe and attachment motion

Use the same photo assets and change the motion according to where the viewer is browsing. The editable inputs below work from the portable skill with the bundled artwork and Clone iMessage UI.

| Situation | What moves | What stays fixed | Evidence |
| --- | --- | --- | --- |
| Native Messages grouping | Apple describes a collage for two or three received items and a stack for four or more. Its guide shows the workflow as open a stack, then swipe between items. | The guide establishes attachment grouping and the opened-stack workflow. Fixed screen layers, swipe timing and page persistence still need a continuous recording with device and build. | No timed native event map is available. [Apple iPhone User Guide](https://support.apple.com/guide/iphone/share-content-iphb66cfeaad/27/ios/27) |
| Place or album rail | The photo rail translates as one layer within its own clip. Use `photos-under-fixed-heading`. | The heading, clip, divider, and footer. In the Linq source the venue title and tabs stay in place as the images change. | The measured rail source is the Linq launch film at frames 1091–1111, 30 fps. The gesture and device are undocumented in that edit. [Rail preview](../../../review/imv-v3/motion/v3.2/venue-rail.mp4) |
| Overlapping attachment stack | The front card leaves with a rotation and its successor advances in depth. Use `messages-attachment-stack` for a film treatment that emphasizes individual cards. | The conversation label, static transcript copy, attachment count, composer, and backdrop. | The inline promotion and its timing are authored. [Stack preview](../../../review/imv-v3/motion/v3.2/attachment-stack.mp4) |
| Inline conversation paging | The adapter slides media inside an existing message and updates the selected page. A later viewer opens that page and returns to the same attachment position. | During paging, the conversation header, prior transcript row, attachment window and composer hold. The viewer separately covers the conversation when it opens. | Authored through Clone iMessage UI at `5e2ff5a`. Field Notes sends at f108, pages at f130, opens at f146 and returns at f166, all at 24 fps. [Field Notes input](https://github.com/tecxbro/imessagevideo/blob/5e2ff5a765dd105b5bdebb51bcfbe2a803e3bb71/skill/imessage-motion-recreation/ui/examples/field-notes.json) |

The pinned iOS 26 simulator photo-picker fixture shows three separate bubbles from one picker action. Dataset confirmed that its available references cover only part of the requested continuous native take. For a new capture, mark the first visible attachment, the first photo displacement, and the first held frame of the next photo. Keep the header, composer, page indicator if present, and one adjacent row in frame for half a second before input and after settlement. Record any viewer transition separately. [UI evidence](https://github.com/tecxbro/imessagevideo/blob/5e2ff5a765dd105b5bdebb51bcfbe2a803e3bb71/skill/imessage-motion-recreation/ui/EVIDENCE.md) · [Dataset acknowledgment](https://github.com/tecxbro/imessagevideo/issues/7#issuecomment-7052681859)

## Render a comparison from the portable skill

Run from the directory containing `motion/`, `ui/`, `contracts/` and `scripts/`.

```sh
out=$(mktemp -d)
PY=${MOTION_PYTHON:-python3}
content=motion/examples/photo-swipe.content.json

node motion/cli.mjs render --id photos-under-fixed-heading --content "$content" --out "$out/venue-rail.mp4"
node motion/cli.mjs render --id messages-attachment-stack --content "$content" --out "$out/attachment-stack.mp4"
node motion/cli.mjs render --id photos-under-fixed-heading --ui --content "$content" --out "$out/conversation-rail.mp4"

"$PY" -m ui.adapter motion/examples/photo-swipe.ui.json --out "$out/photo-swipe.scene.json"
"$PY" scripts/engines/render_pillow.py --scene "$out/photo-swipe.scene.json" --out "$out/photo-swipe.mp4"
"$PY" contracts/timeline.py "$out/photo-swipe.scene.json" > "$out/photo-swipe.events.json"
```

The [Motion content](examples/photo-swipe.content.json) sets the heading, supporting copy, four images, and two authored stack swipes. A new place or album uses the rail so the surrounding context stays readable. For a new conversation, duplicate the [UI input](examples/photo-swipe.ui.json) and edit the participants, prior text and attachment assets. Keep `message.id` and each action’s `messageId` aligned. `media.page.index` uses zero-based photo order. Update event frames for your shot’s pacing.

## Read the event maps

- Both rail examples use `motion.photos-under-fixed-heading.rail-start` at f20 and `motion.photos-under-fixed-heading.rail-settle` at f39, at 30 fps. The venue version moves all photos together. The UI variant pages to one adjacent image.
- The authored stack uses `motion.messages-attachment-stack.swipe` at f21 and `motion.messages-attachment-stack.promoted` at f38. The `swipe-2` and `promoted-2` suffixes identify the second pass at f40 and f57. The clock is 30 fps.
- The focused [UI send and swipe preview](../../../review/imv-v3/motion/v3.2/photo-swipe.mp4) uses `trail.photos.send` f12, `trail.photos.page` f32, `trail.photos.open` f52 and `trail.photos.close` f68, at 24 fps. The inline page settles by f43. The resolved attachment page is 0 after send and 1 at swipe, open, and return.

In the focused UI output, the header and prior-row crops were pixel-identical across f31–43. The composer crop’s maximum mean RGB difference was 0.00551 on a 0–255 scale. The media crop changed 25.58 between f31 and f32. The video and state map agree on the selected photo after the viewer closes. [Measurements and decoded frames](../../../review/imv-v3/motion/v3.2/README.md)
