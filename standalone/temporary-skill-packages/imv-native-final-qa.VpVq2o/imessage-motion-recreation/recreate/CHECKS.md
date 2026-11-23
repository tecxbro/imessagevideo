# Check file inputs

All positions use the decoded coded raster with container crops and orientation reported separately. Frame indices start at zero. Window endpoints are inclusive. Comparison pairs display-order frames by index and fails a separate gate on any PTS mismatch outside the tolerance. A dropped interior frame can cause every later paired picture to disagree. Consult the PTS columns to find where the shift begins.

`frames.csv` maps each reference frame to the paired output frame with integer start and exclusive-end tick columns. Each side uses its own time base from `report.json`. An unmatched side has blank frame and tick fields. A known final hold ends at the measured stream end. `regions.csv` gives the exact coded pixel rectangle for each local observation, and the report identifies each region’s worst MAE and changed-pixel frames.

| Key | Meaning |
| --- | --- |
| `global_mae` | Maximum per-frame mean absolute RGB channel difference on a 0–255 scale. Defaults to 2. |
| `pixel_floor` | A pixel counts as changed in the frame CSV when any channel changes by at least this amount. Defaults to 20. |
| `clock_tolerance_seconds` | Inclusive maximum difference for each frame start and the final end, after subtracting each picture stream's first PTS. Defaults to exact. Use a decimal or a rational string. |
| `regions` | List of local window gates. Use one or more for every visible interaction and the end hold. |
| `tile` | Optional object with integer `size` in coded pixels and `mae` limit. Tests a half-overlapping grid on every frame and gives the worst location. |
| `audio` | `observe` (default) records audio stream metadata. `silent` requires no candidate audio stream. `present` requires a stream. |
| `audio_checks` | Optional decoded first-track alignment tests. `max_start_delta_seconds` compares reference and candidate audio start relative to their pictures. `cues` takes objects with `id`, `frame`, signed `offset_ms`, centered `window_ms`, and `min_peak` (maximum absolute per-channel linear sample amplitude required in the window). These check start and local signal presence; they do not identify specific sounds under a music bed. |

A region uses a unique `id`; inclusive `start` and `end`; either `rect` (fixed) or `rects` (one rectangle for every frame); and a `mae` limit, `changed_pixels` limit or both. A region may override `pixel_floor`. Rectangle fields are `[x,y,width,height]`, in coded pixels.

## Calibrate for the shot review

Before the first full render, use aligned static or settled source frames and
visually accepted decoded probes from the same scene to estimate expected RGB
differences. Record the frames, crop, measured values and reason for each
threshold, including the whole-frame limit. Tie the tolerance to the visual
property it tests and use the same checks for first and final comparisons.
Keep any changed criteria and their rationale alongside the original results.

Use direct checks for placement and state, such as the pointer tip inside the
control at contact, even when the region's RGB average passes. If permitted
asset differences make a color comparison diagnostic, declare that before the
full render, record its result, and check silhouette, scale, placement, light
and motion directly. Run diagnostics separately from required RGB gates.
A required check failure blocks the affected shot's visual pass. Follow the
[shot review](VISUAL-REVIEW.md#review-the-finished-export) for the visual verdict.

## Browse aligned frame pairs

For frame-by-frame diagnosis, add `--pairs` to `recreate.py compare`. Open
`index.html` in the report folder to step through every decoded pair. The left
side is the reference. The same report contains native RGB metrics, presentation
timestamps and region results. The viewer images are scaled JPEG previews for
inspection. Use native crops for small edges and pixel measurements. The viewer
requires an exact clock, matching display geometry and opaque streams.

## Gate exact pixels and motion

Use `compare --exact --crops` for a one-to-one export. A difference of 1 in
one RGB channel of one pixel fails. The report stores exact frame counts,
differing spans, and the frame, enclosing rectangle, pixel count and delta
for the first difference. `frames.csv` counts every differing pixel even when
the diagnostic RGB floor is higher.

For each named region, add `pixel_floor: 1` and `changed_pixels: 0` to flag
any changed pixel locally. For motion windows of two or more frames, add
`step_mae`. It limits the mean absolute error between the reference's
signed RGB change and the candidate's signed RGB change from the previous
frame. Both frames use the current frame's rectangle so a moving crop does
not introduce a synthetic shift. Use zero for exact motion. The step can
range from 0 to 510. The report also lists fully unchanged candidate crops on
frames where the reference crop changes. A lossy encode can change pixels
in a held frame, so use the step metric and inspect feature movement.

`--crops` writes lossless PNGs for each region's first and highest mean
error frame. Read left to right as source, export, and red pixel-difference
mask. Each panel is at native size. For a motion failure, the worst step's
PNG shows source on the left and export on the right, with previous above
current. Read the exact crop coordinates and frame indices in `report.json`.

## Decode and display checks

The display gate checks SAR, dimensions, the full display matrix and container clean aperture. It checks explicitly different primaries/transfer tags and treats adding or removing HDR tags as a difference. Decoded RGB comparisons use FFmpeg's conversion with the signaled matrix and range. Use separate color-managed viewing and measurement for HDR masters. The checker measures the first moving-picture stream and lists audio streams. A damaged stream, missing PTS, unknown final duration or incomplete local window cannot produce a successful verdict. A fresh output directory keeps sheets from older runs out of the evidence.

An alpha-bearing stream fails the opaque picture gate. For an alpha deliverable, verify its alpha plane with an alpha-aware tool and compare explicitly composited exports on a shared matte for a picture check.
