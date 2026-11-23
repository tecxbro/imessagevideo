# Sidehoe UI calibration

**Exact verdict is FAIL.** The revised editable Pillow export matches all 778
picture timestamps and the final hold. Zero frames match in decoded RGB.
The earlier review's scoped shot observations and the new exact gate answer
different questions. [Exact acceptance](acceptance.json)
· [Decoded comparison](final-comparison/report.json)
· [Recorded visual observations](final-visual-review.json)

[Revised MP4](final/sidehoe.mp4) · [Editable project](project/README.md)
· [Source and review plan](../repair-review/native/README.md)

| Native check | Earlier | Revised |
| --- | ---: | ---: |
| Frame 22 Wi‑Fi crop RGB error | 60.86 | 24.67 |
| Frame 327 outgoing bubble crop RGB error | 46.49 | 9.82 |
| Frame 327 keyboard letters crop RGB error | 31.15 | 15.48 |
| First entrance worst consecutive-frame RGB change error | 25.25 | 20.13 |
| Follow-up entrance worst consecutive-frame RGB change error | 18.99 | 16.56 |
| Entire film mean RGB error | 6.97 | 6.63 |

RGB error is mean absolute channel difference. The motion rows compare
signed change between adjacent decoded frames in the same crop. These are
diagnostics, with a zero-difference requirement for exact acceptance.

The revised Wi-Fi glyph has two curved bands and a filled sector. Keyboard
Shift, Delete, emoji-mode and dictation have individually drawn glyphs. The
bubble tail follows a curved silhouette, and the Yes chip uses a different
editable face drawing. Phone entrance poses use measured hull edges and a
separate keyboard-panel top on each observed frame.
[Measured entrance poses](handset-measurements.json)

- [Wi‑Fi, frame 22](final-comparison/crops/01-first.png)
- [Key rows, frame 327](final-comparison/crops/09-first.png)
- [Suggestion bubble, frame 341](final-comparison/crops/14-first.png)
- [Yes emoji, frame 670](final-comparison/crops/17-first.png)
- [First entrance, frames 334–335](final-comparison/crops/04-step.png)
- [Second entrance, frames 627–628](final-comparison/crops/15-step.png)

The suggestion still lacks the source's slight tilt. Font rasterization,
phone materials, emoji shading and blur remain visibly different. The small
icons now depict the right controls and still have different strokes. The
follow-up entrance still places the hull high in frames 627–628, and the
retreat lacks the source's stronger directional smear. All 24 shots remain
open under exact acceptance.

From the workspace root, use a fresh output folder and Python with Pillow
and NumPy. FFmpeg and ffprobe must be on PATH.

```sh
D=sidehoe-skill-trial/ui-repair
S=codex-trial/skill/imessage-motion-recreation/recreate
B=sidehoe-skill-trial/repair-review/native
REF=/Users/darshan/Downloads/sidehoe.mp4
TMP=$(mktemp -d)
"$D/project/export.sh" "$TMP/export" "$TMP/frames"
python3 "$S/recreate.py" compare "$REF" "$TMP/export/sidehoe.mp4" \
  --exact --crops --checks "$B/checks.json" --out "$TMP/comparison"
```
