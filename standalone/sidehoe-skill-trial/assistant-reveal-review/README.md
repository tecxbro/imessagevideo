# Sidehoe assistant reveal and calendar wipe review

November 21, 2026. The [candidate MP4](candidate/sidehoe.mp4) was rendered
from a clean copy of the [editable project](project/README.md).

[Watch side by side with the reference](review/side-by-side.mp4) ·
[Inspect all 778 time-matched frames](review/native/index.html)

## What changed

- Fitted the inbox’s scrolling message rows and pinned strip separately
  through f42–59. Their visible defocus and vertical positions now
  follow the source at the start and peak of the scroll.
- Fitted the full letterforms behind the assistant title’s reveal and
  reconstructed the lower line’s visible width during f135–151.
  Adjusted the camera opening, edge reflections, and the lighting and
  placement of the pinned portraits.
- Matched the departing calendar’s appointment bounds, grid and mosaic
  holes at f473–477. The cursor leaves before the last two partial
  calendar frames. The following ring arrival is available for comparison
  at f478.

| Source time | Encoded comparison | Previous mean RGB error | Revised mean RGB error |
| --- | --- | ---: | ---: |
| 1.88 s | [Inbox during the scroll](review/focus/f047-inbox-chrome-and-rows-during-scroll.png) | 4.48 | 3.68 |
| 5.40 s | [Handset glass refraction](review/focus/f135-assistant-upper-refraction.png) | 4.49 | 4.33 |
| 5.64 s | [Assistant title and pinned portraits](review/focus/f141-assistant-title-and-handset.png) | 4.50 | 4.05 |
| 5.76 s | [Two lines settling](review/focus/f144-assistant-two-lines-settling.png) | 5.44 | 2.13 |
| 18.92 s | [Cursor starts leaving the calendar](review/focus/f473-calendar-cursor-starts-departing.png) | 3.00 | 2.31 |
| 19.04 s | [Calendar mosaic](review/focus/f476-calendar-mosaic-and-cursor-clearance.png) | 4.25 | 1.57 |
| 19.08 s | [Last partially visible calendar cells](review/focus/f477-calendar-last-uncovered-cells.png) | 3.46 | 1.14 |
| 19.12 s | [Ring tile arrival](review/focus/f478-first-ring-tile.png) | 2.95 | 2.95 |

Each row uses the same frame and crop from the three encoded files.
The lower assistant line is closer in width and focus. Its baseline,
the lens highlights and the portrait expressions still differ. The
calendar cells are closer through the wipe. The day glyph edges and
first ring tile’s opacity still differ.
[Crop measurements](review/focus/metrics.csv) ·
[Independent edits from the clean project](review/editability.json)

The requested screenshot examples map most closely to f192 and f706.
The matched views show the remaining differences in the heart
silhouettes and the profile badge artwork.
[Title and hearts at 7.68 s](review/focus/f192-attached-active-title-and-hearts.png) ·
[Profile badge at 28.24 s](review/focus/f706-attached-profile-badge.png)

## Full export verdict

**Exact fidelity fails.** All 778 frames have identical presentation
timestamps and exclusive end times at 2000 × 2000 resolution. The mux
decodes cleanly. Mean full-film RGB error moved from
2.5698 to 2.5411.
0 frames are pixel-identical. The last frame differs by
23 pixels. The largest remaining full-frame error is 4.329
at f658 (26.32 s).
[Exact verdict](review/native/report.json) ·
[All frame measurements](review/native/frames.csv) ·
[Highest-error frame](review/native/pairs/000658.jpg)

**HyperFrames 0.9.77 passed its visual thresholds.** It matched all six cuts.
Mean SSIM moved from 0.9745 to 0.9748.
The pinned reviewer copy passed all 202 file checks.
[Official diff result](review/hyperframes.json) ·
[Ranked misses](review/hyperframes/worst.jpg) ·
[Reviewer copy and license](../hyperframes-review/vendor/hyperframes/UPSTREAM.md)

All 41 affected lossless frames improved and the other 737 matched the
previous render by hash. In the encoded MP4, 41 of the 41 affected
frames improved.
The 48 kHz stems, event map and AAC stream match the previous export
by hash. Motion supplied 55 native crops, verified by
timestamp, region and hash.
[Source observations](review/motion/motion-observations.json) ·
[Stage measurements](review/stage-metrics.json) ·
[Previous export review](../sofia-handoff-review/README.md)

Source SHA-256  
`f821bb58cbdb265a75d572616d0da723e9cfb6de31e3db5f8a17d94dc15b5327`

Candidate SHA-256  
`dc5173a4861bb86a4901d00eb95553d08fd1855da4f5ed793a7143bd85158eef`

## Rerun the comparison

Set `SOURCE` to the locked reference and use a fresh output folder.

```sh
PYTHON=/path/to/render-environment/bin/python \
HYPERFRAMES=/path/to/hyperframes \
bash review.sh "$SOURCE" "$PWD/candidate/sidehoe.mp4" "$PWD/review-rerun"

/path/to/render-environment/bin/python focus.py \
  "$SOURCE" ../sofia-handoff-review/candidate/sidehoe.mp4 \
  candidate/sidehoe.mp4 review-rerun/focus
```
