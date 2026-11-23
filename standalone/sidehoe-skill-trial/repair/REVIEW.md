# Sidehoe recreation repair and verification

**Full-export verdict is FAIL.** 13 of 24 shots meet the frozen shot criteria. 8 of the original 19 failures now pass and 11 remain open. The original and repair have 778 frames at 25 fps, matching every decoded presentation time and the 31.12-second picture end. The full-frame mean RGB error decreased from 8.85 to 6.97. 0 of 778 frames are pixel-identical. The largest average error is at [f150](evidence/final-comparison/index.html?frame=150) (18.45). 1 of 23 named diagnostic regions still fail their preset RGB limit.

[Original left, repair right](exports/original-left-repair-right.mp4) · [Frame-by-frame viewer](evidence/final-comparison/index.html) · [Full native measurements](evidence/final-comparison/report.json) · [Repaired MP4](exports/sidehoe.mp4) · [Editable project](exports/editable-project.zip)

The comparison video carries the original audio. The repaired MP4 carries the editable score and Foley. The score and picture use the same timeline events. The Yes pointer is in the decoded target at frame 675. The frames in the viewer derive from the same hashed MP4 as the shot verdicts. [Contact measurements](evidence/yes-contact.csv) · [Timeline](evidence/resolved-events.json)

## Shot verdicts

The ranges and criteria are frozen from the prior repair plan. A pass applies to that shot’s recorded criterion. The RGB columns report the average over all frames of the shot, using the same measurements for both builds. Each observation links to decoded evidence. [Frozen plan](../repair-review/review-plan.json) · [Recorded observations](evidence/visual-review.json) · [Machine-verified acceptance](evidence/acceptance.json)

