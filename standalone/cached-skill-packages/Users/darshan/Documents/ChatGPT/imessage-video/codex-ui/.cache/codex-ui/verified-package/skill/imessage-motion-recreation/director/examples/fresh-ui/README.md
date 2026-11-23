# Saturday plant swap

This independent assembly trial on 2026-11-18 follows two fictional neighbors, Mara Ortiz and Nico Park. Nico types and sends a reply, then shares a photo of his cuttings. Mara sends a wayfinding photo and Nico reacts as the camera settles on the exchange.

The example imports `Conversation` and `CameraRig` from the public component module. The component kit supplies the transcript, avatars, bubbles, composer, single-photo rows, reaction, clips and camera group. The example supplies the copy, people, assets and timing. The send event uses the authored draft as its message body. Both JPEGs are embedded in the generated scene so the JSON can render from any directory. [Scene](scene.mjs) · [Component contracts](../../component-contracts.md)

## Render

Run from the skill directory with the pinned dependencies installed. Set `CHROME_PATH` to an installed browser when required by the host. [Renderer setup](../../../RUNNING.md)

```sh
node director/examples/fresh-ui/scene.mjs > /tmp/plant-swap.json
node scripts/engines/render.mjs --method gsap --scene /tmp/plant-swap.json --out /tmp/plant-swap.mp4
```

The reviewed checkout copy is `film-trials/codex-ui/previews/fresh-assembly.mp4`. FFprobe counted 270 H.264 video frames at 960 × 540 and 30 fps, for a nine-second silent export. FFmpeg decoded the entire file without errors.

## Frame review

| Frame at 30 fps, starting from zero | Observed in the exported MP4 |
| --- | --- |
| 0 | Mara's name, custom initials and opening question establish the thread. |
| 98–101 | The draft and active send arrow are visible at 98. The composer clears at 99 as the outgoing bubble enters, and the sprout emoji is legible in the bubble at 101. |
| 129 | The pothos photo settles at the right with the jar and roots visible. |
| 168–176 | The yellow table photo rises into the thread as older rows advance behind the fixed header. |
| 176–210 | The viewport pans and scales up 8% as a unit. The header, transcript and composer retain their relationship. |
| 229–260 | The thumbs-up stays attached to the yellow-table photo through the reading hold. |

The first assembly used a wide `photo-strip` row for each still. The default crop cut off some roots, and the final scroll left part of the blue message visible under the header. The documented `photo-attachment` with a 192 × 144 box preserves the 4:3 photo at arrival. A taller viewport and revised camera keys keep the final reply, photo and reaction legible as the older text leaves the frame. The final framing trims the viewport's outer edge and a few pixels of the older photo.

## Photo provenance

Both images were created for this trial with OpenAI's built-in image generation tool and encoded as 760 × 570 JPEGs. The subjects and location are fictional.

- The pothos image used the prompt “Create one horizontal 4:3 candid phone photo for an ordinary private text conversation about a neighborhood plant swap. Close view of a small clear glass jam jar with three pothos cuttings growing thin roots in water, sitting next to a chipped cream windowsill. Natural cloudy morning sidelight. No faces or hands, text, logos, borders or collage. Quiet, imperfect phone camera look, real textures and plausible plant anatomy. Keep the cuttings and jar legible when the photo is displayed as a small message thumbnail.” [Pothos photo](assets/pothos.jpg)
- The yellow table image used the prompt “Create one horizontal 4:3 candid phone photo someone would send a friend to find a neighborhood plant-swap table. At a shaded local community garden, a folding table covered in a plain lemon-yellow cotton cloth with a scattering of little nursery pots and paper seed envelopes. Handheld frame from an outdoor path, close enough that the yellow table is recognizable in a small thumbnail. Slightly imperfect natural phone exposure, soft late-morning light. No people, signs, readable text, logos, collage or border.” [Yellow table photo](assets/yellow-table.jpg)
