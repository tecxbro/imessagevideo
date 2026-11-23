---
videomd: 1
part: remake
tokens: 4498
---

## Remake plan

### Step by step

This is a motion-graphics explainer. Do the steps in this order; the detail for each is in the matching subsection below. 42% of the time is a 3D / animation; its steps are included.

1. **Write the content**: one picture of your own for each of the 9 shots in the shot list
2. **Generate**: 1 call (13 s), several shots each. Each shot gets one source frame for composition (subtitles erased, in `remake/refs/`), the swapped-in people, animals and products get reference images, and the prompt lists the shots in order
3. **Adapt the prompts to your model**: the prompts in this report are generic, and every model reads them differently (how shots are split, how references are addressed, how dialogue is written). Before generating, rewrite them following the official prompt guide of the model you actually use, or have the agent refine them with that model's prompting skill; notes for MiniMax H3 / H3 Max at the top of “AI generation”
4. **Motion graphics**: have the agent make an editable first version and change the text and pictures on top of it rather than starting from scratch; the first version is only a start, where it differs from the original is under “Code build”
5. **Voice**: the original is TTS voice-over; record it yourself or use TTS
6. **Edit**: follow the order and lengths in the shot list; the original has 9 shots at 3.5s each; 7 transitions under “Edit”
7. **Subtitles and styled text**: import `packaging/subtitles.srt` and replace the words; timing and style under “Packaging layer”
8. **Music**: find a track at the same tempo and mood (source: to confirm, about 172 BPM, F major)
9. **Sound effects**: 29; place similar ones from a library at the times under “Sound”
10. **Put it together and compare**: hand the shots you made to the agent; it places them on the original timeline, keeps the original where yours are missing, and renders a side-by-side comparison with the original

**3 3D render shots → 1 generation unit, 1 MiniMax H3 / H3 Max call; code render / screen capture 6 shots → 1 code project (3 parts)**

### Generation units

| Part | Shots | Time | Length | Prepare |
|---|---|---|---|---|
| G1 | #3, #4, #6 | 5.4–12.5s, 19.1–25.0s | 12.9s | reference images |

**Why it is split this way**

- Grouping: consecutive shots share a call where they fit, ≤15s per call, ≤4 shots; a long stretch is cut at a scene change first
- Inputs: the model takes no reference video: one source frame per shot (subtitles erased) fixes composition, swapped-in things get their own images
- Audio: the model can generate action sound effects and ambience along with the picture; voice-over is better done as separate TTS and mixed in, so copy and timing stay editable
- Packaging: the text label, styled text on the generated shots is post-production packaging: keep it out of the prompts (erased from source references) and lay it back on from the packaging timeline after generation

**G1 · shots #3, #4, #6 · 12.9s**

- reference images: source frames of shots #3、#4、#6 (subtitles erased)

- these shots are separated by inserts in the cut: generate them together and put the inserts back in the edit

