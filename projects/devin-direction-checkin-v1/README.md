# Check In: authored Messages motion film

Editable, silent 1920×1080, 30 fps picture. V3 compresses v2's walk from
210 frames to 90; the complete film is 720 frames / 24 seconds. The specialist's
20-second proposal referred to the shorter v1, not the 28-second v2 master.

## Files

- `build_scene.mjs`: v3 generator; edit names, copy, colours, source timing,
  camera and the walk retime in the top-level `CONFIG`.
- `timeline_v3.mjs`: endpoint-preserving scene-keyframe retime and visible-only
  soundable cue extraction. Emitted hold keys sample the authored motion at
  each output frame; no rendered video is accelerated.
- `scene.json`, `events.json`: current v3 scene and native-frame audio receipt.
- `frame-map.json`: every v2 frame's mapped v3 instant/first output frame and
  every v3 frame's fractional v2 source position. V2 210/419 → v3 210/299;
  v2 420 resumes at v3 300. All subsequent timings shift by -120 frames.
- `scene.v1.json`, `events.v1.json`, `build_scene.v1.mjs` and matching `.v2`
  files preserve the earlier authored versions.
- `renders/v3-final.mp4`, its `.render.json` sidecar and `v3-contact.jpg`.
  V1/v2 renders are preserved unchanged.
- `verify_v3.mjs`: scene/frame-map/event, bounds and preservation checks.
- `review_v3.py`: decoded event neighbours, tenth-frame camera samples,
  labelled sheets and native-resolution composer crops in `renders/v3-*`.
- `REVIEW.v2.md` records the earlier unreproduced D1 tear investigation.

## Reproduce on this Mac

Run from the repository root. Prerequisites: engine npm dependencies installed,
FFmpeg/ffprobe on PATH, Google Chrome and `~/venv` Python with Pillow.

```sh
node projects/devin-direction-checkin-v1/build_scene.mjs
node projects/devin-direction-checkin-v1/verify_v3.mjs
CHROME_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" node skill/imessage-motion-recreation/scripts/engines/render.mjs --method gsap --scene projects/devin-direction-checkin-v1/scene.json --out projects/devin-direction-checkin-v1/renders/v3-final.mp4
~/venv/bin/python projects/devin-direction-checkin-v1/review_v3.py
ffprobe -v error -show_entries stream=codec_type,width,height,r_frame_rate,nb_frames:format=duration -of default=noprint_wrappers=1 projects/devin-direction-checkin-v1/renders/v3-final.mp4
shasum -a 256 projects/devin-direction-checkin-v1/renders/v3-final.mp4
git diff --check
```

## Caveats

Authored geometric approximation of Check In UI, not a captured or exact iOS
interface. Arial fallback; colour emoji rendering depends on the Mac fonts.
No Apple marks, logo or SF Symbols; the green speech mark is original geometry.
No audio is included. Cue numbers are zero-based native frames. Spaces without
a visible caret/glyph change are intentionally absent from the sound ledger;
camera reveals, draft entrance and locator motion are also silent.
The opening camera is separately reframed earlier so the actual + tap at f90
is visible; beyond that required correction, non-walk timing remains native.
Old `verify_v2.mjs` / `review_v2.py` are archival v2 tools, not v3 commands.
