# Sidehoe recreation trials

November 21, 2026. The authorized Sidehoe source has SHA-256
`f821bb58cbdb265a75d572616d0da723e9cfb6de31e3db5f8a17d94dc15b5327`.
I ran the current Recreation route, independently staged the editable project
and rebuilt its 778 picture frames and score. The completed baseline matches
the earlier export byte for byte. [Existing project](../../../../sidehoe-skill-trial/ui-repair/project/README.md) ·
[Measured results](sidehoe-verification.json)

## The Messages-to-calendar handoff

REA Video divides this source into nine macroshots. HyperFrames flags frame
401 as a cut. The native frames share visible elements over the interval.
Outgoing bubbles move upward while their opacity falls and the calendar
appears independently. The current authoring had two pose anchors and used
linear interpolation. The existing review called for checking intermediate
frames, so this is an execution error in applying the Recreation workflow.

| Controlled change | Observed result |
| --- | --- |
| Replace the interpolated bubble poses with measured native intermediate poses | Five of six changed frames improve. Frame 402 worsens, isolating an additional visibility discrepancy. |
| Keep the measured poses and fit the fade independently | All six target frames improve. Native ROI mean RGB error at frame 399 falls from 27.213 to 11.185, frame 400 from 22.150 to 8.516, and frame 402 from 6.498 to 5.284. |
| Rerender and mux all 778 frames using the same renderer | Exactly frames 397–402 change in the lossless cache. All three audio stems are byte-identical. Both exports pass the decoded clock, including the ending. The mean whole-film error moves from 6.6343 to 6.6097. Both exact comparisons fail with zero RGB-identical frames. |

The [Motion extraction command](../../../skill/imessage-motion-recreation/motion/WORKFLOW.md#extract-source-motion)
records this as source evidence on the native clock. With RGB `[18,196,250]`,
tolerance 17, and crop `[640,70,1290,1070]`, it returns matches on frames
396–399 and unobserved samples on 400–403. It preserves the per-frame crops
and timestamps. The subsequent fade fit uses separate evidence and keeps the
color threshold's early disappearance distinct from the actor's lifetime.

## Glyph identity and placement

Sidehoe's calendar drew placeholder ovals and a flat cat. Substituting local
system glyphs at the placeholder placement worsened the aubergine/drops crop
from 25.651 to 28.698. In a second experiment, I measured independently bounded
ink placement and size on frames 426, 435, 450 and 470, then rendered the
same emoji identities with those dimensions through Pillow. The experiment
keeps system font data local. [Initial glyph comparison](messages-ui.md#controlled-glyph-probe)

| Frame | Region | Original → calibrated lossless RGB error |
| --- | --- | --- |
| 435 | Aubergine and droplets | 30.625 → 12.944 |
| 435 | Cat | 21.180 → 9.645 |
| 440, held out of calibration | Aubergine and droplets | 26.496 → 23.286 |
| 440, held out of calibration | Cat | 29.189 → 24.700 |
| 450 | Aubergine and droplets | 31.090 → 16.132 |

These crops use the recorded boxes in `sidehoe-verification.json`. The glyph
fit uses five sampled frames, with one held out. Candidate signals include the calendar's
changing background, so the residual mixes underlying box motion, type
placement, and glyph appearance. I then rendered all 85 calendar frames
using the calibrated glyph treatment and encoded the full film. Only frames
397–481 change in the lossless cache against the motion-only candidate. The
audio stems are byte-identical. I recalibrated the local offsets under the
frozen project's Python 3.15.2, Pillow 13.0.0 and NumPy 2.5.5 environment after
the first local runtime differed in 4,243 pixels on the otherwise unedited
f435 control. All eight encoded sample regions improve in the same-runtime
comparison, including the f435 aubergine/droplets crop from 28.55 to 12.31
and the held-out f440 cat from 29.76 to 21.99.

The combined 778-frame mux passes the decoded clock and the ending. Its
overall RGB error is 6.6081. Exact source fidelity still fails at zero
identical frames. Native iOS font version, exact avatar pose and residual
calendar appearance are open. The [numeric file](sidehoe-verification.json)
binds the probes to the candidate and records the exact scope.

## Tile and handset

A Y-only correction improves the blue tile's first five tested frames
after registration. The silhouette and face lighting remain visibly
different. The source is essentially clear of the tile at f621, while the
existing final mux retains a coherent blue region. [Native tile trial](sidehoe-tile.md)

The follow-up handset's dark rails track within a 1.5 px median while their
edge lighting makes the frame appear wider. An independently tracked pointer
reduces mean tip error from 10.05 to 0.87 px in the lossless output. The
pointer's silhouette, defocus and separation from the moving Yes chip are
still wrong. These differences were measured before encoding. The tile and
handset alternatives were each rendered as independent diagnostic passages.
[Native handset and cursor trial](sidehoe-follow-native.md)
