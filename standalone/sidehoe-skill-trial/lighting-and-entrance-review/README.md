# Sidehoe handset lighting, tile turn and entrance

November 21, 2026. The [candidate MP4](candidate/sidehoe.mp4) was rendered
from a clean copy of the [editable project](project/README.md).

[Watch the same-time comparison with the source on the left](review/side-by-side.mp4) ·
[Step through all 778 frame pairs](review/native/index.html)

The pink-lit handset keeps a darker camera cutout under the wash, with
separately measured right bezel and title blur. The follow-up handset's
casing and glass use different exposure lengths and focus. The screen
records keep the bubble, composer, and keyboard positions editable. The
red and calendar tiles now follow the measured trajectories as they
pass each other.

The Motion library extracted 33 native source crops across six tracks.
The crop and plan hashes, dimensions, frame indices and timestamps
verified against the locked source.
[Handset plan](review/motion-plan.json) ·
[Handset observations](review/motion/motion-observations.json) ·
[Tile plan](review/orbit-motion-plan.json) ·
[Tile observations](review/orbit-motion/motion-observations.json)

| Time | Comparison from the decoded MP4 | Previous mean RGB error | Revised mean RGB error |
| --- | --- | ---: | ---: |
| 6.32 s | [Tight camera cutout crop](review/focus/f158-pink-light-camera-cutout.png) | 11.94 | 6.80 |
| 6.36 s | [Downward title blur](review/focus/f159-assistant-title-travel.png) | 14.74 | 6.73 |
| 6.40 s | [Pink-lit handset and title](review/focus/f160-handset-before-last-screen-frame.png) | 6.41 | 5.01 |
| 21.28 s | [Red and calendar tiles during the hold](review/focus/f532-calendar-and-red-tile-hold.png) | 6.13 | 2.59 |
| 25.04 s | [Follow-up handset in motion](review/focus/f626-follow-up-motion-blur.png) | 6.19 | 2.30 |
| 25.08 s | [Follow-up handset with the keyboard](review/focus/f627-follow-up-keyboard-and-glass-entrance.png) | 6.41 | 2.60 |

Mean RGB error is the average absolute difference over the decoded
RGB channels in the crop or, for the last four rows, the full frame.
All 41 revised lossless frames improved. The other 737 lossless frames,
authored audio stems, cue map and AAC stream match the preceding
candidate by hash.
[Selected full-frame and crop measurements](review/focus/metrics.csv) ·
[Previous Sofia, title and badge review](../sofia-and-title-review/README.md)

The pink-lit camera rim and the upper lens still differ, and the
follow-up keyboard remains softer than the source at portions of the
entrance. Tile positions track more closely through the turn. The
flame silhouette, blue face and far-side tile shapes still differ.
The two supplied screenshot times retain the previous visible
differences in the hearts and the rear cards of the badge.
[Title at 7.60 s](review/focus/f190-attached-title-and-hearts.png) ·
[Badge at 28.24 s](review/focus/f706-attached-profile-badge.png)

The title crop at 7.60 s and the departing calendar crop at 24.76 s
show small encoding regressions. Their lossless renders match the
preceding pass by hash.
[Departing tile comparison at 24.76 s](review/focus/f619-calendar-tile-last-visible-finish.png)

## Full export verdict

**HyperFrames 0.9.77 passed.** It located all six cuts at 5.36, 6.40,
8.52, 16.04, 27.72 and 30.80 s. Mean SSIM is 0.9695. All 202 files in
the pinned reviewer copy verified against its manifest.
[HyperFrames verdict and ranked regions](review/hyperframes.json) ·
[Pinned reviewer and license](../hyperframes-review/vendor/hyperframes/UPSTREAM.md)

**The native pixel comparison failed.** The candidate mux decodes cleanly.
All 778 frames align by index, presentation timestamp and exclusive end
timestamp at 2000 × 2000 and 25 fps. All 41 edited frames improved in
the decoded export. Mean absolute RGB error fell from 3.141 to 3.081.
Zero frames are pixel-identical. The final frame differs by 23 pixels.
The largest remaining whole-frame mismatch is the glossy handset at
5.44 s. Its prismatic rim and pinned portraits still differ.
[Native verdict](review/native/report.json) ·
[Measurements for every frame](review/native/frames.csv) ·
[Glossy handset at 5.44 s](review/native/pairs/000136.jpg)

Source SHA-256  
`f821bb58cbdb265a75d572616d0da723e9cfb6de31e3db5f8a17d94dc15b5327`

Candidate MP4 SHA-256  
`f0d35c60b2ee54cc717b90640693cf7e460cb74548f7bc277a14e9e7d21c96ff`

Set `SOURCE` to the locked reference and choose a fresh output directory.

```sh
PYTHON=/path/to/render-environment/bin/python \
HYPERFRAMES=/path/to/hyperframes \
bash review.sh "$SOURCE" "$PWD/candidate/sidehoe.mp4" "$PWD/review-rerun"

/path/to/render-environment/bin/python focus.py \
  "$SOURCE" ../sofia-and-title-review/candidate/sidehoe.mp4 \
  candidate/sidehoe.mp4 review-rerun/focus
```
