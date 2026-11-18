# Credibility-damage ranking — what reviewers notice first

Ranked by damage-if-wrong, grounded in measured scene data + frame evidence. Each entry: what
breaks, proof, and the v2 fix.

## 1. Bubble tail shape + placement (HIGHEST)

The tail is the fastest fake tell. v1's path is a rough guess: `Q` curves that kick out past the
bubble edge and re-enter — real iOS tails are a tight comma hook that stays inside the body's
x-extent, ~14px drop on a 120px bubble (measured linq f750: body y56-172, tail tip y~186,
x 830-847; incoming mirror). Tail appears ONLY on the last message of a same-side run —
"Sure, it'll be $166.89" (followed by Cash card) is tail-less; the card carries the tail.
v2: measured tail path, `tail` only on group-last bubbles, mirrored per side.

## 2. Text wrap + auto-height (forces rework on EVERY copy change)

v1 requires manual width/height/copy-fit per bubble; wrong copy = overflow or underlap.
Measured: radius ≈ fontSize×1.05-1.15 (36-40px on 120px 2-line bubble; 30-33px on 66px 1-line),
padding ≈ 18-20px h / ~12px v, lineHeight ≈ 1.2×fontSize. v2: embedded SF Pro width table
(canvas-measured, `textmetrics.mjs`), `wrapText()` + auto height; overflow throws or reports
lines, never silently shrinks.

## 3. Tapback anchoring (verified failure mode: floating badges)

Badge must ride its bubble through scroll — proven moving together linq f758-765. v1 has NO
tapback component; filmmakers would absolutely float it as a sibling and it would drift on the
first camera move or scroll. v2: `tapback` param on MessageBubble/AppCard parents the badge INSIDE
the message group; standalone `TapbackBadge` for manual anchoring. Anatomy: blue badge ~bubble
proportions, emoji inside, two-bump tail toward anchor corner, pops in with a spring (f722-728).

## 4. Composer draft→send lifecycle (the second most-animated UI in the films)

Measured exact sequence (linq `v19-intro-composer`): placeholder+mic visible → first typed char
ends BOTH at the same instant → send circle fades in INSIDE the field right end over ~3 frames
(#c2d2fd→#70a3ff→#007efe) → send → field returns to placeholder+mic, bubble appended to thread.
v1 errors: mic and send coexist, send outside field, no typed-copy layer, no caret.
v2: `Composer` emits discrete state layers (placeholder, mic, typedText, caret, sendFill) with
documented keyframe contract + `composerLifecycle()` helper that stamps the full timed sequence.

## 5. Typing indicator (missing component; appears in every reply beat)

Gray pill with 3 sequentially-bouncing dots, sits at incoming position; in group chat it rides
next to the sender avatar. danieltian f185-230, photon-mini. v2: `TypingIndicator` with
measured-ish dot stagger (dots rise/fall in sequence, ~0.15s offset, looping ~0.9s).

## 6. Attachment card anatomy (app badge corner + CTA + expand)

v1 AppCard is generic card chrome. Real app messages: app-icon badge overlapping TOP-LEFT corner,
content area, "Tap for details"/CTA caption, and the whole surface morphs to a fullscreen panel
on tap. Apple Cash card is black w/ white "Pay" pill. v2: `AppCard` gains badge, caption row,
CTA pill, and a paired `expanded` surface sharing layer ids for the morph; `PhotoStrip` for
scrolling images under fixed chrome (clip verified linq f1050-1150).

## 7. Group-chat sender label + avatar (wrongly omitted in 1:1 framing)

Every group incoming message shows a small circular avatar at bubble-left AND a gray sender name
ABOVE the bubble (gallery "Cabin trip", danieltian agent names). Missing these reads as a 1:1
chat pasted into a group story. v2: `senderName`/`senderAvatar` params on MessageBubble.

## 8. "Delivered"/"Read" status label

Small gray right-aligned text under the LAST outgoing bubble; appears after send, upgrades
Delivered→Read (linq f145-175). Cheap detail, sells authenticity. v2: `DeliveryStatus` component
aligned to thread width.

## 9. Composer placeholder content + "+" affordance

Placeholder is "iMessage" (or "Message {name}" — poke "Message Poke"); the + is a WHITE circle
with shadow (not gray glyph); it opens the app-list sheet. v1 uses a stroked pill + always-send.
v2: accurate chrome + optional `AppDrawer`.

## 10. Emoji rendering (caveat, not geometry)

Measured scenes embed emoji as raster images; live builders can rely on Chrome's Apple Color
Emoji in text (verified) but Pillow renders Noto artwork — cross-engine emoji parity is NOT free.
v2: emoji allowed in copy; handoff documents the per-engine caveat + `emojiImage` escape hatch.

## 11. Device frame during camera moves

Phone screen content must be a child of the transformed phone group (gallery f330-480 proves
rigid coupling; world-space emoji/titles stay siblings). v1 PhoneFrame is a light viewport card.
v2: `DeviceFrame` (dark bezel, Dynamic Island, screen clip) + `CameraRig` usage contract.

## 12. Voice message bubble

Blue play circle + ~44 white waveform bars (w4-5, r2-2.5, h18-72) + duration + transcript
(poke p0310-wave-*). Recurring surface in agent films. v2: `VoiceMessage` builder from a
seeded waveform profile.

Not ranked but logged: poll/results card (Dinner Choice pattern), card carousel checkboxes
(Ettan/Khazana), calendar time-slot pills — all follow the AppCard anatomy; captured for
filmmakers in components.md as card skinning recipes.
