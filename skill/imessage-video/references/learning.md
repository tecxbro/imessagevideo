# Learn an editable movement from footage

Learning is authoring. The agent inspects the supplied frames, measures the motion, identifies which layers move together, and writes editable keyframes. Registration replays that authored scene in a fresh process and compares it with the measured footage. It does not infer a scene graph, identify native UI, or train a model from an MP4.

## Measure and author

1. Identify the source first with `scripts/sources.py identify FILM`. Reuse an existing verified entry if it answers the request. For a new passage, note the original title/URL, native dimensions, frame rate, first and exclusive last frame, holds and key poses. Inspect source frames around onset, overshoot, landing and any simultaneous camera or layout motion.
2. Measure separate positions against a fixed anchor. A moving card and a camera following a fixed card can have identical screen-space positions and require different reusable scenes. Record what the evidence supports. For a difficult full frame, choose a meaningful cropped study (the gesture, label, and/or stationary landmarks). Preserve crop bounds and identify the missing surrounding action.
3. Write `scene.json` with width, height, fps, duration, background and independently constructed layers. `assets/seed/runtime/scripts/engines/render_pillow.py` is the shipped renderer. The common declarative layer types are rect, circle, text, group, path and image. A candidate may specify `"renderer":"pillow"` (default) or `"renderer":"svg"` (Node plus FFmpeg/librsvg). When both can draw the crucial shot, compare their real outputs and retain the better renderer for this motion. Registration binds the selected implementation and export includes it in the editable project. Keyframes map an animatable property to ordered `{"t": seconds, "value": ..., "ease": "linear"}` samples. Use a few measured keys or an adequately sampled trajectory. Keep IDs stable. Use a group transform when content and its label move as one. Inspect the result around action boundaries.
4. Place independent static art and fonts in `assets/` next to the scene. Record every file in the recipe. Give each a `kind` of `authored`, `licensed-independent` or `user-supplied-independent` and a factual `credit` explaining its origin. Permitted files are single-frame PNG, JPEG, WebP, TTF or OTF. The renderer gets only this declared asset set. Use type, shapes, paths and keyframes for editable UI. Pillow candidates may set an integer `antialias` scale from 1 to 4. The saved replay uses the same scale. Never trace by inserting source screenshots, image sequences, the original clip or its soundtrack. Asset origin needs real review. A digest or passing image comparison cannot prove where an asset was made.
5. Select local regions covering the action and its stationary anchors. Inspect per-frame differences. Set a meaningful maximum per-frame RGB mean absolute error (0–255), explain it, and propose an intentional motion or timing mistake which must fail the same comparison. Choose parameters for real follow-up changes such as copy, location, travel, color or a key time. A look-alike that misses the identifying gesture still needs repair.

## Create a candidate

Make a candidate directory with `scene.json`, optional `assets/` and `candidate.json`. No executable from the candidate is loaded. This minimal example describes a slide beside a fixed line. Its measured values must be replaced for actual footage.

```json
{
  "width":128, "height":72, "fps":12, "duration":1.3333333333333333, "background":"#101010",
  "layers":[
    {"id":"line","type":"rect","x":9,"y":8,"width":95,"height":3,"fill":"#ebebeb"},
    {"id":"tile","type":"rect","x":10,"y":32,"width":16,"height":16,"fill":"#dcdcdc",
     "keyframes":{"x":[{"t":0,"value":10},{"t":0.9166666667,"value":76}]}}
  ]
}
```

```json
{
  "id":"slide-by-line", "title":"Tile slides beneath a stationary line",
  "description":"The tile advances six pixels per frame, then holds.",
  "scene":"scene.json", "fits":["horizontal translation with a fixed header"],
  "avoid":["rail and heading scroll together"], "moving":["tile"], "fixed":["line"],
  "tags":["slide","stationary header"], "assets":{},
  "parameters":{"end-x":"/layers/1/keyframes/x/1/value","color":"/layers/1/fill"},
  "source":{"label":"Name and version of original","start_frame":0,
            "observation":"Left edge moves from x=10 to x=76 at frames 0 to 11. The line stays at x=9."},
  "checks":{"rois":{"tile":[0,27,120,30],"line":[4,4,105,13]},"max_mae":12,
            "max_pts_error_ms":0,
            "reason":"Local regions cover the moving edge and stationary header. A stuck tile must fail.",
            "negative_control":{"set":{"end-x":10},"reason":"Removing travel loses the transition."}}
}
```

Parameter paths use JSON Pointer and point at existing scalar values. For two independently timed parts, expose separate parameters or put them under a shared transform. For a new effect requiring a different graph, author another scene. `moving` and `fixed` contain real layer IDs. `fixed` may be empty for camera-only work. A named region is `[left,top,width,height]` in the compared clip.

## Register and reuse

Run from the installed skill directory. Registration writes to `assets/library` by default. Use `IMESSAGE_VIDEO_MOTION_LIBRARY` or `--library /persistent/location` before the subcommand for a shared or repository-backed library. Set the same location in the later session. Persist new default entries with the installed skill using its normal save workflow.

```sh
python scripts/learn.py register study/candidate.json --reference original.mp4 --frames 85:121 --crop 568,1352,216,236
python scripts/learn.py list "stationary header and sliding photos" --json
python scripts/learn.py show slide-by-line
python scripts/learn.py replay slide-by-line --out /tmp/new-slide.mp4 --set end-x=92 --set 'color="#79bacf"' --project /tmp/editable-new-slide
```

Replace the example source-frame range to agree with the candidate's `source.start_frame`. Omit `--crop` for a full-frame study. `--frames FIRST:EXCLUSIVE_END` extracts video with its native frame order, retains a comparison clip, and hashes the original. For an already trimmed comparator, omit both flags, set its original first frame as observed, and record its provenance. The receipt then identifies the supplied clip; registering against a different original also requires supplying that original for frame selection. Use `--asset 'assets/photo.png=/absolute/path/to/replacement.png'` on replay for a registered independent image, and preserve provenance for the new project. Render outputs and editable project folders must be new paths outside the canonical library.

Published entries contain the portable scene and assets, independently rendered preview, source-window metadata, comparison reference, complete per-frame CSVs, paired worst-frame sheets, deliberate-failure output and file hashes. The reference and diagnostic frames live under `evidence/` and are not available as scene assets. `show` and `replay` verify the saved entry. Exact retries are idempotent. A conflicting ID or duplicate scene is refused without modifying the previous entry.

`frame-compared` records pixel and time checks under the specified bounds, plus the negative control. Use the comparison image and native playback to judge the actual motion, fit, editability, and known defects. Sound needs its own independent cue work. The normal end-to-end save is `python scripts/save_motion.py study/candidate.json original.mp4 --frames 85:121 --crop 568,1352,216,236 --reviewed-by "reviewer name"`. This runs the same checked registration and links the motion ID to its source film. A direct `learn.py register` publishes a reusable motion without the film index link; a verified crop supplies evidence for that passage only. Then use another brief and independent assets to replay the saved motion, change a parameter and inspect the changed frames.
