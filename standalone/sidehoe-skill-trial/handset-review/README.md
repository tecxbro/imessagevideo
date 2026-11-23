# Sidehoe handset entrance review

November 21, 2026. The [revised export](candidate/sidehoe.mp4) came from
a clean copy of the [editable project](project/README.md). The previous
export was the [portrait revision](../portrait-review/candidate/sidehoe.mp4).

[Watch the same-time comparison, source on the left](review/side-by-side.mp4) ·
[Step through all 778 frame pairs](review/native/index.html)

## Handset entrance

The lower bevel and two silver rails use separately measured widths.
The Messages screen follows its own position, proportions, and shutter
spread. The home indicator follows an independent stage track.
The scene's editable copy supplies the outgoing reply. Source pixels
were used for measurement and review.

The Motion library recorded 12 landmark samples for the rail and
outgoing reply. Each sample's crop hash and presentation timestamp
verified against the locked source.
[Motion plan](review/motion-plan.json) ·
[Source observations](review/motion/motion-observations.json)

| Time | Frame evidence | Prior mean RGB error | Revised mean RGB error |
| --- | --- | ---: | ---: |
| 12.48 s | [Before the entrance](review/focus/f312-sofia-entrance-before.png) | 4.05 | 4.05 |
| 12.56 s | [Lower rail and screen appear](review/focus/f314-sofia-case-lower-light.png) | 5.67 | 3.37 |
| 12.64 s | [Handset and keyboard in motion](review/focus/f316-sofia-early-handset.png) | 7.97 | 4.39 |
| 12.72 s | [First visible top rail](review/focus/f318-sofia-first-visible-top-rail.png) | 7.96 | 5.53 |
| 12.76 s | [Handset settles](review/focus/f319-sofia-entrance-exit.png) | 7.43 | 5.82 |
| 13.20 s | [Last registered home indicator](review/focus/f330-sofia-home-indicator-last-registered.png) | 5.52 | 5.45 |
| 13.24 s | [After the edited frames](review/focus/f331-sofia-entrance-after.png) | 5.66 | 5.67 |

All 18 modified stage frames improved on decoded whole-frame mean
absolute RGB error. The two exact region checks still show differences.
The whole frame at 13.24 s changed from 5.66491 to 5.66510 on re-encode,
with identical authored PNGs at that time. The keyboard and rail
differences remain visible even at 12.64 s.
[Case and display difference](review/native/crops/67-worst.png) ·
[Home indicator region difference](review/native/crops/68-worst.png)

## Full export verdict

**HyperFrames 0.9.77 passed.** It found all six cuts at 5.36, 6.40, 8.52,
16.04, 27.72, and 30.80 s. Mean SSIM was 0.9667. The 202 copied reviewer
files verified against their pinned manifest.
[HyperFrames verdict](review/hyperframes.json) ·
[Reviewer source and license](../hyperframes-review/vendor/hyperframes/UPSTREAM.md)

**The native pixel comparison failed.** At 2000 × 2000 and 25 fps,
all 778 frame indices, start timestamps, and exclusive end timestamps
match the reference. Zero frames are pixel-identical. Whole-film mean
absolute RGB error fell from 3.456 to 3.434. The number of changed pixel
observations fell from 1,260,493,196 to 1,260,268,528. The final frame
differs by 23 pixels. The mux decodes cleanly, and the AAC stream, authored
stems, and cue map match the previous export by hash.
[Native verdict](review/native/report.json) ·
[Per-frame measurements](review/native/frames.csv)

The largest remaining whole-frame error is 7.89 at 26.36 s. The
keyboard rows, lettering, status area and casing in the follow-up
handset still diverge. The title and hearts, closing badge, calendar
tile and cursor still have local differences in the same-time crops.
[Follow-up handset](review/focus/f659-follow-before-moving-closeup.png) ·
[Title and hearts](review/focus/f190-attached-title-and-hearts.png) ·
[Closing badge](review/focus/f706-attached-profile-badge.png) ·
[Calendar tile](review/focus/f613-calendar-tile-face.png) ·
[Cursor contact](review/focus/f675-follow-cursor-contact.png)

Source SHA-256  
`f821bb58cbdb265a75d572616d0da723e9cfb6de31e3db5f8a17d94dc15b5327`

Revised MP4 SHA-256  
`4f8842b2a44e4c7dabd647d7ac3a63ceaf2a6097f8e45e9b1821ff4ca9f42126`

## Rerun

Set `SOURCE` to the locked reference and use a fresh review directory.

```sh
PYTHON=/path/to/render-environment/bin/python \
HYPERFRAMES=/path/to/hyperframes \
bash review.sh "$SOURCE" candidate/sidehoe.mp4 review-rerun

/path/to/render-environment/bin/python focus.py \
  "$SOURCE" ../portrait-review/candidate/sidehoe.mp4 \
  candidate/sidehoe.mp4 review-rerun/focus
```
