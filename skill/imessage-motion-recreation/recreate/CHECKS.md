# Check file inputs

All positions use the decoded coded raster with container crops and orientation reported separately. Frame indices start at zero. Window endpoints are inclusive. Comparison pairs display-order frames by index and fails a separate gate on any PTS mismatch outside the tolerance. A dropped interior frame can cause every later paired picture to disagree. Consult the PTS columns to find where the shift begins.

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

The display gate checks SAR, dimensions, the full display matrix and container clean aperture. It checks explicitly different primaries/transfer tags and treats adding or removing HDR tags as a difference. Decoded RGB comparisons use FFmpeg's conversion with the signaled matrix and range. Use separate color-managed viewing and measurement for HDR masters. The checker measures the first moving-picture stream and lists audio streams. A damaged stream, missing PTS, unknown final duration or incomplete local window cannot produce a successful verdict. A fresh output directory keeps sheets from older runs out of the evidence.

An alpha-bearing stream fails the opaque picture gate. For an alpha deliverable, verify its alpha plane with an alpha-aware tool and compare explicitly composited exports on a shared matte for a picture check.
