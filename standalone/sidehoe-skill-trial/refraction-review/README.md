# Sidehoe handset refraction and Sofia close-up

November 21, 2026. The [candidate MP4](candidate/sidehoe.mp4) was rendered
from a clean copy of the [editable project](project/README.md).

[Watch the source and recreation side by side](review/side-by-side.mp4) ·
[Inspect all 778 time-matched frames](review/native/index.html)

## What changed

- Fitted the assistant handset’s badge size, Messages glyphs, status controls,
  portrait lighting, and colored reflections over frames 134–137. The color
  and blur distort live authored shapes and type.
- Aligned Sofia’s handset rails, attachment control, microphone, composer
  outline, and keyboard over frames 343–351. The attachment control and
  keyboard glyphs can be moved independently.
- Checked the calendar tile arrival and the follow-up cursor at the
  same source times. [Calendar tile at 19.16 s](review/focus/f479-calendar-31-tile-arrival.png) ·
  [Cursor contact at 27.00 s](review/focus/f675-yes-cursor-contact.png) ·
  [Earlier tile and cursor repair](../tile-and-cursor-review/README.md)

| Source time | Matched encoded crop | Previous mean RGB error | Revised mean RGB error |
| --- | --- | ---: | ---: |
| 5.36 s | [First handset frame](review/focus/f134-first-assistant-handset-frame.png) | 5.99 | 3.87 |
| 5.40 s | [Colored rim and refracted controls](review/focus/f135-colored-rim-and-refracted-controls.png) | 6.36 | 5.10 |
| 5.44 s | [Portrait lighting and rail reflection](review/focus/f136-side-portrait-light-and-rail-reflection.png) | 6.00 | 4.92 |
| 5.48 s | [Settling refraction](review/focus/f137-handset-refraction-settles.png) | 5.44 | 4.52 |
| 13.72 s | [Sofia handset at the start of the close-up](review/focus/f343-sofia-railing-and-keyboard-start.png) | 4.08 | 2.91 |
| 13.80 s | [Composer and keys during the push](review/focus/f345-sofia-composer-and-key-approach.png) | 4.43 | 2.19 |
| 13.88 s | [Composer and keys at closest approach](review/focus/f347-sofia-composer-and-key-closest.png) | 4.91 | 2.02 |
| 14.04 s | [End of the push](review/focus/f351-sofia-key-end.png) | 4.15 | 2.22 |

The source rim remains softer and its camera island has a different highlight
at 5.40 seconds. The attached examples still show differences in the
title, heart contours, and profile badge artwork.
[Title and hearts at 7.68 s](review/focus/f192-attached-active-title-and-hearts.png) ·
[Profile badge at 28.24 s](review/focus/f706-attached-profile-badge.png)

## Full export verdict

**Exact fidelity fails.** The mux decodes cleanly. All 778 frames have
identical presentation timestamps and exclusive end times at 2000 × 2000.
Mean RGB error moved from 2.4817 to 2.4607.
0 frames are pixel-identical. The last frame differs by 23 pixels.
The largest full-frame error is 4.233 at f160 (6.40 s).
[Exact verdict](review/native/report.json) ·
[All frame measurements](review/native/frames.csv) ·
[Highest-error frame](review/native/pairs/000160.jpg)

**HyperFrames 0.9.77 passed its visual thresholds** and matched all six cuts.
Mean SSIM moved from 0.9754 to 0.9756.
The pinned reviewer copy passed all 202 file checks.
[Official diff result](review/hyperframes.json) ·
[Ranked misses](review/hyperframes/worst.jpg) ·
[Reviewer source and license](../hyperframes-review/vendor/hyperframes/UPSTREAM.md)

All 13 affected frames improved in both the lossless render and the encoded
MP4. The other 765 lossless stage frames match the previous render by hash.
The 48 kHz stems, event map, and AAC stream also match the previous export by hash.
Motion supplied 32 native source crops. Each crop’s region, timestamp,
and file hash were verified. Six isolated edits verified the badge, text,
refraction, light, and Messages layers.
[Motion observations](review/motion/motion-observations.json) ·
[Stage comparison and adjacent control frames](review/stage-metrics.json) ·
[Editability checks](review/editability.json) ·
[Previous review](../follow-handset-review/README.md)

Source SHA-256  
`f821bb58cbdb265a75d572616d0da723e9cfb6de31e3db5f8a17d94dc15b5327`

Candidate SHA-256  
`e34011498f91bef3ac11a99833b360dc50833be96edc8d58b248f353a5328882`

## Rerun the comparison

Set `SOURCE` to the locked reference and use a fresh output folder.

```sh
PYTHON=/path/to/render-environment/bin/python \
HYPERFRAMES=/path/to/hyperframes \
bash review.sh "$SOURCE" "$PWD/candidate/sidehoe.mp4" "$PWD/review-rerun"

/path/to/render-environment/bin/python focus.py \
  "$SOURCE" ../follow-handset-review/candidate/sidehoe.mp4 \
  candidate/sidehoe.mp4 review-rerun/focus
```
