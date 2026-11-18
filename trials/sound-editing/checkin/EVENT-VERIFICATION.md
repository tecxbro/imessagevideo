# Native-picture verification

Picture: `v1-first-export.mp4`, zero-based native frames, 30/1 fps, 720 frames / 24 seconds. Sequential decode (not timestamp seeks) produced PNGs. Before/at/after images and transition sheets were opened and inspected. The director's list is an intent list, not an audio receipt.

`evidence/frame-NNN.png` supplies full-resolution evidence. Named sheets below show adjacent frames. At 48 kHz, frame **f → f × 1600** samples exactly. A cue's early attack peak aligns to that sample; the reference file can start earlier. Audio accents are stock/procedural designs, not claims to proprietary Apple sounds.

| Director f | Observed native picture | Canonical treatment / evidence |
|---:|---|---|
| 12 | Blank at12; first faint incoming ask fade13, clearer14 | Receive13; `receive-onset.png`, frames12–14 |
| 90 | Plus button is offscreen; camera reveals composer/ring97–99. Menu first rises103 | No inferred tap90. Quiet panel movement103 instead; `plus-full.png`, frames90,98,102–104 |
| 132 | Check In row selection/tap indication132, absent131 | Tap132; `early-action-pairs.png`, frames131–133 |
| 140 | Composer still empty; draft's first small edge enters bottom145, clearer146 onward | Silent appearance145, not typing; `draft-onset.png`, frames139–146 |
| 186 | Send-button interaction visible186 | One send186, not tap plus send and not backspace; `send-onset.png`, frames185–187 |
| 432 | Second phone is entering view; first existing card sliver visible435 | Silent camera reveal435, **not a newly arriving message**; `second-phone-onset.png`, frames431–436 |
| 445 | Placeholder → `a` | Key445; `typing-wide.png`, frames444–446 |
| 451 | `a` → `ar` | Key451; frames450–452 |
| 457 | `ar` → `are` | Key457; frames456–458 |
| 463 | `are` remains visibly `are`; trailing space has no visible glyph/caret change | Omit inferred key463; frames462–464 |
| 469 | `are` → `are y` | Key469; frames468–470 |
| 474 | `are y` → `are yo` | Key474; frames473–475 |
| 480 | `are yo` → `are you` | Key480; frames479–481 |
| 486 | `are you` remains visibly unchanged; trailing space not observable | Omit inferred key486; frames485–487 |
| 492 | `are you` → `are you h` | Key492; frames491–493 |
| 505 | Marker is over home around504–505; clock also changes505. Green card confirmation is not yet visible | Retain505 as silent location state; do not double-accent arrival. `arrival-map.png`, frames504–510 |
| 510 | Both cards turn green / Arrived; moving dot disappears | One shared confirmation510; `late-action-pairs.png`, frames509–511 |
| 522 | `are you h` → visibly `are you` | Backspace522; `deletion-pairs.png`, frames521–523 |
| 525 | Trailing-space deletion has no visible glyph/caret change | Omit inferred backspace525; frames524–526 |
| 529 | `are you` → `are yo` | Backspace529; frames528–530 |
| 532 | `are yo` → `are y` | Backspace532; frames531–533 |
| 535 | `are y` → visibly `are` | Backspace535; frames534–536 |
| 538 | Trailing-space deletion has no visible glyph/caret change | Omit inferred backspace538; frames537–539 |
| 542 | `are` → `ar` | Backspace542; frames541–543 |
| 545 | `ar` → `a` | Backspace545; frames544–546 |
| 548 | `a` → empty / iMessage placeholder | Backspace548; frames547–549 |
| 575 | Heart bubble first appears by composer edge, with send interaction | One send575; `late-action-pairs.png`, frames574–576; no backspace for clear |
| 590 | Heart first appears at first-phone composer edge | Receive590; frames589–591 |
| 210–419 | Continuous location/camera travel, no listed UI changes; inspected overview samples210,240,270,300,330,360,390,419 | **Zero UI cues**. Optional continuous motion texture is not a keyboard, notification, or invented footstep. See contact sheet |

Twenty-one audible cues plus three silent state records. Seven visible typing and seven visible deletion updates, not nine physical keystrokes each. The invisible-space omissions follow the visible-change rule rather than attempting to recover hidden application state from later text.

Contact sheet: `evidence/contact-sheet-verified.png`. The complete native-frame evidence and original exploratory sheet are retained. Gap inspection used the listed snapshots, not a claim to have visually scrutinized every one of its 210 frames.
