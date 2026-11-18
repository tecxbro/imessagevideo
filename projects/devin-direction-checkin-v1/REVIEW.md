# Check In: first export

- Source: `build_scene.mjs`, generated `scene.json` and `events.json`.
- Render: `renders/v1-first-export.mp4` (silent GSAP, 1920×1080,
  30 fps, 720 frames, 24 seconds). MP4 and sidecar are read-only to guard
  against accidental replacement. Future exports must use a new filename.
- SHA256: `47a3cd6678980f33788726fd5784d23d20317ce8df7b75c0a28a7f0642e49c81`.
- Contact: `renders/v1-contact.jpg`, 12 evenly spaced and 16 risk frames.
- Full-resolution stills: `renders/event-01.png` through `event-06.png`
  correspond to frames 132, 186, 492, 510, 590 and 640 respectively.

## Review

Inspected the contact sheet and full-resolution frames 132, 492, 510 and
640, plus preflight frames 30, 165 and 530. Checked app row press,
draft attachment, per-character text, simultaneous arrival states,
phone/screen boundaries, bubble tails and the final line. The initial
Home label/walker overlap was corrected before the first MP4 export.
No text clipping or unintended text overlap found in the reviewed export
frames. Deliberate camera close-ups crop the hardware, not active copy.

Scene checks passed: unique layer IDs; one `cardMaya` actor; both cards
switch at frame 510; draft is `are you h` at 492 and empty at 548;
nine character and nine backspace events; sorted tracks and valid event
frames. The scene file hash matches the first-export sidecar. FFmpeg
fully decoded the MP4 without errors. There is only a video stream.

## Timing interpretation and limits

The rightward reveal starts at 420. `cardSam` first intersects the
viewport at 432, so its receive/reveal cue in `events.json` is 432,
derived from the generated scene's camera and actor geometry rather
than copying the shot-table boundary. Other explicit action anchors
remain as planned. Maya's phone translates left on pullback and is
repositioned with the truck so both phones remain on the same plane.

Arial fallback and hand-authored editable UI geometry are intentional,
as disclosed in the plan; this is not verified pixel-exact Apple UI.
No audio was added. No standalone card cuts or card crossfades.

## Reproduce without replacing v1

From the repository root:

```sh
node projects/devin-direction-checkin-v1/build_scene.mjs
CHROME_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" node skill/imessage-motion-recreation/scripts/engines/render.mjs --method gsap --scene projects/devin-direction-checkin-v1/scene.json --out projects/devin-direction-checkin-v1/renders/v2.mp4
```

This FFmpeg build lacks `drawtext`; the contact sheet uses FFmpeg
select/scale/tile, then Pillow adds frame labels. No package changes
were needed. Existing repository files and frozen projects are untouched.
