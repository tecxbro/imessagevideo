# Working with the source projects

## Resolve the two pinned checkouts

Set `SKILL_DIR` to the directory containing this skill's `SKILL.md`. On Linux or macOS, run:

```sh
python3 "$SKILL_DIR/scripts/upstreams.py"
```

With existing clones, add `--source-root /path/containing/the/clones` on the first run. The helper uses clean tracked files at the requested revision, remembers matching checkouts in place, and otherwise fetches only the pinned commit. Set `--cache /persistent/path` to override the default XDG cache. Once resolved, the same cache works offline and across jobs on that machine. Supply `--path rea-video` or `--path hyperframes` to resolve just the source needed. Package installations, analysis models and the render browser have separate caches.

```sh
REA=$(python3 "$SKILL_DIR/scripts/upstreams.py" --offline --path rea-video)
HF=$(python3 "$SKILL_DIR/scripts/upstreams.py" --offline --path hyperframes)
```

The pins are [REA Video 86486c6](https://github.com/JuneYaooo/rea-video/tree/86486c6e104b917fb4b6a2d6501134686c05b219) and [HyperFrames 66156bf](https://github.com/heygen-com/hyperframes/tree/66156bf35ebecfe0075d3d01405773ab2792a6f0). Keep any film, review output and project-specific dependencies outside these source trees.

## Choose a workflow from the user's verb

| Request | Use from the checkouts | Produce |
|---|---|---|
| Recreate this film | REA for a shot, layer and sound inventory; source frames at each change; HyperFrames or the project's named renderer for editable reconstruction | An independently rendered film and a comparison on the source clock. Scope to the requested shots if the user specifies a passage. |
| Learn this motion | Use REA to locate the passage; measure one moving layer relative to a stationary anchor. Trace both the camera and the object when both move. | A reusable implementation with frame range, parameters, motion samples, uncertainty, demonstration and a successful second use with different content. |
| Use this move for another film | Retrieve the saved implementation and its limitations. Use the referenced film for a specific requested timing or characteristic. | New content and shot composition with the named movement. Judge the movement against its measurements and the film against its brief. |
| Direct from a blank brief | Use the product evidence to find an idea, write the visible proof, then choose motions. Consult HyperFrames' `skills/hyperframes/references/story.md` and `references/motion.md` within that upstream skill; use donors only for specific influences. | An original shot plan, editable scene timeline, rendered film and review against the brief. |

## Run the upstream tools

**REA.** Read `$REA/skills/rea-video/SKILL.md`. Use an existing environment with the pinned checkout installed, or set `TOOLS_DIR` to a persistent tools directory and create a dedicated environment once with Python 3.10+, FFmpeg and pip:

```sh
python3 -m venv "$TOOLS_DIR/rea-env"
"$TOOLS_DIR/rea-env/bin/python" -m pip install "$REA"
```

Set `JOB` to this film's directory and `REF` to the absolute source-video path. Run the local analysis with hosted vision disabled. REA may download a small face-detection model on its first run; this processes the footage locally. Keep that model beside the tool environment:

```sh
REA_BIN="$TOOLS_DIR/rea-env/bin/rea-video"
export REA_VIDEO_MODELS="$TOOLS_DIR/rea-models"
"$REA_BIN" decompose "$REF" -o "$JOB/analysis" --lang en --no-vlm --no-stems --no-asr
"$REA_BIN" summary "$JOB/analysis/breakdown.json"
```

The last two switches omit model-based stem separation and speech recognition. The base install also omits optional OCR. Inspect the pixels and audio separately or enable the applicable local analyses. Read `analysis/VIDEO.md`, then the relevant `analysis/video/shots/` entries and frame strips. Inspect ambiguous events in consecutive full-rate frames. On the 299-frame, 60 fps native Messages send recording, the tool found four movement candidates using 15 fps samples. It inferred a code/template render. Use these candidates to locate the gesture, preserve known capture provenance, and inspect source frames 72–74 to locate the first visible change at frame 73. REA's optional `remake` can fill unbuilt shots with source footage and carry the original soundtrack. Use its shot status as a work list. For an independent recreation, build from separate assets, keep reference data in analysis, and inspect the assets actually read on export. An identical MP4 or soundtrack can score perfectly while failing the assignment.

**HyperFrames.** Read `$HF/skills/hyperframes/SKILL.md` and `$HF/skills/hyperframes-cli/SKILL.md`. Use Node 22+, FFmpeg and the supported Chromium setup in the latter guide. The pinned source selects CLI release 0.9.77. The launcher can use npm and the browser can require a one-time download. Run from the working project. For a new composition:

```sh
HF_CLI="$HF/skills/hyperframes/scripts/plugin-cli.mjs"
export HYPERFRAMES_STANDALONE_CLI_VERSION=0.9.77
node "$HF_CLI" init "$JOB/film" --skip-skills
cd "$JOB/film" || exit 1
# Build or edit index.html and its scene compositions before checking and rendering.
node "$HF_CLI" check --json
node "$HF_CLI" snapshot --review
node "$HF_CLI" render --quality delivery -o "$JOB/film.mp4"
```

Use the ordinary local rendering path for authored graphics. When the user has access to HyperFrames Pro and wants its Reverse workflow, consult `$HF/skills/reverse-any-video/SKILL.md`. Its `reverse start` and source-audio/crop defaults belong to that workflow. Keep originals in the analysis folder when the requested film requires independent picture and sound. Missing Pro access still permits a manually authored recreation using the ordinary renderer.

**Check the export independently.** Probe both videos for frame count, timestamps, dimensions and duration. For matching constant-rate sources, the example below extracts source frames 70–85 and the same indexed frames from the final export. Inspect them side by side at native dimensions, including the few frames immediately before and after each gesture. Repeat for every required event. For variable-rate inputs, pair frames by measured presentation time and report any conversion.

```sh
mkdir -p "$JOB/qa/ref" "$JOB/qa/export"
ffmpeg -v error -i "$REF" -vf "select='between(n,70,85)'" -fps_mode passthrough -start_number 70 "$JOB/qa/ref/%06d.png"
ffmpeg -v error -i "$JOB/film.mp4" -vf "select='between(n,70,85)'" -fps_mode passthrough -start_number 70 "$JOB/qa/export/%06d.png"
```

Check motion path, direction and target, viewport clipping, static chrome, copy, and cue timing against the corresponding source or approved brief. Use timestamped full-resolution crops to resolve small differences. Finish by inspecting the decoded export in motion and checking the delivered audio independently. A point in time, mean pixel score or clean renderer exit is insufficient evidence of a gesture.

## Other references already used in this project

- [Launch Video Clone's tracker](https://github.com/per-simmons/launch-video-clone/blob/7e97ac6488eb61ca4d25affe7fc1da7cfb80b376/scripts/track.py) returns each frame's transform and fit score for a chosen region. Use the low-confidence list to find occlusions and manual checks. Its comparison tool samples coarse images for triage.
- [Message UI](https://github.com/theswerd/imessage-ui/blob/1f132909792ff540501385f91d37ef20629c55b7/references/SPEC.md) supplies measured geometry and identifies approximations. Its [typing indicator](https://github.com/theswerd/imessage-ui/blob/1f132909792ff540501385f91d37ef20629c55b7/registry/imessage/typing-indicator.tsx) documents which dot timings and trailing shapes still need evidence.
- [iMessage demo](https://github.com/tecxbro/imessagedemo/blob/807e86e03e4a7e95ae6954b4a8c4dd5e031854bc/src/runtime/project.ts) projects actual conversation state and reactions by stable message ID at any time. Its [Apple Pay track](https://github.com/tecxbro/imessagedemo/blob/807e86e03e4a7e95ae6954b4a8c4dd5e031854bc/src/renderers/ios/apple-pay/motion.ts) covers opening and cancellation. Verify approval separately when the story calls for it.
- [Serena Launch](https://github.com/serenakeyitan/awesome-ai-clonable-launch-videos/tree/6a02fa07dfa5696ba3191dd905a06dbedc932e38) supplies credited clips, source links and descriptions. Choose a relevant clip, inspect it, and implement the measured motion in editable code.
