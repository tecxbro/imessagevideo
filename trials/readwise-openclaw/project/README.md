# Editable Readwise / OpenClaw — Complete Film

`copy.json` owns visible copy, display wrapping, bold runs, keyboard labels,
timestamps and partial predictive-bar observations. `timing.json` owns frame
numbers, typed-prefix lengths, sends, streamed-reply prefix lengths, keyboard
switches, camera samples and end-icon opacity boundaries. All frames are 0-based
at 30 fps. Edit these data files and rebuild; the builder does not read the source
film or extracted frames.

```bash
bash trials/readwise-openclaw/project/render.sh
```

Requires Python with Pillow/NumPy/SciPy, the existing shared HTML-engine
dependencies and Chrome. `PYTHON`, `CHROME_PATH` and the optional MP4 path argument
are configurable. Defaults keep renders/frame caches under `~/work/rw/exports/`.
The command runs scene build → full HTML picture render → 48 kHz stereo audio
render → explicit video/new-audio mux → encoded AAC true-peak gate → immutable
publication at `~/work/rw/exports/readwise-first-export.mp4`. It refuses to replace
the first export or its receipt. Later revisions require a new filename/receipt;
never overwrite the first export. `exports/FIRST-EXPORT.sha256`, ffprobe JSON and
the timing/true-peak report live beside this project in the trial's exports folder.
`build_scene.py` emits `build/scene.json` in the unchanged shared scene contract.
Generated build/cache files are ignored. Output is 1920×1080, 30 fps, 1110 frames.

Components: reusable gradient background, title prefix states with independent
pink runs, drawn app icon, seeded line-doodle wallpaper, vector avatar, body and
clipped screen, status/header, message bubbles with span-level bold, composer,
predictive bar, alphabetic/numeric keyboard, and separate camera parent.

All seven shots are implemented. Frames 1100–1109 are black and silent.
Source evidence shows the
keyboard remains visible during zoom-out/reading holds; it is not hidden.

Font inputs: local repository Inter-600 for titles/command; repository static
SF Pro Text Regular/Semibold for UI; system Georgia Bold for the approximate
custom Readwise R. Static SF files avoid an observed system-variable-SFNS browser
versus Pillow metric mismatch. SF Pro is a visual font identification, not exact
Telegram font metadata. No downloaded/source raster assets are used.
The article uses installed `/System/Library/Fonts/Supplemental/Georgia Italic.ttf`.

Known fidelity limits: doodles and avatar are procedural original geometry;
brand curl is approximated. Prediction transitions originate from the analysis'
partial OCR observations, not an exact complete transcription. Camera x/scale
comes from thresholded source samples; y anchors are fitted estimates. Reply
chunks animate short growth/scroll offsets, not an original Telegram renderer.
OS key-down/click timing cannot be recovered from rendered reference frames.
Titles use measured prefix births, while whitespace is implicit. Editing copy
can require updating prefix counts/wrapping/stream lengths in timing data.

S2/S3 use 2D rotation/scale/translation fits; the shared contract cannot express
the original skew/3D perspective. Off-screen article/footer microcopy remains
partially unresolved in the inventory. The studio is an original vector curtain
gradient and silhouette, not a photograph. Icons are editable approximations.
The S4 camera uses measured rail widths with an authored 0.94 fit factor and y
anchor; true 3D transforms and source motion blur are not reconstructed.
Cursor samples interpolate measured positions; the last measured position is
held in untracked tails, and pre-track cursor motion is not invented.

## Sound and provenance

`audio/cues.json` owns sound timing and music seed/tempo/level. Keys are only the
observed human composer-prefix births, one key per frame even for batched glyphs.
`audio/render_audio.py` reuses the existing `render_ui.build_ui` API for CC0 single
keys and Kenney clicks. Sends and reply pops use the kit's original procedural
`synthesis/bank/air_whoosh.wav` and `bubble_pop.wav`, not claimed CC0 recordings.
Full collection/license paths are in cues and per-event receipts in the external
audio report. Music is original seeded NumPy synthesis (authored 112 BPM), not
the reference soundtrack or a claimed sonic match. No source-media path is read
by the picture/audio/export builders. The mix ends hard at frame 1100.

The mux uses `-map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -ar 48000 -ac 2`.
Before publication, FFmpeg loudnorm measures `input_tp` on the encoded AAC;
publication fails unless it is below −1 dBTP. WAV stems and provenance reports
stay outside Git. Test with:

```bash
cd trials/readwise-openclaw/project
~/work/rw/.venv/bin/python -m unittest -v test_project.py test_audio.py test_export.py
```

## First complete export receipt

The complete pipeline ran once, 03:15–03:25 PST, on 2026-11-18. External wall
time was 585.42 s (internal pipeline 585.37 s); picture 581.79 s, audio 1.46 s,
mux 1.04 s. Encoded AAC true peak was −18.89 dBTP. The external MP4 is
8,878,521 bytes; it is not stored in this repository and has not been modified
after publication. See `../exports/FIRST-EXPORT.sha256`,
`FIRST-EXPORT.ffprobe.json` and `FIRST-EXPORT.report.json` for exact receipts.

All 11 tests passed. The full video/audio decoded without errors; the muxed
video payload equals the rendered picture payload. All 1110 frames were newly
captured, final PNG frames 1100–1109 are RGB zero, and the 1,776,000-sample stereo
PCM mix is zero from sample 1,760,000 (frame 1100). Six checkpoint comparisons
were viewed before one correction pass; final comparisons are outside Git at
`~/work/rw/cmp/first-export-{0104,0120,0180,0245,0278,0325}.png`.

## Historical Part A verification notes

The comparison pass exposed undersized titles, a low empty-chat pill and
variable-SFNS browser/Pillow metric mismatch. The correction pass changed title
sizes, composer/camera anchors and static SF font inputs. Unit checks also caught
ambiguous prediction-label IDs, fixed with an explicit label suffix.

Pixel checks then caught stale-frame reuse in the unchanged HTML engine: when a
transport chunk's frame matched its setup-at-zero markup, it cloned the preceding
capture. This affected gradient-only intervals and the black tail. The reusable
background therefore includes a zero-area animated frame-evaluation anchor. It
does not draw pixels, but keeps frame evaluation live across transport chunks.
The gradient children end at frame 1100; only the black scene background remains.

Verified output: `~/work/rw/readwise-part-a.mp4`, 1920×1080, 30 fps, 37.0 s,
1110 frames, no audio. Full capture took 528.37 s; recapturing the affected
68–342, 403 and 1100–1109 ranges plus re-encoding took 137.56 s. Reused visible
SVG content was checked unchanged. All five project tests pass. Ten requested
source/render comparisons were viewed at `~/work/rw/cmp/frame-NNNN.png`.
Black-tail PNGs are exactly RGB zero; decoded H.264 has residual values up to
2/255. Gradient-only PNGs differ from the first gradient frame by at most 2/255
because of browser raster dithering.
