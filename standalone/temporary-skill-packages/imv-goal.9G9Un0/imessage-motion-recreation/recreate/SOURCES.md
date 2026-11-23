# Source survey and renderer smoke exports

All six source snapshots were cloned and checked out at the commits below in detached study directories outside the working tree. The four historical commits were fetched into a separate shared clone of the base as `refs/imv3-study/{motion,conversation,sound,pinch-hit}`.

| Pinned snapshot | Material inspected and what carries forward |
|---|---|
| [tecxbro/imessagevideo](https://github.com/tecxbro/imessagevideo/tree/c49482aec7b8ed0b840f97c61a5e5b860c4077b6) | [Production index](../../../FINAL-PRODUCTION.md), [reconstruction playbook](../references/reconstruction-playbook.md), accepted scene contract and all five engine entry points. Keep absolute frame evaluation and reuse authored scene primitives. The older [timeline scan](../scripts/verification/scan_timeline.py) stops after the candidate's advertised count, which is useful for intentional trims with an explicit mapping. A full-film check needs both independent decode counts and explicit end coverage. Private repository, with historical provenance preserved in its project manifests. |
| [theswerd/imessage-ui](https://github.com/theswerd/imessage-ui/tree/1f132909792ff540501385f91d37ef20629c55b7) | `registry/imessage/bubble-shape.ts`, `message-bubble.tsx`, and `tokens.ts` expose distinct anatomy and state. `references/SPEC.md` ties geometry to native captures with measured and unmeasured values. Prefer the team's UI adapter for reusable interface states. Repository code and original docs are MIT. Native captures, marks, demo media and fonts have separate terms documented in [THIRD_PARTY_NOTICES.md](https://github.com/theswerd/imessage-ui/blob/1f132909792ff540501385f91d37ef20629c55b7/THIRD_PARTY_NOTICES.md). |
| [tecxbro/imessagedemo](https://github.com/tecxbro/imessagedemo/tree/807e86e03e4a7e95ae6954b4a8c4dd5e031854bc) | `src/runtime/{project,player}.ts` separates compiled flow from logical time and seekable immutable visual state. `examples/typing-reactions.flow.json` and `examples/ios-poll-vote.flow.json` are data-driven conversations, and `src/contracts/` documents stable state targets. The pinned README offers timestamped PNG checkpoints and explicitly omits built-in MP4 export. No root license file was present at this pin. Use as first-party study and observe the separate vendored and media terms. |
| [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes/tree/9813a6cbef97fffda70f5a147b87747f7e35a77b) | `docs/concepts/{determinism,frame-adapters}.mdx`: resolve the frame's state by seek, await fonts and assets, capture, and then encode. `skills/reverse-any-video/SKILL.md`: inspect consecutive frames at cuts and small transitions, carry exact rational rates and read ink geometry. Its workflow can reuse source audio and crops. This project's stricter asset boundary keeps those files on the analysis side. Root code license Apache-2.0, with per-asset notices. |
| [per-simmons/launch-video-clone](https://github.com/per-simmons/launch-video-clone/tree/7e97ac6488eb61ca4d25affe7fc1da7cfb80b376) | `scripts/burst.py` combines histogram scores and motion outliers as cut candidates. `rectrack.py` detects foreground connected components in selected areas. `camtrack_sift.py` estimates a similarity transform with separately moving elements masked out. `trackcheck.py` compares tracked and still residuals. Adapt the methods to measured native dimensions and keep uncertainty where matches run out. `framediff.py` scans only the shared prefix and downscales to grayscale. Use the lag idea as evidence, with native local metrics and separate structural gates. Code license MIT. |
| [serenakeyitan/awesome-ai-clonable-launch-videos](https://github.com/serenakeyitan/awesome-ai-clonable-launch-videos/tree/6a02fa07dfa5696ba3191dd905a06dbedc932e38) | `data/videos.json` supplies local video paths, creator links and processing provenance. `agent/workflow.md` treats catalog entries as discovery material and states that the collection grants no third-party rights. The catalog's MIT license covers its software and documentation. Use the original creator's terms when deciding whether to redistribute or reuse footage. |

## Historical handoffs

- [Motion library](https://github.com/tecxbro/imessagevideo/tree/a23bfb294fbc65739811a84f264ad306ca192fe1) records source intervals, actual decoded PTS and fixed-vs-moving object tests in `reports/motion-catalog/`. `director/motion-library/` ships independent picture adaptations with editable parameters and records both ambiguous and incorrect retrievals. Linq source f1091–1111 separates a moving photo strip from fixed labels and actions. Photon Mini f211–240 separates the rising sheet, scrim and underlying conversation.
- [Editable conversation](https://github.com/tecxbro/imessagevideo/tree/b525e7e11279db836bbdd2ff4b1b8953b56b946f) implements layout and playback in `director/conversation.mjs`, with installed-renderer text metrics and grapheme-aware wrapping. It also demonstrates separately editable composers, rich cards, attachment stacks and camera layers. Its tests and Blue Awning export document a real conversation edit.
- [Sound trial](https://github.com/tecxbro/imessagevideo/tree/69595dfa2ef588a59d1b0b4d5836817a49d0f809) supplies `sound-trial/check_export.py`. Its post-mux checks compare picture packet data hashes and exact timestamps. It locates independent cue templates in the decoded audio and distinguishes early, late and missing cues. The fault fixtures exercise those checks.
- [Pinch-hit trial](https://github.com/tecxbro/imessagevideo/tree/b303dde12ca8a314a36a7e70ed42e3e0f1605464) puts authored timing in `trials/pinch-hit/edit.mjs`, picture in `picture.mjs` and per-version editorial evidence in `EDITORIAL.md`. It records two useful cases for recreation checks: a deliberate blank hold before a new line of copy and a camera move that spans an editorial reset. Trace both from successive decoded frames.

## Additional sources and local measurements

- [PySceneDetect AdaptiveDetector](https://github.com/Breakthrough/PySceneDetect/blob/8a0b5cea50fef0bc216fb230c7010556dcf5010e/scenedetect/detectors/adaptive_detector.py) combines a local motion baseline with a minimum visual change. This helps propose cuts during moving shots. Inspect the candidates with full-frame and local changes together, since one-frame flashes and near-identical UI cuts can land below either threshold. BSD-3-Clause. The source was inspected at the linked commit.
- [Tesseract page segmentation and image quality guidance](https://tesseract-ocr.github.io/tessdoc/ImproveQuality.html) distinguishes contact sheet legibility from OCR. Crop and enlarge stable UI text, choose a line or sparse segmentation mode, and retain recognized words, confidence and boxes for manual checking on adjacent frames. Local tool version 5.5.0.
- [FFmpeg scene detection](https://ffmpeg.org/ffmpeg-filters.html#scdet) gives a second source of cut candidates. [FFprobe show_frames](https://ffmpeg.org/ffprobe.html) supplies observed display timestamps. Save and validate these before using the source's advertised frame rate.

The files below were fully decoded with FFprobe and measured locally. These are study inputs. No source footage was vendored into Recreation.

| Input | Width × height | Decoded frames | Presentation-clock observation | SHA-256 |
|---|---|---:|---|---|
| [Native iOS send](https://github.com/theswerd/imessage-ui/blob/1f132909792ff540501385f91d37ef20629c55b7/references/ios/motion/send-60fps.mp4) | 804 × 1748 | 299 | One 33,333 µs frame gap, other gaps 16,666 or 16,667 µs. Last frame starts at 4,983,333 µs and has 1 µs duration. | `23a9680f70a436a119b786334aeb88c70b59c083703ef273eb0cdad2be98cf8b` |
| [Native iOS long press](https://github.com/theswerd/imessage-ui/blob/1f132909792ff540501385f91d37ef20629c55b7/references/ios/motion/longpress-60fps.mp4) | 804 × 1748 | 239 | One 33,334 µs frame gap, other gaps 16,666 or 16,667 µs. Last frame starts at 3,983,333 µs and has 1 µs duration. | `8e8f3cf3194c5afbfd796056be5d37eb9e50b366f9931d02f092160b3d76f2ec` |
| [Native iOS search open](https://github.com/theswerd/imessage-ui/blob/1f132909792ff540501385f91d37ef20629c55b7/references/ios/motion/search-open.mov) | 1206 × 2622 | 126 | Time base 1/600 s, final start tick 3540, final duration 23 ticks. Gaps range from 1 to 300 ticks. | `eaf91eed724d810de696106ee537a32b3f231bd7e147b5ccdbafb71cfefa7948` |
| [Native iOS search close](https://github.com/theswerd/imessage-ui/blob/1f132909792ff540501385f91d37ef20629c55b7/references/ios/motion/search-close.mov) | 1206 × 2622 | 116 | Time base 1/600 s, final start tick 3626, final duration 23 ticks. Gaps range from 1 to 300 ticks. | `ea79101cd93fef25e29f62be75a8c91a1a3dc2e7f9ebc2fb92abdeb8b1b6a934` |
| [Grok Bot Mac Messages](https://serenatan.org/launchvideo/#video-54) | 1080 × 1350 | 623 | Average rate 30/1, time base 1/15,360 s, duration 20.766667 s. [Creator's post](https://x.com/texas_twins_dad/status/2117824974689890485) | `1d1ccc0973720630592914853735e3cd225aae10de6492df80e3739529702fdb` |
| [Allo phone presentation](https://serenatan.org/launchvideo/#video-48) | 1280 × 720 | 607 | Average rate 30/1, time base 1/3,000,000 s, duration 20.233000 s. [Creator's post](https://x.com/allophonesystem/status/2115793573589258279) | `f98e9fc4c95b570c45d06a3e1cad78a16ff470ef6381a9591db129210a743baf` |

The simulator filenames and advertised rates approximate the clock. Reproduce the observations by reading `stream=time_base` and `frame=best_effort_timestamp,duration` with `ffprobe -show_frames -show_streams -select_streams v:0`.

The Recreation analyzer fully decoded Poke (1,283 pictures at 30,000/1,001, 2,057,216 audio samples at 48 kHz), Grok Bot Mac Messages (623 pictures, 1,003,520 audio samples at 48 kHz), and the native iOS search open (126 pictures, no audio). Poke had exact decoded pixel holds at f1245–f1249 and f1253–f1258. The last decoded search-open picture ends at 3563/600 s according to its packet duration, while the stream reports 3562/600 s. Retain both fields when investigating delivery-clock discrepancies.

The Mac Messages contact sheet shows four successive headings. The full-frame heuristic selected zero cut candidates, so use the sheet and local inspection to locate their transitions. In the final heading's passage, the outgoing bubble changes from a blue outline to a filled blue bubble and starts moving up at f571 (19.033333 s). At that frame the full thumbnail MAE was 1.36 out of 255 and 1.56% of thumbnail pixels crossed the change floor. In the source crop `[650,600,340,170]`, pixels with `B - R > 80` and `G - R > 40` jumped from 1,557 at f570 to 12,393 at f571. Use that region as an interaction check on any authorized recreation of this passage.

```bash
# Point SOURCES at the local detached study clones.
SOURCES=/workspace/scratch/imv3-sources
recreate=skill/imessage-motion-recreation/recreate/recreate.py
mac="$SOURCES/awesome-ai-clonable-launch-videos/videos/grok-bot-text-messages-on-mac.mp4"
python "$recreate" analyze "$mac" --out /tmp/imv3-mac
python "$recreate" inspect "$mac" --out /tmp/imv3-mac-send \
  --frames 568:578 --crop 650 600 340 170 --sheet-width 720 --ocr
```

## Five complete renderer smoke exports

This runs the unchanged base engines with the base [selection-confirm](../director/examples/scenes/selection-confirm.json) authored starter. The scene SHA-256 is `6720bd2e76e2e79eff395785c2da6b4e69bbd6dac5fd9666eb0608e6d3b4eeb7`. It exercises a control fill animation, an editable label change, static holds and the final encode. See the [environment setup](../../../MAC-SETUP.md) and [engine dependencies](../RUNNING.md).

```bash
# Run at the repository root with the locked engine dependencies installed.
# The cloud setup used CHROME_PATH=/usr/bin/chromium and the repo setup's fontconfig.
engine=skill/imessage-motion-recreation/scripts/engines
scene=skill/imessage-motion-recreation/director/examples/scenes/selection-confirm.json
out=/workspace/scratch/imv3-renderer-smoke
mkdir -p "$out"

for method in gsap html remotion; do
  node "$engine/render.mjs" --method "$method" --scene "$scene" --out "$out/$method.mp4"
done
node "$engine/render_motion_canvas.mjs" --scene "$scene" --out "$out/motion-canvas.mp4"
python "$engine/render_pillow.py" --scene "$scene" --out "$out/pillow.mp4"

for movie in "$out"/*.mp4; do
  ffmpeg -v error -xerror -i "$movie" -map 0:v:0 -f null -
  ffprobe -v error -select_streams v:0 -show_frames -show_streams \
    -show_entries stream=width,height,time_base,avg_frame_rate:frame=best_effort_timestamp,duration \
    -of json "$movie"
  sha256sum "$movie"
done
```

All five MP4s contained only video, decoded without FFmpeg errors, and measured 960 × 540, 120 frames, time base 1/15,360, and exact presentation starts `n/30` at every frame, including f119 at 119/30 s. Every picture duration was 1/30 s. At (360, 367) in the confirmation control the first decoded RGB change was f56 on all five, matching the authored event frame. That pixel started RGB (21, 136, 251) and ended at (63, 129, 86). Browser exports were byte-identical for this scene. Pillow and Motion Canvas produced different MP4 hashes. This proves each export path ran and that specific event resolved, with visual fidelity left to the recreation comparison.

| Engine | Captures reported | MP4 SHA-256 |
|---|---:|---|
| GSAP | 15 | `b72515d5e666139b1752306de5ceaef6d65a9fc0cfcb8f845b3e1ebf4fe16976` |
| HTML/SVG | 14 | `b72515d5e666139b1752306de5ceaef6d65a9fc0cfcb8f845b3e1ebf4fe16976` |
| Remotion | 14 | `b72515d5e666139b1752306de5ceaef6d65a9fc0cfcb8f845b3e1ebf4fe16976` |
| Native Motion Canvas | 14 | `7b837dd1a61011b911124892fbef90503c792586c33969f7cd753eaf4b3f86b7` |
| Pillow with FFmpeg | 14 | `889e603d60eb3ccb5a4cc37bc4b4b507476f951c716f9e0ea4dc9479cb197219` |

For further reproductions, render one adapter that supports the requested edit format and hardest layer. Keep the frame cache for that adapter. A passed smoke export confirms its runtime path for this scene, and native-rate checks establish fidelity for a particular film.
