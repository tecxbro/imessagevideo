# Train options

This four-second authored development reference shows a title, two Messages-style bubbles, an options drawer, a small seat selection and a receipt. The reference is an independently rendered SVG document with original synthesized cues. The initial rebuild uses the repository's director components to render editable text, shapes, masks and timing. The companion project below exercises the Clone iMessage UI handoff.

## Reproduce

For the complete render, compare, edit and destructive-test proof, run from the repository root with a fresh output directory.

```sh
bash skill/imessage-motion-recreation/recreate/example/prove.sh /tmp/recreate-train
```

To generate just the reference or just the editable exports, use the separate commands below.

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

## Reproduce the isolated render

On Linux with Bubblewrap and the renderer dependencies installed, stage the editable manifest and engine in a fresh directory. The render mounts the input, an empty output directory and the system runtime, with networking disabled.

```sh
S=skill/imessage-motion-recreation
D=review/imv-v3/recreate/train
WORK=$(mktemp -d)
mkdir -p "$WORK/input/engine"
cp "$D/final.scene.json" "$WORK/input/scene.json"
cp -a "$S/scripts/engines/." "$WORK/input/engine"
bash "$S/recreate/isolated-render.sh" "$WORK/input" "$WORK/output" \
  node /input/engine/render.mjs --method html --scene /input/scene.json --out /output/final.mp4
sha256sum "$WORK/output/final.mp4" "$D/final.mp4"
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

## Clone iMessage UI

[ui-train.json](ui-train.json) carries the same booking interaction and stable event IDs into the Clone iMessage UI film-paper skin. The adapter compiles the editable transcript, header, composer and tray. [compile_clone_ui.py](compile_clone_ui.py) mounts the original product-specific seat control in the first tray item. This portrait project has its own picture layouts. The native source-vs-export comparison above applies to the 640 × 360 development fixture.

Run with a Python environment that has Pillow, Fontconfig and the DejaVu Sans regular/bold fonts. In the integrated checkout, set `PYTHONPATH` to the skill directory when calling the compiler as a script. On the standalone Recreation branch, stage only the teammate's UI folder at the tested handoff commit.

```sh
S=skill/imessage-motion-recreation
STAGE=$(mktemp -d)
git fetch origin refs/heads/codex-video-v3/ui
git archive 9beea91a43c0b24fb7a2061ea54071d426f621c6 "$S/ui" | tar -x -C "$STAGE"
PYTHONPATH="$STAGE/$S" python3 "$S/recreate/example/compile_clone_ui.py" \
  "$S/recreate/example/ui-train.json" --out "$STAGE/train.scene.json"
node "$S/scripts/engines/render.mjs" --method html --scene "$STAGE/train.scene.json" --out "$STAGE/train.mp4"

PYTHONPATH="$STAGE/$S" python3 "$S/recreate/example/compile_clone_ui.py" \
  "$S/recreate/example/ui-train.json" --edit "$S/recreate/example/edited.json" --out "$STAGE/train-edit.scene.json"
node "$S/scripts/engines/render.mjs" --method html --scene "$STAGE/train-edit.scene.json" --out "$STAGE/train-edit.mp4"
```

Both pictures export 120 silent frames at 30/1, 402 × 480. The edit moves `recreate.train.seat-selection` from frame 74 to 69 and changes the outgoing message to “Two seats to Northgate.”
