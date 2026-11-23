# Independent Review — t5 batch (19 entries)

Fresh renders audited against `entries-info.json` documented moves/fixed/events.
Strips = frames 0,14,28,42,56,71 of each 72f render.

| id | verdict | evidence |
|---|---|---|
| message-pin-landing | PASS | f0–f14: blue dot on inline location cue in "…send the trail map?" bubble. f28: dot has left cue, descending toward map. f42–f71: dot anchored at end of route near "The north ridge". Question bubble, map, route, heading stationary throughout. Leaves ~f21 ✓, lands ~f50 ✓. |
| message-wall | PASS | f0: empty wall. f14: 6 tiles in staggered entry. f28–f56: 3×3 tiles accumulated, readable message identities, columns retained. f71: wall shifted up with top row clipped = camera glide through the wall. Settles ~f52 ✓. |
| messages-attachment-stack | PASS | f0–f28: stacked deck, orange card on top. f42: top card translated left + rotated off the deck, next (teal) card visible. f56–f71: teal card in lead slot turned back toward zero. "4 attachments" count, label, composer, backdrop fixed. Swipe ~f21, promote ~f56 ✓. |
| metric-count | PASS | Values 620 → 640 → 859 → 1,146 → 1,280 → 1,280. Whole-number steps in place, final held by ~f55. Heading "A growing delivery total", label "Completed trips", unit and field fixed. |
| metric-wheel-roll | PASS | 28 → (f14: partial next value clipped mid-roll below baseline) → 39 → 42 held. Three values roll upward through the narrow clipped readout. Readout geometry, baseline, "Completed bookings" label fixed. Turned ~f24, lands ~f47 ✓. |
| mini-app-expand | PASS | f0: only "Find a table for two." request bubble. f14: small green card appears mid-thread. f28–f71: card scaled to reading size — "The north ridge · For two · 7:00 PM" + Reserve button readable (~f33 ✓). Request, composer, phone silhouette, header fixed. |
| needle-sweeps-threshold | PASS | Needle rotates about pivot from Low (f0) → f20 near-vertical (past final angle = overshoot) → settles ~2 o'clock inside green threshold ticks by f44–f50 (verified extra decodes f38–f64). Ticks, threshold region, pivot, Low/High labels, "Capacity" fixed. Start ~f13, settled ~f52 ✓. |
| objects-pass-behind | PASS | f0–f14: Intake pill left, Output right of dark "Relay" cover. f28: both slide toward center, partially occluded behind Relay. f42: swapped — Output left, Intake right, still partially behind cover. f56–f71: fully emerged on opposite sides, identities kept. Cover + heading fixed. Occlusion ~f19, emerge ~f33 ✓. |
| photo-album-deal | PASS | f0–f14: 3 stacked thumbnails. f28: cards separating on staggered paths (orange left, teal right, purple peeking). f42–f71: three straightened into an even row. Heading + "The north ridge" label fixed. Open ~f17, dealt ~f47 ✓. |
| photo-compare-wipe | PASS | Divider travels left→right: f0 ~10% "after" (teal) sliver → f28 ~15% → f42 ~85% → f71 ~90%. Same crop origin both sides; After/Before labels and frame fixed. Drag ~f17, stop ~f51 ✓. |
| photo-crop-reframe | PASS | Oversized picture eases sideways under stationary portrait crop: f0 peaks lower-left, sun off-crop → f28 sun enters left edge → f42–f71 sun settled upper-left. Crop bounds + grid lines + heading fixed at same positions. Drag ~f18, settle ~f47 ✓. |
| photo-grid-density | PASS | f0–f14: 2×2 large tiles. f28: existing 4 shrink/converge overlapping mid-reflow. f42–f71: dense 3×2 grid — first 4 identities preserved (top row + bottom-left) + 2 new secondary tiles in newly reachable cells. Grid region, heading fixed. Change ~f17, settle ~f53 ✓. |
| photo-iris-reveal | PASS | f0–f14: dark card, tiny origin dot. f28: circular aperture expanded showing photo patch. f42: nearly full reveal, dark only at corners. f56–f71: fully revealed, geometry identical to unmoving image. Opens ~f17, clears ~f50 ✓. |
| photo-markup-stroke | PASS | f0–f14: clean photo. f28: partial yellow curve + pen-tip marker at stroke end. f42: stroke grown along drawing path, tip moved with it. f56–f71: completed loop remains over peaks. Photo, viewport, heading, footer fixed. Pen-down ~f17, pen-up ~f49 ✓. |
| photo-open-continuity | PASS | f0–f14: 3 thumbnails. f28: middle thumb enlarging, neighbors dimmed. f42–f71: chosen photo as large raised preview; neighbors remain as dimmed slivers at their original slots. Heading/footer/viewport fixed. Open ~f18, settle ~f47 ✓. |
| photo-pinch-detail | PASS | f0: full photo. f14: two gesture markers appear close at center. f28: markers spread apart as image scales around focal point. f42–f71: magnified mountain detail inside same clipped window. Window, "Zoom" control, heading fixed. Pinch ~f19–f48 ✓. |
| photos-under-fixed-heading | PASS | f0–f14: orange+teal photos on rail. f28: rail sliding left, orange clipped, teal large. f42–f71: settled on next pair (purple + red-orange). "Alpine field notes" heading, divider, "Field guide · Autumn" footer all fixed. Rail-start ~f20, settle ~f39 ✓. |
| pin-conversation-avatar | PASS | f0–f14: "T" avatar in highlighted Trail crew row, Pinned tray empty. f28: avatar inside pinned tray, old row fading/collapsing. f42–f71: avatar settled in tray with label; row collapsed, Weekend plans + Project notes slid up. Header, pin lane, other rows' copy fixed. Pin ~f26, arrival ~f50 ✓. |
| rack-focus | PASS | f0–f28: near "Overview" card sharp, far card blurred. f42–f71: far "Specific result" card sharp, near card softened to blur blob — positions/silhouettes unchanged. Heading + frame fixed. Shift ~f24, far-sharp ~f43 ✓. |

## DEFECTS

None. All 19 fresh renders reproduce the documented motion: moving elements move as described, fixed elements hold position, and event timing lands within tolerance of the declared frames.

## PASS: 19/19
