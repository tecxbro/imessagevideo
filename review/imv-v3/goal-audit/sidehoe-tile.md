# Sidehoe blue “31” tile

The frozen project has three independently demonstrated defects in this passage. The tile is too low on entry into the exit move, its registered face lacks the pinched sides and lit rim, and its blurred blue exposure persists too high at the bottom after the source tile has moved out. The differences are present in the lossless render and survive H.264. The matching blank at f622 only verifies the next state. [Original visual audit](../../../../sidehoe-skill-trial/repair/reviewer-audit/AUDIT.md#L11-L20)

## What the local probe isolates

I decoded source and existing full-mux frames 612–623 in display order at the original 2000×2000. Source uses 25 fps, time base 1/60000, and 2,400 ticks per frame. f614–621 is 24.56–24.84 seconds. Fresh renderer output matches all 12 frozen lossless cached pictures exactly. For analysis I upscaled the editable 1000×1000 lossless pictures with Lanczos and used the existing native half-open ROI `[742,1260,1245,1790)`. The paired local encodes use the project’s 25 fps, 2000×2000 scale, x264 veryfast/CRF 16 and yuv420p. The existing full mux and these short encodes have separate measurements. [Original crop definition](../../../../sidehoe-skill-trial/repair/reviewer-audit/targeted-crops.json#L41-L52) · [Prior material probe](../upstream/sidehoe-probes.py#L45-L63)

**Registration-only alternative.** I moved only `blueOrbit` Y on f614–618 by −12, −10, −7, −20 and −22 final-display pixels. The offsets align the centers of bounded source and candidate blue extents. This is an in-sample diagnostic, with art, scale, X, blur, and opacity held constant. It improves all five corrected frames. In the original crop the mean source RGB MAE falls from 15.748 to 13.456 lossless, and from 16.267 to 14.040 in the paired local encodes. Lossless controls f612–613 and f619–623 are pixel-identical before and after the alternative. Encoded guard differences in the larger phase ROI are at most 0.506 RGB MAE in the short encodes. f622 and f623 are pixel-identical even after the local encode.

| Frame | Frozen lossless | Existing full mux | Registered lossless | Frozen → registered local encode |
| --- | ---: | ---: | ---: | ---: |
| 614 | 17.16 | 17.68 | 13.73 | 17.68 → 14.28 |
| 615 | 17.32 | 17.86 | 14.52 | 17.87 → 15.09 |
| 616 | 15.10 | 15.71 | 14.28 | 15.71 → 14.91 |
| 617 | 15.88 | 16.35 | 13.44 | 16.36 → 14.04 |
| 618 | 13.29 | 13.71 | 11.32 | 13.70 → 11.88 |
| 619 | 11.40 | 11.93 | 11.40 | 11.94 → 11.92 |
| 620 | 10.41 | 10.86 | 10.41 | 10.86 → 10.87 |
| 621 | 4.97 | 5.57 | 4.97 | 5.59 → 5.59 |

**Registered material remains different.** At f614 blue top and bottom align within one pixel after the Y correction. The source retains a 398 px width at 40% of visible tile height and opens to 423 px at 80%. The registered tile stays 412 px wide at both rows. The isolated source highlight near x980–1019/y1249–1251 has median RGB (208,237,251), compared with (220,210,252) in the registered same-coordinate crop. Source blue at 73% height in the glyph-free cheek is (87,162,249), versus (66,140,244). The renderer draws a straight-gradient rounded square, hard-edged top band and Inter “31”. The earlier independent curved artwork made the rim visibly dark and improved f614–617 but regressed f618–619. Its six-frame encoded mean improved 15.540 to 15.043 while f619 worsened 11.916 to 13.043. This leaves silhouette, rim, face gradient and numeral outline open. [Frozen tile painter](/tmp/imv-goal.9G9Un0/sidehoe-clean-project/artwork.py#L248-L266) · [Prior probe measurements](/tmp/imv-upstream.tH7Joz/sidehoe-proven/probes.json)

**Late exit needs its own pose and blur check.** The expanded native phase ROI `[742,1110,1245,2000)` keeps the near-bottom tile in scope. A blue landmark requires `B−R > 48, G−R > 20, B−G > 12, R < 190`. At f620 its top is y1734 in the source and y1687 lossless/y1686 in the mux. At f621 the source has 19 isolated matching pixels and no coherent blue landmark, while the frozen lossless still has 41,418 and the mux has 42,873. At f622 all three have zero. Source support is clipped at the bottom during the exit. These observations identify visible exposure, with underlying center, blur and opacity still separate unknowns. The renderer starts vertical blur at f617, ramps it through f621, and controls opacity on a separate f619–623 ramp. An early Y correction does not establish the late pose or optical match. [Frozen exposure and blur](/tmp/imv-goal.9G9Un0/sidehoe-clean-project/render.py#L896-L928)

The independent scratch contains the [native phase sheet](/tmp/imv-sidehoe-tile.q9Ocuh/contact.png), [per-frame measurements](/tmp/imv-sidehoe-tile.q9Ocuh/metrics.json), and [Y-only probe](/tmp/imv-sidehoe-tile.q9Ocuh/tile-pose-probe.py). Source SHA-256 is `f821bb58cbdb265a75d572616d0da723e9cfb6de31e3db5f8a17d94dc15b5327`. Frozen scene SHA-256 is `866937869bfd7ba57ca24820320f9091b3427e4f7e0850c0637eacd3f14aa221` and existing full-mux SHA-256 is `1703ce84a2215c3414a3a98eeeeb9744184d7427b4a7863d5d858d034fd607bf`. This targeted result leaves the material and exit criteria open. No change was promoted to the project, accepted film or skill.
