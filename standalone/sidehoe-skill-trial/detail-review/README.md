# Sidehoe title, tile, cursor and badge review

November 21, 2026. The prior column uses the
[handset motion export](../motion-review/candidate/sidehoe.mp4). The revised
[Sidehoe export](candidate/sidehoe.mp4) came from a clean copy of the
[editable project](project/README.md).

[Watch source and reconstruction side by side](review/side-by-side.mp4) ·
[Step through all 778 frame pairs](review/native/index.html)

## Matched source frames

The two supplied screenshots align to f190 and f706. The first comparison
shows the independently registered title words over the heart animation. The
second shows the measured moving badge perimeter, card outlines and separate
reflection over the dark surface.

| Time | Area measured | Prior RGB error | Revised RGB error |
| --- | --- | ---: | ---: |
| 7.60 s | [Title and hearts from the screenshot](review/focus/f190-attached-title-and-hearts.png) | 10.10 | 6.13 |
| 24.52 s | [Curved calendar tile and 31](review/focus/f613-calendar-tile-face.png) | 4.41 | 4.22 |
| 27.20 s | [Cursor hull at contact](review/focus/f680-follow-cursor-native-hull.png) | 23.45 | 12.80 |
| 28.24 s | [Profile badge from the screenshot](review/focus/f706-attached-profile-badge.png) | 3.88 | 3.68 |
| 28.32 s | [Badge just after the screenshot pose](review/focus/f708-badge-after-screenshot-pose.png) | 3.61 | 3.76 |
| 29.44 s | [Badge after it settles](review/focus/f736-badge-settled-size.png) | 7.94 | 5.06 |

RGB error is the mean absolute channel difference at native resolution
on a 0–255 scale. The arrow now has rounded corners and separate
horizontal and vertical focus. Across all 26 encoded frames f670–695, the
source-derived cursor mask error fell from 23.81 to 13.98 and improved on
each frame. Mean dark contour overlap rose from 0.885 to 0.924. The
cursor region uses the connected neutral dark ink and a six-pixel margin
from the source frame. [Cursor measurements](review/focus/cursor-frames.csv) ·
[Reference motion observations](../hyperframes-review/motion-evidence/motion-observations.json)

The curved tile uses existing orbit poses and separately adjusted numeral
strokes, cheek light and shading. The badge perimeter stays on its
measured trajectory through the final hold. The letter fits, tile
material, arrow outline and badge artwork stay editable in the project.
The source media and extracted crops are review inputs.

## Full export verdict

All 778 frame indices, start timestamps and exclusive end timestamps
agree with the source at 25 fps and 2000 × 2000. The 31.12-second
side-by-side video shows the source on the left. It is silent so the
picture can be compared independently. The authored lossless sequence
changed on 141 frames across the four passages.

Full-frame mean absolute RGB error fell from 3.800 to 3.779. Pixels with a
channel difference rose from 1,274,763,348 to 1,275,079,862 across the
entire sequence. Zero frames are pixel-identical. The first difference
is at f0, and the largest whole-frame error is 8.58 at f341. The
title and profile badge still show visible differences at the supplied
times. [Native pixel verdict](review/native/report.json) ·
[All frame measurements](review/native/frames.csv)

HyperFrames 0.9.77 measured mean SSIM of 0.9646 and still flags the
calendar transition at 16.04 s. Its copied reviewer source was pinned
before the fixes and the 202-file manifest verified again for this build.
[HyperFrames verdict](review/hyperframes.json) ·
[Pinned reviewer source and license](../hyperframes-review/vendor/hyperframes/UPSTREAM.md)

The mux decodes cleanly. Its encoded AAC, editable stems and sound event
map match the previous authored mix by hash. The original audio is
separate from that mix.

Source SHA-256
`f821bb58cbdb265a75d572616d0da723e9cfb6de31e3db5f8a17d94dc15b5327`

Candidate SHA-256
`625aa59f21e07e942a094b97dea004eb00cdb4f7c65fd3cbdf05bc03a511556f`

## Rerun

Set `SOURCE` to the locked reference film and use a fresh output directory.

```sh
PYTHON=/path/to/render-environment/bin/python \
HYPERFRAMES=/path/to/hyperframes \
bash review.sh "$SOURCE" candidate/sidehoe.mp4 review-rerun

/path/to/render-environment/bin/python focus.py \
  "$SOURCE" ../motion-review/candidate/sidehoe.mp4 \
  candidate/sidehoe.mp4 review-rerun/focus
```
