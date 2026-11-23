# Sidehoe suggestion handoff and closing review

November 21, 2026. The [candidate MP4](candidate/sidehoe.mp4) was rendered
from a clean copy of the [editable project](project/README.md).

[Watch side by side with the reference](review/side-by-side.mp4) ·
[Inspect all 778 time-matched frames](review/native/index.html)

## What changed

- Fitted the two cyan messages, suggestion label and response controls
  through f352–359. During the handset pullback, their focus and the glass
  focus can be edited independently.
- Registered the handset casing, messages and controls during the cursor
  approach at f671–672. The returning header’s name, badge trail and
  button optics now follow the withdrawal at f694–695.
- Adjusted the presentation of each closing word and fitted the pink
  lighting and fade. The closing lettering remains editable, with the
  existing word-by-word reveal and ending.

| Source time | Encoded comparison | Previous mean RGB error | Revised mean RGB error |
| --- | --- | ---: | ---: |
| 14.08 s | [Sofia’s suggestion during handset hold](review/focus/f352-sofia-handset-and-suggested-reply.png) | 4.59 | 3.29 |
| 14.16 s | [Suggestion starting to detach](review/focus/f354-suggested-reply-starting-to-detach.png) | 7.22 | 3.63 |
| 14.28 s | [Suggestion detached from handset](review/focus/f357-suggestion-detached-from-handset.png) | 3.01 | 1.69 |
| 26.88 s | [Follow-up cursor approach](review/focus/f672-cursor-approach-before-contact.png) | 4.51 | 3.13 |
| 27.76 s | [Withdrawing handset and header](review/focus/f694-follow-up-handset-withdrawing.png) | 4.55 | 4.10 |
| 29.40 s | [First closing line](review/focus/f735-first-line-settled.png) | 11.88 | 7.78 |
| 30.60 s | [Both closing lines](review/focus/f765-full-closing-title.png) | 28.39 | 13.13 |
| 30.68 s | [Closing fade](review/focus/f767-title-and-pink-wash-in-fade.png) | 4.33 | 2.65 |

Each row uses the same frame and crop from the three encoded files.
The source and candidate both first reach the Yes control at f675.
At f674 the decoded gap measures 2 pixels in the source
and 1 pixel in the candidate. The tap cue lands on that
contact at audio sample 1,296,000.
[Crop measurements](review/focus/metrics.csv) ·
[Cursor gap measurements](review/yes-contact.csv) ·
[Editability checks](review/editability.json)

The user’s screenshot examples map most closely to f192 and f706.
Their current matched crops show the remaining type and heart-shape
differences and the badge’s remaining motif and edge differences.
[Title and hearts at 7.68 s](review/focus/f192-attached-active-title-and-hearts.png) ·
[Profile badge at 28.24 s](review/focus/f706-attached-profile-badge.png)

## Full export verdict

**Exact fidelity fails.** All 778 frames have identical presentation
timestamps and exclusive end times at 2000 × 2000 resolution. The mux
decodes cleanly. Mean full-film RGB error moved from
2.6508 to 2.5698.
0 frames are pixel-identical and the last frame differs by
23 pixels. The largest remaining full-frame error is 4.501
at f141 (5.64 s).
[Exact verdict](review/native/report.json) ·
[All frame measurements](review/native/frames.csv) ·
[Highest-error frame](review/native/pairs/000141.jpg)

**HyperFrames 0.9.77 passed its visual thresholds.** It matched all six cuts.
Mean SSIM moved from 0.9739 to 0.9745.
The pinned reviewer copy passed all 202 file checks.
[Official diff result](review/hyperframes.json) ·
[Ranked misses](review/hyperframes/worst.jpg) ·
[Reviewer copy and license](../hyperframes-review/vendor/hyperframes/UPSTREAM.md)

All 78 affected lossless frames improved and the other 700 matched the
previous render by hash. In the encoded MP4, 78 of the 78 affected
frames improved.
The 48 kHz stems, event map and AAC stream match the previous export
by hash. Motion collected 53 source crops and verified their
timestamps, hashes and sizes. The dark-header detector was empty at
f694 during the blur. The decoded source crop remains available for
inspection in the matched view.
[Source observations](review/motion/motion-observations.json) ·
[Stage measurements](review/stage-metrics.json) ·
[Previous export review](../follow-closeup-review/README.md)

Source SHA-256  
`f821bb58cbdb265a75d572616d0da723e9cfb6de31e3db5f8a17d94dc15b5327`

Candidate SHA-256  
`c71f82886826ee163082abd185e47a218564b3581ee93e2750942836c8dc1194`

## Rerun the comparison

Set `SOURCE` to the locked reference and use a fresh output folder.

```sh
PYTHON=/path/to/render-environment/bin/python \
HYPERFRAMES=/path/to/hyperframes \
bash review.sh "$SOURCE" "$PWD/candidate/sidehoe.mp4" "$PWD/review-rerun"

/path/to/render-environment/bin/python focus.py \
  "$SOURCE" ../follow-closeup-review/candidate/sidehoe.mp4 \
  candidate/sidehoe.mp4 review-rerun/focus
```