| Shot and range | Verdict | RGB error, prior → repaired | Observed result |
| --- | --- | --- | --- |
| 01 · Pinned inbox entrance · 0–9 | FAIL | 7.11 → 6.15 | Separate portrait, header and note tracks restore the side portraits at f2. At f0 the source status marks fan outward while the candidate uses a soft translation. The f3 source tag and downward label streak still read earlier. [f000](evidence/final-comparison/index.html?frame=0)–[f004](evidence/final-comparison/index.html?frame=4) |
| 02 · Inbox hold · 10–41 | PASS | 9.68 → 9.68 | At f22 the three portrait disks, centered note and first two inbox rows retain the held layout. The portrait artwork is independently rendered. [f022](evidence/final-comparison/index.html?frame=22) |
| 03 · Inbox scroll · 42–101 | PASS | 9.67 → 8.56 | Named Eleanor and Charlotte anchors agree through acceleration. The late fit tracks both the rising rows and the change in spacing and scale. Darla and El align at f95 and the leading Margot row is visible again at f101. The home bar and the strength of the departing streak around f56 still differ. [f042](evidence/final-comparison/index.html?frame=42)–[f101](evidence/final-comparison/index.html?frame=101) |
| 04 · Identity · 102–133 | FAIL | 4.96 → 4.41 | The opening and settled badge use separate measured dimensions. At f108 the leftmost original glyph is darker and the trailing part is more displaced. The independently drawn card illustration still has visibly wider pink shapes. [f103](evidence/final-comparison/index.html?frame=103)–[f114](evidence/final-comparison/index.html?frame=114) |
| 05 · Glossy handset · 134–161 | FAIL | 21.09 → 15.16 | The fitted rim and pad improve the shape and lower light. The f136 island and rainbow edge still bend and spread differently. The held lower-right wash and rim contrast at f150 differ. [f136](evidence/final-comparison/index.html?frame=136)–[f150](evidence/final-comparison/index.html?frame=150) |
| 06 · Personal title · 162–212 | FAIL | 6.45 → 5.55 | The candidate opens on ‘For’ and layers the arriving disks under the outgoing title at f212. Around f180, parts of the second line brighten in a different order and several of the tiny incoming patches remain fainter at f212. [f178](evidence/final-comparison/index.html?frame=178)–[f212](evidence/final-comparison/index.html?frame=212) |
| 07 · Dimensional portrait cluster · 213–253 | PASS | 10.35 → 6.79 | Individual disk tracks carry the early components into the settled 13-disk layout through f226–227. At f242 and f249 the major centers and component count correspond. The independently authored portrait expressions and final perimeter still differ. [f213](evidence/final-comparison/index.html?frame=213)–[f253](evidence/final-comparison/index.html?frame=253) |
| 08 · Cluster wipe and profile reveal · 254–281 | FAIL | 7.95 → 7.32 | Measured islands restore parts of the outgoing mosaics and a padded streak brings Lisa in at f258. The visible remnants still have different edges and the profile label fragments at f262–264 resolve differently. [f254](evidence/final-comparison/index.html?frame=254)–[f264](evidence/final-comparison/index.html?frame=264) |
| 09 · Profile push · 282–312 | FAIL | 12.44 → 5.86 | The green disk and Ella’s falloff use separate tracks. At f290 the outline on Lisa’s chip is more uniform. At f300 the source’s facial expression and Ella’s fading edge differ from the blended sprites. [f290](evidence/final-comparison/index.html?frame=290)–[f300](evidence/final-comparison/index.html?frame=300) |
| 10 · First phone entrance · 313–335 | FAIL | 12.40 → 9.41 | The first visible hull bottom and the later rim are closer after fitting the clipped edge. On f316–319 the source keyboard is already sharper and vertically registered differently while the candidate streak persists. [f313](evidence/final-comparison/index.html?frame=313)–[f327](evidence/final-comparison/index.html?frame=327) |
| 11 · Suggestion and controls · 336–359 | PASS | 17.11 → 14.24 | There is no suggestion at f335. Both blue bubbles appear separately at f336. Measured boxes preserve their spacing through the push, and the first No and Send? controls appear below the lower bubble at f341 and f343. Both controls detach below the bubble at f359. [f336](evidence/final-comparison/index.html?frame=336)–[f359](evidence/final-comparison/index.html?frame=359) |
| 12 · Isolated suggestion and pointer · 360–396 | PASS | 6.25 → 6.24 | The detached controls sit under the suggestion at f394, and the pointer reaches the Send? capsule from below. [f394](evidence/final-comparison/index.html?frame=394) |
| 13 · Calendar entry · 397–429 | PASS | 6.07 → 5.48 | The lower calendar band is visible at f397 with the suggestion still above it. Appointments rise through consecutive frames; by f403 the calendar has replaced the suggestion. The padded cursor follows the measured turn around f408–415 and lands beside the lower appointment. [f397](evidence/final-comparison/index.html?frame=397)–[f429](evidence/final-comparison/index.html?frame=429) |
| 14 · Violet appointment drag · 430–451 | PASS | 4.92 → 4.92 | At f435 the violet appointment remains above cyan through their overlap. The grid stays registered. [f435](evidence/final-comparison/index.html?frame=435) |
| 15 · Cyan appointment drag · 452–473 | PASS | 4.76 → 4.76 | At f460 cyan sits below the violet appointment on the same calendar grid. [f460](evidence/final-comparison/index.html?frame=460) |
| 16 · Calendar mosaic and app entry · 474–486 | FAIL | 6.41 → 4.45 | The ring tile leads at f478, then red and blue enter. The source still has a stronger violet block behind the ring and different holes in the outgoing calendar grid. [f475](evidence/final-comparison/index.html?frame=475)–[f479](evidence/final-comparison/index.html?frame=479) |
| 17 · App orbit · 487–612 | FAIL | 7.12 → 4.51 | Individual centers and depth changes keep the four glyphs readable. At f536 and f612 the dark tile has different scale and edge softness, and the red and blue artwork and overlap edges still differ. [f536](evidence/final-comparison/index.html?frame=536)–[f612](evidence/final-comparison/index.html?frame=612) |
| 18 · App exit · 613–623 | PASS | 6.75 → 3.79 | Separate tile paths and a fitted glow move downward together. Motion streaks persist on the last occupied frame f621, and f622–623 are blank. The tile edge blur differs locally. [f613](evidence/final-comparison/index.html?frame=613)–[f623](evidence/final-comparison/index.html?frame=623) |
| 19 · Second phone entrance · 624–647 | FAIL | 10.52 → 9.46 | The visible bottom at f624 and the detached pointer are much closer. At f626–632 the candidate body and keyboard are streaked longer, and the settled bottom and keyboard proportions still differ. [f624](evidence/final-comparison/index.html?frame=624)–[f647](evidence/final-comparison/index.html?frame=647) |
| 20 · Follow up buttons and push · 648–674 | PASS | 15.43 → 12.00 | No and Yes become visible on f648 and f650. In the sampled fast approach, the chip and fitted pointer follow separate measured paths, with the tip just above the composer at f665–667 and nearly at Yes by f674. [f648](evidence/final-comparison/index.html?frame=648)–[f674](evidence/final-comparison/index.html?frame=674) |
| 21 · Yes contact and withdrawal · 675–695 | PASS | 17.27 → 13.86 | The decoded tip has zero gap to Yes at f675. Rim and interior offsets follow the late retreat and keep the chip and tip registered through f695. The keyboard keys and surrounding bubble type still differ. [f675](evidence/final-comparison/index.html?frame=675)–[f695](evidence/final-comparison/index.html?frame=695) |
| 22 · Closing badge entrance · 696–716 | FAIL | 4.06 → 3.36 | Width and height are separately fitted from the first squash to the held badge. The held center card and heart proportions still differ visibly at f703–708. [f696](evidence/final-comparison/index.html?frame=696)–[f708](evidence/final-comparison/index.html?frame=708) |
| 23 · Closing copy and wash · 717–765 | PASS | 4.95 → 4.23 | Each word has separate measured bounds and opacity. ‘The’ reads first at f717, ‘iMessage’ enters on f741, and the complete second line is in place by the final set pose. Wash falloff is approximate. [f717](evidence/final-comparison/index.html?frame=717)–[f765](evidence/final-comparison/index.html?frame=765) |
| 24 · Closing fade and black hold · 766–777 | PASS | 4.63 → 4.64 | Both movies reduce exposure into the final black frame at f777 and share the 40 ms final hold. [f766](evidence/final-comparison/index.html?frame=766)–[f777](evidence/final-comparison/index.html?frame=777) |

