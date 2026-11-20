---
name: imessage-motion-library
description: Choose, preview, adapt, and render editable iMessage and product-film movement.
---

Start in `skill/imessage-motion-recreation`. Describe the visible change, the layer that stays anchored, and what the viewer should understand. Use `select` to read the reason and `info` to see the movement, exclusions, source and exposed content.

```sh
node motion/cli.mjs select --brief "Show the composer send an outgoing blue text and then an incoming gray reply"
node motion/cli.mjs info --id conversation-handoff
node motion/cli.mjs render --id conversation-handoff --out /tmp/handoff.mp4
```

Install the selected renderer dependencies from [RUNNING.md](../RUNNING.md). The default is Pillow plus FFmpeg. With a virtual environment, use its `python3` on PATH or set `MOTION_PYTHON` to its executable. View the MP4 and its adjacent `.scene.json` and `.events.json`. Import `buildMotion` from [scene.mjs](scene.mjs) and `byId` from [catalog.mjs](catalog.mjs) to use the same implementation directly.

Replace copy and artwork in a JSON file and pass it with `--content`. Each entry's `editable` list describes the fields it reads. Artwork paths in a content file resolve from that file. Keep text short enough to read at the preview size.

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
```

Use `scene` with the same inputs and a JSON `--out` to export editable source without encoding. A `combine` decision names successive beats. `--ids ID1,ID2` exports serial cuts. If the result is `hold`, give the viewer reading time. If it is `missing`, use the stated constraint to plan and verify a new recipe.
