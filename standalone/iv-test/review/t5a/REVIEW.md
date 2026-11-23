# Semantic review — t5 batch (20 entries)

Strips = frames 0/14/28/42/56/71 of each fresh 720x480@30fps render (72 frames).
Extra frames decoded where noted.

| id | verdict | evidence |
|---|---|---|
| accordion-displaces-row | PASS | Timing row grows taller with "Hold expires after fifteen minutes." detail; indicator rotates \| → angled → — across f14→f28→f42; "Travel information" row displaced downward. Top edge, titles, viewport fixed. Open lands in f13–44 window. |
| album-page-turn | PASS | Right leaf compresses toward center seam by f28 (next leaf edge peeks at right); its reverse opens over the left page by f42–56 (new spread). Seam/cover fixed; resting-page content has no free translation. Spine-cross ~f36 window fits. |
| app-drawer | PASS | Sheet with grab handle + "Apps" label + 6 icons rises from offscreen as one clipped sheet (mid-rise at f8, fully open f20+); phone header and blue bubble stay put. Note: settle completes ~f20 vs declared drawer-open@31 — event marker fires ~10f after actual settle; motion itself correct. |
| attachment-download-progress | PASS | Determinate fill 5→20→27→47→67→77→87% then green full bar + "Available to open" only at completion (f58+). Pauses confirmed: 27% held f28–f30, 67% held f42–f46 (two pauses as documented). Thumbnail, filename, card geometry fixed. |
| attachment-peek-release | PASS | Middle attachment lifts and enlarges with drop shadow f28–f42 (hold), neighbors stay; returns to exactly its original grid slot by f56–f71. Matches lift@17/release@47/return@61. |
| avatar-ring-assemble | PASS | 5 circular portraits converge from edges on separate paths, arriving blurred f14–f28 then sharpening f42+; headline copy shrinks while its center stays anchored; backdrop fixed. Settled by ~f56 (declared 57). |
| batch-select-messages | PASS | Transcript shifts right f14–f28 exposing check rail; first row checked at f42 with "1 selected" + Forward bar replacing composer; second row checked f56 "2 selected". Checks land separately as documented. Header, order, message text fixed. |
| camera-push-in | PASS | View scales progressively around the Reservation card f14→f71; Overview/History cards carried toward/off the edges; focal card stays centered; Trip-planner heading and frame fixed. Detail framed ~f49 window. |
| camera-truck-between | PASS | Horizontal pan carries view from "Plan" panel to "Check out" panel f14→f42; Check out ends centered with prior panel sliver at left; dot index updates to destination. Constant magnification; heading + window fixed. |
| card-orbit | PASS | Three cards fly in with distinct tilts (f14 clearly rotated mid-flight), level out and settle into an ordered row by f42–f56 on a common baseline (lineup-settled@40). Labels retained. |
| card-reorder-insert | PASS | First (orange) tile lifts with shadow f28, travels over the row to the third position where a drop outline appears f42, docks at slot 3 f56–f71; teal/purple shift left keeping order. Row bounds, heading, footer fixed. |
| center-gutter-open | PASS | Two picture planes slide outward in opposite directions f14→f42 opening a center gutter; "Same destination" label revealed centered f42+. Original frame and centered text fixed. |
| circle-to-panel | PASS | Blue circle → squircle (f14) → rounded panel (f28) → panel gains title/body/button contents only once sized (f42+). Transformation stays centered on stage anchor. |
| comparison-bars-grow | PASS | Both bars grow upward from shared baseline (nubs f14, grown f28, settled f42+); "Now" clears the red Target line, "Earlier" falls short — documented default. Baseline, target line, labels fixed. |
| composer-type | PASS | Composer accumulates characters progressively "Ca|"→"…map?|" f14→f71 with advancing caret; send button activates; transcript bubble, field, heading, viewport stationary. First char ~f11, complete ~f60–71. |
| conversation-handoff | PASS | Draft types in composer (f14 partial, f28 full), transfers into outgoing blue bubble by f42 (send@32 window), gray incoming reply arrives after pause by f56 (receive@51). Phone, header, composer field, reading area fixed. |
| delivery-receipt-handoff | PASS | "Delivered" under first bubble fades between f28–f42; latest bubble rises slightly as its own "Delivered" resolves beneath it by f56 (receipt-reassigned@34). First bubble, composer, heading fixed. |
| depth-parallax | PASS | Foreground blue pill crosses quickly and exits left by f42; middle "Workspace"/"Controls" cards translate a shorter distance; background grid lines barely shift. Drawing window fixed. Three distinct rates confirmed. |
| draft-send-flight | PASS | Composer draft collapses toward its right edge — f16 shows the outgoing blue balloon forming at the right edge of the cleared field (send control gone at trigger) — then the balloon rises, sits high at f28 (overshoot), settles into transcript slot f42+. Heading, prior reply, composer field fixed. |
| edit-message-reflow | PASS | Blue bubble deepens to fit added second line "By the north entrance." at f28 while keeping its slot and identity; gray neighbor reflows down; "Edited" marker appears by f56 (commit@47). Header and composer fixed. |

## DEFECTS

None. All 20 fresh renders reproduce the documented moving elements, preserve the
documented fixed layers, and land in roughly their declared event windows.

Minor observation (not a defect): `app-drawer` finishes its rise ~f20 while the
`drawer-open` event is declared at f31 — the marker fires ~10 frames after the
visible settle. The documented motion itself is fully reproduced.
