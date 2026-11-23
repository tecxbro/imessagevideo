# Sidehoe tile orbit and Sofia’s suggestion

November 21, 2026. The [candidate MP4](candidate/sidehoe.mp4) was rendered
from a clean copy of the [editable project](project/README.md).

[Watch source and recreation side by side](review/side-by-side.mp4) ·
[Inspect all 778 time-matched frames](review/native/index.html)

- Registered the red flame, dark glyph, overlapping rings, and blue
  calendar tile independently over frames 483–621. Their positions,
  proportions, depth of focus, and coverage remain editable.
- Fitted the outlines and tint of Sofia’s reply and suggestion over
  frames 340–346. The edited outline and live text each have a
  measured slope and brightness.

| Source time | Matched encoded crop | Previous mean RGB error | Revised mean RGB error |
| --- | --- | ---: | ---: |
| 13.60 s | [First revised suggestion](review/focus/f340-first-suggestion-fit.png) | 4.69 | 2.94 |
| 13.68 s | [Sofia’s suggestion and live text](review/focus/f342-sofia-suggestion-lettering.png) | 4.77 | 3.47 |
| 19.32 s | [First revised orbit frame](review/focus/f483-first-registered-orbit-frame.png) | 5.40 | 3.25 |
| 19.44 s | [Four independent tile positions](review/focus/f486-four-independent-tiles.png) | 5.36 | 2.89 |
| 22.28 s | [Rings cross forward](review/focus/f557-ring-tile-shift-and-focus.png) | 8.17 | 2.37 |
| 23.00 s | [Curved 31 tile beside the rings](review/focus/f575-calendar-and-ring-tiles.png) | 7.32 | 2.33 |
| 24.68 s | [Tiles descend](review/focus/f617-tile-descent-exposure.png) | 6.04 | 2.93 |
| 24.84 s | [Last tile streak](review/focus/f621-last-visible-tile-streak.png) | 5.13 | 3.75 |

Of the 150 adjacent-frame comparisons, 144 improved. All ten
measured steps around the suggestion improved. The six regressions
are in the tile orbit at frames 505, 515, and 522–525.
At 13.68 s the suggestion lettering is still softer than the
reference. At 22.28 s the ring outline and purple reflection
still differ.
[Adjacent-frame measurements](review/temporal-metrics.csv)

[Title and hearts at 7.68 s](review/focus/f192-attached-title-and-hearts.png) ·
[First 31 tile at 19.16 s](review/focus/f479-calendar-31-tile-arrival.png) ·
[Cursor contact at 27.00 s](review/focus/f675-cursor-contact.png) ·
[Profile badge at 28.24 s](review/focus/f706-attached-profile-badge.png)

## Full export verdict

**Exact fidelity fails.** The mux decodes cleanly. All 778 frames have
matching presentation timestamps and exclusive end times at 2000 × 2000.
Mean full-film RGB error moved from 2.4365 to 2.2244.
0 frames are pixel-identical. The last frame differs by 23 pixels.
The largest full-frame error is 3.990 at f330 (13.20 s).
[Exact verdict](review/native/report.json) ·
[All frame measurements](review/native/frames.csv) ·
[Highest-error frame](review/native/pairs/000330.jpg)

**HyperFrames 0.9.77 passed its visual thresholds** and matched all six cuts.
Mean SSIM moved from 0.9759 to 0.9778.
The pinned reviewer copy passed all 202 file checks.
[Official diff result](review/hyperframes.json) ·
[Ranked misses](review/hyperframes/worst.jpg) ·
[Reviewer source and license](../hyperframes-review/vendor/hyperframes/UPSTREAM.md)

All 146 affected lossless frames improved, and the other 632 match
the previous stage render by hash. 146 of 146 improved in the encoded MP4.
The 48 kHz stems, event map, and AAC stream match the previous export by hash.
Each of 60 Motion source crops was checked for region, timestamp, and hash.
Six isolated edits verified separate control of ring position,
calendar height, dark-glyph focus, bubble slope, and live text.
[Motion crops](review/motion/motion-observations.json) ·
[Stage comparison](review/stage-metrics.json) ·
[Edit checks](review/editability.json) ·
[Previous review](../keyboard-exposure-review/README.md)

Source SHA-256  
`f821bb58cbdb265a75d572616d0da723e9cfb6de31e3db5f8a17d94dc15b5327`

Candidate SHA-256  
`5bfb7d75b3edb2c28afe8ede4a0c9682b38159dbb8ca824cbbe96010aba60962`

## Rerun the comparison

Set `SOURCE` to the locked reference and use a fresh output folder.

```sh
PYTHON=/path/to/render-environment/bin/python \
HYPERFRAMES=/path/to/hyperframes \
bash review.sh "$SOURCE" "$PWD/candidate/sidehoe.mp4" "$PWD/review-rerun"

/path/to/render-environment/bin/python focus.py \
  "$SOURCE" ../keyboard-exposure-review/candidate/sidehoe.mp4 \
  candidate/sidehoe.mp4 review-rerun/focus
```
