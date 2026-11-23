# Sidehoe handset and cursor close-up review

The November 21, 2026 [candidate MP4](candidate/sidehoe.mp4) was rendered from
a clean copy of the [editable project](project/README.md).

[Watch the source and candidate side by side](review/side-by-side.mp4) ·
[Step through all 778 time-matched pairs](review/native/index.html)

## Changes in the rendered film

- Registered Sofia’s casing and glass through the push at f319–329, then
  refined the follow-up handset’s header, corners and composer at f650–659.
- Rebuilt the follow-up’s side buttons and rail reflections as independent
  stage controls. Fitted the outgoing message and gray reply, composer,
  two visible keyboard rows, response chips and inset emoji through contact.
- Adjusted the cursor silhouette, position and blur during the hold.
  Its first contact with Yes is f675 (27.00 s) in both decoded exports.
  Both show a two-pixel gap on the preceding frame. The tap remains at
  sample 1,296,000 on the 48 kHz clock.

[Cursor and target measurements](review/yes-contact.csv) ·
[Independent layer edit checks](review/editability.json) ·
[Verified Motion source observations](review/motion/motion-observations.json)

| Source time | Encoded comparison | Previous mean RGB error | Revised mean RGB error |
| --- | --- | ---: | ---: |
| 12.96 s | [Sofia’s handset during the push](review/focus/f324-sofia-handset-and-keyboard.png) | 4.45 | 2.97 |
| 26.32 s | [Follow-up casing and header](review/focus/f658-follow-up-header-and-casing.png) | 4.50 | 4.33 |
| 26.96 s | [Cursor just before contact](review/focus/f674-yes-before-contact.png) | 5.78 | 2.47 |
| 27.00 s | [First Yes contact](review/focus/f675-first-yes-contact.png) | 6.40 | 2.28 |
| 27.24 s | [Held Yes close-up](review/focus/f681-follow-up-close-up-with-yes-held.png) | 5.51 | 3.45 |
| 27.40 s | [First press feedback](review/focus/f685-first-yes-feedback.png) | 6.30 | 2.65 |
| 27.72 s | [Withdrawal](review/focus/f693-phone-and-cursor-withdrawing.png) | 4.05 | 3.94 |

Each row uses the same frame and native crop from the three encoded
files. At f681 the full-frame error moved from
4.763 to 2.983.
The first gray reply’s weight and focus, the key shadows, and the bottom
edge of the response are still visibly different.
[Crop bounds and scores](review/focus/metrics.csv) ·
[Previous candidate](../assistant-detail-review/README.md)

## Full export verdict

**Exact fidelity fails.** All 778 frames match in their native 2000 × 2000
dimensions, presentation timestamps and exclusive end times. The mux
decodes cleanly. Mean full-film RGB error moved from
2.7023 to 2.6508.
0 frames are pixel-identical. The final frame differs by
23 pixels, each by one grayscale level. The greatest remaining
full-frame error is 4.590 at f352 (14.08 s).
[Exact verdict](review/native/report.json) ·
[Full frame measurements](review/native/frames.csv) ·
[Highest-error matched frame](review/native/pairs/000352.jpg)

**HyperFrames 0.9.77 passed its visual thresholds.** It matched all six
cuts and its mean SSIM moved from 0.9733
to 0.9739. The official reviewer copy passed all 202
file checks.
[HyperFrames report](review/hyperframes.json) ·
[Ranked misses](review/hyperframes/worst.jpg) ·
[Pinned reviewer and license](../hyperframes-review/vendor/hyperframes/UPSTREAM.md)

All 42 modified lossless frames improved. The other 736 lossless
frames are byte-identical to the prior render. In the final decoded MP4,
42 of 42 modified frames improved.
The 48 kHz stems, event map and AAC stream match the previous candidate
by hash. The Motion review verifies 110 native source crops by
timestamp, region and SHA-256.
[Lossless render comparison](review/stage-metrics.json)

Source SHA-256  
`f821bb58cbdb265a75d572616d0da723e9cfb6de31e3db5f8a17d94dc15b5327`

Candidate SHA-256  
`f115b42ae1fd191114ed58772804bf7f25223d4d0c505301a103563a94a007d6`

## Rerun the comparison

Set `SOURCE` to the locked reference and use a fresh review output directory.

```sh
PYTHON=/path/to/render-environment/bin/python \
HYPERFRAMES=/path/to/hyperframes \
bash review.sh "$SOURCE" "$PWD/candidate/sidehoe.mp4" "$PWD/review-rerun"

/path/to/render-environment/bin/python focus.py \
  "$SOURCE" ../assistant-detail-review/candidate/sidehoe.mp4 \
  candidate/sidehoe.mp4 review-rerun/focus
```
