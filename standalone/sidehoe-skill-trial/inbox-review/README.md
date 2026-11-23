# Sidehoe inbox and glossy handset review

November 21, 2026. The [latest MP4](candidate/sidehoe.mp4) came from a
clean copy of the [editable project](project/README.md).

[Watch the same-time comparison, source on the left](review/side-by-side.mp4) ·
[Step through all 778 frame pairs](review/native/index.html)

## Inbox before the scroll

The header, pinned contacts, and rows use independent timing at
f10–41. The first two unread dots establish the row position and
spacing. The clock and heading retain editable text and use separate
measured ink boxes. The 746 authored PNGs outside the revised inbox
window match the preceding export by hash.

The Motion library extracted 20 measurements of the unread dots and
Marie’s pinned background. Their output crop hashes, measured bounds,
and presentation times verified against the locked source.
[Motion plan](review/motion-plan.json) ·
[Source observations](review/motion/motion-observations.json)

| Time | Whole-frame comparison | Prior mean RGB error | Revised mean RGB error |
| --- | --- | ---: | ---: |
| 0.36 s | [Before the revised inbox window](review/focus/f009-inbox-pre-registration-control.png) | 6.03 | 6.03 |
| 0.40 s | [Inbox header and rows](review/focus/f010-inbox-first-registered-header-and-rows.png) | 6.16 | 4.27 |
| 1.48 s | [Rows approaching the scroll](review/focus/f037-inbox-pre-scroll-row-motion.png) | 7.39 | 4.73 |
| 1.64 s | [Last registered inbox frame](review/focus/f041-inbox-last-registered-frame.png) | 7.52 | 4.92 |
| 1.68 s | [First measured scroll frame](review/focus/f042-inbox-first-scroll-frame.png) | 5.60 | 5.60 |

All 32 edited inbox frames improved in the decoded export. The portrait
details, pinned note, row lettering, and dividers still differ, and the
native case-specific regions fail the exact comparison.
[Inbox region results](review/native/report.json)

## Glossy handset revision retained

The handset’s separately registered status symbols and heading, contact
positions, and top and side bevels remain in this export. The preceding
handset revision improved all 28 edited encoded frames. At 5.44 s,
mean RGB error fell from 7.58 to 6.17. The lower flare and portrait
detail still differ. The title and hearts crop at 7.60 s rose from
3.88928 to 3.89454 when that revision was encoded. Its lossless title
frames are identical to the preceding revision.
[Glossy handset close-up](review/focus/f136-handset-and-lower-refraction.png) ·
[Glossy handset report](../glossy-review/README.md)

## Full export verdict

**HyperFrames 0.9.77 passed.** It found all six cuts at 5.36, 6.40, 8.52,
16.04, 27.72, and 30.80 s. Mean SSIM is 0.9683. All 202 files in the
pinned reviewer copy verified against its manifest.
[HyperFrames verdict](review/hyperframes.json) ·
[Pinned reviewer and license](../hyperframes-review/vendor/hyperframes/UPSTREAM.md)

**The native pixel comparison failed.** All 778 frames match the
reference indices and presentation and exclusive end timestamps at
2000 × 2000 and 25 fps. Zero frames are pixel-identical. Mean RGB error
fell from 3.305 to 3.250 in the inbox revision. Changed pixel
observations fell from 1,259,361,184 to 1,258,453,208. The final frame
differs by 23 pixels. The mux decodes cleanly. Its AAC stream,
authored stems, and cue map match the preceding export by hash.
[Native verdict](review/native/report.json) ·
[All decoded frame measurements](review/native/frames.csv)

The largest remaining whole-frame miss is the follow-up handset pullback
at 27.76 s, with mean RGB error of 6.96. The history and keyboard soften
and move differently in that passage. The attached title and badge
crops, calendar tile, and cursor contact still show local differences.
[Follow-up pullback](review/native/pairs/000694.jpg) ·
[Title and hearts](review/focus/f190-attached-title-and-hearts.png) ·
[Closing badge](review/focus/f706-attached-profile-badge.png) ·
[Calendar tile](review/focus/f613-calendar-tile-face.png) ·
[Cursor contact](review/focus/f675-follow-cursor-contact.png)

Source SHA-256  
`f821bb58cbdb265a75d572616d0da723e9cfb6de31e3db5f8a17d94dc15b5327`

Revised MP4 SHA-256  
`c18264b5babd0b1605254ce17b879ce43be2093e6f39ddf619d5bd6f3778fdca`

Set `SOURCE` to the locked reference and use a fresh review directory.

```sh
PYTHON=/path/to/render-environment/bin/python \
HYPERFRAMES=/path/to/hyperframes \
bash review.sh "$SOURCE" candidate/sidehoe.mp4 review-rerun

/path/to/render-environment/bin/python focus.py \
  "$SOURCE" ../glossy-review/candidate/sidehoe.mp4 \
  candidate/sidehoe.mp4 review-rerun/focus
```
