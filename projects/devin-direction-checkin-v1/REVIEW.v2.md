# Check In v2 picture review

- Export: `renders/v2-revised.mp4`; sidecar: `renders/v2-revised.mp4.render.json`.
- SHA256: `22f306c8151be6aea3e51e474063904c7ba3deb780bf9cb871fc16dc00488b3c`.
- ffprobe: video only, 1920×1080, 30/1 fps, 840 frames, 28.000000 seconds.
- The original movie, sidecar and contact sheet are unchanged. Original builder,
  scene and ledger are preserved as `build_scene.v1.mjs`, `scene.v1.json` and
  `events.v1.json`. Current unsuffixed source files generate v2.

## Changes

- Maya's single Check In card is outgoing/right aligned before and after arrival;
  Sam's received card stays left aligned.
- Closer Sam composer, 17 unevenly timed characters spelling `are you home yet?`,
  arrival at 580 while the complete draft remains, hold through 607, then 17
  backspaces to empty at 661. Oversized heart sends at 690 and arrives at 735.
  Its initial position was raised after review to avoid the composer masking it.
- Larger walking phone (about 72% frame height at the widest point), enlarged
  walker and legible route/Home pin. Phone opacity staging prevents off-screen
  shell slivers during camera moves.
- Larger centred end line and original green speech-bubble mark; camera and
  mark keep moving through frame 839.
- Runtime extended from 24 to 28 seconds for the longer draft, arrival hold,
  deletion and heart delivery. Arrival moves from 510 to 580; end from 625 to
  750. This intentionally revises the fixed v1 timing. No audio added.

## D1 investigation: not reproduced, cause unconfirmed

Direct full-resolution extractions from the unchanged v1 MP4 at frames 15 and
60 (`renders/d1-v1-01.png`, `renders/d1-v1-02.png`) show a continuous phone shell
across y=540, not displaced top/bottom halves. Measured dark shell boundaries
at approximately x=507 and x=1367 remain unchanged over rows 520–560. The app
sheet cannot appear there: its scene start is frame 96. A montage/contact-sheet
row boundary is a possible explanation of the reported tear, but the reviewer's
actual viewing artifact was not available, so that explanation is unverified.
No renderer fix is claimed. V2 frames 15 and 60 also show a continuous shell.

## Checks and visual evidence

`node projects/devin-direction-checkin-v1/verify_v2.mjs`:

```text
PASS: 17 uneven typed characters, arrival-with-draft hold, 17 backspaces to empty, correct card sides, one outgoing actor, sorted tracks and scene-derived events.
PASS: no horizontal phone-shell clipping at any of 840 frames; walk phone height >=45%; v1 movie and scene hashes preserved.
```

Full decode: 840 frames; longest identical-frame run: 1 frame; final 60 decoded
frame hashes all distinct. `git diff --check` produced no output.

Reviewed `renders/v2-contact.jpg`, full-frame 1920×1080 stills at non-character
events and frames 15, 60, 300, 700 and 839. Every typed/backspace event was reviewed
at native pixel size in `v2-typing-native.jpg` and `v2-backspace-native.jpg`, using
composer crops from the full-resolution stills. Camera sheets `v2-camera-*.jpg`
were inspected at every tenth frame; bounds were also checked on all 840 frames.
Full-resolution source stills for every event and camera sample remain under
`renders/v2-stills/`; `v2-evidence-frames.json` indexes them. No remaining clipping
or unintended text overlap found on these reviewed surfaces.

The ledger includes animation-onset cues: frame 140 starts the draft card's
entrance from below the clipped phone screen, not its first fully readable frame.
No commit made.
