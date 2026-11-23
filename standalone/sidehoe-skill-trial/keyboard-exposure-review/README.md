# Sidehoe glass clearance and keyboard withdrawal exposure

November 21, 2026. The [candidate MP4](candidate/sidehoe.mp4) was rendered
from a clean copy of the [editable project](project/README.md).

[Watch source and recreation side by side](review/side-by-side.mp4) ·
[Inspect all 778 time-matched frames](review/native/index.html)

- Cleared the band inside the handset casing and above the camera island
  across frames 139–161. The falloff is a separate editable property from
  the speaker and metal shoulders.
- Registered the white key faces and the letters separately in the
  final follow-up pullback. Individual glyphs now follow the source's
  changing skew and direction of blur from f691 through f695.

| Source time | Matched encoded crop | Previous mean RGB error | Revised mean RGB error |
| --- | --- | ---: | ---: |
| 5.56 s | [First fitted glass frame](review/focus/f139-first-revised-glass-frame.png) | 5.06 | 4.42 |
| 5.80 s | [Glass and casing hold](review/focus/f145-case-and-glass-hold.png) | 4.51 | 4.33 |
| 6.08 s | [Clear glass above the camera island](review/focus/f152-clear-glass-above-camera-island.png) | 5.11 | 4.35 |
| 6.12 s | [Glass during handset exit](review/focus/f153-glass-as-the-handset-exits.png) | 4.65 | 3.85 |
| 27.64 s | [Keyboard in early withdrawal](review/focus/f691-keyboard-letters-in-early-withdrawal.png) | 4.40 | 3.97 |
| 27.68 s | [Key faces and ink exposure](review/focus/f692-keyboard-shear-and-caps.png) | 5.05 | 4.49 |
| 27.72 s | [Three independently drawn rows](review/focus/f693-three-key-rows-during-pullback.png) | 8.35 | 4.89 |
| 27.76 s | [Individual directional key streaks](review/focus/f694-individual-key-streaks.png) | 8.62 | 5.61 |
| 27.80 s | [Last visible keyboard](review/focus/f695-last-visible-keyboard.png) | 7.83 | 5.98 |

All 30 adjacent-frame comparisons improved across the two revised
passages. The shift and delete icons and the composer still show
different blur at 27.76 s. At 6.08 s the camera island is still softer
than the reference.
[Adjacent-frame measurements](review/temporal-metrics.csv)

[Title and hearts at 7.68 s](review/focus/f192-attached-title-and-hearts.png) ·
[Calendar tile at 19.16 s](review/focus/f479-calendar-31-tile-arrival.png) ·
[Cursor contact at 27.00 s](review/focus/f675-cursor-contact.png) ·
[Profile badge at 28.24 s](review/focus/f706-attached-profile-badge.png)

## Full export verdict

**Exact fidelity fails.** The mux decodes cleanly. All 778 frames have
identical presentation timestamps and exclusive end times at 2000 × 2000.
Mean full-film RGB error moved from 2.4423 to 2.4365.
0 frames are pixel-identical. The last frame differs by 23 pixels.
The largest full-frame error is 3.995 at f342 (13.68 s).
[Exact verdict](review/native/report.json) ·
[All frame measurements](review/native/frames.csv) ·
[Highest-error frame](review/native/pairs/000342.jpg)

**HyperFrames 0.9.77 passed its visual thresholds** and matched all six cuts.
Mean SSIM moved from 0.9758 to 0.9759.
The pinned reviewer copy passed all 202 file checks.
[Official diff result](review/hyperframes.json) ·
[Ranked misses](review/hyperframes/worst.jpg) ·
[Reviewer source and license](../hyperframes-review/vendor/hyperframes/UPSTREAM.md)

All 28 affected lossless frames improved, and the other 750 match
the previous stage render by hash. 28 of 28 improved in the encoded MP4.
The 48 kHz stems, event map, and AAC stream match the previous export by hash.
Each of 43 Motion source crops was checked for region, timestamp, and hash.
Six isolated edits verified independent control of the glass feather,
key face, and letter position, shear, and shutter.
[Motion crops](review/motion/motion-observations.json) ·
[Stage comparison](review/stage-metrics.json) ·
[Edit checks](review/editability.json) ·
[Previous review](../hold-and-withdrawal-review/README.md)

Source SHA-256  
`f821bb58cbdb265a75d572616d0da723e9cfb6de31e3db5f8a17d94dc15b5327`

Candidate SHA-256  
`96ed75d44b020dad05f99941ddfa1f1b500abf70413ebca64701d450dbdaa465`

## Rerun the comparison

Set `SOURCE` to the locked reference and use a fresh output folder.

```sh
PYTHON=/path/to/render-environment/bin/python \
HYPERFRAMES=/path/to/hyperframes \
bash review.sh "$SOURCE" "$PWD/candidate/sidehoe.mp4" "$PWD/review-rerun"

/path/to/render-environment/bin/python focus.py \
  "$SOURCE" ../hold-and-withdrawal-review/candidate/sidehoe.mp4 \
  candidate/sidehoe.mp4 review-rerun/focus
```
