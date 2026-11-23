# Sidehoe glossy handset entrance review

November 21, 2026. This MP4 was rendered from a clean copy of the
[editable project](project/README.md). The
[title revision](../title-review/candidate/sidehoe.mp4) supplies the previous column.

[Watch the same-time comparison, source on the left](review/side-by-side.mp4) ·
[Step through all 778 frame pairs](review/native/index.html)

The status symbols, clock, Messages heading, and pin positions are
registered separately in f134–161. The independently drawn casing uses
measured top and side bevel positions and contrast through the
refraction and the pink wash. The Motion library extracted 21 source
samples of the top rim, right rail, and battery. Their crop hashes,
bounds, and timestamps were verified against the locked source.
[Motion plan](review/motion-plan.json) ·
[Source observations](review/motion/motion-observations.json)

| Time | Whole-frame comparison | Prior mean RGB error | Revised mean RGB error |
| --- | --- | ---: | ---: |
| 5.32 s | [Before the entrance](review/focus/f133-before-handset-entrance.png) | 2.16 | 2.16 |
| 5.36 s | [First visible handset](review/focus/f134-first-handset-and-pin.png) | 7.55 | 5.95 |
| 5.44 s | [Handset and lower refraction](review/focus/f136-handset-and-lower-refraction.png) | 7.58 | 6.17 |
| 5.64 s | [Handset after the rim refraction](review/focus/f141-handset-after-rim-refraction.png) | 7.27 | 5.55 |
| 5.72 s | [Glass and contact pins](review/focus/f143-handset-glass-and-contact-pins.png) | 7.20 | 5.18 |
| 6.44 s | [Last screen frame](review/focus/f161-handset-last-screen-frame.png) | 5.42 | 4.81 |
| 6.48 s | [Next title frame](review/focus/f162-handset-after-cut.png) | 1.18 | 1.18 |

All 28 edited frames improved on decoded whole-frame mean absolute
RGB error. The other 750 authored PNGs are byte-identical. Some decoded
values outside the edited span change on re-encode. For example, the
title and hearts crop at 7.60 s rose from 3.88928 to 3.89454. Portrait
detail, glass reflectance and the lower flare remain visibly different.
[Native region results](review/native/report.json)

**HyperFrames 0.9.77 passed.** All six cuts match, with mean SSIM 0.9679.
All 202 files in the pinned reviewer copy verified against the manifest.
[HyperFrames verdict](review/hyperframes.json) ·
[Reviewer source and license](../hyperframes-review/vendor/hyperframes/UPSTREAM.md)

**The exact pixel comparison failed.** At 2000 × 2000 and 25 fps,
all 778 frame indices, timestamps and exclusive end timestamps match.
Zero frames are pixel-identical. Whole-film mean RGB error fell from
3.353 to 3.305. The number of changed pixel observations fell from
1,259,619,342 to 1,259,361,184. The final frame differs by 23 pixels.
The mux decodes cleanly. Its AAC stream, sound stems and cue map
match the previous authored export by hash.
[Native verdict](review/native/report.json) ·
[All decoded frame measurements](review/native/frames.csv)

Source SHA-256  
`f821bb58cbdb265a75d572616d0da723e9cfb6de31e3db5f8a17d94dc15b5327`

Revised MP4 SHA-256  
`ae6736b567b140bb6fc304f31a63b7e0703fce8b0d7f5afdaaa2b40e5a74ef6e`

Set `SOURCE` to the locked reference and use a fresh output directory.

```sh
PYTHON=/path/to/render-environment/bin/python \
HYPERFRAMES=/path/to/hyperframes \
bash review.sh "$SOURCE" candidate/sidehoe.mp4 review-rerun

/path/to/render-environment/bin/python focus.py \
  "$SOURCE" ../title-review/candidate/sidehoe.mp4 \
  candidate/sidehoe.mp4 review-rerun/focus
```
