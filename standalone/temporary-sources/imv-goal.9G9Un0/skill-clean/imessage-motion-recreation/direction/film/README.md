# The Moon Cue — picture source

An original 15-second, 960 × 540 film at 24 fps. The world, miniatures, props,
cast, choreography and screen lighting were authored for this brief.

## Edit and render

- `edit.json` holds cut frames, message copy and endline.
- `stage.py` defines the layered theater, puppet pivots, moving paper crescent,
  foreground audience, table, tin, brass stars and glove. Shape geometry,
  palettes, light and seeded texture are editable.
- `conversation.py` compiles the conversation through the Clone iMessage UI
  adapter. Text and send/receive timing remain in editable UI geometry. The
  film takes the paper skin through a dark grade and adds practical framing
  plus a two-frame press. It uses the same renderer as the base Pillow engine.
- `movement.py` defines the travel, focus handoff and continuous push toward
  the physical clue. `render.py` sets the cut and exports picture plus events.

Run from the repository root with Python 3.11+, FFmpeg with libx264, Pillow,
NumPy, fontconfig and DejaVu Sans and Serif installed. The frame evidence was
made with Pillow 13.0.0, NumPy 2.3.5 and FFmpeg 7.1.5.

```sh
D=skill/imessage-motion-recreation/direction/film
python3 -m pip install -r "$D/requirements.txt"
python3 "$D/render.py" --out /tmp/moon-picture.mp4
python3 "$D/render.py" --frame 153 --out /tmp/moon-frame-153.png
```

The integrated skill finds `ui/` alongside `direction/`. In the standalone
Direction branch, use the pinned adapter below and pass its parent directory.
Use the same pin for byte-for-byte reproduction in any checkout. The current
adapter also compiles this edit, with its own screen pixels. A newly rendered
picture needs its own Sound landmark check before mixing.

```sh
git fetch origin refs/heads/codex-video-v3/ui:refs/remotes/origin/codex-video-v3/ui
ui_root=$(mktemp -d)
git archive 9beea91a43c0b24fb7a2061ea54071d426f621c6 skill/imessage-motion-recreation/ui |
  tar -x -C "$ui_root" --strip-components=2
python3 "$D/render.py" --ui-root "$ui_root" --out /tmp/moon-picture.mp4
```

`--map-only` exports the complete frame/addressable event map without encoding.
The event map uses Observer's timeline clock. The initial rough renderer and
its alternate cut frames are preserved at `2873e04`. The locked version uses
a revised composition and compilation path.

A clean export with only this film source, the pinned UI adapter, and the
base Pillow renderer reproduced both locked file hashes. Values appear in
`locked.sha256` in the review folder.

For exact review media, product claims and revision frames, see
[the Direction review folder](../../../../review/imv-v3/direction/README.md).
