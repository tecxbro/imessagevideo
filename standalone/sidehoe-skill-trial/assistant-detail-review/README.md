# Sidehoe assistant handset and suggestion review

November 21, 2026. The [candidate MP4](candidate/sidehoe.mp4) was rendered from a clean
copy of the [editable project](project/README.md).

[Watch the source and candidate side by side](review/side-by-side.mp4) ·
[Step through all 778 matched frame pairs](review/native/index.html)

## Edits

- The handset’s upper reflection follows its own narrow light field
  at f134–142. The portrait positions and center badge geometry are
  editable independently. The title uses measured positions, opacity
  and focus while the handset rises.
- At f337–342, Sofia’s screen exposure follows the push. The suggestion
  and first visible No or Send? controls have measured outlines and
  label positions at f340–342.

The Motion library supplied 34 native source crops across 4 tracks.
All crop hashes, dimensions and presentation times verified.
Editing the title, Darla’s face position, the badge, and Sofia’s
suggested reply in a clean copy changed their visible regions.
[Motion observations](review/motion/motion-observations.json) ·
[Editability evidence](review/editability.json)

| Source time | Matched screenshots | Previous mean RGB error | Revised mean RGB error |
| --- | --- | ---: | ---: |
| 5.36 s | [First visible handset and rim](review/focus/f134-first-handset-and-pin.png) | 4.43 | 4.24 |
| 5.40 s | [Crown refraction](review/focus/f135-handset-and-upper-refraction.png) | 4.79 | 4.49 |
| 5.60 s | [Title and portraits before settling](review/focus/f140-assistant-title-and-portraits-before-held-frame.png) | 4.71 | 4.34 |
| 5.68 s | [Assistant title and pinned portraits](review/focus/f142-assistant-title-pinned-portraits-and-badge.png) | 4.88 | 4.24 |
| 5.84 s | [Title and center badge under light](review/focus/f146-assistant-title-and-center-badge-under-light.png) | 4.64 | 4.22 |
| 6.16 s | [Center badge under the pink wash](review/focus/f154-assistant-center-badge-as-pink-wash-rises.png) | 4.46 | 4.12 |
| 6.24 s | [Last edited badge frame](review/focus/f156-assistant-center-badge-before-handset-leaves.png) | 4.07 | 3.94 |
| 6.28 s | [Adjacent frame after the badge adjustment](review/focus/f157-assistant-control-after-badge-adjustment.png) | 3.94 | 3.94 |
| 13.60 s | [First measured suggestion shape](review/focus/f340-sofia-suggestion-in-first-visible-shape.png) | 4.60 | 3.65 |
| 13.64 s | [No control enters during the push](review/focus/f341-sofia-no-control-enters-during-push.png) | 4.83 | 3.76 |
| 13.68 s | [Next suggestion frame](review/focus/f342-sofia-closeup-entry.png) | 4.57 | 3.99 |
| 13.72 s | [First frame after the new controls](review/focus/f343-sofia-suggestion-and-controls-enter.png) | 4.08 | 4.08 |

Each row compares the same crop and frame from the three encoded files.
[Selected crop bounds and metrics](review/focus/metrics.csv) ·
[Previous candidate](../profile-arrival-review/README.md)

## Final MP4 review

**Exact comparison failed.** The final mux decodes cleanly, and all 778 frame indices,
presentation times and exclusive end times match at 2000 × 2000 and 25 fps.
Whole-film mean RGB error moved from 2.716 to 2.702.
The reviewer found 0 pixel-identical frames. The last frame differs by
23 pixels. The highest remaining whole-frame RGB error is 4.76
at f681 (27.24 s).
[Exact verdict](review/native/report.json) ·
[All frame measurements](review/native/frames.csv) ·
[Highest-error frame](review/native/pairs/000681.jpg)

At 5.68 s, the two title lines and pinned faces are closer in
position. The source still differs at the rim, lens highlights and
portrait expressions. Sofia’s first suggestion is closer through the
push, and its text and controls still differ in stroke and shape.
[Title and hearts at 7.60 s](review/focus/f190-attached-title-and-hearts.png) ·
[Profile badge at 28.24 s](review/focus/f706-attached-profile-badge.png)

**HyperFrames 0.9.77 passed its visual thresholds.** Its mean SSIM moved from
0.9731 to 0.9733. All six cuts aligned at
5.36, 6.40, 8.52, 16.04, 27.72 and 30.80 s. All 202 files in the official reviewer
copy verified against its manifest.
[HyperFrames report](review/hyperframes.json) ·
[Ranked comparison sheet](review/hyperframes/worst.jpg) ·
[Pinned reviewer and license](../hyperframes-review/vendor/hyperframes/UPSTREAM.md)

29 of 29 edited frames improved before encoding.
29 improved in the decoded MP4. The other 749
lossless frames, authored audio stems, audio cue map and AAC stream match the
previous candidate by hash.
[Lossless measurements](review/stage-metrics.json)

Source SHA-256  
`f821bb58cbdb265a75d572616d0da723e9cfb6de31e3db5f8a17d94dc15b5327`

Candidate MP4 SHA-256  
`493e132cf2b861ed79b46d4c6e84075f9305c5621bc686285bb42937d5fcb6d0`

## Rerun the review

Set `SOURCE` to the locked source and use a fresh review directory.

```sh
PYTHON=/path/to/render-environment/bin/python \
HYPERFRAMES=/path/to/hyperframes \
bash review.sh "$SOURCE" "$PWD/candidate/sidehoe.mp4" "$PWD/review-rerun"

/path/to/render-environment/bin/python focus.py \
  "$SOURCE" ../profile-arrival-review/candidate/sidehoe.mp4 \
  candidate/sidehoe.mp4 review-rerun/focus
```
