# Sidehoe follow-up handset and app-tile handoff

November 21, 2026. The [candidate MP4](candidate/sidehoe.mp4) was rendered
from a clean copy of the [editable project](project/README.md).

[Watch side by side with the reference](review/side-by-side.mp4) ·
[Inspect all 778 time-matched frames](review/native/index.html)

## What changed

- Registered the calendar fragments that overlap the ring tile at f478
  and fitted the arrival positions, focus and coverage of the other tiles
  through f482.
- Fitted the follow-up conversation, composer, keys, and handset bevel
  across f630–659. The No and Yes controls each have editable shape,
  lettering and emoji at their first visible frames.
- Measured the handset’s deformation through f660–670 and applied it
  before the renderer draws the cursor. The cursor is still an
  independently editable layer.

| Source time | Encoded comparison | Previous mean RGB error | Revised mean RGB error |
| --- | --- | ---: | ---: |
| 19.12 s | [Ring tile and foreground calendar cell](review/focus/f478-calendar-cell-crosses-ring-tile.png) | 2.95 | 2.11 |
| 19.16 s | [Flame and 31 tile arrival](review/focus/f479-flame-and-31-arrive.png) | 3.25 | 2.19 |
| 19.28 s | [First four-tile overlap](review/focus/f482-four-tile-overlap.png) | 2.62 | 2.01 |
| 25.32 s | [Handset settles](review/focus/f633-phone-nearly-settled.png) | 3.88 | 2.34 |
| 25.92 s | [First No response](review/focus/f648-no-first-appears.png) | 9.31 | 2.53 |
| 26.00 s | [First Yes response](review/focus/f650-yes-first-appears.png) | 9.01 | 3.59 |
| 26.32 s | [Handset case and keyboard](review/focus/f658-bevel-chips-and-keyboard.png) | 4.33 | 3.30 |
| 26.40 s | [First cropped push frame](review/focus/f660-first-cropped-push-frame.png) | 3.57 | 3.42 |
| 26.68 s | [Lens deformation during the push](review/focus/f667-cropped-handset-lens-push.png) | 4.18 | 3.64 |

Each row uses the same frame and crop from the three encoded files.
Native checks of the six frames around the reveals found the first
visible No at f648 (25.92 s) and the first Yes at f650 (26.00 s) in both
movies. The source No still has a sharper label and a smaller emoji
highlight at its first visible frame. The curvature of the keyboard
and composer still differs during the cropped camera push.
[Decoded reveal measurements](review/reveal-timing.csv) ·
[Crop measurements](review/focus/metrics.csv) ·
[Independent layer edit checks](review/editability.json)

The matched views for the requested screenshot examples still show
differences in the floating heart silhouettes and badge artwork.
[Title and hearts at 7.68 s](review/focus/f192-attached-active-title-and-hearts.png) ·
[Profile badge at 28.24 s](review/focus/f706-attached-profile-badge.png)

## Full export verdict

**Exact fidelity fails.** All 778 frames have identical presentation
timestamps and exclusive end times at 2000 × 2000 resolution. The mux
decodes cleanly. Mean full-film RGB error moved from
2.5411 to 2.4817.
0 frames are pixel-identical. The last frame differs by
23 pixels. The largest remaining full-frame error is 4.327
at f135 (5.40 s).
[Exact verdict](review/native/report.json) ·
[All frame measurements](review/native/frames.csv) ·
[Highest-error frame](review/native/pairs/000135.jpg)

**HyperFrames 0.9.77 passed its visual thresholds.** It matched all six cuts.
Mean SSIM moved from 0.9748 to 0.9754.
The pinned reviewer copy passed all 202 file checks.
[Official diff result](review/hyperframes.json) ·
[Ranked misses](review/hyperframes/worst.jpg) ·
[Reviewer copy and license](../hyperframes-review/vendor/hyperframes/UPSTREAM.md)

All 46 affected lossless frames improved and the other 732 matched the
previous render by hash. In the encoded MP4, 46 of the 46 affected
frames improved.
The 48 kHz stems, event map and AAC stream match the previous export
by hash. Motion supplied 70 native source crops, verified by
timestamp, region and hash.
[Source observations](review/motion/motion-observations.json) ·
[Stage measurements](review/stage-metrics.json) ·
[Previous export review](../assistant-reveal-review/README.md)

Source SHA-256  
`f821bb58cbdb265a75d572616d0da723e9cfb6de31e3db5f8a17d94dc15b5327`

Candidate SHA-256  
`4fe7dec639e2d6a077d3f2496c56525a86a28820f8ad5a60f16fc621e6e171ab`

## Rerun the comparison

Set `SOURCE` to the locked reference and use a fresh output folder.

```sh
PYTHON=/path/to/render-environment/bin/python \
HYPERFRAMES=/path/to/hyperframes \
bash review.sh "$SOURCE" "$PWD/candidate/sidehoe.mp4" "$PWD/review-rerun"

/path/to/render-environment/bin/python focus.py \
  "$SOURCE" ../assistant-reveal-review/candidate/sidehoe.mp4 \
  candidate/sidehoe.mp4 review-rerun/focus
```
