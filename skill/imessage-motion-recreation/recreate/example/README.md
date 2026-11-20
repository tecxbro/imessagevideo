# Train options

This four-second authored development reference shows a title, two Messages-style bubbles, an options drawer, a small seat selection and a receipt. The reference is an independently rendered SVG document with original synthesized cues. The rebuild uses editable text, shapes, masks and timing in a shared scene manifest. The repository's existing director components are the stand-in for the Clone iMessage UI handoff.

## Reproduce

Use Node, Chromium, Python 3 and FFmpeg/ffprobe. Install the pinned shared browser dependencies from the repository root with `npm ci --prefix skill/imessage-motion-recreation/scripts/engines`. For a nondefault Chromium executable, set `CHROME_PATH`.

```sh
S=skill/imessage-motion-recreation
node "$S/recreate/example/reference/render.mjs" /tmp/train-reference.mp4
bash "$S/recreate/example/reproduce.sh" /tmp/train-recreation
```

Either command runs independently. The second reads the editable project and shared renderer code. It never opens the reference movie, reference page, measured frames or recorded audio. It first renders the 14-frame interaction preview, creates a complete first export with a four-frame delay, recaptures frames 74–77 in the retained native cache, re-encodes the complete final picture, then produces the edited export. All boundaries are zero-based and inclusive when passed to the renderer.

| File | What it contains |
| --- | --- |
| `hardest.mp4` | Original frame numbers 70–83, recentered to output frame 0 |
| `first.mp4` | Full picture with selection appearing on frame 78 |
| `final.mp4` | Full picture with selection appearing on frame 74 |
| `edited.mp4` | Full picture with “Two seats to Northgate.” and selection on frame 69 |
| `*.scene.json` | Standalone editable text and vector layer manifests |
| `*.events.json` | Picture clock, stable interaction IDs, UI states and cue anchors |
| `native-before.sha256`, `native-after.sha256` | One hash for every retained native PNG across the repair |
| `repair-and-edit.json` | Native repair extent and changed copy/selection evidence from the decoded MP4s |

Edit the copy and selection frame in [edited.json](edited.json). Change layout, tail paths, panel clipping, easing or shot timing in [scene.mjs](scene.mjs). Generate the scene and invoke one renderer for a new edit.

```sh
node "$S/recreate/example/scene.mjs" /tmp/train-edit.scene.json --config "$S/recreate/example/edited.json"
node "$S/scripts/engines/render.mjs" --method html --scene /tmp/train-edit.scene.json --out /tmp/train-edit.mp4
```

## Picture clock

The reference and each full output contain 120 frames at 30/1, 640 × 360. Validation on this authored fixture exercises independent video and audio analysis plus a one-control repair. It complements comparison against the repository's production films and Observer's reserved tests.

| Frames | Picture and edit boundaries |
| --- | --- |
| 0–17 | Full-frame title holds, then a hard cut |
| 18–29 | Panel, header, composer and incoming bubble hold |
| 30–38 | Outgoing message arrives and lifts eight pixels |
| 56–66 | Options drawer rises 29 pixels above the chat and composer, clipped by the phone frame |
| 74 | First choice changes within a 32 × 28 region at x 426, y 202 |
| 89–96 | Drawer disappears. Receipt arrives and lifts seven pixels |
| 96–119 | Terminal hold through the last frame |

The source has authored audio cues at frames 30, 56, 74 and 89. The rebuilt exports are silent picture masters for a separate soundtrack handoff.
