# Sidehoe handset and calendar review

November 21, 2026. The [previous reviewed reconstruction](../hyperframes-review/candidate/sidehoe.mp4)
is the previous column in the focused comparisons. The [new reconstruction](candidate/sidehoe.mp4)
renders from the [editable project](project/README.md).

## Export verdict

The source and the muxed reconstruction decoded at 2000 × 2000 and 25 fps.
All 778 frame starts and ends match over 31.12 seconds. The exact pixel
check failed with zero identical frames. Mean absolute RGB error over the
whole film fell from 4.49 to 4.27 on a 0–255 scale. The largest remaining
whole-frame error is 10.88 at 5.60 seconds, where the title reveal, handset
softness and pinned portraits differ. [Exact report](review/native/report.json)
· [5.60 s frame pair](review/native/pairs/000140.jpg)

| Export frame | Compared area | Previous RGB error | Revised RGB error |
|---|---|---:|---:|
| 13.44 s | Whole Sofia push frame | 14.45 | 6.59 |
| 15.64 s | Send cursor crop | 24.48 | 12.74 |
| 16.04 s | Whole calendar overlap frame | 3.84 | 2.82 |
| 24.48 s | Calendar tile crop | 5.69 | 4.39 |
| 26.20 s | Whole follow-up handset frame | 11.93 | 6.29 |
| 26.68 s | Whole follow-up push frame | 13.25 | 8.51 |

HyperFrames 0.9.77 measured mean SSIM of 0.9600 and still flagged the
transition at 16.04 seconds. The source's change at f401 is 12.97 gray
levels, just over four times its 3.22 local median. The revised change
is 12.31 against a 3.12 median, below the reviewer's fourfold threshold.
The cue map and all 56 events, the score and Foley stems, the mix and
the AAC packet stream match the preceding reviewed export byte for byte.
[HyperFrames findings](review/hyperframes.json)

The reviewed source SHA-256 is
`f821bb58cbdb265a75d572616d0da723e9cfb6de31e3db5f8a17d94dc15b5327`.
The reviewed candidate SHA-256 is
`c393c191445abd6b4f02de5afb8aad438872450f8d8d49a1a10071f6e35fd898`.

## Matched frames

- The Sofia push now moves the handset, history and keyboard on separate
  tracks. The outgoing type, controls and bezel buttons follow measured positions
  as the push settles. [13.44 s](review/focus/f336-sofia-push.png)
  · [13.56 s](review/focus/f339-sofia-keyboard.png)
  · [13.92 s](review/focus/f348-sofia-settled-controls.png)
- The outgoing suggestion uses measured vertical blur. The Send cursor has
  an independent footprint, soft edge and fade. Incoming weekday and date
  labels follow the marker's path. The two appointment bars keep their own
  exposures during the overlap. [15.64 s](review/focus/f391-send-cursor-approach.png)
  · [15.92 s](review/focus/f398-send-cursor-in-motion.png)
  · [16.00 s](review/focus/f400-calendar-before.png)
  · [16.04 s](review/focus/f401-calendar-overlap.png)
  · [16.64 s](review/focus/f416-calendar-headings.png)
- The calendar tile has a separate cyan glass cap, curved blue front
  and drawn numerals. The exit exposure starts as the tile accelerates.
  [24.48 s](review/focus/f612-calendar-tile-face.png)
- The follow-up camera holds the shell bounds and keyboard alignment through
  the first push. The steel reflections track each rail as the bevels narrow
  and the cursor approaches Yes. [26.20 s](review/focus/f655-follow-handset-registration.png)
  · [26.68 s](review/focus/f667-follow-handset.png) · [27.00 s](review/focus/f675-follow-cursor-contact.png)

The source measurements include [motion-library observations](motion/motion-observations.json)
on the native clock. The calendar tracks use separate landmarks for date
position, appointment boundaries and the outgoing bubble silhouettes.
The film renders its own geometry, type, artwork and audio.

## Supplied screenshots

Matching both panes of each supplied screenshot against the decoded source
and the [screenshot-era reconstruction](../finish/sidehoe.mp4) placed them
closest to frame 190 and frame 706. The comparisons use those same frame
indices for all three columns. The title crop still shows differences in the
type and heart edges. The badge crop still shows differences in the card
spacing and heart shading. [7.60 s title and hearts](review/attachments/f190-attached-title-and-hearts.png)
· [28.24 s profile badge](review/attachments/f706-attached-profile-badge.png)
· [Crop measurements](review/attachments/metrics.csv)

## Reproduce the review

Render from a clean copy of the [project](project/README.md) and use a fresh
review directory. This pass
uses the prior [pinned HyperFrames reviewer source](../hyperframes-review/vendor/hyperframes/UPSTREAM.md)
and the published CLI version `0.9.77`.

```sh
PYTHON=/path/to/render-environment/bin/python \
HYPERFRAMES=/path/to/hyperframes \
bash review.sh "$SOURCE" candidate/sidehoe.mp4 review-rerun

/path/to/render-environment/bin/python focus.py \
  "$SOURCE" ../hyperframes-review/candidate/sidehoe.mp4 \
  candidate/sidehoe.mp4 review-rerun/focus

/path/to/render-environment/bin/python focus.py --attachments \
  "$SOURCE" ../finish/sidehoe.mp4 \
  candidate/sidehoe.mp4 review-rerun/attachments
```

Both checks run on the muxed MP4. The focused captures decode all three
inputs at the same frame indices and measure the crops before display
scaling. [Per-frame viewer](review/native/index.html) ·
[Native RGB measurements](review/native/frames.csv) ·
[Exact comparison](review/native/report.json) ·
[Three-way crop measurements](review/focus/metrics.csv) ·
[HyperFrames findings](review/hyperframes.json)
