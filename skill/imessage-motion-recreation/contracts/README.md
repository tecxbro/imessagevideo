# Picture, interaction and sound contract

Extend the repository's [measured scene](../scripts/shared/SCHEMA.md) with a
`timeline` object. The existing layers and their output-second keyframes are
editable picture. The extension adds frame-addressed evidence and sound timing
to that same file. Older scenes remain valid renderer inputs. When bringing one
into v3, measure its event frames and add the extension before handing it off.

- `timeline.version` is `1`. `picture` contains reduced positive integer fps
  terms `fpsNum` and `fpsDen`, and a positive integer `frameCount`. Frame zero is
  the first output frame. The last is `frameCount - 1`. Frame `f` begins at
  `f * fpsDen / fpsNum` seconds. Use this conversion for picture keyframes and
  lifecycle boundaries. The existing root `fps` and `duration` are numeric
  projections of that rate and `frameCount / fps`. Keep reference-source time
  and any retime or omitted passages in the existing source mapping.
- `events` are in ascending frame order. Each has `id`, `kind`, `target`, and
  `frame`. Use lowercase ASCII letters, digits, dots, dashes, underscores or
  colons for semantic IDs. Make each ID unique inside a film. Preserve an event
  ID when its picture timing, renderer or copy changes. Assign a new ID to a
  different occurrence. `target` is the semantic subject. Optional `layerIds`
  identify editable picture geometry linked to the event. Record the first
  visible frame of the named action, then verify the frames on either side.
- `initialUI` is the full state before frame zero. An event may supply a full
  `uiState` that applies on its frame and persists until the next state change.
  At most one event changes state on a frame. Order same-frame events so
  consumers resolve the intended state. A state is null for a shot without UI
  or an object with `conversationId`, ordered `messages`, `composer` and
  `viewport`. Each message has `id`, `senderId`, `text` and optional
  `attachmentIds`, `replyTo` message ID, `reactions` (sender ID to mark),
  zero-based attachment `page`, `edited` flag, and `receipt` text. The composer
  has `text`, `focused` and an optional `keyboardVisible`. The viewport has a
  semantic `surface`, nullable `anchorMessageId`, optional message-ID
  `selection` and optional logical `scrollOffset` in scene pixels. The state can
  also carry `typingSenderIds`. Include the fields the interaction changes so
  another specialist can reproduce its result. Keep animation in the layers.
- `cues` contain a stable `id`, an `eventId` and a signed integer
  `offsetSamples`. The audio clock is 48 kHz from output sample zero. A cue's
  onset is `floor(f * 48000 * fpsDen / fpsNum + 1/2) + offsetSamples`.
  Resolve the anchor again after a picture edit. Keep asset, gain, envelope,
  provenance and mix decisions in the Sound project. A placed asset with a
  pre-roll lead should use that lead when converting onset to asset start.

Run the example from the **skill directory** with the Pillow runtime installed
as described in [RUNNING.md](../RUNNING.md).

```sh
python3 contracts/timeline.py contracts/example.scene.json
python3 scripts/engines/render_pillow.py --scene contracts/example.scene.json --out /tmp/imv-contract.mp4
ffprobe -v error -select_streams v:0 -show_entries stream=avg_frame_rate,nb_frames -of csv=p=0 /tmp/imv-contract.mp4
```

Expect event `demo.message.send` at frame **12**, event sample **24000**, cue
`demo.send.click` at sample **24120**, and a **24-frame, 24/1** export. The amber
card is on the left at frame 11 and on the right at frame 12. The example
declares a cue and exports silent picture so each specialist can use the same
picture independently.
