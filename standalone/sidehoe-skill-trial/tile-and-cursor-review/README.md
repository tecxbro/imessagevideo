# Sidehoe tile, lighting and cursor review

November 21, 2026. The [candidate MP4](candidate/sidehoe.mp4) was rendered from a clean
copy of the [editable project](project/README.md) and reviewed against the locked reference.

[Watch side by side with the source on the left](review/side-by-side.mp4) ·
[Step through the same-time screenshots for all 778 frames](review/native/index.html)

## What changed

- **Calendar tile, f615–619.** The editable curves for “31” have their own position and stroke treatment.
  The upper shoulder and fold use separate light fields. The source digits still have a sharper core
  during the vertical exit.
- **Handset lighting, f136–137.** The upper rim and lower flare were fitted independently. The source
  spreads the rainbow more at the left edge, and its dark rim is rounder. The entrance at f314–328
  also registers the outer case, glass, conversation and keyboard separately.
- **Cursor, f670–694.** The editable arrow shape now has a wider stem and rounder endpoint through
  the approach, contact and withdrawal. Visible differences remain at the stem edges and in the
  emoji and bubble behind the arrow. The original pinned inbox entrance at f0–9 also has independently
  timed status streaks, pinned contacts, note and first two rows.

The Motion library extracted 45 native crops across 7 tracks.
All 45 crop hashes and presentation times verified. The selected blue-dot
mask found no matching pixels at f4 and found the dot from f5. Reopening a clean copy
and editing the inbox note, Sofia reply, “31” placement and cursor contour changed the
corresponding regions. [Motion observations](review/motion/motion-observations.json) ·
[Edit evidence](review/editability.json)

| Time | Same-time source, previous export and revised export | Previous mean RGB error | Revised mean RGB error |
| --- | --- | ---: | ---: |
| 0.00 s | [Opening streaks](review/focus/f000-opening-streaks-and-central-pin.png) | 1.19 | 0.48 |
| 0.36 s | [Pins, note and inbox rows](review/focus/f009-inbox-last-entrance-registration.png) | 6.03 | 3.58 |
| 5.44 s | [Glossy reveal lighting](review/focus/f136-handset-and-lower-refraction.png) | 5.83 | 5.75 |
| 12.76 s | [Sofia’s handset entrance](review/focus/f319-sofia-entrance-exit.png) | 5.83 | 4.92 |
| 24.76 s | [Calendar tile at exit](review/focus/f619-calendar-tile-last-visible-finish.png) | 6.15 | 5.80 |
| 27.00 s | [Cursor at contact](review/focus/f675-follow-cursor-contact-outline.png) | 7.65 | 7.29 |
| 27.40 s | [Cursor during the hold](review/focus/f685-follow-cursor-native-hull.png) | 14.52 | 13.13 |
| 27.76 s | [Cursor withdrawing](review/focus/f694-follow-cursor-native-hull.png) | 10.99 | 10.71 |

Scores are mean absolute RGB errors on the same crop in the two encoded exports.
The [selected frame measurements](review/focus/metrics.csv) give the crop bounds.
The [previous candidate](../inbox-and-lens-review/README.md) is the baseline.

## Full export verdict

**Exact comparison failed.** The mux decodes cleanly and all 778 frames align by index,
presentation time and exclusive end time at 2000 × 2000 and 25 fps. Whole-film mean RGB
error moved from 2.911 to 2.867.
Zero frames are pixel-identical. The last frame differs by 23 pixels. The glossy handset
at f136 has the highest mean RGB error, 5.75.
[Exact verdict](review/native/report.json) · [Measurements for every frame](review/native/frames.csv)

**HyperFrames 0.9.77 passed its visual thresholds.** Its mean SSIM rose from
0.9711 to 0.9715.
It found the same six cuts at 5.36, 6.40, 8.52, 16.04, 27.72 and 30.80 s.
All 202 files in the official reviewer copy verified against the pinned file manifest.
[HyperFrames report](review/hyperframes.json) ·
[Ranked comparison sheet](review/hyperframes/worst.jpg) ·
[Pinned reviewer code and license](../hyperframes-review/vendor/hyperframes/UPSTREAM.md)

All 56 edited lossless frames improved on mean RGB error. Of those, 54 also improved
in the decoded export. The full-frame error increased slightly at f674 and f693.
The other 722 lossless frames, authored audio stems, cue map and AAC payload match
the preceding baseline by hash.
[Opening, lighting and Sofia render measurements](review/stage-metrics.json) ·
[Tile and cursor render measurements](review/tile-and-cursor-stage-metrics.json)

The title and hearts at 7.60 s and the profile badge at 28.24 s still have the same crop
errors as the previous candidate. [Title and hearts](review/focus/f190-attached-title-and-hearts.png) ·
[Profile badge](review/focus/f706-attached-profile-badge.png)

Source SHA-256  
`f821bb58cbdb265a75d572616d0da723e9cfb6de31e3db5f8a17d94dc15b5327`

Candidate MP4 SHA-256  
`fdcea5386252eec71ae71835ec7f4beb4b666f53b711cd37a6990da3a0f26952`

## Rerun the review

Set `SOURCE` to the locked reference and use a fresh review directory.

```sh
PYTHON=/path/to/render-environment/bin/python \
HYPERFRAMES=/path/to/hyperframes \
bash review.sh "$SOURCE" "$PWD/candidate/sidehoe.mp4" "$PWD/review-rerun"

/path/to/render-environment/bin/python focus.py \
  "$SOURCE" ../inbox-and-lens-review/candidate/sidehoe.mp4 \
  candidate/sidehoe.mp4 review-rerun/focus
```
