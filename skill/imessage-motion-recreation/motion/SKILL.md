---
name: imessage-motion-library
description: Choose, preview, adapt, and render editable iMessage and product-film movement.
---

Start in `skill/imessage-motion-recreation`. Describe what changes, what must stay anchored and what the viewer should notice. The [catalog](catalog.json) records source ranges, editable fields, event IDs, renderer checks, and an MP4 for each entry. The preview paths resolve from the repository root. The command in each entry rebuilds the preview from the skill directory.

```sh
node motion/cli.mjs select --brief "Move the photos beneath a fixed heading"
node motion/cli.mjs select --brief "Hold the photos still while the heading moves"
node motion/cli.mjs info --id heading-over-fixed-photos
node motion/cli.mjs render --id heading-over-fixed-photos --out /tmp/gallery.mp4
```

The first brief selects a clipped rail with an anchored heading. The second selects a moving title above stationary image crops. Selection reports the reason and one of five actions.

- **Retrieve** uses a matching recipe.
- **Adapt** recommends an editable change. `render --brief ...` applies its structured values, and your `--content` file can override them.
- **Combine** suggests successive beats. Pass the brief to `render`, or use `--ids ID1,ID2` for a sequence of cuts. A reading hold within a selected sequence freezes the adjacent shot for one second.
- **Hold** means the intended beat needs quiet reading time. Keep the current scene's image and timing.
- **Missing** states which requested relationship or mechanism needs a new recipe.

Write replacement copy and artwork to a JSON file, then pass it with `--content`. Use `info` for field types and entry-specific photo limits. The inverse heading entry takes one or two photos. The photo rail takes two through twelve. File paths resolve from the content file. Use short text when replacing labels and keep evidence such as the send or reply readable.

```json
{
  "heading": "Workshop crew",
  "copy": "Can you open the west entrance?",
  "reply": "It is open. Use the ramp.",
  "detail": "Event operations"
}
```

```sh
node motion/cli.mjs render --id conversation-handoff --content /tmp/workshop.json --out /tmp/workshop.mp4
node motion/cli.mjs scene --id conversation-handoff --content /tmp/workshop.json --out /tmp/workshop.scene.json
```

The default uses Pillow and FFmpeg. Set `MOTION_PYTHON` to the Python executable with the [pinned dependencies](../RUNNING.md). Use `--method html`, `gsap`, `remotion` or `motion-canvas` to select another installed engine. The default MP4s decode at 720×480 and 30 fps. Renderer evidence distinguishes complete previews from nine-frame probes. Set `--fps` to 24, 25, 30 or 60 and `--duration` to 1.6–12 seconds per motion. After changing timing or content, check the consecutive frames where each relevant event first affects the picture.

## Use the shared conversation UI

Use `--ui` with a catalog entry that lists an adapter variant. The motion compiler sends editable messages, assets and frame-addressed actions through Clone iMessage UI. The adapter owns layout, transit clips and interaction behavior. The local recipe and adapter give you two editable treatments where timing or styling differs, with separate exact previews and event maps.

```sh
node motion/cli.mjs render --id conversation-handoff --ui --content /tmp/workshop.json --out /tmp/workshop-ui.mp4
node motion/cli.mjs render --id photos-under-fixed-heading --ui --out /tmp/attachment-ui.mp4
```

If `ui/` lives in a separate checkout, use `--ui-root /absolute/path/to/skill/imessage-motion-recreation`. For the pinned version used in the review files, `git archive 5e2ff5a skill/imessage-motion-recreation/ui` yields the adapter from its fetched ref. Unpack it into a working directory and pass the skill directory as `--ui-root`.

Render produces an MP4, an editable `.scene.json` and an `.events.json` with the shared frame clock. `scene` produces the same editable scene and event map without encoding. For programmatic reuse, import `buildMotion(entry, content, options)` from [scene.mjs](scene.mjs), `byId` from [catalog.mjs](catalog.mjs), or `buildUiMotion(entry, content, options)` from [ui-bridge.mjs](ui-bridge.mjs). Insert the returned layers and timeline into a matching scene, or use [composeScenes](sequence.mjs) for serial beats. It resets UI state at cuts and prefixes each occurrence's layer, event and cue links. Keep artwork as individual source files when relocating a generated manifest.

Read [source provenance](SOURCES.md), the [observed-only inventory](observed.json) and the [review evidence](../../../review/imv-v3/motion/README.md) for limits and reuse results. Selector tests include unfamiliar wording, negation, invariant layers and near matches.

```sh
node --test motion/tests/*.test.mjs
```
