# Sidehoe reviewer audit

**Corrected visual verdict: 0 of 24 shots pass the one-to-one check.** A fresh decode compared every RGB channel at all 2,000 × 2,000 pixel positions, across all 778 aligned frames. Every frame differs. In 773 frames, at least one channel differs by 30 or more on a 0–255 scale. All 778 presentation times and the exact 31.12-second picture end match. [Frame-by-frame measurements](exact/frames.csv) · [Every second](each-second.csv) · [Every shot](shot-verdicts.csv) · [Exact verdict](verdict-exact.json)

## Why the prior reviewer passed shots

1. **I wrote a smaller test than the requested match.** The old plan marked all its RGB thresholds diagnostic. The computer still compared every frame, but those differences could not block a historical scoped shot pass. The old overall verdict was already FAIL. My description of 13 shots passing overstated what those checks established. [Historical plan](../../repair-review/review-plan.json) · [Old review](../REVIEW.md)
2. **Three multi-frame shots had one required observation each.** Detached iMessage was judged at f394 by where the pointer reached Send?. The violet and cyan calendar shots were judged at f435 and f460 by appointment stacking. Those three shots cover 81 frames in total. Their criteria omitted typography, emoji, shape and the cursor trajectory. App exit checked motion, streaks, glow and the blank beat, so the blue 31 tile could look wrong during a shot counted as passed. The app orbit was already marked failed. [Old criterion windows](shot-verdicts.csv)
3. **The verifier trusted the pass notes.** It checked the candidate and plan hashes, range coverage, a nonempty observation and whether an evidence file existed. I tested it with deliberately invented pass notes pointing to an unrelated JSON file. Scoped verification accepted all 24 using the historical comparison. Exact verification rejected all 24 on the freshly decoded comparison. The strict mode already exists in the current verifier. This audit used it without editing the reviewer or skill. [Negative control](negative-control.json) · [Verifier](../../../codex-trial/skill/imessage-motion-recreation/recreate/review.py#L119)

## Visible errors the scoped checks missed

| Frame | What actually differs | Native comparison |
| --- | --- | --- |
| 394, detached iMessage | Fill, text weight and padding, curved bubble tails versus triangular tails, and the Send? pill with its gradient reversed. The cursor silhouette and its spacing from the pill also differ. | [Original, recreation and differences](native-crops/bubble.png) |
| 435, Calendar | The day header, grid, appointment fills and type differ. The original uses an eggplant and droplets. The candidate uses a purple oval and a blue bead. The cat glyph differs as well. | [Calendar](native-crops/calendar.png) · [Emoji crop](native-crops/calendar-emoji.png) |
| 616, blue 31 tile | The candidate uses Inter digits on a flat rounded square. The original has a different numeral silhouette, a curved and pinched tile face, edge highlight and blur. | [Blue 31 tile](native-crops/app-31.png) |
| 675, No and Yes | The candidate uses hand-drawn approximations of the crying and tongue-out wink emoji. The type, pill, and arrow silhouettes differ even though the click reached the Yes target. | [Buttons](native-crops/buttons.png) |

Each native crop shows original, recreation, and a mask of pixels with a channel delta of at least 30. The exact verdict counts any nonzero channel delta. [Crop measurements](targeted-crops.json)

## Why the pointer looks shaky

At f419→420 the original pointer's dark area shrinks from 2,713 to 2,617 pixels. The recreation grows from 2,206 to 3,088 pixels, about 40% in one frame, then drops again. The fitted scale was keyed from 0.98 to 1.16 to 1.08 on consecutive frames, and the renderer rounds its placement and raster size. At f429→430 the fitted path hands off to a second track. The original pointer's dark centroid moves up 9.4 coded pixels while the recreation's moves down 9.4 pixels, and the authored rotation snaps from −18° to −4°. The matched frame clock does not constrain those motion choices. These are measured examples of local instability. [Pointer frame strip](native-crops/pointer-motion.png) · [Pointer measurements](calendar-pointer.csv) · [Track handoff](../project/render.py#L828) · [Compositing](../project/artwork.py#L79)

## Who chose the assets

I did. The renderer turns brace tokens into hand-drawn marks. In the calendar I even labeled the eggplant as `{plum}`. Standard emoji need the matching glyph artwork. The 31 tile is custom icon artwork and needs matching lettering, material and deformation. The dimensional portrait heads were already made with reference-guided ImageGen. They were replacement assets whose appearance still needed to be judged in the shot. [Scene copy](../project/scene.json#L71) · [Pictograms](../project/artwork.py#L28) · [31 tile](../project/artwork.py#L248) · [Portrait provenance](../../evidence/PORTRAITS.md)
