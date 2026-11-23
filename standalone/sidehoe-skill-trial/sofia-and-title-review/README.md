# Sidehoe Sofia push, title and badge review

November 21, 2026. The [candidate MP4](candidate/sidehoe.mp4) was rendered
from a clean copy of the [editable project](project/README.md).

[Watch the same-time comparison, source on the left](review/side-by-side.mp4) ·
[Step through all 778 frame pairs](review/native/index.html)

The Sofia push uses separately measured casing, screen and message
placements. The keyboard follows the target's row pitch and focus while
its layers stay clipped to the glass. The suggestion appears at f336 in
the source and the candidate. The title uses revised bounds and weight
per editable glyph with independent heart placement and focus. The
closing badge has revised card edges, face detail and heart shading
during its arrival. The cursor's shape and focus are separate from the
control it approaches.

The Motion library extracted 18 source crops across five tracks.
The exact source hash, crop hashes, frame indices and presentation
timestamps verified. A text edit in the reopened project affected the
intended Sofia bubble, and a title copy edit affected the intended line.
[Motion plan](review/motion-plan.json) ·
[Motion observations](review/motion/motion-observations.json)

| Time | Comparison from the decoded MP4 | Previous mean RGB error | Revised mean RGB error |
| --- | --- | ---: | ---: |
| 7.60 s | [Title and hearts](review/focus/f190-attached-title-and-hearts.png) | 3.89 | 3.64 |
| 13.24 s | [Sofia handset push](review/focus/f331-sofia-first-casing-push.png) | 5.66 | 3.49 |
| 13.44 s | [Suggestion arrival with the keyboard](review/focus/f336-sofia-suggestion-arrival.png) | 6.59 | 3.96 |
| 27.00 s | [Tight cursor crop at contact](review/focus/f675-follow-cursor-contact-outline.png) | 8.48 | 7.65 |
| 27.40 s | [Tight crop of the held cursor](review/focus/f685-follow-cursor-native-hull.png) | 15.33 | 14.44 |
| 28.24 s | [Profile badge](review/focus/f706-attached-profile-badge.png) | 3.26 | 3.01 |

Mean RGB error is the average absolute difference across decoded RGB
channels in the linked crop or, for the Sofia rows, the full frame.
All 49 revised lossless frames improved. The other 729 lossless
frames, authored audio stems, cue map and AAC stream match the preceding
candidate by hash.
[Measurements for the pictured comparisons](review/focus/metrics.csv) ·
[Previous calendar tile and handset review](../tile-and-push-review/README.md)

The source keyboard has more directional blur during Sofia's push.
The hearts near the end of the title still overlap the letters
differently, and the rear cards of the badge still differ in contour.
The cursor's silhouette and the calendar tile's fold still differ in
the decoded comparison.
[Calendar tile at 24.72 s](review/focus/f618-calendar-tile-fold-during-exit.png)

## Full export verdict

**HyperFrames 0.9.77 passed.** It found all six cuts at 5.36, 6.40, 8.52,
16.04, 27.72 and 30.80 s. Mean SSIM is 0.9690. All 202 files in the
pinned reviewer copy verified against its manifest.
[HyperFrames verdict and worst regions](review/hyperframes.json) ·
[Pinned reviewer and license](../hyperframes-review/vendor/hyperframes/UPSTREAM.md)

**The native pixel comparison failed.** All 778 frames decode and align
by index, presentation timestamp and exclusive end timestamp at
2000 × 2000 and 25 fps. All 49 revised frames improved in the decoded
export. Whole-film mean RGB error fell from 3.163 to 3.141. Zero frames
are pixel-identical, and the final frame differs by 23 pixels.
The largest whole-frame errors are the pink-lit handset at 6.40 s
and the follow-up handset entrance at 25.08 s, both at 6.41.
[Native verdict](review/native/report.json) ·
[Measurements for every frame](review/native/frames.csv) ·
[Pink-lit handset](review/native/pairs/000160.jpg) ·
[Follow-up entrance](review/native/pairs/000627.jpg)

Source SHA-256  
`f821bb58cbdb265a75d572616d0da723e9cfb6de31e3db5f8a17d94dc15b5327`

Candidate MP4 SHA-256  
`f8bb7cb8953f8c960cd3dd256ecf3b50cb82b9190cd2ec44a28e14035b0ec359`

Set `SOURCE` to the locked reference and choose a fresh review directory.

```sh
PYTHON=/path/to/render-environment/bin/python \
HYPERFRAMES=/path/to/hyperframes \
bash review.sh "$SOURCE" "$PWD/candidate/sidehoe.mp4" "$PWD/review-rerun"

/path/to/render-environment/bin/python focus.py \
  "$SOURCE" ../tile-and-push-review/candidate/sidehoe.mp4 \
  candidate/sidehoe.mp4 review-rerun/focus
```
