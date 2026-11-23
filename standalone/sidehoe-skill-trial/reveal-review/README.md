# Sidehoe handset reveal, title and badge review

November 21, 2026. The previous column in this review uses the
[optical review render](../optical-review/candidate/sidehoe.mp4). The revised
column uses the [new MP4](candidate/sidehoe.mp4) rendered from a clean copy
of the [editable project](project/README.md).

## Export verdict

All 778 decoded frames have the same start and end timestamps as the
source. Both files run for 31.12 seconds at 2000 × 2000 and 25 fps.
Mean whole-film RGB error fell from 4.27 to 4.09 on a 0–255 scale.
The native exact check still fails with 0 of 778 pixel-identical frames.
Even the final black frame has 23 differing pixels, each by one level.
The largest remaining whole-frame error is 10.26 at 13.92 seconds.
[Exact report](review/native/report.json) · [13.92 s frame pair](review/native/pairs/000348.jpg)

| Time | Compared area | Previous RGB error | Revised RGB error |
| --- | --- | ---: | ---: |
| 5.44 s | Whole handset entrance and rim | 10.69 | 9.19 |
| 5.60 s | Whole title and handset reveal | 10.88 | 7.23 |
| 6.28 s | Whole handset with colored light | 9.18 | 5.92 |
| 7.60 s | Supplied title and hearts crop | 15.44 | 10.10 |
| 8.36 s | Whole title exit | 4.49 | 2.63 |
| 16.04 s | Whole calendar overlap | 2.82 | 2.64 |
| 28.24 s | Supplied profile badge crop | 13.35 | 3.88 |
| 30.64 s | Whole closing fade entrance | 5.55 | 4.08 |

HyperFrames 0.9.77 measured mean SSIM of 0.9612 and still flagged 16.04
seconds. The gray-level change into that frame is 12.52 against a local
median of 3.28. The source changes by 12.97 against a median of 3.22.
The revised transition remains below the published reviewer's fourfold
criterion. The audio packet stream, render stems and all 56 cue events
match the preceding reviewed export. [HyperFrames findings](review/hyperframes.json)

The source SHA-256 is
`f821bb58cbdb265a75d572616d0da723e9cfb6de31e3db5f8a17d94dc15b5327`.
The reviewed candidate SHA-256 is
`820dc76e279f2e36e6528b660ba9f9021ab1a186f97a92a12fa677ae55dd7254`.

## Matched frames

- The handset reveal uses independent tracks for the title's left-to-right
  reveal, the phone's focus, the pinned portraits, and the first inbox row.
  The light wash now acts on the dark glass and portraits at the measured
  strength. The rim has a separately authored color split at entry.
  [5.44 s rim and inbox row](review/focus/f136-first-row-and-refraction.png)
  · [5.60 s title and phone](review/focus/f140-assistant-reveal.png)
  · [6.28 s light wash](review/focus/f157-handset-veil.png)
- The personal title's two lines and the nine moving hearts have their own
  tracks. Each text line uses separate horizontal and vertical focus on exit.
  [7.60 s title and hearts](review/focus/f190-attached-title-and-hearts.png)
  · [8.36 s title exit](review/focus/f209-personal-title-exit.png)
- The timing labels and the incoming calendar cursor move independently of
  the appointment bars. The cursor follows its own tip, rotation and optical
  spread through its entrance. [16.04 s overlap](review/focus/f401-calendar-handoff.png)
  · [16.20 s labels and cursor](review/focus/f405-calendar-labels-and-pointer.png)
- The profile badge has separate perspective-shaped rear cards, a taller
  front card and shading inside the heart. The final fade keeps the measured
  positions of the settled badge and the six caption words.
  [28.24 s profile badge](review/focus/f706-attached-profile-badge.png)
  · [30.64 s fade entrance](review/focus/f766-closing-fade-start.png)

The attachment registration from the previous pass matched both panes of
the supplied screenshots to frames 190 and 706. The crops here use those
exact frame indices and preserve the source, previous and revised columns.
[Attachment registration](../optical-review/README.md#supplied-screenshots)

## Reproduce

Render with the [project commands](project/README.md). Pass the encoded
MP4 and a fresh review directory to the review script. This uses the
published HyperFrames CLI at 0.9.77 and the native decoded RGB comparison.
The HyperFrames source was copied before the Sidehoe repairs and verified
against its manifest. [Pinned reviewer source](../hyperframes-review/vendor/hyperframes/UPSTREAM.md)

```sh
PYTHON=/path/to/render-environment/bin/python \
HYPERFRAMES=/path/to/hyperframes \
bash review.sh "$SOURCE" candidate/sidehoe.mp4 review-rerun

/path/to/render-environment/bin/python focus.py \
  "$SOURCE" ../optical-review/candidate/sidehoe.mp4 \
  candidate/sidehoe.mp4 review-rerun/focus
```

[All frame pairs](review/native/index.html) ·
[Native pixel measurements](review/native/frames.csv) ·
[Exact verdict](review/native/report.json) ·
[HyperFrames findings](review/hyperframes.json) ·
[Focused crop measurements](review/focus/metrics.csv)
