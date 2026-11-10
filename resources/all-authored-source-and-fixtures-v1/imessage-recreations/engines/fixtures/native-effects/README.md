# Native rendering diagnosis fixtures

These authored neutral scenes contain no supplied-video frames. Render one frame with either native CLI. They expose failures that ordinary solid-shape parity tests missed.

- `transparent-image.json`: opaque red must stay(255,0,0), half-blue over gray must be(119,119,247), and transparent pixels must preserve gray(238,238,238). A black transparent region means the Img geometry fill was accidentally enabled.
- `scaled-blur.json`: the 160px black square has local20px blur under0.25 parent scale. At y80, x40/55/80/105/120, the SVG reference and correctedMC are255/213/0/226/255. A gray center indicates world-sized blur instead of layer-local blur.
- `white-blur.json`: white blur over gray136 cannot produce any channel below136. A darker fringe indicates straight-alpha color bleed; use premultiplied blur. Native kernel edges may differ from CSS.

After a failure, isolate the smallest fixture, inspect native API semantics, correct the adapter, verify the fixture, then recapture only active affected intervals from immutable source snapshots. Renderer-to-renderer parity can preserve the same bug; also compare exact original frames and foreground regions.
