# Sidehoe native-pixel review

The earlier review passed some shot criteria when a button appeared or a
pointer landed, even where surrounding bubbles and glyphs differed. At frame
327, the old render used missing-font fallback boxes for both keyboard icons.
At frame 341, the suggestion's tail was a disconnected triangle. At frame 670,
the Yes emoji was a different drawing. These are separate review tasks in the
new plan. [Frozen historical plan](../review-plan.json)
· [Native review plan](review-plan.json)

Original supplied locally at `/Users/darshan/Downloads/sidehoe.mp4`.
The decoded raster is 2000 by 2000, with 778 frames and a 25 fps clock.
The reference SHA-256 is
`f821bb58cbdb265a75d572616d0da723e9cfb6de31e3db5a17d94dc15b5327`.
Both the old repair and the UI calibration are compared to the same source
and use the same [19 inspection regions](checks.json).
[Revised Sidehoe comparison and verdict](../../ui-repair/README.md)

- [Old Wi-Fi crop, frame 22](comparison/crops/01-first.png)
- [Old keyboard emoji-mode crop, frame 327](comparison/crops/11-first.png)
- [Old suggestion bubble crop, frame 341](comparison/crops/14-first.png)
- [Old Yes emoji crop, frame 670](comparison/crops/17-first.png)

Each crop reads source, export, and pixel difference from left to right.
The motion strips use a previous and current row with source left and export
right. [Full old-export comparison](comparison/report.json)

## Shared renderer check

The editable `ui/examples/send-keyboard.json` scene rendered through all five
routes. The HTML/SVG render served as the comparison reference for this
fixture. It tests interoperability of the renderer output and the exact gate.

| Renderer | Identical decoded frames | Mean RGB channel error |
| --- | ---: | ---: |
| HTML/CSS/SVG | 68/68 | 0 |
| GSAP | 68/68 | 0 |
| Remotion | 68/68 | 0 |
| Motion Canvas | 0/68 | 0.2765 |
| Pillow/FFmpeg | 0/68 | 2.9914 |

All five exports matched the fixture's 68 frame timestamps and final hold.
The Sidehoe calibration is a separate Pillow project.
[Renderer evidence](renderer-matrix.json)
· [Reusable native component measurements](../../../codex-trial/skill/imessage-motion-recreation/recreate/UI-FIDELITY.md)
