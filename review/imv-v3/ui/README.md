# Editable Messages film interface review

See the [standalone interaction sequences](sequences/README.md) for the three edited comparisons and the payment test mock.

The [station source](../../../skill/imessage-motion-recreation/ui/examples/conversation.json)
renders the same interaction through [Pillow](station-pillow.mp4),
[HTML/SVG](station-html.mp4), [GSAP](station-gsap.mp4),
[Remotion](station-remotion.mp4) and [Motion Canvas](station-motion-canvas.mp4).
Each silent export decoded all 136 frames at 402×874 and 24 fps. Its
[decoded before/action/after strip](station-pillow-consecutive.jpg) follows
send at f12, receive at f44, context at f53, reaction at f64, scroll at f80
and camera at f87. Remotion reported a browser-tab cleanup warning after
rendering. Its encoded file fully decoded.

[Field notes](../../../skill/imessage-motion-recreation/ui/examples/field-notes.json)
adds moving list/search, an independently pressed suggestion, a clipped
photo rail, a viewer, a poll vote and a long edit. Both the
[Pillow export](field-notes-pillow.mp4) and [HTML export](field-notes-html.mp4)
decoded 272 frames at 488×968 and 24 fps. The
[adjacent-frame strip](field-notes-pillow-consecutive.jpg) covers the action
boundaries. At f86 the “Use observation notes” control begins to dim in
place. At f130 the photo rail starts moving horizontally under the fixed thread header.
At f166 the viewer closes on a cut. At f220 new copy wraps in the same
outgoing row. The 402×874 logical screen fits inside the canvas at the
settled 1.08× camera scale.

The [send comparison](send-motion-trace.mp4) and
[long-press comparison](context-motion-trace.mp4) pair time-aligned native
geometry measurements against the film skin. Their JSON sidecars carry
source hashes and editable film inputs. The
[evidence ledger](../../../skill/imessage-motion-recreation/ui/EVIDENCE.md)
has the native versions, complete local paired comparison commands,
residual differences and missing captures.

## Checks

```sh
sha256sum -c SHA256SUMS
ffmpeg -v error -xerror -i station-pillow.mp4 -f null -
```

[Decoded results](decode-report.json) give dimensions, cadence, audio stream
count, file digest and the before-to-action pixel change for each tested
boundary. These measurements establish visible changes on the exported
clock. The adjacent-frame strips identify the visible changes.

The [Station event map](station.events.json) carries the reply's
`{"alex":"Love"}` reaction at f64. At f80 it retains the reaction and records
a 158 pt scroll offset after clamping to the available history. Composer
focus keeps the keyboard open through send. The
[Field notes event map](field-notes.events.json) records the attached photo
page at f130 and the persistent edit at f220. Sound's resolver independently
located the [Station send landmark](station-send-landmark.json) from the
composer button pixels at f12 / PTS 1/2 / sample 24000 with zero cue offset.

## Independent authoring

A fresh agent started with the UI skill. It authored a print-room interaction,
then changed it into a night survey with different participants, assets,
dimensions, cadence, dialogue and events. It changed descriptions and insert
artwork. The adapter generated the UI layers. The revised interaction rendered
through Pillow and HTML.

The exercise exposed second-frame movement on a reply cut and a viewer cut.
The final decoded [cut probes](cold-cuts.png) show both landing at their
declared frames. It exposed clipping during a camera push and text collision
behind a lifted quote. The canvas option supports framing margin, and the
target owns its backing during lift. The final
[long quote probe](cold-quote.png) retains readable text and an 18 px
outgoing gutter. The independent retest found no further defect in those
cases.
