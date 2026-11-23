# How this video was made: reference.mp4

**How it was made**: code / template render 100%

- 0:04 · horizontal 16:9 · 2 shots, 2.0s each on average
- Confidence 73%, based on: tool measurements
- ⚠️ **Nobody has looked at the picture yet**: live action / AI / 3D / code render come from pixel statistics only and are often wrong across the board after platform transcoding. Turn on a VLM or have an agent review the shots (`rea-video review`) before remaking from this report
- ⚠️ 2 points are uncertain, see “Open questions”

<!--mix-->

![storyboard](storyboard.jpg)

# Part one · Breakdown: how this video is built

## At a glance: picture, packaging, sound

Any short video splits into three layers: the picture, what is laid on top of it (subtitles, styled text, stickers), and the sound. Remake it one layer at a time.

| Layer | In this video | How to make it | Detail |
|---|---|---|---|
| **Picture** (base) | code / template render 2 shots | screen recording / motion graphics in code | “Remake it yourself” |
| **Packaging** (on top) | none | — | “Packaging layer” |
| **Sound** | 4 sound effects | effects: add from a library at the listed times | “Sound” |

## Content and structure

- The whole video's content was not analysed this time (needs AI image reading); subtitle text is under “Packaging layer”

- No narrative line this time (what each shot is doing in the story needs AI image reading); the “Picture” column of the shot list is a start

## Shot list

