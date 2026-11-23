# unseen-doors editable project

Reconstruction of `iv-test/unseen.mp4` (960x720, 30fps, 150 frames).

- `scene.json` — full-film Pillow scene: nav chrome + avatar + "Sam" + divider,
  outgoing bubble "train gets in at 6", incoming "see you there" (fixed), and the
  `doors` group ("doors at 7") that slides up at t=0.5s then runs the learned
  jelly squash-stretch (library entry `jelly-settle-arrive`).
- `renderer/render_pillow.py` — the pinned renderer (same engine the motion was
  registered with).
- `assets/` — none required; fonts resolve through `fc-match` (Helvetica).

Render:
```
python3 -I renderer/render_pillow.py --scene scene.json --out film.mp4 --frames-dir native
```
