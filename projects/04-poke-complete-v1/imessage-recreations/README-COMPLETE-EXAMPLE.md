# Complete example: 04-poke

This private project contains the full accepted scene JSON and every declared
image/font asset, genuine shared implementations for all five completed methods,
the original reference movie, five final reference-audio MP4s and their provenance,
native source-comparison evidence and all retained per-example authoring programs.

The source implementation is one measured scene plus real shared adapters. The
five small examples/04-poke/render-METHOD.py files are explicit entry wrappers;
they do not pretend that five independent standalone code projects were authored.
Underlying React/Remotion code is engines/remotion-entry.jsx, GSAP and HTML runtime
code is engines/render.mjs +web-runtime.mjs +common.mjs, native Motion Canvas is
engines/render_motion_canvas.mjs +motion-canvas-runtime.mjs, and Pillow is
engines/render_pillow.py. Figma was not a completed method; its prototype is marked.

Install Node dependencies with `cd engines && npm ci`, Python dependencies from
engines/requirements.txt into a virtualenv, and Chromium +FFmpeg/ffprobe. Set
CHROME_PATH to the verified browser executable. Get the separate environment-font
pack for the pinned Linux fallbacks; respect its original licenses.

Run from this project root:
`python tools/render_example.py --example 04-poke --method gsap --dry-run`
`python tools/render_example.py --example 04-poke --method all`

The cold-build runner creates fresh frame caches, applies measured Pillow AA
overrides, performs full-range BT.709 encoding, then muxes the supplied audio using
the explicit Rene cut when relevant. It writes new results to new-deliverables.
Existing deliverables are frozen comparison targets. Use --checkpoint FRAME for
a single native-frame capability check. Fonts/renderers/encoders must be matched
before expecting the same pixels; code completeness is not a fresh full-render claim.

Historical authoring programs can refer to old working paths and superseded inputs.
They are included as the requested complete authored code, not the cold-render path.
Full source history/provenance and silent masters are separately indexed in the
private library. Per-file SHA256 values are in PACK-CHECKSUMS.json.
