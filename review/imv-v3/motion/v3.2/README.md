# Motion v3.2 selector and photo comparison proof

The [test output](selector-tests.txt) and [decoded measurements](decoded-measurements.json) were generated from an extract of Observer’s portable v3.2.0 skill with this Motion patch and its bundled inputs applied. Render inputs are under `motion/examples/` inside the skill. See [the photo comparison](../../../../skill/imessage-motion-recreation/motion/PHOTO-SWIPE.md) for the editable recipes, exact preview commands, event IDs and evidence limits.

A clean extraction of a locally rebuilt test ZIP passed all 68 tests and reproduced all five preview MP4s byte for byte. The render used the package’s Pillow engine and current Clone iMessage UI adapter.

With the UI directory replaced at `f54b400` and `ce1b5bd`, all four adapter tests passed at each pin and the sequence proof reproduced all 22 entries in UI’s checksum file. The focused send-and-page retained its Motion preview hash at both pins. The inline rail retained its preview hash at `f54b400`. [Pinned UI sequences](https://github.com/tecxbro/imessagevideo/tree/ce1b5bd13c893c117fb894d16152d63d1a11146b/review/imv-v3/ui/sequences) · [Independent UI replay](https://github.com/tecxbro/imessagevideo/issues/7#issuecomment-7052813303)

## Reproduce the counter

From the portable directory containing `motion/`, run:

```sh
out=$(mktemp -d)
node --test motion/tests/*.test.mjs
node motion/cli.mjs select --brief "Leave the snapshots pinned while the title travels over them"
node motion/cli.mjs render --brief "Leave the snapshots pinned while the title travels over them" \
  --out "$out/heading.mp4"
node motion/cli.mjs select --brief "Show a count climb to the real total then give the statistic time to read"
node motion/cli.mjs render --brief "Show a count climb to the real total then give the statistic time to read" \
  --content motion/examples/metric-hold.json --out "$out/metric-hold.mp4"
```

The selector retrieves `heading-over-fixed-photos` and `metric-count` respectively. The counter brief leaves endpoints to the supplied [content file](../../../../skill/imessage-motion-recreation/motion/examples/metric-hold.json). A subsequent push-in remains a separate sequence beat, including when the request also mentions reading time.

Both commands were also replayed with the patched Motion directory in Observer’s v3.2.1 two-ZIP extraction. The heading replay matches the published heading preview SHA-256 `eb0b16aa32336f42b04cc2ef00abcb967f13d577587edf0f1b1aa270b90fe3cf`, with onset f20 and settle f51. Observer and Clone iMessage UI separately reran the selector cases and reproduced the count MP4. [Observer rerun](https://github.com/tecxbro/imessagevideo/issues/7#issuecomment-7052737345) · [UI rerun](https://github.com/tecxbro/imessagevideo/issues/7#issuecomment-7052742468)

The [counter MP4](metric-hold.mp4) is 720 × 480 with 72 decoded frames at 30 fps. The [editable scene](metric-hold.scene.json) and [event map](metric-hold.events.json) record `motion.metric-count.count-begins` at f10 and `motion.metric-count.final-value-held` at f55. The decoded counter reads 86 at f9, 88 at f10 and 2,142 at f54. OCR returns 2,147 on every frame from f55 through f71. The maximum mean change in the held value crop is 0.01092 RGB levels. [Decoded frames](metric-hold-frames.png)

## Photo preview comparison

| Preview | Event map | Decoded checkpoints |
| --- | --- | --- |
| [Venue rail](venue-rail.mp4) | [Events](venue-rail.events.json) | [Frames](venue-rail-frames.png) |
| [Overlapping attachment stack](attachment-stack.mp4) | [Events](attachment-stack.events.json) | [Frames](attachment-stack-frames.png) |
| [Inline rail via Clone iMessage UI](conversation-rail.mp4) | [Events](conversation-rail.events.json) | [Frames](conversation-rail-frames.png) |
| [Send, page, open, and return via Clone iMessage UI](photo-swipe.mp4) | [Resolved events](photo-swipe.events.json) | [Frames](photo-swipe-frames.png) |

The first three clips are 720 × 480 with 72 decoded frames at 30 fps. The send-and-page clip is 402 × 874 with 84 decoded frames at 24 fps. Its source is the portable [editable UI recipe](../../../../skill/imessage-motion-recreation/motion/examples/photo-swipe.ui.json).

Recreation changed the opening question and moved the page event from f32 to f37. The new clip kept its top 100 rows pixel-identical during the swipe boundary. Its SHA-256 is `c878ed7d207848aa6d6c879895b0110a82c214de0fe70714a35df5651a642c7d`. [Recreation reuse](https://github.com/tecxbro/imessagevideo/issues/7#issuecomment-7052752832)

Run `sha256sum -c SHA256SUMS` in this directory to check the committed artifacts.
