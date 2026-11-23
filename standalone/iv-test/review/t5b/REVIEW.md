# Independent Review — t5 batch (19 entries)

Fresh renders audited against documented moves/fixed/events in `entries-info.json`.
Evidence = 6-frame strips (`jobs/t5/strips/<ID>.jpg`); extra frames decoded from
`jobs/t5/renders/<ID>.mp4` where noted.

| id | verdict | evidence |
|---|---|---|
| exploded-layer-view | PASS | f0/14 compact stack; f28 three planes (Surface/Tools/Content) mid-separation; f42+ spread diagonally with shared orientation and each layer's label/border intact. Separates @13 → separated @47 window matches. |
| freeze-around-live-detail | PASS | f0→14 peripheral dots on top/bottom tracks shift right (mid-travel); f28+ they hold identical positions (freeze @24). Blue "Priority task" dot keeps advancing f14→42 and rests at right end by f56 (arrival @53). Tracks fixed throughout. |
| grid-reflow | PASS | f0/14: order Archive/Due today/Next/Waiting; f28 cards mid-flight on individual overlapping paths; f42+ new order Due today/Next/Waiting/Archive settled. Copy/proportions preserved, heading fixed. Reflow @10 → reordered @49. |
| heading-over-fixed-photos | PASS | Heading "Alpine field notes" glides within its band: left at f0–24, traveling right at f44, settled centered by f50–71 (decoded f20,24,32,44,50,55,58,60,62,65,66,69,71 confirm start ≈f20–28, settle ≈f50 vs documented 20/51). Photos, crop, backdrop, bottom caption pixel-identical across all frames. |
| hinged-swatch-fan | PASS | f0/14 single stack; f28 outer leaves (red left, blue right) rotating out in opposite directions around bottom pin; f42+ standing fan held. Center yellow leaf, pivot, heading, camera fixed. Opens @16 → settled @47. |
| history-prepend-anchor | PASS | Decoded f29–45: "Loading earlier…" appears at top f29 while read rows (gray question + blue "That was helpful.") stay pixel-fixed through f39; drag begins @39 and f41–45 rows travel down together revealing prepended "Here it is. Meet at the north gate." + "Yesterday" marker. Heading/composer fixed. |
| identity-morph | PASS | f0/14 blue circle w/ check mark; f28 mid-morph: dark squircle (radius+size+color changed) with mark exchanging; f42+ dark tile with "A". Same center anchor, background fixed. Resolved @44. |
| inline-card-expand | PASS | f0/14 conversation w/ photo card; f28 grabber+sheet risen partway, chat dimmed; f42+ sheet settled w/ title, photo, Open button, dimmed thread above. Header and underlying card fixed. Enter @24 → settle @55. |
| inline-thread-open | PASS | f0/14 parent + unrelated "One more thing."; f28 connector line grown from parent, unrelated row moved down; f42 two indented replies emerging in sequence (gray "Here it is…", blue "I will leave at noon." fading in); f56+ both readable. Parent/heading/composer fixed. Expand @23 → readable @51. |
| items-collapse-into-count | PASS | f0 three items + "0 Completed"; f14 Verify arcing toward counter; f28 Verify shrinking at counter, Send in flight; f42 Send at counter, count ~2; f56+ all consumed, "3 Completed". Count surface/label/framing fixed. Events @31/41/50 align. |
| jump-to-unread | PASS | f0/14 transcript + "Jump to unread" pill; f21–28 single scroll advances rows (pill fading); f42+ "Unread messages" divider rests at top with unread rows below, pill cleared. Header/composer anchored. Jump @21 → destination @52. |
| keyboard-focus-reflow | PASS | f0/14 composer at bottom, no keyboard; f28 keyboard rising from below lifting composer + last message; f42+ keyboard fully open, composer+message reachable above it. Header fixed; textarea still shows "Message" placeholder — no characters entered. Focus @25 → ready @44. |
| link-preview-upgrade | PASS | f0–28 plain URL bubble; f42+ card extended horizontally with "Trail map / Maps and access notes" metadata + icon revealed inside clipped region. URL text, row height, adjacent reply, heading, composer fixed. Ready @33. |
| location-question-bridge | PASS | f0/14 question + keyboard/composer; f28 "Current location" suggestion visible (@25); f42 pill pressed/highlighted (@44); f56 keyboard+composer cleared (empty interval, question held); f71 map occupies former region w/ "Shared location · North gate" (@58). Question stays readable anchor throughout. |
| long-press-actions | PASS | f0/14 three rows; f28+ context dimmed, reaction rail (Love/Like/Laugh/Emphasize) grown above held blue bubble, Copy/Reply/More tray open below it. Selected message remains on its original slot f28–71. Hold @20 → actions @31. |
| media-caption-disclosure | PASS | f0/14 photo + "Open" control, gray neighbor row directly below; f28+ "Field guide · Autumn" caption unfolded inside the card (window gained height) and the neighbor row pushed down. Photo bounds/control/heading fixed. Toggle @17 → settle @42. |
| media-progressive-sharpen | PASS | f0/14 uniformly soft photo; f28 top band (sky/sun/peaks) sharp over still-soft base; f42 sharp region extended, bottom band still soft; f56+ fully resolved. Same picture geometry/window throughout — bands sharpen, not replaced. First region @18 → full @54. |
| media-trim-range | PASS | f0/14 handles at filmstrip ends; f28 left handle advanced inward (left segment dimmed) — first gesture @18; f42 right handle advanced inward (right end dimmed) — second gesture @38; f56+ selection settled, excluded ranges dimmed, filmstrip/time axis fixed. Settle @53. |
| media-video-scrub | PASS | f0/14 playhead at 0:00 (warm scene); f28 playhead ~1/3 (teal scene); f42 near 0:18 end (sunset scene); f56/71 playhead backtracked to ~mid (purple scene). Forward drag → pause → backtrack; viewer sample follows position; preview frame/timeline/chrome fixed. Seek @16 → stop @56. |

## DEFECTS

None. All 19 fresh renders reproduce the documented movement with fixed elements
stationary and events landing roughly at declared frames.

Notes (non-blocking):
- heading-over-fixed-photos: the heading overshoots toward the right edge (~f44)
  before settling centered (~f50); this reads as an eased glide and still matches
  "glides within its own clipped band" with settle at documented f51.
