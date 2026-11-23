---
name: imessage-film-interface
description: Author editable Messages-style interaction for films with one shared scene contract and five renderer routes.
---

# Messages film interface

Use this kit when a shot needs a Messages-style conversation, its surrounding
surfaces, or a camera move over an editable interaction. First decide who acts,
which message or control the action changes, and the frame where it starts.
Give repeated actions separate event IDs and keep those IDs when editing the
copy, camera or timing.

## Start with a conversation

Copy [the station conversation](examples/conversation.json) for text, send,
typing, reaction and scroll. Copy [the field-notes conversation](examples/field-notes.json)
with its assets for search, suggestion, multi-photo paging, a viewer and a
poll. Use the [content and state contract](CONTRACT.md) to choose event kinds.
Choose `film-paper` for plum/lavender bubbles or `film-ink` for blue/gray.
Both share the same authored screen geometry and state.

For isolated interactions, start with [send with keyboard up](examples/send-keyboard.json),
[Tapback and scroll](examples/tapback-scroll.json), or [in-thread photo swipe](examples/photos-fixed-header.json).
Each has an edited input and decoded evidence in the
[sequence kit](../../../review/imv-v3/ui/sequences/README.md). For payment
storyboarding, the [test mock](examples/payment-mock.json) separates the
approval overlay from the inline card and its simulated result.

Run from `skill/imessage-motion-recreation` with Python 3.11+, Pillow,
fontconfig and DejaVu Sans regular and bold. Install the
[renderer requirements](../RUNNING.md) for the route you want.

```sh
python3 -m ui.adapter ui/examples/conversation.json --out /tmp/station.scene.json
python3 scripts/engines/render_pillow.py --scene /tmp/station.scene.json --out /tmp/station.mp4
```

Expect a silent 402×874 picture, 136 frames at 24 fps. Send clears the draft
at frame 12 and the reply starts at 44. Context starts at 53. A reaction
attaches to the reply at 64. Scroll starts at 80 and the camera starts at 87.

For Python, import `compile_conversation` from `ui.adapter`. Pass a
description dictionary and input and output directories for image path
resolution. Editors using Node or shell can call the CLI and reuse the exact
output scene. Edit the description and compile again to regenerate wrapping,
extent, attachment placement and frame anchors.

## Match a recreation shot

Use the adapter for the supported conversation states, layer ownership and
event anchors. The default palettes, type and geometry are starter designs.
Set measured properties where the adapter exposes them and adapt the editable
components or scoped layers for the rest. Keep wrap, clipping, event targets
and state transitions linked to the edited geometry. Author handset materials,
portraits and product-specific control artwork separately when needed. Record
unsupported surfaces and their editable replacements. Measure each component
from the approved source with the [native interface guide](../recreate/UI-FIDELITY.md).
Compare the assembled shot using the
[recreation visual review](../recreate/VISUAL-REVIEW.md) on each required export.

## Frame a shot

Set `display` to the logical interface size. The `canvas` sets the movie
size and provides margin around the screen. For example, a 402×874 display on a
488×968 canvas can push to 1.08× around screen center while retaining the
whole interface. Use camera x/y offsets to select a crop on purpose. Camera
changes move the entire screen, while `scroll` and `media.page` stay inside
their own clips.

A cue follows a visible event. Check the decoded frame before, at and after
each action. Recheck the edited output if text wraps differently, if you
replace media, or if the camera covers a control. Use the
[coverage map](COVERAGE.md) and [evidence ledger](EVIDENCE.md) for supported
behaviors, native comparisons and open evidence.

## Export with another renderer

Pass the same scene to any of the following.

```sh
node scripts/engines/render.mjs --method html --scene /tmp/station.scene.json --out /tmp/station-html.mp4
node scripts/engines/render.mjs --method gsap --scene /tmp/station.scene.json --out /tmp/station-gsap.mp4
node scripts/engines/render.mjs --method remotion --scene /tmp/station.scene.json --out /tmp/station-remotion.mp4
node scripts/engines/render_motion_canvas.mjs --scene /tmp/station.scene.json --out /tmp/station-motion-canvas.mp4
```

Use `python3 contracts/timeline.py /tmp/station.scene.json` to resolve the
shared event and cue map. If the Observer branch has yet to be integrated,
run these commands from the skill directory to get its resolver locally.

```sh
git fetch origin refs/heads/codex-video-v3/observer
git show FETCH_HEAD:skill/imessage-motion-recreation/contracts/timeline.py > /tmp/imv-timeline.py
python3 /tmp/imv-timeline.py /tmp/station.scene.json
```

The event `station.send` resolves to frame 12 and audio sample 24000 at
48 kHz. The [review exports](../../../review/imv-v3/ui/README.md) document
decoded checks and hashes. The [source audit](SOURCES.md) records the pinned
references and their reuse terms.
