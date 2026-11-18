# Unfamiliar-content test — components v2

Scene: `work/ui/components/scenes/unfamiliar.json` (builder `test-scene.mjs unfamiliar`)
Render: `work/ui/components/previews/unfamiliar.mp4` — 180 f @ 30 fps, html engine, re-rendered 2025 build.

Content deliberately not designed for the builders:
- Sender name: `Isabella-Catherine Montgomery-Whitfield` (47 chars, double hyphen)
- Copy: `guess who finally passed her sommelier exam 🍷🥂🎉`, `obviously yes 🙌 but why is the reservation under "Dr. Bartholomew Featherstonehaugh III"?`, `long story 😅`, typed draft `lmao ok 😂`
- Assets: three generated SVG photos (sky/sun/hill variants) via data-URI, in `PhotoStrip` carousel
- Tapback 🎉 (from: me) on `celebration dinner thursday — you in?`
- Reply bubble + thread scroll at t=3.2–3.8 to test anchor retention

## Passes

- Long name renders unclipped in `NavBar` title and as `senderName` line above the group bubble.
- Emoji (🍷🥂🎉🙌😂) render in-bubble and inside the Tapback badge at all sizes tried.
- Auto-wrap handles 5-line outgoing copy and 4-line incoming copy without overflow; auto-height keeps tails attached.
- Three-photo attachment behaves as a carousel: first photo full-width, next photo peeking, viewport clip clean (matches Linq verified photo-strip behavior — swipeable set, not a grid).
- Tapback badge remains glued to its parent bubble through the -180 px thread scroll (child-of-bubble architecture working as designed).
- Group avatar `I` + sender-name line align; bubble tail present on last-in-group `long story 😅`.
- Composer typed `lmao ok 😂` with send-arrow transition.

## Defects found

| # | Severity | Defect | Status |
|---|----------|--------|--------|
| 1 | low | Tapback badge overlaps first-line text of its own bubble ("dinner" under the badge). Real badges also overlap the corner, but copy under the badge center is less readable than in reference footage. | Accepted — anatomy-correct position; mitigate by anchoring badge to bubble corner, not text. |
| 2 | low | Third photo never visible without a swipe keyframe — carousel only peeks photo 2 at rest. | By design; editors must keyframe `PhotoStrip` `x` to reveal photos 2–3, or pick `speed`. |
| 3 | low | `long story 😅` passes under the composer during scroll — real iOS also lets the transcript slide behind the composer field; no fix needed. | Accepted. |

## Fixes applied during this test round

- Earlier rounds (thread scene): fixed malformed path serialization, outgoing-text overflow (font metrics), black-blob `+` glyph (open stroked path → two filled rects), NavBar now ships translucent backdrop so scrolled copy does not collide with chrome.

## Verdict

Components v2 tolerate unfamiliar copy/assets at production scale (24–30 px) with no layout-breaking defects. Remaining issues are editorial choices (swipe timing, badge offset) rather than renderer failures.
