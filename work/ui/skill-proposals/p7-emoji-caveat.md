# P7 — Emoji cross-engine caveat (doc-only patch)

Measured scenes bake emoji as raster images (`v10-flight-reply-emoji-0` image 40x30).
Live builders rely on the text stack, which differs per engine:

- html/gsap/remotion (Chrome): Apple Color Emoji — closest to iOS artwork.
- Pillow: Noto Color Emoji — visibly different glyphs.
- Motion Canvas (Skia): platform emoji — verify per machine.

## Proposed addition to `component-contracts.md`

> Emoji belong in `copy` and render from the engine's font stack — Chrome gives Apple
> artwork, Pillow gives Noto. For pixel-critical frames substitute a raster `image` layer
> (`emojiImage`) at the measured position; do not rely on cross-engine emoji parity.
