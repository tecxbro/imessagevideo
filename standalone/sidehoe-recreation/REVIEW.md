# Sidehoe recreation review

The revised film runs **31.120 seconds**, with 778 pictures at 25 fps. The first finished export took **11 min 26 s** from measurement kickoff. The first-pass review was frozen before any edit. [Run timing](first/elapsed.md) · [Router result](route.json) · [First-pass review](first/FIRST-PASS.md)

## Handoff

| Item | First pass | Revised |
|---|---|---|
| Finished H.264 and original stereo score | [MP4](first/sidehoe.mp4) | [MP4](revised/sidehoe.mp4) |
| Silent picture | [MP4](first/picture.mp4) | [MP4](revised/picture.mp4) |
| Portable source | [ZIP](first/source.zip) | [ZIP](revised/source.zip) |
| Frame-indexed review | [Overview](first/visual/overview.jpg) · [Native checker report](first/skill-check/report.json) | [Overview](revised/visual/overview.jpg) · [Native checker report](revised/skill-check/report.json) |
| Resolved event and cue map | [Observer map](first/observer-events.json) | [Observer map](revised/observer-events.json) |
| Authored audio | [Score](first/sound/score.wav) · [Foley](first/sound/foley.wav) | [Score](revised/sound/score.wav) · [Foley](revised/sound/foley.wav) |

[Source ledger](SOURCE-LEDGER.md) · [Locked acceptance checks](ACCEPTANCE.md) · [Native check inputs](checks.json) · [Full frame map](revised/skill-check/frames.csv) · [Packaged review evidence](review-evidence.zip)

Pillow is the single picture renderer. It lets the cursor, phone plate, two translucent calendar appointments, clipping, text, and end-card exposure be authored independently on the native integer frame clock. FFmpeg encodes the rendered RGB pictures and muxes the separately authored sound. A procedural scene fits the layered interaction and orbit better than a montage of sampled stills. Text and timeline live in JSON. UI components are reusable drawing code with original vector artwork and a bundled Inter font. The Observer resolver validates the metadata via a projection of the procedural scene. The portable project is a Python editor-in-code workflow.

## First and revised against the same checks

| Check | First pass | Revised |
|---|---|---|
| Decoded clock and raster | Pass. Exact 778/778 starts and sample spans, 2000×2000, no crop or rotation | Pass. Same exact clock |
| Yes cursor at source-contact frame 675 / 27.000 s | 76.7 coded px from capsule, no overlap through the evaluated hold | 6.7 px at 675, overlap at 676 / 27.040 s, within the two-frame limit |
| Yes capsule position at 675 | Top 56.6 px above source | Top matches at measurement precision. Right edge is 13.3 px inside the source edge |
| Follow-up group frames 661–695 | Mean full-frame RGB MAE 21.90 | 19.15 |
| Yes ROI, limit 25 | Worst 23.03, pass | Worst 21.24, pass. The separate contact gate detects the interaction failure |
| Calendar | Appointment checks pass. Red day disk fails by 80.0 px at 420 and 60.1 px at 427. The first drag pointer loses alignment | Same day-disk and pointer misses |
| Whole-frame RGB MAE, limit 18 per picture | 125 frames over. Worst 40.56 at 134 | 121 frames over. Worst 40.56 at 134 |
| ROI thresholds | 11 pass, 12 fail | 11 pass, 12 fail |
| Closing hold and fade | Finished copy visible at 765. Mean RGB within 9.49 levels during fade. Black 777, full 40 ms | Same. End-copy region still fails with worst 30.45 against 27 |
| Sound and picture lock | 48 kHz stereo, 31.120 s, 22 cue anchors. Decoded picture hashes equal between silent and scored versions | Same. Audio, silent export, and mux reproduced byte-for-byte from the extracted ZIP |

Native checker MAE measures RGB differences at coded resolution. The target diagnostic measures a pastel mask and dark cursor component at 600 px scale, reported in coded pixels in 3.3 px increments. At 688 its mask misses part of the desaturated Yes chip. The image shows the cursor on the chip. The MP4s contain original, quiet audio with a measured peak of −18.2 dBFS and mean of −35.9 dBFS. Verification was by stream, decoded level, and cue samples. Listening was outside the verification performed.

## Largest misses and when they were detectable

