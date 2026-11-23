# Editable contact thread

Select `"skin": "contact-thread"` for a light Messages-style thread with blue outgoing bubbles, neutral incoming bubbles, curved tails, an independently editable portrait, and three-dot typing. The conversation and event input still own the copy, sender, and timing. This is an original film appearance informed by measured interaction behavior. It has no qualified native iPhone or iOS build profile. Source-specific hardware and character likeness need their own approved artwork and evidence. [Design evidence and limits](../../../review/imv-v3/goal-audit/messages-ui.md)

## Run and edit the example

From `skill/imessage-motion-recreation`, use Python 3.11+, Pillow, fontconfig and DejaVu Sans regular/bold. Use the existing [renderer setup](../RUNNING.md).

```sh
python3 -m ui.adapter ui/examples/contact-thread.json --out /tmp/contact-thread.scene.json
python3 scripts/engines/render_pillow.py --scene /tmp/contact-thread.scene.json --out /tmp/contact-thread.mp4
python3 contracts/timeline.py /tmp/contact-thread.scene.json
```

The [example conversation](examples/contact-thread.json) opens a keyboard at frame 6, fills the draft at 14, sends at 34, starts Jamie’s typing at 52, changes camera at 62 and receives the reply at 86. Edit the draft/action frames or replace the original [fixture portrait](examples/assets/contact-thread-avatar.png), then rerun the same commands. Copy the input JSON and its referenced `assets` with any moved project and compile in the destination after font setup. The cue anchors resolve from picture events at 48 kHz. This example’s picture is silent.

`avatarAssetId` resolves a still in the existing `assets` map and crops it to a circle using cover. Omit it to display initials. Set `display.statusTime` to fixed visible copy. `display.handset` adds a stylized hardware body and separate aperture with an independently clipped display. A canvas with enough margin keeps the body visible during a camera move. Handset is off unless requested.

The optional `glyphAssets` map binds a complete Unicode grapheme to `{assetId, advance, ink}`. `advance` is the horizontal advance in em. `ink` is `[left, top, width, height]` in em relative to the glyph’s line-top pen position. At 16 px, `advance: 1.25` occupies 20 px. Provide an independently sourced local asset with approved use. The message state retains Unicode copy and the picture renders editable text runs around the positioned glyph. Platform-dependent fallback draws unconfigured glyphs, so region/state checks should verify each required glyph and avoid calling those pixels portable. Grouped participants, system-grade status icon variants, device-specific key labels, Memoji, and physical lighting all require additional independent evidence.

## Motion layer ownership

| Role | Layer IDs |
|---|---|
| Stage and silhouette | `ui.camera` moves `ui.handset` and `ui.screen`; `ui.handset` is optional. `ui.handset.rim`, `.aperture` and `.side-key` are individual shapes. |
| Screen and chrome | `ui.screen` clips the display. `ui.header`, `ui.header.status`, `ui.header.avatar`, `ui.footer` and `ui.footer.home` remain in display coordinates. Portrait artwork has its own `ui.header.avatar.image`. |
| Transcript and messages | `ui.viewport` clips `ui.transcript`; `ui.message/<id>` and its `/body`, `/receipt`, `/reaction`, `/media` and `/card` groups remain stable across state changes. Body revisions contain independently editable `.ink`, `.tail` when unjoined and `.copy` with editable runs. |
| Composer and keyboard | `ui.composer` moves independently of `ui.keyboard`; draft/plus/field/send or mic actors are frame-bounded component revisions. Stable `ui.keyboard.key.<name>` groups have individual key body and label. Keyboard geometry is stylized QWERTY. |
| Typing | `ui.typing` moves with the transcript. Address any of `ui.typing.dot.1`, `ui.typing.dot.2` and `ui.typing.dot.3`. Each resets its authored phase on a new typing interval and follows the picture clock across camera moves and seeks. |

Use the stable parent groups for motion presets. Component revisions suffix their new leaf IDs with the first frame of the revision. This prevents earlier edits from replacing a different visual state. Film-paper and film-ink remain available with their original appearance, and `film-paper` remains the default.
