# Independent Review — t5 batch (19 entries)

Fresh renders audited against `entries-info.json` documentation. Evidence drawn from
6-frame strips (`jobs/t5/strips/<ID>.jpg`, frames 0/14/28/42/56/71) plus targeted
frame decodes and pixel measurements of `jobs/t5/renders/<ID>.mp4` (720x480@30fps).

| ID | Verdict | Evidence |
|---|---|---|
| reaction-attach | PASS | "Love" pill below bubble (f0-14) → mid-flight overlapping bubble corner w/ ghost trail (f28) → shrunk corner badge (f42+). Pixel check: gray reply row shifts down ~20px (y240-300→260-320) between f40-44 = "nearby text row makes room". Heading/composer/messages fixed. Events @26/@49 consistent. |
| registered-shape-cut | PASS | Mean brightness jumps 233.9→188.2 exactly between f35-f36 — true one-frame cut (doc: registered-cut@36). "Approve" button identical position/size/wording in both contexts; supporting line "The same action is available here." fades in post-cut (new-context-readable@52). |
| reply-makes-room | PASS | Old rows lift together (blue y349→281, gray y250-310→190-250, ~60-68px each); new incoming reply cluster appears at bottom y~330-390 starting ~f35-38 (doc: arrival@35), rising a shorter distance. Composer fixed at y410-450. |
| schedule-send-wheel | PASS | Wheel values roll 7:15→7:45 PM behind fixed middle selection band (f0-14 vs f28+); wheel closes and "7:45 PM" chip persists (f56 closing, f71 chip only). Band, draft, history fixed. Events @18/@49 consistent. |
| screen-to-physical-prop | PASS | Phone slides left/offscreen while prop sharpens ("MOON" readable f42). Prop width 185px→347px cut between f47-48 (doc: cut@48), then pushes in 349→375 through f60 and holds (doc: hold@60). Prop stays on table; reply moves with phone. |
| selection-confirm | PASS | Three stages verified: blue "Confirm" (≤f30, RGB 23,135,246) → desaturated dark pressed state (f35-39, saturated px ≈0, press@36) → green "Confirmed" (f40+, RGB 60,123,84). Button geometry/card fixed throughout. |
| send-failure-retry | PASS | Damped shake measured: bubble x-centroid oscillates 426→414→437→419→429→426 (decaying ±12px) starting f30 (doc: delivery-failed@30). Red "!" retry badge beside + "Not Delivered" below bubble by f42 (doc: retry-ready@42). Other rows fixed. |
| signal-radiation | PASS | Concentric thin rings grow from static source dot and fade: 1 ring f14, 3-4 rings f28, 1 large fading ring f42, cleared f56+ (doc: emitted@11, clears@53). Source/heading/caption fixed. |
| signals-merge-routes | PASS | Two dots travel separate branches from Availability/Preferences endpoints, converge at junction ~f35-42 (doc: merge@38), single packet continues shared route reaching Reservation f56+ (doc: arrives@57). Geometry/labels fixed. |
| spotlight-cross-text | PASS | Bounded bright opening (white box) in dimmed field sits on "Pick a time" f0-14, mid-travel f28, rests on "Reserve now" f42+ (doc: start@17, in-spotlight@44). All text positions/type/spacing identical across frames. |
| step-indicator-travel | PASS | Measured underline centroid: holds at Choose cx≈242 (f8-14), travels f16-26, arrives Review cx=360 @f26 (doc: middle-step@26), holds f26-40, travels f42-50, arrives Reserve cx=477 (doc: final-step@53). Labels/rail/caption fixed. |
| swipe-to-quote | PASS | Only gray bubble translates right w/ blue ← arrow revealed behind it (f28); row returns (f42-56, other rows unmoved) and "Replying to this message" quote strip opens above fixed composer (faint f42, full f56; doc: commit@35, open@47). Blue bubble/header fixed. |
| tear-perforated-ticket | PASS | Dashed seam parts left→right (left half open f28, right edge still joined), stub tilts around joined edge, fully detached and dropped/rotated f42+ (doc: tear@18, detach@44). Main ticket/copy pinned. |
| text-scramble-resolve | PASS | Glyph slots change in place: "CK4P8 DW 3N7S" (f14) → "CLEAR 4P TDWH" (f28) → "CLEAR TO OP4P" (f42) → "CLEAR TO OPEN" (f56+), resolving left-to-right (doc: start@11, readable@46). Field/heading/camera fixed. |
| transcript-timestamp-peek | PASS | All bubbles shift left revealing trailing-edge times 1:25/1:26/1:28 PM in right gutter (f28-42), spring back with times gone by f56 (doc: peek@16, release@47). Heading/composer/vertical positions fixed. |
| trend-line-trace | PASS | Leading dot traverses chart leaving completed polyline behind: origin f0, 1 segment f14 (doc: start@11), ~2-3 segments f28, near-complete f42, full trace to final point f56+ (doc: final@50). Grid/axes/endpoints fixed. |
| typing-indicator-cycle | PASS | Indicator appears ~f9-10 (doc: visible@8, fade-in) and dot dark-pixel counts oscillate cyclically (225→135→80→183→116→78→166) with cy stable ~282-289 — staggered lift/dim inside stationary bubble. Prior message/composer/heading fixed. |
| typographic-tracking-contract | PASS | "T o g e t h e r" wide-tracked f0-14 → contracted f28 → normal "Together" f42+ (doc: contracts@12, readable@42). Word center, baseline, type size and axis tick underneath all fixed. |
| undo-send-remove | PASS | Blue bubble contracts toward its own tail while shrinking/fading f30→38 (measured width/scale collapse right-side, doc: unsend@26), gone by f42 w/ gray row closing gap (doc: removed@42), "You unsent a message" status appears f56+. Header/composer/surviving copy fixed. |

## DEFECTS

None. All 19 renders reproduce the documented motion at roughly the declared event
frames, with documented fixed elements verified stationary.
