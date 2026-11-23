# Sidehoe handset pullback and profile motion review

November 21, 2026. The [candidate MP4](candidate/sidehoe.mp4) came from a
clean copy of the [editable project](project/README.md).

[Watch the same-time comparison, source on the left](review/side-by-side.mp4) ·
[Step through all 778 frame pairs](review/native/index.html)

The profile push now registers the measured disk contours, caption and chip
positions, and the light washing over Ella. During the follow-up pullback,
the history, header, keyboard and controls move separately from the casing.
The cursor has its own fitted silhouette, softness and opacity. The Motion
library extracted 13 measurements for the right rail, cursor, and profile
disks. Each measurement was checked against its source crop and timestamp.
[Motion plan](review/motion-plan.json) ·
[Source measurements](review/motion/motion-observations.json)

| Time | Decoded comparison | Prior mean RGB error | Revised mean RGB error |
| --- | --- | ---: | ---: |
| 10.80 s | [Profile arrival](review/native/pairs/000270.jpg) | 6.51 | 2.46 |
| 11.48 s | [Profile push](review/native/pairs/000287.jpg) | 6.78 | 3.33 |
| 11.52 s | [Ella's disk during the push](review/native/pairs/000288.jpg) | 6.57 | 2.43 |
| 27.76 s | [First revised pullback frame](review/native/pairs/000694.jpg) | 6.96 | 4.56 |
| 27.80 s | [Second revised pullback frame](review/native/pairs/000695.jpg) | 6.45 | 4.26 |
| 27.80 s | [Tight crop of the cursor's last trace](review/focus/f695-cursor-last-visible-trace.png) | 10.03 | 7.34 |

All 32 edited frames improved in the lossless render and the decoded MP4.
The other 746 lossless frames match the preceding export by hash. The
authored stems, cue map and AAC stream also match by hash. The selected
portrait assets still differ in expression and lighting, and the handset
header and cursor outline remain visibly different during the pullback.
[Same-time detail crops and metrics](review/focus/metrics.csv)

## Full export verdict

**HyperFrames 0.9.77 passed.** It found all six cuts at 5.36, 6.40, 8.52,
16.04, 27.72, and 30.80 s. Mean SSIM rose from 0.9683 to 0.9687. All 202
files in the pinned reviewer copy verified against its manifest.
[HyperFrames verdict](review/hyperframes.json) ·
[Pinned reviewer and license](../hyperframes-review/vendor/hyperframes/UPSTREAM.md)

**The native pixel comparison failed.** The encoded film decodes cleanly
and all 778 frames match the 2000 × 2000 reference's 25 fps presentation
and exclusive end timestamps. Mean absolute RGB error fell from 3.250
to 3.177. Zero frames are pixel-identical. The final frame differs by 23
pixels. The highest mean RGB error is 6.73 at 26.40 s, where the follow-up
handset begins pushing close. The render is still softer than the source
and frames the status area differently.
[Native verdict](review/native/report.json) ·
[Decoded frame measurements](review/native/frames.csv) ·
[Follow-up push](review/native/pairs/000660.jpg)

The calendar tile's glyphs and highlights, the handset lighting, the
cursor at contact, and the attached title and badge remain open in the
exact comparison.
[Calendar tile](review/focus/f613-calendar-tile-face.png) ·
[Handset refraction](review/focus/f136-handset-and-lower-refraction.png) ·
[Cursor contact](review/focus/f675-follow-cursor-contact.png) ·
[Title and hearts](review/focus/f190-attached-title-and-hearts.png) ·
[Profile badge](review/focus/f706-attached-profile-badge.png)

Source SHA-256  
`f821bb58cbdb265a75d572616d0da723e9cfb6de31e3db5f8a17d94dc15b5327`

Candidate MP4 SHA-256  
`803b71eba9d3144ed1a07e77c39fdf6202b2a161fd22a4f7addf99e7e1f6190e`

Set `SOURCE` to the locked source and use a fresh review directory.

```sh
PYTHON=/path/to/render-environment/bin/python \
HYPERFRAMES=/path/to/hyperframes \
bash review.sh "$SOURCE" "$PWD/candidate/sidehoe.mp4" "$PWD/review-rerun"

/path/to/render-environment/bin/python focus.py \
  "$SOURCE" ../inbox-review/candidate/sidehoe.mp4 \
  candidate/sidehoe.mp4 review-rerun/focus
```
