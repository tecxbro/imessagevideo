# Sidehoe Sofia handset casing and orbit continuity

November 21, 2026. The [candidate MP4](candidate/sidehoe.mp4) was rendered
from a clean copy of the [editable project](project/README.md).

[Watch source and recreation side by side](review/side-by-side.mp4) ·
[Inspect all 778 time-matched frames](review/native/index.html)

- Rebuilt the metal and glass contours around Sofia’s handset. Fitted
  the light around the four corners and measured the side controls
  as independent parts.
- Registered the moving composer, mic, and attachment control.
  The gray Messages history and the keyboard lettering remain live.
- Refined the tile movement where the earlier orbit pass regressed.
  All six previous regressions now score better than the pre-orbit
  export in the original encoded crop.

| Source time | Matched encoded crop | Previous mean RGB error | Revised mean RGB error |
| --- | --- | ---: | ---: |
| 12.76 s | [First fitted case](review/focus/f319-first-fitted-case.png) | 5.69 | 4.27 |
| 13.00 s | [Casing and composer in motion](review/focus/f325-case-and-composer-moving.png) | 5.30 | 4.36 |
| 13.20 s | [Sofia’s handset and composer](review/focus/f330-sofia-casing-and-composer.png) | 7.23 | 4.91 |
| 13.32 s | [Bottom corners during the push](review/focus/f333-last-visible-bottom-case.png) | 6.04 | 4.84 |
| 13.44 s | [Independent key lettering](review/focus/f336-keyboard-ink-as-the-phone-grows.png) | 4.50 | 3.46 |
| 13.68 s | [Closest Sofia Messages frame](review/focus/f342-sofia-messages-at-closest-approach.png) | 3.79 | 3.33 |
| 20.20 s | [First corrected tile transition](review/focus/f505-first-orbit-continuity-change.png) | 3.02 | 2.91 |
| 20.88 s | [Overlapping tiles](review/focus/f522-overlapping-tiles-track-the-source.png) | 2.88 | 2.82 |

All 40 adjacent-frame comparisons improved in the checked passages.
At 13.20 s the status bar and camera island still sit higher than the
source, and the keyboard footer still differs in scale and detail.
[Adjacent-frame measurements](review/temporal-metrics.csv) ·
[Original six orbit regressions](review/orbit-regression-closure.csv)

[Title and hearts at 7.68 s](review/focus/f192-attached-title-and-hearts.png) ·
[First 31 tile at 19.16 s](review/focus/f479-calendar-31-tile-arrival.png) ·
[Cursor contact at 27.00 s](review/focus/f675-cursor-contact.png) ·
[Profile badge at 28.24 s](review/focus/f706-attached-profile-badge.png)

## Full export verdict

**Exact fidelity fails.** The mux decodes cleanly. All 778 frames have
matching presentation timestamps and exclusive end times at 2000 × 2000.
Mean full-film RGB error moved from 2.2244 to 2.2056.
0 frames are pixel-identical. The last frame differs by 23 pixels.
The largest full-frame error is 3.839 at f152 (6.08 s).
[Exact verdict](review/native/report.json) ·
[All frame measurements](review/native/frames.csv) ·
[Highest-error frame](review/native/pairs/000152.jpg)

**HyperFrames 0.9.77 passed its visual thresholds** and matched all six cuts.
Mean SSIM moved from 0.9778 to 0.9780.
The pinned reviewer copy passed all 202 file checks.
[Official diff result](review/hyperframes.json) ·
[Ranked misses](review/hyperframes/worst.jpg) ·
[Reviewer source and license](../hyperframes-review/vendor/hyperframes/UPSTREAM.md)

All 36 affected lossless frames improved, and the other 742 match
the previous stage render by hash. 36 of 36 improved in the encoded MP4.
The 48 kHz stems, event map, and AAC stream match the previous export by hash.
Each of 52 Motion source crops was checked for region, timestamp, and hash.
Six isolated edits verified separate control of glass and metal curves, a
side button, composer text, key lettering, and the red tile.
[Motion crops](review/motion/motion-observations.json) ·
[Stage comparison](review/stage-metrics.json) ·
[Edit checks](review/editability.json) ·
[Previous review](../orbit-registration-review/README.md)

Source SHA-256  
`f821bb58cbdb265a75d572616d0da723e9cfb6de31e3db5f8a17d94dc15b5327`

Candidate SHA-256  
`a44630cf69451dc26012f09611155681380720d757e3786f2b7a5155dc60ce46`

## Rerun the comparison

Set `SOURCE` to the locked reference and use a fresh output folder.

```sh
PYTHON=/path/to/render-environment/bin/python \
HYPERFRAMES=/path/to/hyperframes \
bash review.sh "$SOURCE" "$PWD/candidate/sidehoe.mp4" "$PWD/review-rerun"

/path/to/render-environment/bin/python focus.py \
  "$SOURCE" ../orbit-registration-review/candidate/sidehoe.mp4 \
  candidate/sidehoe.mp4 review-rerun/focus
```
