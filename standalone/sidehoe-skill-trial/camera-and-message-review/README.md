# Sidehoe camera cutout and message review

November 21, 2026. The [candidate MP4](candidate/sidehoe.mp4) was rendered from a clean
copy of the [editable project](project/README.md).

[Watch the source and candidate side by side](review/side-by-side.mp4) ·
[Step through all 778 matched frame pairs](review/native/index.html)

## Edits

- The camera cutout has an editable dark outline, separate sensor window,
  and its own lens reflections through f134–161. The lower rainbow flare
  follows the casing in f136–137.
- Natalie’s portrait, name, preview and timestamp have separate positions
  through the handset reveal. The first gray reply during the cursor hold
  follows its measured shape and color at f671–693.
- The closing badge uses finer sampling of its editable curves during the
  profile reveal.

The Motion library supplied 37 native source crops across 4 tracks.
All crop hashes, dimensions and presentation times verified.
Editing the camera outline, Natalie’s name, the first reply and the badge
in a clean copy changed their visible regions.
[Motion observations](review/motion/motion-observations.json) ·
[Editability evidence](review/editability.json)

| Source time | Matched screenshots | Previous mean RGB error | Revised mean RGB error |
| --- | --- | ---: | ---: |
| 5.36 s | [Camera cutout first visible](review/focus/f134-first-handset-and-pin.png) | 4.96 | 4.43 |
| 5.40 s | [Camera during the upper refraction](review/focus/f135-handset-and-upper-refraction.png) | 5.13 | 4.79 |
| 5.44 s | [Camera cutout, Natalie’s row and lower flare](review/focus/f136-handset-and-lower-refraction.png) | 5.26 | 4.31 |
| 5.48 s | [Next frame of the reveal](review/focus/f137-last-handset-refraction.png) | 4.86 | 4.06 |
| 6.20 s | [Camera under pink light](review/focus/f155-handset-status-during-pink-wash.png) | 4.23 | 4.14 |
| 27.12 s | [First reply before the cursor holds](review/focus/f678-follow-first-reply-before-contact-hold.png) | 6.22 | 5.79 |
| 27.24 s | [First reply and held cursor](review/focus/f681-follow-first-reply-and-cursor-hold.png) | 6.26 | 5.81 |
| 27.48 s | [First reply before withdrawal](review/focus/f687-follow-first-reply-before-withdrawal.png) | 6.06 | 5.60 |
| 28.24 s | [Profile badge](review/focus/f706-attached-profile-badge.png) | 2.99 | 2.97 |

Each row compares the same crop and frame from the three encoded files.
[Selected crop bounds and metrics](review/focus/metrics.csv) ·
[Previous candidate](../handset-rim-review/README.md)

## Final MP4 review

**Exact comparison failed.** The final mux decodes cleanly, and all 778 frame indices,
presentation times and exclusive end times match at 2000 × 2000 and 25 fps.
Whole-film mean RGB error moved from 2.849 to 2.834.
The reviewer found 0 pixel-identical frames. The last frame differs by
23 pixels. The highest remaining whole-frame RGB error is 5.11
at f346 (13.84 s).
[Exact verdict](review/native/report.json) ·
[All frame measurements](review/native/frames.csv) ·
[Highest-error frame](review/native/pairs/000346.jpg)

At 5.44 s, the capsule is closer in shape and Natalie’s name is closer in
position. The source still has a different spectrum on the top rim and the
bottom corners. During the cursor hold, the first gray reply has a closer
outline and its letters still read shorter than the source in some frames.
The profile badge still differs around its card edges and outline.
[Title and hearts at 7.60 s](review/focus/f190-attached-title-and-hearts.png)

**HyperFrames 0.9.77 passed its visual thresholds.** Its mean SSIM moved from
0.9717 to 0.9718. All six cuts aligned at
5.36, 6.40, 8.52, 16.04, 27.72 and 30.80 s. All 202 files in the official reviewer
copy verified against its manifest.
[HyperFrames report](review/hyperframes.json) ·
[Ranked comparison sheet](review/hyperframes/worst.jpg) ·
[Pinned reviewer and license](../hyperframes-review/vendor/hyperframes/UPSTREAM.md)

65 of 65 edited frames improved before encoding.
64 improved in the decoded MP4. The decoded error increased on f700. The other 713
lossless frames, authored audio stems, audio cue map and AAC stream match the
previous candidate by hash.
[Lossless measurements](review/stage-metrics.json)

Source SHA-256  
`f821bb58cbdb265a75d572616d0da723e9cfb6de31e3db5f8a17d94dc15b5327`

Candidate MP4 SHA-256  
`9582f1600b6591c3652895742bae681d83db26970c4e6e285de9253f69acd989`

## Rerun the review

Set `SOURCE` to the locked source and use a fresh review directory.

```sh
PYTHON=/path/to/render-environment/bin/python \
HYPERFRAMES=/path/to/hyperframes \
bash review.sh "$SOURCE" "$PWD/candidate/sidehoe.mp4" "$PWD/review-rerun"

/path/to/render-environment/bin/python focus.py \
  "$SOURCE" ../handset-rim-review/candidate/sidehoe.mp4 \
  candidate/sidehoe.mp4 review-rerun/focus
```
