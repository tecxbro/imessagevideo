# Search the footage, then build the shot

From the checkout root, with Node.js 20+:

```sh
D=skill/imessage-motion-recreation
node "$D/director/motion-catalog-cli.mjs" search "Pictures slide left under still tabs and buttons"
node "$D/director/motion-catalog-cli.mjs" show linq-fixed-chrome-photo-rail
```

Read **moves**, **stays**, and **avoid** before choosing. Ranking counts distinct
cues, not repeated words. A tie or one generic cue is ambiguous; add context
about what moves, what remains fixed, or the source frame range. Contrast
entries identify similar requests without claiming verified footage or offering
a made-up preset.

| Motion | Footage (Linq, zero-based, inclusive, 30 fps) | Playable adaptation |
| --- | --- | --- |
| Photos move under fixed controls | 1091–1111 | [Design museum](../../../release-evidence/film-trials/devin-bot/motion-catalog/linq-fixed-chrome-photo-rail.mp4) |
| Fare cards move with their Select buttons | 384–397 | [Fare selector](../../../release-evidence/film-trials/devin-bot/motion-catalog/linq-flight-fare-rail.mp4) |
| Ones digit rolls as the plus control pulses | 786–810 | [Balance stepper](../../../release-evidence/film-trials/devin-bot/motion-catalog/linq-amount-units-roll.mp4) |
| Messages attachment stack | Not verified in this catalog | None — overlapping deck, not a row |

## Play the source and adapt the scene

Choose a new output directory. The source command verifies the film hash, then
extracts exactly the inclusive window into a silent clip for visual comparison.
If a source file is missing, run the library sync with Python 3.11 or later.
Install the existing [Pillow engine dependencies](../scripts/engines/README.md)
in a venv; rendering also needs FFmpeg, Cairo and fontconfig.

```sh
D=skill/imessage-motion-recreation
C="$D/director/motion-catalog-cli.mjs"
ID=linq-fixed-chrome-photo-rail
node "$C" source "$ID" --out work/catalog/photo-reference.mp4
node "$C" scene "$ID" --config "$D/director/examples/solar-lab-artwork.json" --out work/catalog/new-scene.json
.venv/bin/python "$D/scripts/engines/render_pillow.py" --scene work/catalog/new-scene.json --out work/catalog/new-scene.mp4 --aa 2
```

The [Solstice Observatory preview](../../../release-evidence/film-trials/devin-bot/motion-catalog/solstice-observatory.mp4) swaps
the gallery title, controls, vector art and palette without changing its rail keys.
The corresponding editable scene is beside the MP4; the builder also accepts
five artwork objects with local `src` image paths relative to the output scene.
Pre-crop raster images to the card dimensions (417, 268, 504, 334, and 444 pixels
wide, each 334 pixels high); the renderer sizes them to the card. With no
`src`, each card's `label`, `color`, `accent`, and `motif` control authored geometry.
Fare scenes accept `title`, `subtitle`, `tiers` and `accent`. Amount scenes accept
`title`, `prefix`, `suffix`, `startDigit` (0–5, no carry), and `accent`.

These are new, editable scene adaptations, not the source's product art or a
pixel-exact recreation. The included tracks are rounded samples of the
accepted scene's footage fits. The photo adaptation continues its fitted track
through 1122 to show the deceleration after the requested range; the exact
source clip stops at 1111. All adaptations add short reading holds. The plus
disc pulse is a separate, simplified scale track aligned to the fitted digit
steps; it is not a source-exact control fit.

```sh
node --test "$D/director/test_motion_catalog.mjs" "$D/director/test_toolkit.mjs"
```
