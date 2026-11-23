# Sidehoe follow-up handset review

November 21, 2026. The [revised export](candidate/sidehoe.mp4) came from
a clean copy of the [editable project](project/README.md). The
[preceding export](../handset-review/candidate/sidehoe.mp4) supplies the
previous column in the comparisons.

[Watch the same-time comparison, source on the left](review/side-by-side.mp4) ·
[Step through all 778 frame pairs](review/native/index.html)

## What changed

Frames 631–659 now register the contact badge, status cutout, header,
message bodies and ink, composer, keyboard rows, and home indicator
independently. The pale outgoing message uses a vertical gradient.
The later casing move has its own pose controls, and the cursor has separate
horizontal and vertical blur. The Messages copy and artwork are editable.
All 749 other authored frames match the previous PNGs byte for byte.

The Motion library extracted 30 observations of the contact badge,
left casing, and cursor. The locked source hash, pixel bounds,
presentation time, and crop hash were checked for each observation.
[Motion plan](review/motion-plan.json) ·
[Source observations](review/motion/motion-observations.json)

## Encoded comparison

| Time | Whole-frame evidence | Prior mean RGB error | Revised mean RGB error |
| --- | --- | ---: | ---: |
| 25.20 s | [Frame before the revised passage](review/focus/f630-follow-before-registered-history.png) | 4.57 | 4.57 |
| 25.40 s | [Contact badge and messages](review/focus/f635-follow-badge-and-replies.png) | 5.32 | 3.77 |
| 26.00 s | [Casing in motion](review/focus/f650-follow-registered-casing.png) | 5.45 | 3.85 |
| 26.32 s | [Frame before the close-up](review/focus/f658-follow-preceding-largest-mismatch.png) | 6.60 | 4.89 |
| 26.36 s | [Previous largest whole-frame error](review/focus/f659-follow-before-moving-closeup.png) | 7.89 | 4.42 |
| 26.40 s | [First frame of the moving close-up](review/focus/f660-follow-moving-closeup-entry.png) | 6.73 | 6.73 |

All 29 edited frames improve on decoded whole-frame mean absolute RGB
error. The isolated cursor region improves on mean absolute RGB error
in 12 of 14 encoded frames and on mean squared RGB error in all 14.
Its mean number of differing pixels per frame rises from 2,710 to
2,776. The cursor, the keyboard and home indicator, the header and
status area, and the dialogue still have visible differences in the exact comparison.
[Cursor measurements](review/cursor-native.csv) ·
[Cursor difference crop](review/native/crops/73-worst.png) ·
[Keyboard and home indicator difference](review/native/crops/72-worst.png) ·
[Header and status difference](review/native/crops/70-worst.png)

## Full export verdict

**HyperFrames 0.9.77 passed.** It found all six cuts at 5.36, 6.40, 8.52,
16.04, 27.72, and 30.80 s. Mean SSIM is 0.9673. All 202 copies of the
pinned reviewer files verified against their manifest.
[HyperFrames verdict](review/hyperframes.json) ·
[Reviewer source and license](../hyperframes-review/vendor/hyperframes/UPSTREAM.md)

**The native pixel comparison failed.** All 778 frames, including the
ending, match the reference's start and end timestamps at 2000 × 2000
and 25 fps. Zero frames are pixel-identical. Mean RGB error fell from
3.434 to 3.373 across the film. The number of changed pixel observations
fell from 1,260,268,528 to 1,259,173,789. The last frame still differs
by 23 pixels. The mux decodes cleanly. The AAC stream, stems, and cue
map match the preceding export by hash.
[Native verdict](review/native/report.json) ·
[All frame measurements](review/native/frames.csv)

The largest remaining whole-frame error is 7.72 at 14.20 s. The Sofia
pullback still differs in the diagonal trail of the history text and
keyboard and in the right rail. The title and hearts, closing badge,
calendar tile, and cursor contact remain open in their same-time crops.
[Sofia pullback](review/focus/f355-sofia-pullback-exit-control.png) ·
[Title and hearts](review/focus/f190-attached-title-and-hearts.png) ·
[Closing badge](review/focus/f706-attached-profile-badge.png) ·
[Calendar tile](review/focus/f613-calendar-tile-face.png) ·
[Cursor contact](review/focus/f675-follow-cursor-contact.png)

Source SHA-256  
`f821bb58cbdb265a75d572616d0da723e9cfb6de31e3db5f8a17d94dc15b5327`

Revised MP4 SHA-256  
`bb7bc84ec7005f580a61befa7f3e034c827388ae9d01805925661698662fa0af`

## Rerun

Set `SOURCE` to the locked reference and use a fresh review directory.

```sh
PYTHON=/path/to/render-environment/bin/python \
HYPERFRAMES=/path/to/hyperframes \
bash review.sh "$SOURCE" candidate/sidehoe.mp4 review-rerun

/path/to/render-environment/bin/python focus.py \
  "$SOURCE" ../handset-review/candidate/sidehoe.mp4 \
  candidate/sidehoe.mp4 review-rerun/focus
```
