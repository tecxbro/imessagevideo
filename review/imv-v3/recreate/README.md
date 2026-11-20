# Recreation review

[Train options](train/) is a complete authored development fixture and independent editable rebuild. The silent final picture is `train/final.mp4`; its events are in `train/final.events.json`. [Editable source and commands](../../../skill/imessage-motion-recreation/recreate/example/README.md)

| Export | Decoded result |
| --- | --- |
| First | 120 of 120 pictures. Whole-frame gate passed. Seat selection fails on 74–77. |
| Final | 120 of 120 pictures, exact measured clock through 4 seconds. All six local windows pass. Mean RGB channel error is 0.02963 on a 0–255 scale. |
| Truncated test against the final master | 110 paired frames with zero RGB error. Gate fails for frames 110–119 missing, a short final hold, and an unscanned last-hold window. |
| Edited | Real copy changes from “Two seats to Union Station.” to “Two seats to Northgate.” and the first selected frame moves from 74 to 69. |

The repair changed only native frames 74–77 and retained 116 PNGs byte for byte. The complete final encode was compared again. The isolated output matches the final file SHA-256. Refer to the [full-frame result](train/final-check/report.json), [native repair and edit](train/repair-and-edit.json) and [independent adversarial suite](qa/suite.json). This evidence uses decoded frames and audio measurements.

[Poke](poke/README.md) is a measured source passage for Direction and Motion, along with a complete comparison of the archived original and silent GSAP master. It is separate from the Train reconstruction.

The [portrait companion](ui/train-proof.json) uses the Clone iMessage UI adapter. It was rendered before and after the text and timing edit. Its visual treatment differs from the landscape fixture. [UI compiler and reproduction](../../../skill/imessage-motion-recreation/recreate/example/README.md)

The [variable frame clock probe](clock/README.md) applied 126 exact source timestamps to separately authored frames. The [Motion handoff](motion/README.md) verifies an editable asset swap in the motion library.

The [scored final](train/scored.mp4) and [scored edit](train/edited-scored.mp4) preserve the decoded pictures. The score is independently authored, and its four cue stems and decoded timing evidence are [included](train/sound/README.md). A [full source audit](library/source-clocks.json) records the native clocks and audio sample counts of the six existing library films, totaling 7,680 decoded source frames.
