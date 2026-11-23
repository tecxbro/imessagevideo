# Measure the interface at native resolution

Use the supplied frame or approved device capture for the specific screen,
state, theme, locale and scale. Measure the frame as it actually appears in the
film. If a phone is angled, record the visible corners, use a screen-space
coordinate system for authoring, and compare the final projected output in the
original movie's coded pixels.

Keep one measurement record per component variant. Record the source SHA-256,
zero-based frame, native crop `[x,y,width,height]`, feature, values and units.
Use `recreate.py inspect --frames … --crop X Y WIDTH HEIGHT` for lossless PNGs.
Use `landmarks` for flat color bounds and centroids. Inspect the mask before
using those bounds. Keep source measurements in the project's review inputs.

| Component | Record these numbers and identifiers |
| --- | --- |
| Handset | Outer and inner bounds, four corner radii or contour samples, bezel thickness at each side and corner, screen inset, island and camera opening bounds, side buttons, shine width and sampled RGB with coordinates. |
| Message bubble | Bounds for each incoming, outgoing and grouped variant, baseline and ink box for each line, insets from text to body, corner radii, tail side and visible contour points from root to tip, fill sample points and RGB, gradient stops and shadow spread. Include a grouped message with a hidden tail if the reference shows one. |
| Status icons | Separate crops for time, cellular, Wi‑Fi and battery. Record time ink box, each cellular bar's bounds, Wi‑Fi band count and center/outer/inner radii or contour samples, battery body and terminal bounds, stroke widths, fill and gaps. |
| Composer and small controls | Separate bounds for field, send, plus, mic, back and camera when visible. Record stroke thickness, cap shape, icon ink box, baseline, spacing and RGB. Verify the empty and filled states if both occur. |
| Keyboard | Crop the whole panel and each row and special control separately. Record top edge and panel fill, row offsets, key bounds, widths, gaps, radii, shadows, labels and ink baselines. Inspect shift, delete, emoji mode, dictation and home indicator individually. Include the active keyboard state, case and layout visible in the source. |
| Emoji, stickers and inline glyphs | Record the asset or Unicode sequence when identifiable, including variation selectors, observed face or symbol, ink bounds, baseline, fill samples and visible details. Use an explicit asset with provenance or editable geometry when a runtime font substitutes the glyph. Keep the keyboard's emoji-mode icon distinct from inline color emoji. |

Use native pixels for the bounds and samples above. For an artist's working
scale, record the transform to the decoded raster. Estimate a radius from a
blurred silhouette only when you can mark it as estimated. If a detail is
occluded, record the missing observation and find another frame where it is
visible. Compare color in flat interiors and separately at anti-aliased edges.
Use the exact literal for label and glyph checks. A named crop like `status`
cannot stand in for inspecting its three tiny icons.

An example entry for one keyboard pose is shown below. Transfer the
measurements through the scene's stage transform and validate them on the
decoded export. Use a separate record for the rest of the panel and controls.

```json
{
  "frame": 327,
  "native_size": [2000, 2000],
  "feature": "keyboard.top-row",
  "crop": [617, 1297, 767, 112],
  "panel_top_y": 1289,
  "panel_rgb_at_1000_1400": [215, 216, 222],
  "white_key_x_spans_at_y_1325": [[623, 688], [698, 764], [776, 841]],
  "x_span_end": "exclusive",
  "units": "coded pixels"
}
```

## Motion measurements

Record last absent, first visible, fastest change, settle and last visible
frames. At each native frame in a critical passage, record independent feature
positions and extents, opacity or composite color, and blur direction and
extent. Record the frame intervals from decoded PTS. Plot position and its
frame-to-frame changes through the fastest section and around handoffs. Use
consecutive decoded pairs to identify a repeated frame, stutter, position snap,
stagger error or tail that disappears. Confirm which tracks moved. A moving
phone can still have a frozen keyboard or flash a wrong glyph.

Set a named `step_mae` region for the passage. It compares the signed change
from the previous decoded frame in the same crop on both sides. Use the
worst adjacent frame pair to find the failure and the measured feature track
to diagnose it. Use the exact frame and zero-pixel-difference gates on the
complete export.

## Build once and check each renderer

Use the same measured geometry, paths, font or explicit glyph assets, color
values, clipping and frame-indexed tracks in the editable scene. The
[conversation adapter](../ui/WORKFLOW.md) supplies editable structure. For a
missing control, add authored geometry or a shared, individually replaceable
asset at the right layer and measured coordinates. When text or outlines
rasterize differently, first isolate the affected component and check size,
baseline, antialiasing, fractional transform, mask, device scale, and the
encoder. Pin the renderer and fonts in the editable project.

Render and decode the same in-context probe in Pillow/FFmpeg, HTML/CSS/SVG,
GSAP, Remotion and Motion Canvas when those methods are in scope. Run
`compare --exact --crops` with the same source and check file on each MP4
independently. Inspect each renderer's worst crop and adjacent frames. Fix
shared scene data once, then rerun every affected export. Record each method's
verdict and hashes with its own report. An adapter smoke test only establishes
that the adapter runs. Apply the same checks to any additional renderer once
it produces an export.
