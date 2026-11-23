# Sidehoe recreation

November 21, 2026. The authorized source is `sidehoe.mp4`, SHA-256
`f821bb58cbdb265a75d572616d0da723e9cfb6de31e3db5f8a17d94dc15b5327`.
The prior full export used for comparison is SHA-256
`d5415679aaac724b5deb3598f980c9f62cc0e318d7a7c50a37fedbffdd699c4a`.
This folder contains the revised film, edited scene, silent picture,
editable sound stems, and frame-indexed review.

- [Revised film](sidehoe.mp4) · [Editable project](project/README.md)
- [Frame-by-frame viewer](review/index.html) · [Native pixel comparisons](review/frames.csv) · [Exact report](review/report.json)
- [Motion observations with source timestamps and hashed crops](motion-evidence/motion-observations.json) · [Component measurements](focus/measurements.json)

## What changed

Motion extraction tracked the tile cheek, two handset rails and cursor
ink on the decoded source clock. I used the library's independent orbit
actors and focus planes as the component model. The measured poses live
in the existing Sidehoe timeline.

- **Blue 31 tile.** The face now has a pinched silhouette, separate cyan
  rim and editable type. Height, vertical position, blur and exposure
  have independent keys, including the last visible streak and the
  blank f622 control. [Exit frames f612–617](focus/tile-612-617.png) ·
  [Exit frames f618–623](focus/tile-618-623.png)
- **Follow-up handset.** The two bevel reflections have separate control
  tracks. The inner gasket, side key, exit taper and defocus are distinct
  from the screen and camera geometry. The first revision overlit the
  right rail in the held view. The second revision fitted each rail's
  blend independently and rerendered the full follow-up passage. A
  final six-frame probe exposed a clipped blur edge on withdrawal.
  Transparent padding now gives the rail exposure room to feather.
- **Follow-up cursor.** The stage track controls its tip, footprint,
  blur and opacity. The Yes chip has a separate measured registration
  track. The cursor withdraws independently and tapers into the weak
  trace visible at f695. [Approach f670–676](focus/cursor-670.png) ·
  [Withdrawal f691–695](focus/cursor-691.png)

The renderer generated 778 lossless frames from the editable scene. The
scoped passes rerendered f624–695 and then f690–695. The final mux uses
the complete revised cache. Against
the prior film's cache, changed lossless frames are f479–621 and f632–695.
Nine targeted pictures rerendered byte for byte from a clean copy of
the edited project. The generated score, Foley, mix and encoded AAC
matched the prior authored sound. The source is kept outside the
render inputs. The calendar glyphs use the local Apple Color Emoji
font, declared in the editable project's setup.

## Final encoded comparison

All 778 source and candidate frames align at 25 fps. The picture ends at
31.12 seconds. Full-frame mean absolute RGB error fell from 6.6081 to
6.5154, on the 0–255 channel scale. All 778 frames still have at least one
different decoded pixel. The largest full-frame difference is the
assistant reveal at f150. [Frame 150](review/pairs/000150.jpg)

| Locked crop | Frames checked | Prior mean RGB error | Revised mean RGB error |
| --- | ---: | ---: | ---: |
| Blue tile exit | 12 | 10.16 | 7.36 |
| Cursor and Yes control | 26 | 12.95 | 8.07 |
| Left rail | 24 | 38.36 | 19.87 |
| Right rail | 24 | 29.69 | 23.82 |

Mean cursor-tip error fell from 11.98 px to 1.62 px across all 26
detected frames. At f621 the comparison crop has 19 matching blue
pixels in the source, 42,873 in the prior export and zero in the revised
export. Right-rail error is still slightly higher on f672. The tile
lettering, hardware reflections and cursor footprint still have visible
residuals. Exact recreation remains open. [Encoded summary](focus/encoded-summary.json)
· [Left rail f684–695](review/region-21-01.png) · [Right rail f684–695](review/region-22-01.png)

## Rerun

Render with the commands in the [project README](project/README.md).
From the iMessage skill directory, compare the supplied source and final
mux with the saved region definitions.

```sh
python3 recreate/recreate.py compare "$SOURCE" "$RECREATED" \
  --exact --checks "$FINISH/comparison-checks.json" \
  --pairs --crops --sheets --out "$REVIEW"
```

There is one native RGB measurement row per decoded frame. The viewer
uses reduced display previews for browsing. The scores come from the
2000 × 2000 encoded pictures before preview scaling.