| # | Frame | Time | Picture | Camera |
|---|---|---|---|---|
| 1 | ![#1](shots/shot_001_first.jpg) | 0:00.0 · 0.6s | — | static |
| 2 | ![#2](shots/shot_002_first.jpg) | 0:00.6 · 3.4s | — | static |

## Cast, scenes and props

- No cast extracted this time (needs AI image reading)

## Camera and lighting

## Packaging layer (subtitles / styled text / stickers / sound-effect hits)

- 4 subtitle lines (bottom/middle, up to 1 rows): cyan text, keywords highlighted in blue, line height 4.2%; entrance: hard in×3
- Possible SFX hits (unconfirmed signal candidates) on: subtitle in ×3

<details class="ref"><summary>text timeline (4 rows)</summary>

| Time | Kind | Text | Style | In / out | SFX |
|---|---|---|---|---|---|
| 1.00–1.60s | subtitle | Two seats toUnionStation. | cyan text, keywords highlighted in blue, line height 4.2% (about 15px) | hard in / hard out | pop |
| 2.00–3.00s | subtitle | 19:10 | black text, line height 4.2% (about 15px) | hard in / hard out | pop |
| 3.00–4.00s | subtitle | Two seats to Unlon Station. | cyan text, keywords highlighted in blue, line height 4.4% (about 16px) | hard in | pop |
| 3.00–4.00s | subtitle | Bookedfor18:40. | black text, line height 3.9% (about 14px) | — | — |

</details>

- Remake: import `packaging/subtitles.srt` into your editor and put in your own words; the styled version is `packaging/overlays.ass`

## Sound

**Sound effects** (4)

| Time | Listen | Type | Description | On screen |
|---|---|---|---|---|
| 0.96s | [listen](sfx/sfx_01.wav) | pop | — | subtitle "Two seats toUnio" appears |
| 1.83s | [listen](sfx/sfx_02.wav) | pop | — | subtitle "19:10" appears |
| 2.44s | [listen](sfx/sfx_03.wav) | pop | — | — |
| 2.94s | [listen](sfx/sfx_04.wav) | pop | — | subtitle "Two seats to Unl" appears |

- Remake: take a similar effect from your editor's library and place it at that time

<details class="ref"><summary>Sound measurements and evidence</summary>

![audio](audio.png)

- Loudness -31.1 dBFS, peak -8.9 dBFS
- Effects source: added in post from an SFX library / editor (added in post from an SFX library / editor 57%, generated with the picture by the video model (native audio) 29%, location sound 14%)

</details>

## Open questions

- The VLM did not run (No VLM; live action / AI / 3D are told apart from pixel statistics only, so confidence is limited. An agent that can see images: run rea-video review, look at each shot and merge with apply-review; otherwise configure a VLM (any OpenAI-compatible multimodal model, e.g. Gemini / GPT-4o / Doubao / Qwen-VL): set REA_VLM_BASE_URL, REA_VLM_API_KEY and REA_VLM_MODEL (several models comma-separated as fallbacks), then rerun with --vlm): live action / AI / 3D is decided by signal forensics alone; configure a multimodal model and rerun with --vlm, or have an agent review the frames
- No AI listened to the soundtrack: real voice versus TTS is inferred from the waveform; the effects were picked off the mix where the sound jumps, so plosives and drum hits can be counted too. Play the stems and each effect under “Sound” to check

# Part two · Remake plan

## Remake it yourself: do it in this order

Copy the method and the rhythm, not the pictures: keep what each part does and fill it with your own content and material.

This is a motion-graphics explainer. Do the steps in this order; the detail for each is in the matching subsection below.

1. **Write the content**: one picture of your own for each of the 2 shots in the shot list
2. **Motion graphics**: have the agent make an editable first version and change the text and pictures on top of it rather than starting from scratch; the first version is only a start, where it differs from the original is under “Code build”
3. **Subtitles and styled text**: import `packaging/subtitles.srt` and replace the words; timing and style under “Packaging layer”
4. **Sound effects**: 4; place similar ones from a library at the times under “Sound”
5. **Put it together and compare**: hand the shots you made to the agent; it places them on the original timeline, keeps the original where yours are missing, and renders a side-by-side comparison with the original

### Code build

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

<details class="ref"><summary>Motion #1 0.0–0.6s · 0 events</summary>

![#1 0.0–0.6s](shots/shot_001_strip.jpg)

- Ground #1f2141; other main colours —; drawn layer #f9f9fc #9b9ab4 #ccccdb #6c6b88
Element crops (numbers match the motion list below; L = the continuously moving layer mid-shot and at the end, S = elements that never move), full-size files in `shots/`:

![#1 0.0–0.6s](shots/shot_001_elements.jpg)

- S1. never moves: shape / text block · x 39%–60%, y 34%–40% · #8a88b3 · text “RAIL PLANNER / Where are we heading?” · [crop](shots/shot_001_st_01.jpg)
- S2. never moves: shape / text block · x 26%–45%, y 43%–55% · #fbfcff · [crop](shots/shot_001_st_02.jpg)
- S3. never moves: shape / text block · x 46%–73%, y 43%–58% · #fcfcff · text “Train options” · [crop](shots/shot_001_st_03.jpg)

</details>

<details class="ref"><summary>Motion #2 0.6–4.0s · 2 events</summary>

![#2 0.6–4.0s](shots/shot_002_strip.jpg)

- Ground #e9ecf1; other main colours #f9fcfd #f3f5f9 #1787f8 #cbced3; drawn layer #1586f7 #acadb2 #5f6064 #61a7ee
Element crops (numbers match the motion list below; L = the continuously moving layer mid-shot and at the end, S = elements that never move), full-size files in `shots/`:

![#2 0.6–4.0s](shots/shot_002_elements.jpg)

- S1. never moves: shape / text block · x 42%–47%, y 16%–22% · #68686b · [crop](shots/shot_002_st_01.jpg)
- S2. never moves: shape / text block · x 49%–58%, y 16%–22% · #646466 · text “RailPlanner” · [crop](shots/shot_002_st_02.jpg)
- S3. never moves: shape / text block · x 27%–51%, y 33%–39% · #828285 · text “Whereareweheading? / Where are weheading?” · [crop](shots/shot_002_st_03.jpg)
- [crop L1](shots/shot_002_ly_01.jpg) [crop L2](shots/shot_002_ly_02.jpg) · Continuous layer: 11% of the frame moves through the whole shot (x 24%–76%, y 44%–80%), e.g. drifting gradients, particle flow, breathing glow
1. 1.00–1.27s · middle (x 40%–76%, y 40%–48%) · appears, slides leftward, ease-out · #1486f9 · text “Two seats toUnionStation. / Two seats to Unlon Station.” · [crop](shots/shot_002_el_01.jpg)
2. 3.00–3.07s · bottom (x 27%–56%, y 64%–76%) · changes, instant · #e7e7eb · text “19:10 / 4seats / Bookedfor18:40.” · [crop](shots/shot_002_el_02.jpg)

</details>

### Edit

- Cut in the order and lengths of the shot list
- Rhythm: 15.0 cuts per minute, 2.0s average shot; no live-action shots; transitions cut×1

## Appendix

### Shot by shot

Each shot has two parts: what is visible on screen, and how the tools infer it was made (with the basis); remake prompts last. Folded by default.

<details class="ref"><summary>#1 00:00.000–00:00.600 · code / template render</summary>

![shot_001](shots/shot_001.jpg)

**Visible on screen** (check against the frames)
- Text track (text in the picture/bottom): Message
- Text track (text in the picture/middle): RAIL PLANNER / Where are we heading?
- Text track (text in the picture/middle): Train options
- Text track (text in the picture/top): RailPlanner

**How it was made, as inferred by the tools** (inferred, not seen)
- Inference: code / template render 86%, screen recording / screenshot 9%, static hold 1% (deterministic)
- Material: rendered by the creator
- Basis (tool measurements, not necessarily visible to the eye):
  - Picture is almost entirely still: 100% of adjacent frames are pixel-identical, first-to-last frame difference 0.00
  - The picture is large saturated colour fields with almost no material texture (1% fine-texture pixels; footage, AI and 3D renders keep fabric / skin / noise texture): vector / gradient graphics drawn by code
  - Rendered texture: 94% flat colour blocks, 95% of pixels use only 1 colours, 35% axis-aligned edges

- Remake: Code render: rebuild in an HTML video framework (such as HyperFrames or Remotion) from the rhythm, key frames and layout, 100% controllable, no generative model needed

</details>

<details class="ref"><summary>#2 00:00.600–00:04.000 · code / template render</summary>

![shot_002](shots/shot_002.jpg)

**Visible on screen** (check against the frames)
- Text track (text in the picture/bottom): Message
- Text track (text in the picture/bottom): 19:10 / 4seats
- Text track (text in the picture/middle): Whereareweheading? / Where are weheading?
- Text track (text in the picture/middle): Two seats toUnionStation. / Pickatrain / Two seats to Unlon Station.

**How it was made, as inferred by the tools** (inferred, not seen)
- Inference: code / template render 71%, screen recording / screenshot 14%, 3D render 10% (deterministic)
- Material: rendered by the creator
- Basis (tool measurements, not necessarily visible to the eye):
  - 78% of adjacent frames are exact duplicates, only local elements move (typical of template / motion-graphics animation, or a hold with local motion)
  - Rendered texture: 74% flat colour blocks, 95% of pixels use only 4 colours, 43% axis-aligned edges
  - 100% of background pixels never change frame to frame while local elements move: 2D compositing / code-driven motion graphics

- Remake: Code render: rebuild in an HTML video framework (such as HyperFrames or Remotion) from the rhythm, key frames and layout, 100% controllable, no generative model needed

</details>

### Metadata clues

- Encoder: `Lavf61.7.100`

### Notes

- Deterministic forensics is reliable on motion, whole-frame pan/zoom, rendered texture and 24→30 fps conversion; telling live action from AI from 3D needs image reading (a VLM or an AI assistant's review), and a look at the frames yourself.
- Platform transcoding usually strips metadata; missing metadata proves nothing.
- The full data is in `breakdown.json`; the package for models starts at `VIDEO.md`.

---

Made with [REA-VIDEO](https://github.com/JuneYaooo/rea-video) · https://github.com/JuneYaooo/rea-video
