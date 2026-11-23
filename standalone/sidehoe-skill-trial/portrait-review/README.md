# Sidehoe portrait cluster and profile review

November 21, 2026. The prior column uses the
[calendar handoff export](../handoff-review/candidate/sidehoe.mp4).
The [revised export](candidate/sidehoe.mp4) came from a clean copy of the
[editable project](project/README.md).

[Watch the same-time comparison, source on the left](review/side-by-side.mp4) ·
[Step through all 778 frame pairs](review/native/index.html)

## What changed

The portrait cluster now uses independently registered disks, colors
and portrait bounds. An editable outer path drives the lavender surround
and shades inward toward the center. That plate carries into the first
four frames of the existing wipe. The three profile cards now use
measured disk positions and gradients, independent names and interest
chips, and Lisa’s wink. The heads are supplied by the project’s editable
asset layers. The source frame measurements serve as geometry and color
references.

The Motion library extracted 20 source crops around the pink and cyan
cluster disks and Lisa’s profile. The crops match the motion plan,
source hash and source presentation times.
[Motion plan](review/motion-plan.json) ·
[Hashed source observations](review/motion/motion-observations.json)

## Checked in the encoded export

| Time | Compared area | Prior RGB error | Revised RGB error |
| --- | --- | ---: | ---: |
| 8.72 s | [Cluster entrance](review/focus/f218-cluster-registered-entrance.png) | 3.37 | 1.30 |
| 9.04 s | [Cluster at its prior largest mismatch](review/focus/f226-cluster-largest-prior-mismatch.png) | 8.34 | 1.51 |
| 9.08 s | [Next cluster frame](review/focus/f227-cluster-next-frame.png) | 4.53 | 1.51 |
| 10.20 s | [Portrait wipe in motion](review/focus/f255-portrait-wipe-moving.png) | 5.74 | 3.11 |
| 11.00 s | [Profile disks, names and interest chips](review/focus/f275-profile-wink-and-interest-chips.png) | 23.45 | 6.10 |
| 11.44 s | [Profile row before focus acceleration](review/focus/f286-profile-before-focus-acceleration.png) | 6.15 | 2.79 |

The 11.00 s measurement uses the profile-card crop. The other rows
measure the whole frame. All 56 edited frames improved on decoded
whole-frame mean absolute RGB error. The portraits’ hair, expression
and interest-chip details still differ from the reference. The two
supplied screenshot comparisons remain open.
[Title and hearts at 7.60 s](review/focus/f190-attached-title-and-hearts.png) ·
[Closing badge at 28.24 s](review/focus/f706-attached-profile-badge.png)

## Full export verdict

**HyperFrames 0.9.77 passes** and detects all six source cuts, including
the 16.04 s calendar handoff. Mean SSIM is 0.9665. All 202 copied
reviewer files verified against the pinned manifest.
[HyperFrames verdict](review/hyperframes.json) ·
[Pinned reviewer source and license](../hyperframes-review/vendor/hyperframes/UPSTREAM.md)

**The exact native comparison fails.** All 778 frame indices, start
timestamps and exclusive end timestamps agree at 2000 × 2000 and
25 fps. Zero frames are pixel-identical. Mean RGB error fell from 3.740
to 3.456, and changed pixels fell from 1,271,640,663 to 1,260,493,196
across the sequence. The largest whole-frame error is 7.97 at 12.64 s,
where the early handset body and screen travel at different positions
from their source counterparts.
[Early handset frame](review/focus/f316-sofia-early-handset.png) ·
[Native verdict](review/native/report.json) ·
[All frame measurements](review/native/frames.csv)

The mux decodes cleanly. Its AAC stream, stems and event map match the
previous authored export by hash. The silent side-by-side has 778
frames and a duration of 31.12 seconds.

Source SHA-256
`f821bb58cbdb265a75d572616d0da723e9cfb6de31e3db5f8a17d94dc15b5327`

Revised MP4 SHA-256
`58ecb4e2829cee0e1abc87302b3db914ff3efc6e3c4fc82a6379331bf20a2179`

## Rerun

Set `SOURCE` to the locked reference and use a fresh review directory.

```sh
PYTHON=/path/to/render-environment/bin/python \
HYPERFRAMES=/path/to/hyperframes \
bash review.sh "$SOURCE" candidate/sidehoe.mp4 review-rerun

/path/to/render-environment/bin/python focus.py \
  "$SOURCE" ../handoff-review/candidate/sidehoe.mp4 \
  candidate/sidehoe.mp4 review-rerun/focus
```
