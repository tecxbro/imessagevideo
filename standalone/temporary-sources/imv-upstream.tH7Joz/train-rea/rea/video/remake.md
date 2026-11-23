---
videomd: 1
part: remake
tokens: 1704
---

## Remake plan

### Step by step

This is a motion-graphics explainer. Do the steps in this order; the detail for each is in the matching subsection below.

1. **Write the content**: one picture of your own for each of the 2 shots in the shot list
2. **Motion graphics**: have the agent make an editable first version and change the text and pictures on top of it rather than starting from scratch; the first version is only a start, where it differs from the original is under “Code build”
3. **Subtitles and styled text**: import `packaging/subtitles.srt` and replace the words; timing and style under “Packaging layer”
4. **Sound effects**: 4; place similar ones from a library at the times under “Sound”
5. **Put it together and compare**: hand the shots you made to the agent; it places them on the original timeline, keeps the original where yours are missing, and renders a side-by-side comparison with the original

**code render / screen capture 2 shots → 1 code project**

### Code composition

Rebuild it as one project in an HTML video framework (such as HyperFrames or Remotion): cuts, transitions and each shot's key frames from "Rhythm and key frames", layout, colours and elements from the scenes below. Text and UI are 100% controllable, changing copy is a data change, and an AI coding assistant can write the project.

`rea-video code-remake <breakdown folder>` only makes a quick draft: it renders `code/remake.mp4` from each scene's sampled points / cut-out, motion and background glow and scores it. Particles, point clouds and data visualisations on a dark ground come close; an illustrated character's acting and morph transitions do not.

- Part 1: shots #1, #2 (0.0–4.0s)

Remake assets (all in the report folder; hand them over together with the data below to whoever writes the code, or to an LLM):
- `shots/shot_XXX_first.jpg` / `_last.jpg`: first / last frame of each shot at full size, for layout, type size and margins
- `shots/shot_XXX_strip.jpg`: key frames about every 0.5 s, to follow the animation
- `shots/shot_XXX_elements.jpg` and `_el_NN.jpg` / `_st_NN.jpg` / `_ly_NN.jpg`: full-size crop of every element once settled, numbered as in the motion timeline; redraw shapes from them, cut out icons, logos and illustrations that cannot be redrawn
- `packaging/overlays.ass`, `packaging/timeline.json`: timing, position and colour of the text

How to build the pictures (by the measured picture type):
- gradients / colour fields: CSS linear / radial gradients, or a few large circles with filter: blur() drifting slowly; glass cards with backdrop-filter
- data chart: SVG / D3 scales for axes and marks, numbers counted up with interpolate(), bars / lines grown with spring()

| Shot | Time | Build | Picture | Camera | Colours | On-screen text |
|---|---|---|---|---|---|---|
| #1 | 0.0–0.6s | gradients / colour fields | (to fill from the images: what the elements form and how they move) | static | ground #1f2141 ·  · drawn #f9f9fc #9b9ab4 #ccccdb #6c6b88 | Message / Train options / RailPlanner |
| #2 | 0.6–4.0s | data chart | (to fill from the images: what the elements form and how they move) | static | ground #e9ecf1 · #f9fcfd #f3f5f9 #1787f8 #cbced3 · drawn #1586f7 #acadb2 #5f6064 #61a7ee | Message / Bookedfor18:40. / RailPlanner |

**Picture scenes** (a new scene whenever what is drawn moves or changes shape as a whole inside a shot. `frames/` holds first / middle / last full-size frames per scene, `scene_XX_layer.png` the drawn layer of the middle frame (background and text removed, alpha by how strongly it stands out), `frames/points/scene_XX.json` samples of that layer, one `x y r g b a` per row with x, y in 0–1. Place particles, trace lines or redraw shapes from these instead of guessing from a description. `track` in `frames/scenes.json` follows the layer's centre and spread over time)

| Scene | Shot | Time | Ground | Background glow | Drawn colours | Pieces | Area (x0 y0 x1 y1) | Motion |
|---|---|---|---|---|---|---|---|---|
| scene_01 | #1 | 0.0–0.6s | #242041 | #514e68, centre (0.51, 0.49), radius 0.12 | — | — | — | — |
| scene_02 | #2 | 0.6–4.0s | #eeedf3 | #bfd5eb, centre (0.50, 0.42), radius 0.09 | #8fc2e9 #bebdc1 #4792d8 | 5 | 0.25 0.18 0.70 0.73 | pans (-0.0%, -1.0%)/s |

When built, score it with `rea-video compare original remake --scenes frames/scenes.json -o dir` (each side's drawn layer is taken against its own ground, so a new ground colour still compares) and fix the lowest-scoring scenes first, from `compare_worst.jpg`.

Per-shot motion timeline (measured: positions in % of frame width / height, colours sampled once the element settles; read together with the key-frame strip)

**Motion #1 0.0–0.6s · 0 events**

- Ground #1f2141; other main colours —; drawn layer #f9f9fc #9b9ab4 #ccccdb #6c6b88
Element crops (numbers match the motion list below; L = the continuously moving layer mid-shot and at the end, S = elements that never move), full-size files in `shots/`:

- S1. never moves: shape / text block · x 39%–60%, y 34%–40% · #8a88b3 · text “RAIL PLANNER / Where are we heading?” · [crop](shots/shot_001_st_01.jpg)
- S2. never moves: shape / text block · x 26%–45%, y 43%–55% · #fbfcff · [crop](shots/shot_001_st_02.jpg)
- S3. never moves: shape / text block · x 46%–73%, y 43%–58% · #fcfcff · text “Train options” · [crop](shots/shot_001_st_03.jpg)

**Motion #2 0.6–4.0s · 2 events**

- Ground #e9ecf1; other main colours #f9fcfd #f3f5f9 #1787f8 #cbced3; drawn layer #1586f7 #acadb2 #5f6064 #61a7ee
Element crops (numbers match the motion list below; L = the continuously moving layer mid-shot and at the end, S = elements that never move), full-size files in `shots/`:

- S1. never moves: shape / text block · x 42%–47%, y 16%–22% · #68686b · [crop](shots/shot_002_st_01.jpg)
- S2. never moves: shape / text block · x 49%–58%, y 16%–22% · #646466 · text “RailPlanner” · [crop](shots/shot_002_st_02.jpg)
- S3. never moves: shape / text block · x 27%–51%, y 33%–39% · #828285 · text “Whereareweheading? / Where are weheading?” · [crop](shots/shot_002_st_03.jpg)
- [crop L1](shots/shot_002_ly_01.jpg) [crop L2](shots/shot_002_ly_02.jpg) · Continuous layer: 11% of the frame moves through the whole shot (x 24%–76%, y 44%–80%), e.g. drifting gradients, particle flow, breathing glow
1. 1.00–1.27s · middle (x 40%–76%, y 40%–48%) · appears, slides leftward, ease-out · #1486f9 · text “Two seats toUnionStation. / Two seats to Unlon Station.” · [crop](shots/shot_002_el_01.jpg)
2. 3.00–3.07s · bottom (x 27%–56%, y 64%–76%) · changes, instant · #e7e7eb · text “19:10 / 4seats / Bookedfor18:40.” · [crop](shots/shot_002_el_02.jpg)
