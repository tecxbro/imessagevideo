# Sidehoe handset hold, follow-up withdrawal, and closing badge

November 21, 2026. The [candidate MP4](candidate/sidehoe.mp4) was rendered
from a clean copy of the [editable project](project/README.md).

[Watch source and recreation side by side](review/side-by-side.mp4) ·
[Inspect all 778 time-matched frames](review/native/index.html)

- Extended the fitted metal and glass shoulders through the handset
  hold. Added a separate speaker recess and lip reflection.
- Measured individual key faces and letter bounds through the final
  follow-up pullback. Fitted exposure through the end of the withdrawal.
- Registered the closing badge’s three cards and heart independently
  and extended the outer silhouette fit toward the fade.

| Source time | Matched encoded crop | Previous mean RGB error | Revised mean RGB error |
| --- | --- | ---: | ---: |
| 5.56 s | [First revised casing frame](review/focus/f139-first-curved-shoulder.png) | 5.11 | 4.93 |
| 6.08 s | [Casing and restored speaker](review/focus/f152-source-matched-case-and-speaker.png) | 5.54 | 4.93 |
| 6.12 s | [Transition into the handset exit](review/focus/f153-first-exit-after-continuous-hold.png) | 4.47 | 4.42 |
| 27.64 s | [Keyboard in the follow-up pullback](review/focus/f691-keyboard-letters-during-withdrawal.png) | 6.28 | 4.15 |
| 27.68 s | [Keycaps as the camera pulls back](review/focus/f692-keycaps-track-camera.png) | 6.61 | 4.44 |
| 28.04 s | [First registered badge artwork](review/focus/f701-first-separated-badge-elements.png) | 7.77 | 5.36 |
| 28.24 s | [Profile badge](review/focus/f706-attached-profile-badge.png) | 1.91 | 1.78 |
| 28.48 s | [Transition out of the initial badge outline](review/focus/f712-badge-outline-join.png) | 2.43 | 2.03 |
| 28.64 s | [Badge as it scales down](review/focus/f716-badge-marks-shrinking.png) | 3.39 | 2.17 |
| 29.28 s | [Held card and heart artwork](review/focus/f732-held-card-artwork.png) | 6.63 | 6.30 |

The transitions into frames 153 and 712 improved. Forty-five of
64 measured adjacent-frame changes improved. Nineteen moved farther
from the source, including the start of the revised shoulder at f139 and
the entrance to the revised badge artwork at f701.
The 27.60 s keyboard crop also has a small increase in RGB error.
At 6.08 s the handset retains a faint line above the camera island.
The card fill and heart highlights still differ at 28.24 s.
[Adjacent-frame measurements](review/temporal-metrics.csv) ·
[First withdrawal frame](review/focus/f690-first-withdrawal-keyboard.png)

The [title and hearts at 7.68 s](review/focus/f192-attached-title-and-hearts.png)
retain the lettering differences noted in the previous review.
[Calendar tile at 19.16 s](review/focus/f479-blue-calendar-31-tile-arrival.png) ·
[Cursor contact at 27.00 s](review/focus/f675-cursor-contacts-yes.png)

## Full export verdict

**Exact fidelity fails.** The mux decodes cleanly. All 778 frames have
identical presentation timestamps and exclusive end times at 2000 × 2000.
Mean full-film RGB error moved from 2.4524 to 2.4423.
0 frames are pixel-identical. The last frame differs by 23 pixels.
The largest full-frame error is 4.046 at f694 (27.76 s).
[Exact verdict](review/native/report.json) ·
[All frame measurements](review/native/frames.csv) ·
[Highest-error frame](review/native/pairs/000694.jpg)

**HyperFrames 0.9.77 passed its visual thresholds** and matched all six cuts.
Mean SSIM moved from 0.9757 to 0.9758.
The pinned reviewer copy passed all 202 file checks.
[Official diff result](review/hyperframes.json) ·
[Ranked misses](review/hyperframes/worst.jpg) ·
[Reviewer source and license](../hyperframes-review/vendor/hyperframes/UPSTREAM.md)

All 104 affected lossless frames improved, and the other 674 match the
previous stage render by hash. 104 of 104 improved in the encoded MP4.
The 48 kHz stems, event map, and AAC stream match the previous export by hash.
Each of 66 Motion source crops was checked for region, timestamp, and hash.
Six isolated edits verified independent control of the speaker, keyboard
glyph, badge card, heart, and outline.
[Motion crops](review/motion/motion-observations.json) ·
[Lossless stage comparison](review/stage-metrics.json) ·
[Edit checks](review/editability.json) ·
[Previous review](../exit-casing-review/README.md)

Source SHA-256  
`f821bb58cbdb265a75d572616d0da723e9cfb6de31e3db5f8a17d94dc15b5327`

Candidate SHA-256  
`da81eee3364a70dbf2b1338d7dca55698f1ab93fc4749e02f997069261cefa2c`

## Rerun the comparison

Set `SOURCE` to the locked reference and use a fresh output folder.

```sh
PYTHON=/path/to/render-environment/bin/python \
HYPERFRAMES=/path/to/hyperframes \
bash review.sh "$SOURCE" "$PWD/candidate/sidehoe.mp4" "$PWD/review-rerun"

/path/to/render-environment/bin/python focus.py \
  "$SOURCE" ../exit-casing-review/candidate/sidehoe.mp4 \
  candidate/sidehoe.mp4 review-rerun/focus
```
