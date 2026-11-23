# Sidehoe profile reveal and follow-up handset review

November 21, 2026. The [candidate MP4](candidate/sidehoe.mp4) was rendered from a clean
copy of the [editable project](project/README.md).

[Watch the source and candidate side by side](review/side-by-side.mp4) ·
[Step through all 778 matched frame pairs](review/native/index.html)

## Edits

- At f260–270, Lisa, Ella and Maria use separate disk and face
  positions and focus. The names, tags and emoji have independent
  positions and appear at the measured points in the reveal.
- At f650–659, the handset’s camera and directional exposure follow
  the pre-contact move. The cursor has a separate editable track.

The Motion library supplied 35 native source crops across 4 tracks.
All crop hashes, dimensions and presentation times verified.
Editing a portrait position, a profile name, an interest tag and the
handset exposure in a clean copy changed their visible regions.
[Motion observations](review/motion/motion-observations.json) ·
[Editability evidence](review/editability.json)

| Source time | Matched screenshots | Previous mean RGB error | Revised mean RGB error |
| --- | --- | ---: | ---: |
| 10.36 s | [Before the profile reveal adjustment](review/focus/f259-profile-reveal-before-tracked-faces.png) | 0.70 | 0.70 |
| 10.40 s | [Lisa and Ella enter](review/focus/f260-profile-reveal-lisa-and-ella-enter.png) | 1.29 | 0.89 |
| 10.52 s | [Names and tags begin](review/focus/f263-profile-reveal-names-and-tags-begin.png) | 2.84 | 1.08 |
| 10.56 s | [Frame before the largest difference](review/focus/f264-profile-reveal-before-largest-mismatch.png) | 3.95 | 1.24 |
| 10.60 s | [All three profiles during the reveal](review/focus/f265-profile-reveal-three-actors.png) | 4.90 | 1.38 |
| 10.64 s | [Next reveal frame](review/focus/f266-profile-reveal-next-names-and-tags.png) | 4.73 | 1.57 |
| 10.76 s | [Faces settling](review/focus/f269-profile-reveal-faces-settling.png) | 2.32 | 1.99 |
| 10.84 s | [First held profile frame](review/focus/f271-profile-reveal-first-held-frame.png) | 2.25 | 2.26 |
| 25.96 s | [Before the follow-up exposure adjustment](review/focus/f649-follow-up-before-exposure-adjustment.png) | 3.98 | 3.98 |
| 26.20 s | [Handset before contact](review/focus/f655-follow-up-handset-moving-before-contact.png) | 4.15 | 4.00 |
| 26.32 s | [Handset and cursor before the push](review/focus/f658-follow-up-handset-and-cursor-before-push.png) | 4.90 | 4.50 |
| 26.36 s | [Last edited follow-up frame](review/focus/f659-follow-up-last-edited-handset-frame.png) | 4.41 | 4.25 |
| 26.40 s | [First follow-up close-up](review/focus/f660-follow-moving-closeup-entry.png) | 3.57 | 3.57 |

Each row compares the same crop and frame from the three encoded files.
[Selected crop bounds and metrics](review/focus/metrics.csv) ·
[Previous candidate](../inbox-contacts-review/README.md)

## Final MP4 review

**Exact comparison failed.** The final mux decodes cleanly, and all 778 frame indices,
presentation times and exclusive end times match at 2000 × 2000 and 25 fps.
Whole-film mean RGB error moved from 2.737 to 2.716.
The reviewer found 0 pixel-identical frames. The last frame differs by
23 pixels. The highest remaining whole-frame RGB error is 4.88
at f142 (5.68 s).
[Exact verdict](review/native/report.json) ·
[All frame measurements](review/native/frames.csv) ·
[Highest-error frame](review/native/pairs/000142.jpg)

At 10.60 s, the portraits and tag silhouettes are closer. The
source’s partial letters and blurred tag shapes still differ during
their entrance. At 26.32 s, the handset exposure is closer and
the casing edge and some of the key shapes still differ.
[Title and hearts at 7.60 s](review/focus/f190-attached-title-and-hearts.png) ·
[Profile badge at 28.24 s](review/focus/f706-attached-profile-badge.png)

**HyperFrames 0.9.77 passed its visual thresholds.** Its mean SSIM moved from
0.9729 to 0.9731. All six cuts aligned at
5.36, 6.40, 8.52, 16.04, 27.72 and 30.80 s. All 202 files in the official reviewer
copy verified against its manifest.
[HyperFrames report](review/hyperframes.json) ·
[Ranked comparison sheet](review/hyperframes/worst.jpg) ·
[Pinned reviewer and license](../hyperframes-review/vendor/hyperframes/UPSTREAM.md)

21 of 21 edited frames improved before encoding.
21 improved in the decoded MP4. The other 757
lossless frames, authored audio stems, audio cue map and AAC stream match the
previous candidate by hash.
[Lossless measurements](review/stage-metrics.json)

Source SHA-256  
`f821bb58cbdb265a75d572616d0da723e9cfb6de31e3db5f8a17d94dc15b5327`

Candidate MP4 SHA-256  
`217221b9a5f9bf5b49bea2158ea359234b04a86080cb6831f094be0bec5de649`

## Rerun the review

Set `SOURCE` to the locked source and use a fresh review directory.

```sh
PYTHON=/path/to/render-environment/bin/python \
HYPERFRAMES=/path/to/hyperframes \
bash review.sh "$SOURCE" "$PWD/candidate/sidehoe.mp4" "$PWD/review-rerun"

/path/to/render-environment/bin/python focus.py \
  "$SOURCE" ../inbox-contacts-review/candidate/sidehoe.mp4 \
  candidate/sidehoe.mp4 review-rerun/focus
```
