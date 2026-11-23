# Sidehoe pinned inbox and keyboard exposure review

November 21, 2026. The [candidate MP4](candidate/sidehoe.mp4) was rendered from a clean
copy of the [editable project](project/README.md).

[Watch the source and candidate side by side](review/side-by-side.mp4) ·
[Step through all 778 matched frame pairs](review/native/index.html)

## Edits

- During the inbox hold at f10–41, each face has its own position
  and proportions inside its contact disk. The independent disk
  lighting and name bounds follow the source.
- The note uses separate positions for its text and broken heart.
  The note shadow, unread dots, row copy and timestamps follow the
  corresponding source frames.
- During Sofia’s entrance at f319–328, the screen artwork uses more
  vertical exposure and the keyboard tray uses source-measured colors.

The Motion library supplied 43 native source crops across 4 tracks.
All crop hashes, dimensions and presentation times verified.
Editing Darla’s face position, the note, the first preview and the
keyboard tray color in a clean copy changed their visible regions.
[Motion observations](review/motion/motion-observations.json) ·
[Editability evidence](review/editability.json)

| Source time | Matched screenshots | Previous mean RGB error | Revised mean RGB error |
| --- | --- | ---: | ---: |
| 0.36 s | [Frame before the held inbox](review/focus/f009-inbox-last-entrance-registration.png) | 3.58 | 3.57 |
| 0.56 s | [Pinned portraits after the entrance](review/focus/f014-opening-pinned-portraits-after-entrance.png) | 4.20 | 2.46 |
| 1.32 s | [Pins before the previous largest mismatch](review/focus/f033-opening-pinned-portraits-before-largest-mismatch.png) | 4.84 | 2.82 |
| 1.36 s | [Pinned contacts, note and first conversations](review/focus/f034-opening-pinned-portraits-note-and-rows.png) | 4.93 | 2.93 |
| 1.44 s | [The next measured portrait state](review/focus/f036-opening-pinned-portraits-next-measured-frame.png) | 4.77 | 2.86 |
| 1.56 s | [Conversations before scrolling](review/focus/f039-opening-pins-and-conversations-before-scroll.png) | 4.70 | 2.81 |
| 1.64 s | [Last edited inbox frame](review/focus/f041-inbox-last-registered-frame.png) | 4.92 | 2.99 |
| 1.68 s | [The first scroll frame](review/focus/f042-inbox-first-scroll-frame.png) | 4.02 | 4.02 |
| 12.76 s | [Sofia’s phone and keyboard exposure](review/focus/f319-sofia-entrance-exit.png) | 4.92 | 4.24 |
| 13.08 s | [Keyboard as the phone settles](review/focus/f327-sofia-keyboard-as-the-phone-settles.png) | 4.35 | 4.19 |

Each row compares the same crop and frame from the three encoded files.
[Selected crop bounds and metrics](review/focus/metrics.csv) ·
[Previous candidate](../suggestion-and-type-review/README.md)

## Final MP4 review

**Exact comparison failed.** The final mux decodes cleanly, and all 778 frame indices,
presentation times and exclusive end times match at 2000 × 2000 and 25 fps.
Whole-film mean RGB error moved from 2.817 to 2.737.
The reviewer found 0 pixel-identical frames. The last frame differs by
23 pixels. The highest remaining whole-frame RGB error is 4.90
at f265 (10.60 s).
[Exact verdict](review/native/report.json) ·
[All frame measurements](review/native/frames.csv) ·
[Highest-error frame](review/native/pairs/000265.jpg)

At 1.36 s, the pins, text and note are closer to the source. The
source still shows differences in expressions, disk edges and the
chevrons near the row times. Sofia’s lower screen still differs around
the keyboard keys and handset rim.
[Title and hearts at 7.60 s](review/focus/f190-attached-title-and-hearts.png) ·
[Profile badge at 28.24 s](review/focus/f706-attached-profile-badge.png)

**HyperFrames 0.9.77 passed its visual thresholds.** Its mean SSIM moved from
0.9720 to 0.9729. All six cuts aligned at
5.36, 6.40, 8.52, 16.04, 27.72 and 30.80 s. All 202 files in the official reviewer
copy verified against its manifest.
[HyperFrames report](review/hyperframes.json) ·
[Ranked comparison sheet](review/hyperframes/worst.jpg) ·
[Pinned reviewer and license](../hyperframes-review/vendor/hyperframes/UPSTREAM.md)

42 of 42 edited frames improved before encoding.
42 improved in the decoded MP4. The other 736
lossless frames, authored audio stems, audio cue map and AAC stream match the
previous candidate by hash.
[Lossless measurements](review/stage-metrics.json)

Source SHA-256  
`f821bb58cbdb265a75d572616d0da723e9cfb6de31e3db5f8a17d94dc15b5327`

Candidate MP4 SHA-256  
`3127e0f0c4f52380d0c49bd337f52b792b55dc74a28ed0a3133a47cd728dc262`

## Rerun the review

Set `SOURCE` to the locked source and use a fresh review directory.

```sh
PYTHON=/path/to/render-environment/bin/python \
HYPERFRAMES=/path/to/hyperframes \
bash review.sh "$SOURCE" "$PWD/candidate/sidehoe.mp4" "$PWD/review-rerun"

/path/to/render-environment/bin/python focus.py \
  "$SOURCE" ../suggestion-and-type-review/candidate/sidehoe.mp4 \
  candidate/sidehoe.mp4 review-rerun/focus
```
