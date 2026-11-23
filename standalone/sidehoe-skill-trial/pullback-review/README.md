# Sidehoe pullback and closing badge review

November 21, 2026. The [revised export](candidate/sidehoe.mp4) came from
a clean copy of the [editable project](project/README.md). The
[preceding export](../follow-entry-review/candidate/sidehoe.mp4) supplies
the previous column.

[Watch the same-time comparison, source on the left](review/side-by-side.mp4) ·
[Step through all 778 frame pairs](review/native/index.html)

## What changed

The Sofia pullback now exposes the upper history and lower keyboard
and composer on separate shutter paths. The right rail uses its own
material profile as it fades. The closing badge's card and heart
pigments were revised, and the badge has an editable focus and pose
track through the move. The closing pass preserves the existing
editable artwork and dialogue. The 697 authored frames outside these
two windows are byte-identical to the previous render.

The Motion library sampled the keyboard tray, rail, and badge.
All 23 observations were verified against the source hash,
presentation times, bounds, and crop hashes.
[Motion plan](review/motion-plan.json) ·
[Source observations](review/motion/motion-observations.json)

## Encoded comparison

| Time | Compared area | Prior mean RGB error | Revised mean RGB error |
| --- | --- | ---: | ---: |
| 14.16 s | [Whole frame before the pullback optics](review/focus/f354-sofia-pullback-registration.png) | 3.61 | 3.61 |
| 14.20 s | [Whole frame at the prior largest error](review/focus/f355-sofia-pullback-exit-control.png) | 7.72 | 4.31 |
| 14.24 s | [Whole frame as the rail and display fade](review/focus/f356-sofia-pullback-rail-and-display.png) | 5.11 | 4.01 |
| 14.36 s | [Whole frame with the last keyboard exposure](review/focus/f359-sofia-pullback-final-keyboard.png) | 2.38 | 2.35 |
| 28.24 s | [Badge at the time of the supplied screenshot](review/focus/f706-attached-profile-badge.png) | 3.68 | 3.26 |
| 28.64 s | [Badge as focus softens](review/focus/f716-badge-focus-falling.png) | 8.50 | 3.56 |
| 28.72 s | [Badge at peak defocus](review/focus/f718-badge-largest-defocus.png) | 9.98 | 4.97 |
| 28.80 s | [Badge during the soft-focus move](review/focus/f720-badge-moving-in-soft-focus.png) | 7.73 | 3.39 |

All 81 edited lossless frames improved on whole-frame mean absolute RGB
error. In the encoded export, 80 improved. Frame 728 at 29.12 s rose
from 1.63769 to 1.63866. The right rail and blur direction still differ
at 14.20 s, and the defocused badge motif is still larger than the source.
[History shutter difference](review/native/crops/74-worst.png) ·
[Rail difference](review/native/crops/76-worst.png) ·
[Badge defocus difference](review/native/crops/78-worst.png)

## Full export verdict

**HyperFrames 0.9.77 passed.** It found all six cuts at 5.36, 6.40, 8.52,
16.04, 27.72, and 30.80 s. Mean SSIM is 0.9675. All 202 files in the
pinned reviewer copy verified against its manifest.
[HyperFrames verdict](review/hyperframes.json) ·
[Reviewer source and license](../hyperframes-review/vendor/hyperframes/UPSTREAM.md)

**The native pixel comparison failed.** All 778 frames match the source
presentation and exclusive end timestamps at 2000 × 2000 and 25 fps.
Zero frames are pixel-identical. Mean RGB error fell from 3.373 to 3.362
across the film. The count of changed pixel observations rose from
1,259,173,789 to 1,259,815,141. The last frame differs by 23 pixels.
The mux decodes cleanly. The AAC stream, authored stems, and cue map
match the preceding export by hash.
[Native verdict](review/native/report.json) ·
[All frame measurements](review/native/frames.csv)

The assistant handset entrance at 5.44 s is now the largest whole-frame
error, 7.58. The title and hearts, calendar tile, and cursor contact
still have visible local differences.
[Assistant handset entrance](review/focus/f136-handset-and-lower-refraction.png) ·
[Title and hearts](review/focus/f190-attached-title-and-hearts.png) ·
[Calendar tile](review/focus/f613-calendar-tile-face.png) ·
[Cursor contact](review/focus/f675-follow-cursor-contact.png)

Source SHA-256  
`f821bb58cbdb265a75d572616d0da723e9cfb6de31e3db5f8a17d94dc15b5327`

Revised MP4 SHA-256  
`00f2f32ca2fec4563ef0f676ea9f6bc9b69b9488589553a2d93e574a2c528e97`

## Rerun

Set `SOURCE` to the locked reference and use a fresh review directory.

```sh
PYTHON=/path/to/render-environment/bin/python \
HYPERFRAMES=/path/to/hyperframes \
bash review.sh "$SOURCE" candidate/sidehoe.mp4 review-rerun

/path/to/render-environment/bin/python focus.py \
  "$SOURCE" ../follow-entry-review/candidate/sidehoe.mp4 \
  candidate/sidehoe.mp4 review-rerun/focus
```
