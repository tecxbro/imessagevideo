# Sidehoe title, handset, and badge review

November 21, 2026. The [latest MP4](candidate/sidehoe.mp4) was rendered
from a clean copy of the [editable project](project/README.md).

[Watch the same-time comparison, source on the left](review/side-by-side.mp4) ·
[Step through all 778 frame pairs](review/native/index.html)

## Title and hearts

Frames 186–206 use separately registered glyph positions, opacity,
and softness. The nine independently drawn hearts use their own
position, proportions, rotation, shear, and focus. A copy edit
rendered through the same entry point using the word layout for the
revised caption. The 757 authored control frames outside the title
window are byte-identical to the [pullback and badge export](../pullback-review/candidate/sidehoe.mp4).

The Motion library sampled three heart regions in five consecutive
source frames. All 15 crop hashes and presentation times verified.
[Motion plan](review/motion-plan.json) ·
[Source observations](review/motion/motion-observations.json)

| Time | Compared area | Prior mean RGB error | Revised mean RGB error |
| --- | --- | ---: | ---: |
| 7.40 s | [Whole frame before the title controls](review/focus/f185-title-before-registration.png) | 3.56 | 3.56 |
| 7.52 s | [Title and hearts in motion](review/focus/f188-title-and-hearts-moving.png) | 5.20 | 3.37 |
| 7.60 s | [Title and hearts at the supplied screenshot](review/focus/f190-attached-title-and-hearts.png) | 6.13 | 3.89 |
| 7.64 s | [Title and hearts one frame later](review/focus/f191-title-next-attached-frame.png) | 6.27 | 3.97 |
| 8.24 s | [Whole frame at the last registered pose](review/focus/f206-title-last-registered-words.png) | 2.12 | 1.50 |
| 8.28 s | [Whole frame after the title controls](review/focus/f207-title-post-registration.png) | 2.29 | 2.28 |

All 21 edited frames also improved on decoded whole-frame mean
absolute RGB error. The title and hearts still have visible differences,
including letter edges and the large heart over the middle of
“personal.” The region at the supplied screenshot still fails the
exact check.
[Title difference crop](review/native/crops/80-worst.png)

## Handset and badge changes retained in this export

The previous revision added separate exposure paths for the history and
keyboard during the Sofia pullback. The closing badge gained independently
painted card and heart pigments and a focus track. The table compares
the prior follow-up handset revision with this export.

| Time | Compared area | Prior mean RGB error | Revised mean RGB error |
| --- | --- | ---: | ---: |
| 14.20 s | [Whole frame during the Sofia pullback](review/focus/f355-sofia-pullback-exit-control.png) | 7.72 | 4.31 |
| 28.24 s | [Badge at the supplied screenshot](review/focus/f706-attached-profile-badge.png) | 3.68 | 3.26 |
| 28.72 s | [Badge during defocus](review/focus/f718-badge-largest-defocus.png) | 9.98 | 4.97 |

The outgoing rail and blur direction still differ during the pullback.
The defocused badge motif is still larger than the source. That revision
improved 80 of 81 edited encoded frames and slightly increased mean
RGB error at frame 728.
[Pullback and badge report](../pullback-review/README.md)

## Full export verdict

**HyperFrames 0.9.77 passed.** It found all six cuts at 5.36, 6.40, 8.52,
16.04, 27.72, and 30.80 s. Mean SSIM is 0.9676. All 202 files in the
pinned reviewer copy verified against the manifest.
[HyperFrames verdict](review/hyperframes.json) ·
[Reviewer source and license](../hyperframes-review/vendor/hyperframes/UPSTREAM.md)

**The native pixel comparison failed.** All 778 frames match the source
presentation and exclusive end timestamps at 2000 × 2000 and 25 fps.
Zero frames are pixel-identical. Mean RGB error fell from 3.362 to 3.353
in the title revision. The count of changed pixel observations fell
from 1,259,815,141 to 1,259,619,342 in that revision. The source and final
frame differ by 23 pixels. The MP4 decodes cleanly and its AAC, authored
stems and cue map match the preceding export by hash.
[Native verdict](review/native/report.json) ·
[All frame measurements](review/native/frames.csv)

The glossy handset entrance at 5.44 s has the largest remaining
whole-frame error at 7.58. The calendar tile and cursor contact
still differ in their native crops.
[Handset entrance](review/focus/f136-handset-and-lower-refraction.png) ·
[Calendar tile](review/focus/f613-calendar-tile-face.png) ·
[Cursor contact](review/focus/f675-follow-cursor-contact.png)

Source SHA-256  
`f821bb58cbdb265a75d572616d0da723e9cfb6de31e3db5f8a17d94dc15b5327`

Latest MP4 SHA-256  
`bc783b503d648f4a331fdf5a38f7d62bec0680ac3fd80469e4bbeecfdc4ea10b`

## Rerun

Set `SOURCE` to the locked reference and use a fresh review directory.

```sh
PYTHON=/path/to/render-environment/bin/python \
HYPERFRAMES=/path/to/hyperframes \
bash review.sh "$SOURCE" candidate/sidehoe.mp4 review-rerun

/path/to/render-environment/bin/python focus.py \
  "$SOURCE" ../pullback-review/candidate/sidehoe.mp4 \
  candidate/sidehoe.mp4 review-rerun/focus
```
