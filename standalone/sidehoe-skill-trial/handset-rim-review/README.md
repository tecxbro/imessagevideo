# Sidehoe handset rim and lighting review

November 21, 2026. The [candidate MP4](candidate/sidehoe.mp4) was rendered from a clean
copy of the [editable project](project/README.md).

[Watch the source and candidate side by side](review/side-by-side.mp4) ·
[Step through all 778 matched frame pairs](review/native/index.html)

## Edits

- The handset's top rim and two side rails have separate tracks for the placement
  and thickness of the bevel across f134–161. The pink light has separate values
  for its color on the paper and glass and how much it lifts the dark hardware.
- The heart colors are set individually in the title shot. The two angled cards
  behind the closing badge have rounded outer shoulders.
- The calendar tile's vertical exposure is shorter during its exit, so more of
  the “31” stays legible through the move.

The Motion library supplied 30 native source crops across 4 tracks.
All crop hashes, dimensions and presentation times verified.
Changing the upper rim, hardware reflection, heart color and tile exposure in a
clean copy affected the corresponding region.
[Motion observations](review/motion/motion-observations.json) ·
[Editability evidence](review/editability.json)

| Source time | Matched screenshots | Previous mean RGB error | Revised mean RGB error |
| --- | --- | ---: | ---: |
| 5.40 s | [Handset and upper refraction](review/focus/f135-handset-and-upper-refraction.png) | 5.63 | 5.13 |
| 5.44 s | [Glossy rim and lower flare](review/focus/f136-handset-and-lower-refraction.png) | 5.75 | 5.26 |
| 6.04 s | [Glass and hardware under the pink wash](review/focus/f151-handset-glass-and-rail-reflected-light.png) | 5.25 | 4.70 |
| 6.44 s | [Last handset frame](review/focus/f161-handset-last-screen-frame.png) | 4.38 | 3.65 |
| 7.60 s | [Title and hearts](review/focus/f190-attached-title-and-hearts.png) | 3.64 | 3.57 |
| 24.68 s | [Calendar tile beginning its exit](review/focus/f617-calendar-tile-initial-vertical-exposure.png) | 4.50 | 4.07 |
| 24.76 s | [Calendar tile just before the cut](review/focus/f619-calendar-tile-last-visible-finish.png) | 5.80 | 4.85 |
| 28.24 s | [Profile badge](review/focus/f706-attached-profile-badge.png) | 3.01 | 2.99 |

Each row compares the same crop and frame from the three encoded files.
[Selected crop bounds and metrics](review/focus/metrics.csv) ·
[Previous candidate](../tile-and-cursor-review/README.md)

## Final MP4 review

**Exact comparison failed.** The final mux decodes cleanly, and all 778 frame indices,
presentation times and exclusive end times match at 2000 × 2000 and 25 fps.
Whole-film mean RGB error moved from 2.867 to 2.849.
The reviewer found 0 pixel-identical frames. The last frame differs by
23 pixels. The highest remaining whole-frame RGB error is 5.26
at f136 (5.44 s).
[Exact verdict](review/native/report.json) ·
[All frame measurements](review/native/frames.csv) ·
[Highest-error frame](review/native/pairs/000136.jpg)

The rim at 5.44 s is closer. Natalie's incoming row remains too far left, and the
camera cutout and colored flare still differ. The title still shows differences
where the hearts overlap the letterforms. The closing badge still differs around
the outline and the colored card edges.

**HyperFrames 0.9.77 passed its visual thresholds.** Its mean SSIM moved from
0.9715 to 0.9717. All six cuts aligned at
5.36, 6.40, 8.52, 16.04, 27.72 and 30.80 s. All 202 files in the official reviewer
copy verified against its manifest.
[HyperFrames report](review/hyperframes.json) ·
[Ranked comparison sheet](review/hyperframes/worst.jpg) ·
[Pinned reviewer and license](../hyperframes-review/vendor/hyperframes/UPSTREAM.md)

60 of 62 edited frames improved before encoding. The mean RGB error increased on f707, f708.
58 improved in the decoded MP4. The decoded error increased on f205, f707, f708, f709. The other 716
lossless frames, authored audio stems, audio cue map and AAC stream match the
previous candidate by hash.
[Lossless measurements](review/stage-metrics.json)

Source SHA-256  
`f821bb58cbdb265a75d572616d0da723e9cfb6de31e3db5f8a17d94dc15b5327`

Candidate MP4 SHA-256  
`6ad14ce52b09328dcb0aba086fc1f74fbc5ebc64cbb8177b7dd3d8bffe1a4362`

## Rerun the review

Set `SOURCE` to the locked source and use a fresh review directory.

```sh
PYTHON=/path/to/render-environment/bin/python \
HYPERFRAMES=/path/to/hyperframes \
bash review.sh "$SOURCE" "$PWD/candidate/sidehoe.mp4" "$PWD/review-rerun"

/path/to/render-environment/bin/python focus.py \
  "$SOURCE" ../tile-and-cursor-review/candidate/sidehoe.mp4 \
  candidate/sidehoe.mp4 review-rerun/focus
```
