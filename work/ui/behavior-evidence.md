# Behavior evidence — relationships a screenshot hides

All frame numbers are source-frame indices (native fps: linq/danieltian/gallery/photon 30, poke 30000/1001).
Verification method: `ffmpeg` select/crop extracts under `work/ui/frames/`; pixel scans via raw RGB reads (no PIL).

## Q1. Which bubble owns a Tapback after the conversation scrolls?

**VERIFIED: the badge is glued to its message and scrolls with it.**

- `05-linq` f750: 👍 Tapback = small blue bubble-badge (~65x60px at this film scale) containing
  the emoji, anchored so its center sits ON the top-right corner of the incoming Apple Cash card
  (card x 110-540, badge x 504-571 y 292-352). A tail of two descending bumps below-right of the
  badge points back at the card corner (y 352-370).
- `05-linq` f722-728: the badge pops in — starts as a ~10px dot at the anchor corner, springs to
  full size over ~6-8 frames (~0.25s). The emoji is already inside during growth.
- `05-linq` f758-765: the thread scrolls up for the payment sheet; the Cash card AND its badge
  translate together, badge stays locked at the card corner (zoom sheet `tapback-zoom-sheet.png`
  rows 6-7).
- `04-poke` f384-392: same pattern on a gray incoming text bubble ("want me to find a spot?") —
  blue badge with white 👍 pops in at the top-right corner, two-bump tail on the badge's lower
  side facing the bubble. Still attached while "where are you rn?" reflows below (f410-430,
  `poke-sendzoom.png` rows 4-6).
- Anchor rule verified in both films: a reaction **you** add to an incoming (left) message lands
  on the bubble's **top-right** corner (your side of the screen). No footage shows a reaction by
  the other party; symmetric assumption (their reaction → top-left) is marked inferred.
- Gap: no film shows a tapback already present on a mid-thread bubble that then scrolls a long
  distance — the observed scroll is ~1 bubble height before the card exits. The anchoring rule
  itself is fully verified.

## Q2. What disappears when a draft is sent?

Measured in `05-linq` scene.json `v19-intro-composer` (exact timed layers, not guessed):

- t<0.767: placeholder glyphs + mic icon visible, no send control.
- t=0.767: typed glyph layer starts; placeholder and mic END the same instant — first typed char
  removes both. Blue caret rect (2x42, #0088ff) tracks the text end.
- t=0.800-0.900: send circle appears INSIDE the right end of the input field and fills through
  #c2d2fd → #70a3ff → #007efe over ~3 frames (fill sweep, not just opacity).
- Draft→send is a cut in all films (no footage shows the mid-flight bubble leaving the composer;
  poke f384 shows the send-arrow circle already docked as the message exists). After send:
  field returns to placeholder+mic; the outgoing bubble is appended to the thread bottom and the
  thread scrolls so it lands above the composer; later "Delivered" then "Read 12:0x" appear as a
  small gray label under the last outgoing bubble (linq f145-175, `linq-send2.png` rows 3-5).

## Q3. Phone-space vs world-space during camera moves

- `06-gallery` f330-480: the iPhone slides/scales as one unit — lock screen, banner and all
  pixels move rigidly with the hardware (phone-space). Marketing titles and the floating ⚽
  emoji around the phone do NOT move with it (world-space, `gallery-mid-sheet.png` +
  `gallery-cam-sheet.png` tiles 5-8).
- `04-poke` measured scene uses the same discipline: hardware PNG + separate screen-mask PNG
  layers (`early-left-hardware-v11.png`, `*-screenmask.png`); screen content is a child of the
  transformed phone group, not the stage. `v15-selected-card-camera`/`v15-first-board-material-camera`
  groups carry the camera keyframes.
- Implication for the kit: DeviceFrame must own a clipped `screen` child group; camera rigs
  transform the phone group, never the stage. World-space props stay siblings of the phone.

## Q4. Layout vs copy length

Measured bubbles show height follows text lines, radius follows font size (not half-height):

- linq f750, 960x720: outgoing 2-line "can you order my weekly groceries?" — body w≈356 h≈120,
  corner radius ≈36-40 (radius≈0.33h). Tail extends ~14px below the bottom-right as a comma hook.
- linq f750: incoming 1-line "Sure, it'll be $166.89" — w≈384 h≈66, radius ≈30-33 (radius≈0.5h).
- Both ≈ fontSize(≈29px) × ~1.1 radius. iOS uses a near-fixed corner radius (continuous corner);
  builders should use `radius = min(h/2, fontSize*1.15)`.
- Horizontal text padding ≈ 18-20px each side; vertical ≈ 10-12px; line height ≈ 1.2×fontSize.
- The measured scene does NOT auto-wrap text — every baked bubble is traced per copy. Our builders
  must wrap with real font metrics (width table embedded from canvas measureText, see
  components/v2 `textmetrics.mjs`).

## Other verified anatomy

- **Tail only on the last bubble of a consecutive same-side run**: "Sure, it'll be $166.89"
  (followed by Cash card, same side) has no tail; the Cash card carries the tail (bottom-left
  hook, linq f750 y670-680). Outgoing "can you order…" (last of its run) carries the tail.
- **Group chat**: incoming bubble gets a small circular sender avatar at its left AND a gray
  sender-name label above the bubble (gallery f60-200: "Cabin trip" thread; danieltian f950+:
  "Airbnb"/"Lyft"/"Resy" name labels above each agent's message).
- **Typing indicator**: small gray pill with 3 dots sits at the incoming position before the
  reply (danieltian ~f185-230; photon-mini tile 2 "Draft an email…" shows it again). Dots bounce
  in sequence.
- **Composer**: white "+" circle with soft shadow at left; white pill field w/ shadow; mic icon
  right side when empty; send arrow replaces mic INSIDE the field when text exists; blue caret
  #0088ff. "+" opens the app list sheet (Photos/Apple Cash/Polls/Store/… → Games grid), linq
  f95-135.
- **App-card anatomy**: rounded card + **app-icon badge overlapping the top-LEFT corner**
  (GamePigeon chess card, linq f136+) + photo/content area + caption ("LET'S PLAY CHESS!" CTA or
  "Tap for details"). Apple Cash variant: black card, white "Pay" pill (linq f750).
- **Card → panel expand**: tapping "Tap for details" morphs the card into a fullscreen app panel
  (Flight Details w/ seat map, Jewelry picker w/ "Add to Bag", Cash pay sheet) — the small card
  surface grows to cover the thread; a back chevron top-left returns (linq f350-410, f585-690).
- **Emoji inside text** are raster images in the measured scenes (`v10-flight-reply-emoji-0`
  image 40x30 at x=122,y=25) — baked fidelity choice. For live builders, Chrome renders Apple
  Color Emoji in text directly (verified `frames/emoji-test.png`); Pillow falls back to Noto
  artwork — keep emoji in text copy but flag the font caveat.
- **Voice message**: bubble containing a blue play circle, a waveform of ~44 white rounded bars
  (w 4-5, radius 2-2.5, heights 18-72), a "0:04" duration label and a transcript text line below
  (04-poke measured `p0310-wave-*`; survey tile row 3).
- **Poll/results card**: "🌮 Dinner Choice" header + "🍛 Indian / Selected option" rows — an
  incoming app message, tail-less (poke f270-330).
