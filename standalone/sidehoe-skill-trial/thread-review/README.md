# Sidehoe conversation and portrait wipe review

November 21, 2026. The previous column uses the
[reveal review export](../reveal-review/candidate/sidehoe.mp4). The revised
column uses the [new MP4](candidate/sidehoe.mp4) encoded from a clean copy
of the [editable project](project/README.md).

## Export verdict

The native comparison decoded the full 31.12-second export at 2000 × 2000
and 25 fps. All 778 frame start and end timestamps match the source.
Mean absolute RGB error fell from 4.09 to 3.86 on a 0–255 scale.
The exact check still fails with 0 of 778 identical frames.
The largest remaining whole-frame error is 9.39 at 5.36 seconds.
The first handset frame still differs at the casing edge, optical spread
and badge distortion. [First handset frame](review/native/pairs/000134.jpg)

| Time | Compared area | Previous RGB error | Revised RGB error |
| --- | --- | ---: | ---: |
| 10.20 s | Whole portrait wipe frame | 9.91 | 5.74 |
| 13.92 s | Whole Sofia close-up frame | 10.26 | 5.03 |
| 14.60 s | Whole departing message frame | 2.91 | 2.41 |
| 16.04 s | Whole calendar overlap frame | 2.64 | 2.48 |
| 26.96 s | Whole follow-up arrival frame | 9.96 | 4.96 |
| 27.00 s | Cursor contact and controls crop | 7.28 | 5.96 |
| 27.72 s | Whole follow-up pullback frame | 10.07 | 4.24 |

HyperFrames measured a mean SSIM of 0.9637 and still flagged the 16.04-second
transition. The gray-level change at that frame went from 12.52 to 12.70
against a local median of 3.28. The source change is 12.97 against a
median of 3.22. The source clears the published reviewer's fourfold
criterion, while the revised cut remains below it.
[HyperFrames findings](review/hyperframes.json)

The source SHA-256 is
`f821bb58cbdb265a75d572616d0da723e9cfb6de31e3db5f8a17d94dc15b5327`.
The reviewed candidate SHA-256 is
`024a216432ebe838357a763dede0e4678d63dafbba713c294801faaafea4fa90`.

## Same-time comparisons

- The Sofia and follow-up close-ups use independent bounds for each message,
  text line, keyboard row and rail. The Sofia bubbles keep their measured
  text height through the push-in. The follow-up takes the composer and
  No button to their measured positions during the pullback. The Yes
  highlight blooms at the recorded feedback frame with the cursor above it.
  [13.92 s Sofia close-up](review/focus/f348-sofia-message-and-keyboard.png)
  · [27.00 s cursor contact](review/focus/f675-follow-cursor-contact.png)
  · [27.44 s feedback](review/focus/f686-follow-feedback.png)
  · [27.72 s follow-up pullback](review/focus/f693-follow-handset-pullback.png)
- The portrait group carries the established actor positions into the wipe.
  The cluster moves left beneath the rectangular masks through the last
  fragments. [10.16 s wipe entrance](review/focus/f254-portrait-wipe-entry.png)
  · [10.20 s wipe in motion](review/focus/f255-portrait-wipe-moving.png)
  · [10.28 s final fragments](review/focus/f257-portrait-wipe-tail.png)
- The departing messages have individual letter bounds inside their moving
  bubbles. [14.60 s departing type](review/focus/f365-send-typography.png)
  · [15.64 s exit](review/focus/f391-send-typography-exit.png)
  · [16.04 s calendar overlap](review/focus/f401-calendar-handoff.png)

The clip also includes the two same-time comparisons from the supplied
screenshots. [7.60 s title and hearts](review/focus/f190-attached-title-and-hearts.png)
· [28.24 s profile badge](review/focus/f706-attached-profile-badge.png)

## Reproduce the review

The published HyperFrames CLI is version 0.9.77. The copied reviewer source
used for this work was pinned before the Sidehoe fixes. Run the reviewer
against the encoded MP4 and put its outputs in a fresh directory.
[Pinned source and manifest](../hyperframes-review/vendor/hyperframes/UPSTREAM.md)

```sh
PYTHON=/path/to/render-environment/bin/python \
HYPERFRAMES=/path/to/hyperframes \
bash review.sh "$SOURCE" candidate/sidehoe.mp4 review-rerun

/path/to/render-environment/bin/python focus.py \
  "$SOURCE" ../reveal-review/candidate/sidehoe.mp4 \
  candidate/sidehoe.mp4 review-rerun/focus
```

[All frame pairs](review/native/index.html) ·
[Native pixel measurements](review/native/frames.csv) ·
[Native verdict](review/native/report.json) ·
[HyperFrames findings](review/hyperframes.json) ·
[Focused crop measurements](review/focus/metrics.csv)
