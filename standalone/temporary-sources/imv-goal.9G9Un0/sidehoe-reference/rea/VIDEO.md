---
videomd: 1
name: sidehoe
description: 'Made with (inferred): code / template render 52%, 3D render 48%'
source:
  file: sidehoe.mp4
  sha256: f821bb58cbdb265a75d572616d0da723e9cfb6de31e3db5f8a17d94dc15b5327
  duration: 31.12
  size: 2000x2000
  fps: 25.0
  aspect: '1:1'
shots: 9
lang: en
made_mix:
  code_render: 0.5231
  cg_3d: 0.4769
confidence: 0.621
readers:
- tools
open_questions: 7
generator:
  name: rea-video
  version: 0.1.0
---

# sidehoe.mp4

**Verdict** (inferred): Mixed production: code / template render 52% + 3D render 48%; overlays: styled text, subtitles (composited in code / an editor); audio: voice + music 172.3BPM (to confirm, leaning stock library music) + 29 possible sound effects (unconfirmed signal candidates); packaging: 5 subtitle lines, styled text ×1, text labels ×37, 15 possible sound effects at text / sticker pops (unconfirmed)
**Made with** (inferred, by duration): code / template render 52%, 3D render 48%
**Remake**: 4 3D render shots → 1 generation unit, 1 MiniMax H3 / H3 Max call; code render / screen capture 5 shots → 1 code project (3 parts)

## Next steps

- No VLM ran: if you can see images, review first: `rea-video review <this dir>` → fill `review_answers.json` → `rea-video apply-review <this dir>`
- Remake: `rea-video remake <this dir>` does what can be done automatically and keeps the original elsewhere; `remake/status.md` says per shot what is left. Add incoming clips to `remake/mine.json` and run it again
- Code-rendered shots are best rebuilt in an HTML video framework (such as HyperFrames) from the rhythm and key frames in `video/rhythm.md`; `rea-video code-remake <this dir>` only makes a quick draft for particles / data-visualisation pictures
- AI shots: prompts are in the generation units of `video/remake.md`; for automatic generation run `rea-video remake-plan` + `remake-run --dry-run` (paid: ask the user first)

## Open questions

- The VLM did not run (No VLM; live action / AI / 3D are told apart from pixel statistics only, so confidence is limited. An agent that can see images: run rea-vi…
- Shot #3 (5.4–8.5s): 3D render at only 55% confidence, runner-up code_render
- Shot #4 (8.5–12.5s): 3D render at only 60% confidence, runner-up code_render
- Shot #5 (12.5–19.1s): code / template render at only 59% confidence, runner-up cg_3d
- Shot #9 (29.2–31.1s): 3D render at only 40% confidence, runner-up code_render
- No AI listened to the soundtrack: real voice versus TTS is inferred from the waveform; the effects were picked off the mix where the sound jumps, so plosives an…
- music source to confirm: most likely stock library music (52%); how to check is under “Sound”

## Map

Read this page first; for detail, open only the file you need. Each line is `path | ~tokens | what is in it · when to read it`; paths are relative to this directory.

```videomd-map
video/timeline.md | 643 | Timeline: one line per shot · what a stretch says, which shots need review, how a shot was made
video/moments.md | 83 | Special moments · reveals, twists, climaxes, goofs: times, key frames, clips
video/content.md | 87 | Content and structure · what it says, the narrative line, structure, the script
video/cast.md | 32 | Cast, scenes and props · reference images for characters, first-frame prompts
video/sound.md | 1343 | Sound · voice, music, sound effects, beats and sources
video/rhythm.md | 462 | Rhythm and key frames · when cuts and transitions happen, shot lengths, the change curve, key frames of each shot
video/look.md | 462 | Camera, lighting and editing · for filmed shots: framing, camera, lighting, kit
video/packaging.md | 1653 | Packaging · subtitles, styled text, stickers, picture-in-picture: timing and style
video/remake.md | 4183 | Remake plan · generation units, shoots, code builds, real material to collect, acting and emotion
video/shots/*.md | 495 | Per-shot detail, tokens per file on average · checking one shot: what is seen, the inference and its basis, prompts, frames
breakdown.json | 108978 | Full raw data · for programs; a model rarely needs it
shots/ | - | contact sheet, first and last frame of each shot · checking by eye
storyboard.jpg | - | storyboard of the whole video · the whole video at a glance
sfx/ | - | a clip of each sound effect · finding matching effects
packaging/ | - | subtitle files, packaging timeline, sticker frames · remaking subtitles and packaging
frames/ | - | picture scenes: full-size frames, the drawn layer cut out and sampled, measurements · remaking rendered pictures
audio.png | - | waveform and beat chart · seeing the rhythm
```

## How to read

- One shot per line: `#<n> start-end (s) | key value | …`. A key ending in `~` is the tools' inference; keys without it are visible on screen or measured directly.
- `story` job in the story and the point · `seen` what is on screen · `act` acting (emotion, strength, face) · `camera` camera move · `overlay` overlays · `made~` how it was made (inferred) · `material~` where the material came from (inferred) · `remake` remake route · `flag` needs a second look
- Full detail for a shot is in `video/shots/<n>.md` (e.g. `video/shots/07.md`).
- What is “seen” can be checked against the frames; what is “inferred” is the tools' and image readers' judgement, with the basis in each shot file. When they disagree, trust the frames.
