# Sidehoe handset exit, title hearts, and badge outline

November 21, 2026. The [candidate MP4](candidate/sidehoe.mp4) was rendered
from a clean copy of the [editable project](project/README.md).

[Watch the source and recreation side by side](review/side-by-side.mp4) ·
[Inspect all 778 time-matched frames](review/native/index.html)

- Rebuilt the handset exit around separate metal and glass contours.
  The bevel reflection follows the curved corners. The time, status symbols,
  and Messages labels have separate vertical shutter treatments over the
  underlying glass tint. This pass covers all nine frames from 6.12 to 6.44 s.
- Fitted the left and right lobes and the notch of the floating hearts
  through the held title at frames 188–196. The title and hearts remain
  separate editable layers.
- Refined the closing profile badge’s outline over frames 701–711.
  Its three cards and heart still have visible differences at 28.24 s.

| Source time | Matched encoded crop | Previous mean RGB error | Revised mean RGB error |
| --- | --- | ---: | ---: |
| 6.12 s | [First revised case frame](review/focus/f153-first-casing-adjustment.png) | 4.07 | 3.72 |
| 6.32 s | [Moving shoulders and status](review/focus/f158-moving-shoulders-and-status.png) | 6.29 | 4.55 |
| 6.36 s | [Status streaks before the cut](review/focus/f159-refracted-status-before-cut.png) | 6.70 | 4.36 |
| 6.40 s | [Curved rim and status at 6.40 s](review/focus/f160-casing-and-shutter-streaks.png) | 6.98 | 4.43 |
| 6.44 s | [Last frame before the cut](review/focus/f161-last-phone-frame.png) | 3.58 | 2.66 |
| 7.68 s | [Title and floating hearts](review/focus/f192-attached-active-title-and-hearts.png) | 3.84 | 3.51 |
| 28.16 s | [Badge shoulders in motion](review/focus/f704-badge-shoulders-in-motion.png) | 2.86 | 2.26 |
| 28.24 s | [Profile badge](review/focus/f706-attached-profile-badge.png) | 2.24 | 2.03 |

The right shoulder retains a faint interior reflection at 6.40 s.
The source camera island is more defined and its status letters are
streaked more vertically. The title still has different ink edges at
7.68 s. In the closing badge, the artwork remains softer than the source.
Thirty of 32 adjacent-frame comparisons improved. The transitions
into frame 153 and out to frame 712 show a larger temporal difference.
[Adjacent-frame measurements](review/temporal-metrics.csv)
[Matched cut frames](review/focus/f161-last-phone-frame.png) ·
[First title frame](review/focus/f162-first-title-frame.png)

## Full export verdict

**Exact fidelity fails.** The mux decodes cleanly. All 778 frames have
identical presentation timestamps and exclusive end times at 2000 × 2000.
Mean RGB error moved from 2.4607 to 2.4524.
0 frames are pixel-identical. The last frame differs by 23 pixels.
The largest full-frame error is 4.141 at f152 (6.08 s).
[Exact verdict](review/native/report.json) ·
[All frame measurements](review/native/frames.csv) ·
[Highest-error frame](review/native/pairs/000152.jpg)

**HyperFrames 0.9.77 passed its visual thresholds** and matched all six cuts.
Mean SSIM moved from 0.9756 to 0.9757.
The pinned reviewer copy passed all 202 file checks.
[Official diff result](review/hyperframes.json) ·
[Ranked misses](review/hyperframes/worst.jpg) ·
[Reviewer source and license](../hyperframes-review/vendor/hyperframes/UPSTREAM.md)

All 29 affected lossless stage frames improved, and the other 749 matched
the previous render by hash. 29 of 29 improved in the encoded MP4.
The 48 kHz stems, event map, and AAC stream match the previous export by hash.
Each of 65 Motion crops was checked for region, timestamp, and file hash.
Six isolated edits verified independent control of the glass and metal
contours, rim lighting, clock streak, floating heart, and badge.
[Motion crops](review/motion/motion-observations.json) ·
[Lossless stage comparison](review/stage-metrics.json) ·
[Edit checks](review/editability.json) ·
[Previous review](../refraction-review/README.md)

Source SHA-256  
`f821bb58cbdb265a75d572616d0da723e9cfb6de31e3db5f8a17d94dc15b5327`

Candidate SHA-256  
`c740a4698ffb4b8598587163917ffa2c38209520f14d771a9398e6d46b2d2393`

## Rerun the comparison

Set `SOURCE` to the locked reference and use a fresh output folder.

```sh
PYTHON=/path/to/render-environment/bin/python \
HYPERFRAMES=/path/to/hyperframes \
bash review.sh "$SOURCE" "$PWD/candidate/sidehoe.mp4" "$PWD/review-rerun"

/path/to/render-environment/bin/python focus.py \
  "$SOURCE" ../refraction-review/candidate/sidehoe.mp4 \
  candidate/sidehoe.mp4 review-rerun/focus
```
