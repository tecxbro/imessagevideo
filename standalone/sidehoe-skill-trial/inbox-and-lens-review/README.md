# Sidehoe inbox scroll and glossy handset review

November 21, 2026. The [candidate MP4](candidate/sidehoe.mp4) was rendered
from a clean copy of the [editable project](project/README.md).

[Watch the comparison with the source on the left](review/side-by-side.mp4) ·
[Step through all 778 frame pairs](review/native/index.html)

The inbox's chrome, pinned contacts, unread dots, conversation rows
and home indicator use measured positions through the scroll and zoom.
The rows retain editable copy, timestamps and emoji. Darla and El have
independently drawn portraits for the small contact disks. The glossy
handset's camera cutout, badge and lower and upper reflections use
separate tracks through the reveal.

The Motion library extracted 26 native crops across five tracks from
the locked source. Their hashes, dimensions, frame indices and
presentation times verified. In the reopened project, changing an
inbox reply affected its preview, and moving the camera cutout affected
its local region.
[Motion plan](review/motion-plan.json) ·
[Motion observations](review/motion/motion-observations.json)

| Time | Whole frame from the decoded MP4 | Previous mean RGB error | Revised mean RGB error |
| --- | --- | ---: | ---: |
| 1.80 s | [Pinned contacts and first scrolling rows](review/focus/f045-inbox-moving-header-and-first-rows.png) | 6.04 | 4.37 |
| 2.08 s | [Motion blur and the first row fading](review/focus/f052-inbox-motion-blur-and-row-fade.png) | 5.14 | 3.93 |
| 3.00 s | [Settled rows and home indicator](review/focus/f075-inbox-settled-rows-with-inline-emoji.png) | 5.38 | 2.75 |
| 4.04 s | [Last inbox frame before the cut](review/focus/f101-inbox-final-frame-before-badge.png) | 3.66 | 1.91 |
| 5.36 s | [First handset frame](review/focus/f134-first-handset-and-pin.png) | 5.95 | 5.17 |
| 5.44 s | [Camera cutout and lower refraction](review/focus/f136-handset-and-lower-refraction.png) | 6.17 | 5.83 |

All 67 edited lossless frames improved. The other 711 lossless frames,
authored audio stems, cue map and AAC stream match the preceding
export by hash. The title crop at 7.60 s regressed slightly after
encoding. The screenshot at 28.24 s retains differences in the
badge's rear card contours.
[Title and hearts at 7.60 s](review/focus/f190-attached-title-and-hearts.png) ·
[Profile badge at 28.24 s](review/focus/f706-attached-profile-badge.png) ·
[Selected crop measurements](review/focus/metrics.csv)

The compact portraits still differ in expression and shading. At
5.44 s, the source's rainbow rim and the flare across the lower
left corner remain visibly different.

## Full export verdict

**HyperFrames 0.9.77 passed.** It found all six cuts at 5.36, 6.40, 8.52,
16.04, 27.72 and 30.80 s. Mean SSIM was 0.9711. All 202 files in the
pinned reviewer copy verified against its manifest.
[HyperFrames verdict and ranked regions](review/hyperframes.json) ·
[Pinned reviewer and license](../hyperframes-review/vendor/hyperframes/UPSTREAM.md)

**The native pixel comparison failed.** The candidate mux decodes
cleanly. All 778 frames align by index, presentation time and exclusive
end time at 2000 × 2000 and 25 fps. All 67 edited frames improved
in the decoded export. Whole-film mean RGB error went from 3.081
to 2.911. Zero frames are pixel-identical, and the final frame
differs by 23 pixels. The pinned contacts during the opening at 0.36 s
now have the highest whole-frame error, at 6.03.
[Native verdict](review/native/report.json) ·
[Measurements for every frame](review/native/frames.csv) ·
[Opening pinned contacts](review/native/pairs/000009.jpg)

Source SHA-256  
`f821bb58cbdb265a75d572616d0da723e9cfb6de31e3db5f8a17d94dc15b5327`

Candidate MP4 SHA-256  
`9b7c7af2833b97a358c4ee4256fc672b5e6ad7dedc5e22205d7936d4219b3c5e`

Set `SOURCE` to the locked reference and choose a fresh output directory.

```sh
PYTHON=/path/to/render-environment/bin/python \
HYPERFRAMES=/path/to/hyperframes \
bash review.sh "$SOURCE" "$PWD/candidate/sidehoe.mp4" "$PWD/review-rerun"

/path/to/render-environment/bin/python focus.py \
  "$SOURCE" ../lighting-and-entrance-review/candidate/sidehoe.mp4 \
  candidate/sidehoe.mp4 review-rerun/focus
```
