---
name: imessage-film-interface
description: Author an editable Messages-style conversation for a film and render it through the repository's shared engines.
---

# Messages film interface

Copy [the editable conversation](examples/conversation.json). Edit the title,
participants, draft, messages and event frames in JSON. Compile after each
edit. The adapter makes the message geometry, scroll, composer, keyboard,
reaction, overlay and camera layers from that one input.

Run from `skill/imessage-motion-recreation` with the
[engine dependencies](../RUNNING.md), Pillow, fontconfig and DejaVu Sans regular
and bold installed.

```sh
python3 -m ui.adapter ui/examples/conversation.json --out /tmp/station.scene.json
python3 scripts/engines/render_pillow.py --scene /tmp/station.scene.json --out /tmp/station.mp4
```

Expect 402×874, 136 frames at 24 fps. The draft clears and the outgoing
message enters at frame 12. The remote reply enters at 44. A context menu
opens at 53, then the reaction attaches to the reply at 64. The transcript
scrolls at 80 and the camera starts moving at 87.

Keep event IDs when editing words, timing or exports. To integrate from
Python, import `compile_conversation` from `ui.adapter`. Pass the description
dictionary and the input/output directories. Other languages can call the
CLI and consume the same scene JSON. See [the contract](CONTRACT.md).

The available `film-paper` skin uses original visual styling. Crown, fonts,
icons and colors are art direction for the film. See the
[coverage map](COVERAGE.md) before describing motion as native.

## Use another renderer

Use the same compiled scene and change the output path per engine.

```sh
node scripts/engines/render.mjs --method html --scene /tmp/station.scene.json --out /tmp/station-html.mp4
node scripts/engines/render.mjs --method gsap --scene /tmp/station.scene.json --out /tmp/station-gsap.mp4
node scripts/engines/render.mjs --method remotion --scene /tmp/station.scene.json --out /tmp/station-remotion.mp4
node scripts/engines/render_motion_canvas.mjs --scene /tmp/station.scene.json --out /tmp/station-motion-canvas.mp4
```

Check consecutive decoded frames before, at and after the named action.
Resolve `scene.timeline` with Observer's `contracts/timeline.py` on its branch
or after integration. Sound can use the stable frame/sample anchors and link
each cue to a visible event in the exported picture.
