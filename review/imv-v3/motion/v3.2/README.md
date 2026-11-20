# Motion v3.2 selector and photo comparison proof

The [test output](selector-tests.txt) and [decoded measurements](decoded-measurements.json) were generated from an extract of Observer’s portable v3.2.0 skill with this Motion patch and its bundled inputs applied. Render inputs are under `motion/examples/` inside the skill. See [the photo comparison](../../../../skill/imessage-motion-recreation/motion/PHOTO-SWIPE.md) for the editable recipes, exact preview commands, event IDs and evidence limits.

A clean extraction of a locally rebuilt test ZIP passed all 68 tests and reproduced all five preview MP4s byte for byte. The render used the package’s Pillow engine and current Clone iMessage UI adapter.

## Reproduce the counter

From the portable directory containing `motion/`, run:

```sh
out=$(mktemp -d)
node --test motion/tests/*.test.mjs
node motion/cli.mjs select --brief "Leave the snapshots pinned while the title travels over them"
node motion/cli.mjs select --brief "Show a count climb to the real total then give the statistic time to read"
node motion/cli.mjs render --brief "Show a count climb to the real total then give the statistic time to read" \
  --content motion/examples/metric-hold.json --out "$out/metric-hold.mp4"
```

The selector retrieves `heading-over-fixed-photos` and `metric-count` respectively. The counter brief leaves endpoints to the supplied [content file](../../../../skill/imessage-motion-recreation/motion/examples/metric-hold.json). A subsequent push-in remains a separate sequence beat, including when the request also mentions reading time.

The [counter MP4](metric-hold.mp4) is 720 × 480 with 72 decoded frames at 30 fps. The [editable scene](metric-hold.scene.json) and [event map](metric-hold.events.json) record `motion.metric-count.count-begins` at f10 and `motion.metric-count.final-value-held` at f55. The decoded counter reads 86 at f9, 88 at f10 and 2,142 at f54. OCR returns 2,147 on every frame from f55 through f71. The maximum mean change in the held value crop is 0.01092 RGB levels. [Decoded frames](metric-hold-frames.png)

## Photo preview comparison

| Preview | Event map | Decoded checkpoints |
| --- | --- | --- |
| [Venue rail](venue-rail.mp4) | [Events](venue-rail.events.json) | [Frames](venue-rail-frames.png) |
| [Overlapping attachment stack](attachment-stack.mp4) | [Events](attachment-stack.events.json) | [Frames](attachment-stack-frames.png) |
| [Inline rail via Clone iMessage UI](conversation-rail.mp4) | [Events](conversation-rail.events.json) | [Frames](conversation-rail-frames.png) |
| [Send, page, open, and return via Clone iMessage UI](photo-swipe.mp4) | [Resolved events](photo-swipe.events.json) | [Frames](photo-swipe-frames.png) |

The first three clips are 720 × 480 with 72 decoded frames at 30 fps. The send-and-page clip is 402 × 874 with 84 decoded frames at 24 fps. Its source is the portable [editable UI recipe](../../../../skill/imessage-motion-recreation/motion/examples/photo-swipe.ui.json).

Run `sha256sum -c SHA256SUMS` in this directory to check the committed artifacts.