Draft prompt (generic; rewrite it in MiniMax H3 / H3 Max's format into remake/prompts.json before generating):

```text
Generate the shots below in order in one go, hard cuts between them; each shot takes composition, size and camera from its source frame image. Square 1:1; high key (bright overall, almost no shadows), soft light (almost no lit / shadow edge), cool (daylight / cool-white LED), background clearly blurred (shallow depth of field / portrait mode). No subtitles, captions or watermarks in the picture.
Shot 1 (from 0.0s): Glossy handset and cream highlights move into pink bloom and editable text; the precise production method is uncertain. (composition: @图片1)
Shot 2 (from 3.1s): Portrait discs fly in and resolve to three labelled profiles; track portraits independently from their name chips. (composition: @图片2)
Shot 3 (from 7.1s): Colored app tiles orbit; check the distinct edge light and numeral silhouette on the blue tile during the exit. (composition: @图片3)
```

### Code composition

Rebuild it as one project in an HTML video framework (such as HyperFrames or Remotion): cuts, transitions and each shot's key frames from "Rhythm and key frames", layout, colours and elements from the scenes below. Text and UI are 100% controllable, changing copy is a data change, and an AI coding assistant can write the project.

`rea-video code-remake <breakdown folder>` only makes a quick draft: it renders `code/remake.mp4` from each scene's sampled points / cut-out, motion and background glow and scores it. Particles, point clouds and data visualisations on a dark ground come close; an illustrated character's acting and morph transitions do not.

- Part 1: shots #1, #2 (0.0–5.4s)
- Part 2: shots #5 (12.5–19.1s)
- Part 3: shots #7–#9 (25.0–31.1s)

Remake assets (all in the report folder; hand them over together with the data below to whoever writes the code, or to an LLM):
- `shots/shot_XXX_first.jpg` / `_last.jpg`: first / last frame of each shot at full size, for layout, type size and margins
- `shots/shot_XXX_strip.jpg`: key frames about every 0.5 s, to follow the animation
- `shots/shot_XXX_elements.jpg` and `_el_NN.jpg` / `_st_NN.jpg` / `_ly_NN.jpg`: full-size crop of every element once settled, numbered as in the motion timeline; redraw shapes from them, cut out icons, logos and illustrations that cannot be redrawn
- `packaging/overlays.ass`, `packaging/timeline.json`: timing, position and colour of the text

How to build the pictures (by the measured picture type):
- data chart: SVG / D3 scales for axes and marks, numbers counted up with interpolate(), bars / lines grown with spring()
- UI / document: HTML / CSS cards and layout matched to the frame (radius, shadow, type sizes), elements enter with spring(); a real UI can be screen-recorded
- line art / dots: SVG paths drawn on with stroke-dashoffset, or Canvas flow lines from a noise field / dots placed on a target shape; match stroke width, colour and density from the frame
- kinetic type: Word-by-word spring() entrances (offset + scale + opacity), highlight boxes on key words; match font, size and leading from the frame

| Shot | Time | Build | Picture | Camera | Colours | On-screen text |
|---|---|---|---|---|---|---|
| #1 | 0.0–4.1s | data chart | Three pinned portraits flow into scrollable rows with UI labels; image crops and UI geometry should be treated separately. | picture drifts up | ground #fafcfc · #eaeeef #d9d8dd #968f8b · drawn #988777 #c7bfbf #504b48 #4c95c6 | 7:13 / Darla / 9:55AM / hey bby what ru doin? / EI / 1:30 PM |
| #2 | 4.1–5.4s | UI / document | Dark rounded logo settles, then an enlarged handset rim enters; mark and shell need separate measurements. | pull out 17%/s, picture drifts right | ground #fbfcfd · #3f4041 #656869 #d8d9db #212223 · drawn #363636 #0f0f0f #5d5e5e #959697 | Sidehoe |
| #5 | 12.5–19.1s | data chart | Handset, detached blue suggestion, pointer, and calendar share one detected segment; subdivide UI states and inspect the calendar overlap. | push in 10%/s, picture drifts up | ground #fbfcfd · #d2f0fc #ddcffb #bfd0d8 · drawn #19c5f8 #b9b3d0 #1d1d1d #80636f | 9:41 / Yes, it was awesome! / M / T / 17 / Yesterdaywasreallynice:) |
| #7 | 25.0–27.8s | line art / dots | Second handset reframes and the pointer closes in on controls; inspect the path after the contact. | push in 4%/s, picture drifts left | ground #f9fcfd · #e7e9ec #d7d9dd #e0f3f9 #474849 · drawn #b5b4b5 #0d0d0e #767676 #444444 | toLiliana.Wantme toshoothera / 9:41 / Sidehoe / Does thatworkforyou? |
| #8 | 27.8–29.2s | UI / document | The black badge appears first and the closing copy follows as a separate reveal. | pull out 8%/s, picture drifts right | ground #fbfcfd · #f8e0fb #f8cffd #fbf0fd #f5c0fb · drawn #353535 #4e4d51 | — |
| #9 | 29.2–31.1s | kinetic type | Pink wash, lockup, and final fade change together; verify the last black hold using decoded timestamps. | static | ground #626365 · #5f5461 #605c62 #5e4b60 #141516 · drawn #363637 #100f10 #746f73 | — |

**Picture scenes** (a new scene whenever what is drawn moves or changes shape as a whole inside a shot. `frames/` holds first / middle / last full-size frames per scene, `scene_XX_layer.png` the drawn layer of the middle frame (background and text removed, alpha by how strongly it stands out), `frames/points/scene_XX.json` samples of that layer, one `x y r g b a` per row with x, y in 0–1. Place particles, trace lines or redraw shapes from these instead of guessing from a description. `track` in `frames/scenes.json` follows the layer's centre and spread over time)

| Scene | Shot | Time | Ground | Background glow | Drawn colours | Pieces | Area (x0 y0 x1 y1) | Motion |
|---|---|---|---|---|---|---|---|---|
| scene_01 | #1 | 0.0–2.0s | #ffffff | #99a7b3, centre (0.52, 0.50), radius 0.14 | #c0a692 #5aa1d1 #5f4b43 | 38 | 0.18 0.22 0.81 0.94 | zoom in 10%/s, pans (+0.2%, -9.3%)/s |
| scene_02 | #1 | 2.0–4.1s | #ffffff | #e8e7e6, centre (0.28, 0.42), radius 0.19 | #dfbcb3 #796456 #25a9f4 | 28 | 0.17 0.07 0.66 0.88 | morphs in from the last scene, zoom out 7%/s, pans (+1.6%, -0.8%)/s |
| scene_03 | #2 | 4.1–5.4s | #ffffff | #846e78, centre (0.50, 0.47), radius 0.14 | #343434 | 4 | 0.38 0.38 0.61 0.58 | zoom out 17%/s, turns clockwise 1.0°/s, pans (+0.9%, +3.8%)/s |
| scene_04 | #5 | 12.5–14.3s | #ffffff | #929192, centre (0.51, 0.20), radius 0.12 | #202021 #7e7e7f #31d0fa | 50 | 0.24 0.04 0.75 0.98 | zoom in 21%/s, pans (-1.8%, +7.9%)/s |
| scene_05 | #5 | 14.3–19.1s | #ffffff | #cecdf7, centre (0.50, 0.47), radius 0.18 | #dedddd #cdc5fa #972ab5 | 5 | 0.19 0.27 0.88 0.83 | morphs in from the last scene, zoom out 4%/s, turns clockwise 1.4°/s, pans (+0.7%, -4.2%)/s |
| scene_06 | #7 | 25.0–27.8s | #ffffff | #787879, centre (0.50, 0.04), radius 0.06 | #1d1d1d #5e5e5e #a5a2a7 | 37 | 0.24 0.00 0.88 1.00 | zoom in 16%/s, pans (+0.1%, +6.8%)/s |
| scene_07 | #8 | 27.8–29.2s | #ffffff | #77666e, centre (0.50, 0.49), radius 0.14 | #343434 #4a4143 | 7 | 0.41 0.45 0.62 0.57 | zoom out 20%/s, turns clockwise 1.0°/s, pans (+0.1%, -5.9%)/s, points wander |

When built, score it with `rea-video compare original remake --scenes frames/scenes.json -o dir` (each side's drawn layer is taken against its own ground, so a new ground colour still compares) and fix the lowest-scoring scenes first, from `compare_worst.jpg`.

Per-shot motion timeline (measured: positions in % of frame width / height, colours sampled once the element settles; read together with the key-frame strip)

**Motion #1 0.0–4.1s · 2 events**

- Ground #fafcfc; other main colours #eaeeef #d9d8dd #968f8b; drawn layer #988777 #c7bfbf #504b48 #4c95c6
Element crops (numbers match the motion list below; L = the continuously moving layer mid-shot and at the end, S = elements that never move), full-size files in `shots/`:

- [crop L1](shots/shot_001_ly_01.jpg) [crop L2](shots/shot_001_ly_02.jpg) · Continuous layer: 12% of the frame moves through the whole shot (x 18%–80%, y 9%–96%), e.g. drifting gradients, particle flow, breathing glow
1. 1.20–4.07s · middle (x 16%–84%, y 0%–100%) · disappears, moves upward, ease-in-out · #aca09a · text “7:13 / Edit / Messages” · [crop](shots/shot_001_el_01.jpg)
2. 3.73–4.07s · middle (x 44%–56%, y 56%–60%) · disappears, moves leftward, ease-in · #d3d3d3 · text “Sydney” · [crop](shots/shot_001_el_02.jpg)

**Motion #2 4.1–5.4s (fade in) · 3 events**

- Ground #fbfcfd; other main colours #3f4041 #656869 #d8d9db #212223; drawn layer #363636 #0f0f0f #5d5e5e #959697
Element crops (numbers match the motion list below; L = the continuously moving layer mid-shot and at the end, S = elements that never move), full-size files in `shots/`:

- [crop L1](shots/shot_002_ly_01.jpg) [crop L2](shots/shot_002_ly_02.jpg) · Continuous layer: 8% of the frame moves through the whole shot (x 33%–64%, y 36%–73%), e.g. drifting gradients, particle flow, breathing glow
1. 4.19–4.25s · middle (x 33%–67%, y 40%–60%) · appears, instant · #353333 · [crop](shots/shot_002_el_01.jpg)
2. 5.39–5.45s · top (x 31%–42%, y 11%–20%) · appears, instant · #e5e5e5 · [crop](shots/shot_002_el_02.jpg)
3. 5.39–5.45s · middle right (x 76%–82%, y 51%–58%) · appears, instant · #fffaec · [crop](shots/shot_002_el_03.jpg)

**Motion #5 12.5–19.1s (slide in) · 6 events**

- Ground #fbfcfd; other main colours #d2f0fc #ddcffb #bfd0d8; drawn layer #19c5f8 #b9b3d0 #1d1d1d #80636f
Element crops (numbers match the motion list below; L = the continuously moving layer mid-shot and at the end, S = elements that never move), full-size files in `shots/`:

- [crop L1](shots/shot_005_ly_01.jpg) [crop L2](shots/shot_005_ly_02.jpg) · Continuous layer: 16% of the frame moves through the whole shot (x 29%–91%, y 18%–64%), e.g. drifting gradients, particle flow, breathing glow
1. 12.59–18.99s · middle (x 0%–100%, y 0%–100%) · disappears, moves leftward, ease-out · #dfe4e5 · text “9:41 / Sofia> / Yesterday was really nice:)” · [crop](shots/shot_005_el_01.jpg)
2. 12.59–14.25s · top (x 29%–51%, y 9%–36%) · disappears, moves upward, linear · #e2e2e5 · text “9:41 / Sofia> / Yes, it was awesome!” · [crop](shots/shot_005_el_02.jpg)
3. 13.05–14.25s · top (x 29%–71%, y 0%–36%) · disappears, moves upward, ease-in-out · #eceef0 · text “9:41 / Sofia> / Yesterday was really nice:)” · [crop](shots/shot_005_el_03.jpg)
4. 13.85–16.32s · top (x 29%–69%, y 0%–36%) · disappears, moves rightward, ease-in-out · #e8e8eb · text “9:41 / Sofia> / Yesterday was really nice:)” · [crop](shots/shot_005_el_04.jpg)
5. 14.45–17.39s · top (x 13%–73%, y 7%–47%) · changes, moves leftward, ease-in-out · #bec3f9 · text “9:41 / Sofia> / Yesterday was really nice:)” · [crop](shots/shot_005_el_05.jpg)
6. 17.99–19.05s · middle (x 11%–91%, y 11%–62%) · disappears, moves downward, ease-in-out · #c0c3fb · text “9:41 / Sofia> / Yesterday was really nice:)” · [crop](shots/shot_005_el_06.jpg)

**Motion #7 25.0–27.8s (fade in) · 8 events**

- Ground #f9fcfd; other main colours #e7e9ec #d7d9dd #e0f3f9 #474849; drawn layer #b5b4b5 #0d0d0e #767676 #444444
Element crops (numbers match the motion list below; L = the continuously moving layer mid-shot and at the end, S = elements that never move), full-size files in `shots/`:

- [crop L1](shots/shot_007_ly_01.jpg) [crop L2](shots/shot_007_ly_02.jpg) · Continuous layer: 49% of the frame moves through the whole shot (x 11%–89%, y 0%–100%), e.g. drifting gradients, particle flow, breathing glow
1. 25.03–26.23s · middle (x 31%–69%, y 27%–58%) · changes, unfolds upward (draw-on / grow / wipe), ease-out · #fdfdfd · text “Today / lt's been 6 menths sinee yeu spoke / to Liliana.Want me to sheet her a” · [crop](shots/shot_007_el_01.jpg)
2. 26.03–26.89s · middle (x 16%–64%, y 4%–78%) · changes, moves downward, ease-in-out · #e8e9ef · text “9:41 / Certainiy, Linda is available at 4pm / Does that werk for you?” · [crop](shots/shot_007_el_02.jpg)
3. 26.29–27.76s · bottom left (x 16%–27%, y 87%–100%) · appears, slides leftward, ease-in-out · #cbd0d3 · [crop](shots/shot_007_el_03.jpg)
4. 26.69–27.69s · middle right (x 87%–91%, y 7%–100%) · changes, scales up, ease-in-out · #fdfdfd · [crop](shots/shot_007_el_04.jpg)
5. 26.83–27.63s · middle left (x 7%–11%, y 0%–100%) · changes, scales up, linear · #fdfdfd · [crop](shots/shot_007_el_05.jpg)
6. 27.43–27.76s · middle left (x 16%–42%, y 0%–78%) · changes, moves upward, ease-in · #ebeced · text “9:41 / Does that werk for you? / text?” · [crop](shots/shot_007_el_06.jpg)
7. 27.43–27.76s · middle right (x 71%–84%, y 0%–71%) · appears, slides upward, ease-in · #ddecec · [crop](shots/shot_007_el_07.jpg)
8. 27.69–27.76s · top (x 53%–67%, y 18%–20%) · appears, instant · #d6d6d7 · [crop](shots/shot_007_el_08.jpg)

**Motion #8 27.8–29.2s · 2 events**

- Ground #fbfcfd; other main colours #f8e0fb #f8cffd #fbf0fd #f5c0fb; drawn layer #353535 #4e4d51
Element crops (numbers match the motion list below; L = the continuously moving layer mid-shot and at the end, S = elements that never move), full-size files in `shots/`:

- [crop L1](shots/shot_008_ly_01.jpg) [crop L2](shots/shot_008_ly_02.jpg) · Continuous layer: 39% of the frame moves through the whole shot (x 0%–100%, y 33%–100%), e.g. drifting gradients, particle flow, breathing glow
1. 28.71–29.11s · middle (x 29%–40%, y 58%–67%) · appears, slides upward, linear · #909090 · text “The” · [crop](shots/shot_008_el_01.jpg)
2. 28.91–29.11s · middle (x 49%–69%, y 58%–64%) · appears, slides rightward, ease-in · #c0bbc1 · text “The most personal” · [crop](shots/shot_008_el_02.jpg)

**Motion #9 29.2–31.1s (slide in) · 1 events**

- Ground #626365; other main colours #5f5461 #605c62 #5e4b60 #141516; drawn layer #363637 #100f10 #746f73
Element crops (numbers match the motion list below; L = the continuously moving layer mid-shot and at the end, S = elements that never move), full-size files in `shots/`:

- [crop L1](shots/shot_009_ly_01.jpg) [crop L2](shots/shot_009_ly_02.jpg) · Continuous layer: 22% of the frame moves through the whole shot (x 0%–100%, y 38%–100%), e.g. drifting gradients, particle flow, breathing glow
1. 30.67–31.07s · middle (x 0%–100%, y 0%–100%) · disappears, moves upward, linear · #fdfafd · text “The most personal / iMessage / iMessage assistant” · [crop](shots/shot_009_el_01.jpg)