## Iterations and reusable changes

The original 19 failures were reworked in groups and checked in decoded probes before merging repairs into complete exports. The full-film RGB averages from the original benchmark and three intermediate builds were 8.85, 7.83, 7.42 and 7.22. The next benchmarks measured 7.13 and 7.00 before the inbox pullback and handset exposure refinements. The same checks file stayed in use.

- The two missing onsets came from scene geometry and tween opacity. The suggestion and calendar now have positive visible coverage at f336 and f397. The transition layers remain independent. [Suggestion probes](evidence/suggestion-probe.jpg) · [Calendar and follow-up probes](evidence/calendar-and-contact-probe.jpg)
- Independent row, portrait, tile, keyboard and word measurements replaced several shared paths. The phone hull can continue using its side walls for scale while registering the on-screen controls against an interior feature. [Portrait probes](evidence/portrait-transition-probe.jpg) · [Closing probes](evidence/closing-probe.jpg)
- The calendar pointer shrank at sharp angles because the renderer rotated it inside a tightly cropped image. Transparent padding preserves its outline, and the angle and tip are fitted independently. Testing only the starting and ending pointer poses missed that defect. [Calendar turn](evidence/final-comparison/index.html?frame=408)
- The reusable skill now calls for identifiable repeated features, an interior landmark when the hull is cropped, per-word ink bounds, enough space for a rotated or blurred layer, and color and opacity samples across both light and dark areas. [Updated visual review](../../codex-trial/skill/imessage-motion-recreation/recreate/VISUAL-REVIEW.md)

The remaining material, artwork and mask differences are visible in the decoded comparison. The supplied reference is a flattened film. This project uses independent art and compositing, including the previously generated head sprites, and has no original editable portrait, handset or effects layers. The review uses the authored visual criteria and records pixel equality independently. The film still falls short of the requested one-to-one match.

## Reproduce the review

From the workspace root, set `REF` to the supplied original MP4. Use Python with Pillow and NumPy, plus FFmpeg. The export command renders the editable project into a new directory. The comparison below checks the delivered MP4.

```sh
D=sidehoe-skill-trial/repair
S=codex-trial/skill/imessage-motion-recreation/recreate
B=sidehoe-skill-trial/repair-review
"$D/project/export.sh" /tmp/sidehoe-check-export /tmp/sidehoe-check-frames
python3 "$S/recreate.py" compare "$REF" "$D/exports/sidehoe.mp4" \
  --checks sidehoe-skill-trial/evidence/checks/diagnostic-settings.json \
  --out /tmp/sidehoe-check-comparison --pairs
python3 "$S/recreate.py" verify-review "$D/exports/sidehoe.mp4" \
  --plan "$B/review-plan.json" --review "$D/evidence/visual-review.json" \
  --comparison "$D/evidence/final-comparison/report.json" --scoped --out /tmp/sidehoe-check-acceptance.json
```

The two review commands return exit 1 while the recorded visual failures remain open. [Project instructions](project/README.md)
