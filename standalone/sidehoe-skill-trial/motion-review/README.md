# Sidehoe handset motion review

November 21, 2026. The prior column uses the
[conversation and portrait wipe export](../thread-review/candidate/sidehoe.mp4).
The new column uses the [revised export](candidate/sidehoe.mp4), rendered
from a clean copy of the [editable project](project/README.md).

**Picture fidelity remains open.** The decoder completed all 778 frames
at 2000 × 2000 and 25 fps. Every frame index, presentation timestamp and
exclusive frame end matches the source. Mean absolute RGB error fell from
3.864 to 3.800 on the 0–255 scale. No frame is pixel-identical. The raw
count of pixels with any channel difference increased from 1,272,631,356
to 1,274,763,348 across the export. The last frame differs by one level
in 23 pixels. [Full native measurements](review/native/frames.csv) ·
[Exact verdict](review/native/report.json)

## Changes and same-time checks

The first handset pass now extends the casing past the viewport and
evaluates the exposed rails between measured contours. The entrance has
separate parameters for the Messages title distortion, Sidehoe pin,
prismatic rim and lower rail light. The Sofia pullback and follow-up push
carry independent positions for bubble ink, screen edges and keyboard
rows. The cursor keeps its separate visible tip and focus track. The
calendar handoff has independent bounds and vertical exposure for the
appointment bars and time captions.

| Time | Compared area | Prior RGB error | Revised RGB error |
| --- | --- | ---: | ---: |
| 5.36 s | [First handset and pin](review/focus/f134-first-handset-and-pin.png) | 9.39 | 7.55 |
| 5.44 s | [Lower rail refraction](review/focus/f136-handset-and-lower-refraction.png) | 9.19 | 7.58 |
| 14.16 s | [Sofia pullback](review/focus/f354-sofia-pullback-registration.png) | 9.22 | 3.61 |
| 16.04 s | [Calendar handoff](review/focus/f401-calendar-handoff.png) | 2.48 | 2.40 |
| 24.52 s | [Curved calendar tile and numerals](review/focus/f613-calendar-tile-face.png) | 4.41 | 4.41 |
| 26.80 s | [Follow-up cursor approach and handset](review/focus/f670-follow-cursor-approach.png) | 8.84 | 4.76 |
| 26.84 s | [Follow-up just before the close-up](review/focus/f671-follow-before-closeup.png) | 9.30 | 4.85 |

The calendar tile still differs in face shading and the shape of the
surrounding tiles. The cursor still differs in its edges as it approaches
the Yes control. The supplied screenshot regions remain open at
[7.60 s for the title and hearts](review/focus/f190-attached-title-and-hearts.png)
and [28.24 s for the profile badge](review/focus/f706-attached-profile-badge.png).
Their crop errors are 10.10 and 3.88 respectively. The highest remaining
whole-frame error is 8.58 at [13.64 s in Sofia's push](review/focus/f341-sofia-before-revision.png).

The Motion library's previous extraction for this same source covers the
calendar tile, both handset rails and the follow-up cursor. The extraction
missed the fading tile at f621–622 and cursor at f695–696. The native
comparison covers those frames as well. [Source motion observations](../hyperframes-review/motion-evidence/motion-observations.json)

## Review and export

HyperFrames 0.9.77 measured mean SSIM at 0.9644, up from 0.9637, and
still flags the calendar transition at 16.04 s. Using the reviewer's
64 × 36 gray signature, the source's change is 12.97 against a nearby
median of 3.22, and the revised change is 12.59 against 3.22.
The revised transition remains below the published fourfold threshold.
The pinned reviewer copy and its 202-file manifest predate these changes.
[HyperFrames findings](review/hyperframes.json) ·
[Reviewer source and license](../hyperframes-review/vendor/hyperframes/UPSTREAM.md)

The clean source render changes 31 frames across f134–137, f352–354,
f401–412 and f660–671. The mux's 48 kHz AAC stream, sound stems and event
map match the previous export by hash. The original audio differs from
this procedural mix. The side-by-side review video is silent, puts the
source on the left, and contains all 778 matching presentation times.
[Side-by-side video](review/side-by-side.mp4) ·
[Frame-by-frame viewer](review/native/index.html) ·
[Focused measurements](review/focus/metrics.csv)

Source SHA-256
`f821bb58cbdb265a75d572616d0da723e9cfb6de31e3db5f8a17d94dc15b5327`

Revised MP4 SHA-256
`ce7e8d5ba4d783cb5b1ea2cd33b6b1207b710f4bdd56c9aca166a147614ec04e`

To rerun review from this directory, point `SOURCE` at the locked source
and use a fresh output directory.

```sh
PYTHON=/path/to/render-environment/bin/python \
HYPERFRAMES=/path/to/hyperframes \
bash review.sh "$SOURCE" candidate/sidehoe.mp4 review-rerun

/path/to/render-environment/bin/python focus.py \
  "$SOURCE" ../thread-review/candidate/sidehoe.mp4 \
  candidate/sidehoe.mp4 review-rerun/focus
```
