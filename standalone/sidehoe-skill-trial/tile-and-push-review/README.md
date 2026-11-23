# Sidehoe calendar tile and handset review

November 21, 2026. The [candidate MP4](candidate/sidehoe.mp4) was rendered
from a clean copy of the [editable project](project/README.md).

[Watch the same-time comparison, source on the left](review/side-by-side.mp4) ·
[Step through all 778 frame pairs](review/native/index.html)

The calendar tile keeps its independently drawn glass cap, pinched blue
face and numeral paths. The new measurements adjust the numeral stroke,
fold highlight, tile height and directional softness from f603 through
f619. The revised handset push uses separate focus for the casing and
display. The keyboard footer is drawn inside the rounded casing, and the
cursor retains its independent position and focus track. The Motion
library provided 14 native source crops across four tracks for the tile
and the handset. Their hashes, frame indices and presentation timestamps
verified against the locked input.
[Motion plan](review/motion-plan.json) ·
[Motion observations](review/motion/motion-observations.json)

| Time | Comparison from the encoded MP4 | Previous mean RGB error | Revised mean RGB error |
| --- | --- | ---: | ---: |
| 24.40 s | [Calendar numeral stroke](review/focus/f610-calendar-tile-numeral-stroke.png) | 4.17 | 3.86 |
| 24.72 s | [Calendar face during exit](review/focus/f618-calendar-tile-fold-during-exit.png) | 6.18 | 4.66 |
| 24.76 s | [Last visible tile finish](review/focus/f619-calendar-tile-last-visible-finish.png) | 9.77 | 6.14 |
| 26.40 s | [Handset, including the rounded casing and footer](review/focus/f660-follow-moving-closeup-entry.png) | 6.73 | 3.57 |
| 26.44 s | [Next frame in the handset push](review/focus/f661-follow-camera-and-keyboard.png) | 6.10 | 3.54 |
| 27.00 s | [Cursor at the Yes control](review/focus/f675-follow-cursor-contact.png) | 5.84 | 5.83 |
| 27.76 s | [Tight cursor crop during the pullback](review/focus/f694-follow-cursor-native-hull.png) | 10.81 | 10.89 |

Error is the mean absolute difference on the decoded 8-bit RGB channels
within the displayed crop or, for the two handset-push rows, across
the whole frame. All 27 revised lossless frames improved. The other 751
lossless frames, authored audio stems, cue map and AAC stream match the
preceding candidate by hash. The slight regression in the tight
27.76 s cursor crop appears in the encoded frames. The separate change
to that cursor's shape is in the preceding pass.
[Earlier cursor and handset measurements](../exit-review/README.md) ·
[All selected crop measurements](review/focus/metrics.csv)

In the reopened project, changing a message at f660 affected only the
bubble's ink. Moving the cursor at f675 affected only the cursor region.

The tile's upper fold and the shape of its `3` still differ during
exit. The handset retains differences in its bevel highlights and
header badge. The title lettering and hearts and the closing badge
also retain local differences at the supplied screenshot times.
[Handset refraction](review/focus/f136-handset-and-lower-refraction.png) ·
[Title and hearts at 7.60 s](review/focus/f190-attached-title-and-hearts.png) ·
[Profile badge at 28.24 s](review/focus/f706-attached-profile-badge.png)

## Full export verdict

**HyperFrames 0.9.77 passed.** It found all six cuts at 5.36, 6.40, 8.52,
16.04, 27.72 and 30.80 s. Mean SSIM is 0.9688. All 202 files in the
pinned reviewer copy verified against its manifest.
[HyperFrames verdict and worst regions](review/hyperframes.json) ·
[Pinned reviewer and license](../hyperframes-review/vendor/hyperframes/UPSTREAM.md)

**The native pixel comparison failed.** The mux decodes cleanly. All 778
frames align by index, presentation timestamp and exclusive end timestamp
at 2000 × 2000 and 25 fps. All 27 edited frames improved in the decoded
export. Mean absolute RGB error fell from 3.177 to 3.163. Zero frames
are pixel-identical, and the last frame differs by 23 pixels. The
largest remaining whole-frame error is 6.59 at 13.44 s during Sofia's
handset push. The keyboard and casing soften differently in that frame.
[Native verdict](review/native/report.json) ·
[Measurements for all frames](review/native/frames.csv) ·
[Sofia's handset push](review/native/pairs/000336.jpg)

Source SHA-256  
`f821bb58cbdb265a75d572616d0da723e9cfb6de31e3db5f8a17d94dc15b5327`

Candidate MP4 SHA-256  
`f1e4205ad8a963c5cc5d5e0de2ae188eaf4cbc4db344e0334d605a9da33550c6`

Set `SOURCE` to the locked reference and choose a fresh review directory.

```sh
PYTHON=/path/to/render-environment/bin/python \
HYPERFRAMES=/path/to/hyperframes \
bash review.sh "$SOURCE" "$PWD/candidate/sidehoe.mp4" "$PWD/review-rerun"

/path/to/render-environment/bin/python focus.py \
  "$SOURCE" ../exit-review/candidate/sidehoe.mp4 \
  candidate/sidehoe.mp4 review-rerun/focus
```