| Frame and source PTS | Visible miss and likely cause | Earliest evidence or scope decision |
|---|---|---|
| **62 · 2.480 s** | Scroll is about two rows behind during the fast sweep. Sparse interpolation followed arrival and settled holds while missing the middle of the acceleration. | Track one named row through 53–69, plus the fixed sibling spacing. Lock its vertical samples and blur length before drawing the list. |
| **134 · 5.360 s** | Handset arrives lower, with a thin authored rim and reduced optical distortion. 54.20 worst regional MAE, largest of the pass. The first cut inherits a much lighter handset design and a single blur. | Measure both hull corners, top edge, and middle badge center at 133–138. Decide whether the chromatic fringe is part of motion acceptance before implementing a generic blur. |
| **201 · 8.040 s** | Headline is lower and smaller, hearts sit farther outside, and the wash is stronger. 41.97 regional MAE. One shared title layout and synthesized gradient miss the source line spacing and heart relationship. | Record each line’s first legible bounds plus the heart envelope at 185, 195, and 201. Sample blank gradient patches on the same frames. |
| **255 · 10.200 s** | Original portraits and lavender islands remain larger and sharper. Wipe gaps open later and follow longer horizontal bars. 44.91 regional MAE. | Lock the mask rectangles, directional streaks, and residual group offset at 254–258 on a six-frame strip. Choose intentional portrait stylization separately from wipe geometry. |
| **308 · 12.320 s** | Lisa is larger and more centered; Ella remains too visible. 40.55 regional MAE. Per-card opacity and local translation are approximated by a simple shared push. | Measure both portrait disks, crop boundary, and chip together at 289, 300, and 308, preserving relative offset and right-edge fade. |
| **394 · 15.760 s** | The pointed tip reads near the upper-right of Send? rather than approaching from below. The group is lower and the cursor is undersized. 36.29 worst approach MAE. | Track outgoing bubble corners and the Send? hitbox, then measure the pointer’s tip and shaft separately at 382–396. |
| **420 / 437 · 16.800 / 17.480 s** | Early day center is 80 px too far right. The pointer dips below the cards earlier than the source after the first drag. Appointment top edges generally match. The early ruler width was inferred from its left edge and a fixed right gutter. | Sample both grid edges and the day center during entry, then the four corners of the active appointment and pointer tip during each drag. |
| **675 · 27.000 s** | First-pass cursor misses Yes. The phone transform puts the capsule 56.6 px too high while an independently keyed stage cursor stops below it. | Place the source cursor tip and capsule bounds on the same decoded frame as the hull landmarks. Use a capsule-local landing anchor before building the camera push. This is the one revision made. |
| **765 · 30.600 s** | Both renders preserve the copy and black endpoint. End wash is denser and deeper on the right and type proportions differ. The final hold ROI fails. | Measure both copy line bounds and use several background patches across the frame to fit the wash before authoring the fade. |

[Scroll, handset, title, mosaic and profile frames](evidence/boards/largest-misses-a.jpg) · [Send and calendar frames](evidence/boards/largest-misses-b.jpg) · [Yes comparison](evidence/boards/yes-contact.jpg) · [Both endings](evidence/boards/both-endings.jpg)

## Interaction and ending review

The two visual folders carry source and render crops at **every frame** in 22 windows. The full decoded RGB CSV covers the intervals between them. I inspected the overview, the onset and settlement strips, both calendar moves, both pointer contacts, and the final fade.

| Passage | Consecutive evidence | Observed in the exports |
|---|---|---|
| Opening, scroll and identity | 0–12, 43–69, 98–118 | Pinned row and note assemble; initial scroll lags; wordmark builds beneath the badge. |
| Assistant, title, and portrait cluster | 130–165, 174–187, 210–226, 251–273 | Oversized phone, typed lines, and cluster-to-profiles order read. Optical entrance, heart positions, and mosaic masks differ. |
| Lisa and Sofia | 282–313, 313–342, 334–360 | Green chip is accented; isolation and phone entry occur in order. Suggestion and options mount while handset pushes in, then the group detaches on white. Opacity and placement differ. |
| Send and calendar | 382–406, 400–423, 427–443, 447–462, 470–487 | Approach, overlap, two moves, and mosaic resolve. Send’s contact side, grid tracking, and first drag cursor fall short. |
| App orbit and phone return | 529–590, 613–634 | Red, dark, rings, blue foreground order achieved, with approximate depth and path. Drop, white break and second phone remain distinguishable. |
| No/Yes and closing cut | 644–659, 659–689, 690–713 | Actions appear separately, then the camera pushes. First misses Yes. Revision reaches it at 676 and follows the tint response. There is no confirmation bubble in the reference or either export. |
| Closing type and black | 716–757 and 755–777 | Line sequence stays readable into the full hold. Both fade from 766 with exact terminal black at 777. |

## Revision and portability proof

Only the follow-up approach was repainted. The local change corrects the vertical registration of the follow-up plate using the capsule landmarks, then transforms the cursor from a stage-space approach into a relative target corner on the Yes control. The lossless frame cache differs exactly on 661–695. H.264 interframe encoding changed 8 additional decoded hashes near that window. Both exports retain the same exact final black frame. [Lossless scope](evidence/cache-scope.csv) · [Encoded scope](evidence/encoded-revision-scope.json)

I extracted the revised ZIP into an empty directory. The clean render ran under a macOS sandbox that denied network access, the source movie path, and the repository path. The new picture, mux, three audio WAVs and event map match the delivered versions byte-for-byte. An isolated edit changed **Yes → Go!** and moved the contact anchor **675 → 681**. The decoded frames show both changes. The confirm cue moved 11,520 samples, exactly six frames at the project rate. [Clean reopen hashes](evidence/clean-reopen.json) · [Edit proof frames](evidence/edit-proof/edit-proof.jpg) · [Edit proof clip](evidence/edit-proof/proof.mp4)

**Reusable rule.** Measure a pointer tip in its target’s local coordinates through approach, contact and settlement whenever the camera or target is moving. On a second unseen film, lock these anchors before rendering, including one adjacent camera landmark. Decode the consecutive window and require contact within two source frames. Then shift the event six frames and resize the target in a copied project. The tip should still land inside the new control at the moved time and the cue should move by the same sample count.
