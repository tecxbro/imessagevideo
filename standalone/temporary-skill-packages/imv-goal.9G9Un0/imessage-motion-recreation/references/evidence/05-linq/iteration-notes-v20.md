# Linq V20 — close two failures found by full-master review

The full V19 master improved its 1,458-frame mean MAE to1.322315, but visual review of all 24 separated peaks rejected propagation. A new dark backing halo appeared around the Cash plus control at 828, and the restaurant exit1145 clipped the price row and omitted Find a table. Numeric improvement alone was insufficient.

## Cash: separate the real panel from a false fade

At828 the original parent alpha .96638655 turned the static17–19-gray panel material into26–27 over white, while source remained19. The native control backing had correctly recovered19 locally, making the inaccurate surrounding plane visible as a dark ring. Correct the panel alpha and recalibrate native control shades; keep the native camera, amount state, glyph geometry and single static plus detail.

The first continuous source/material median-ratio fit removed the ring but regressed 24 held states. Regional attribution at 820 showed that +.14351 global error came mainly from the flat panel(+.12738), not the amount(+.00866) or plus(+.00074). Source/old/new pixels were19/19/18 at many ordinary plane locations.

Native renderer probes identify the8-bit premultiplied-floor response:

`displayed = (255 - alphaByte) + floor(material * alphaByte / 255)`

The independently calibrated read-only model predicts existing flat pixels with .000064-gray mean error across 65 states. Exclude independent foreground actors from the static plate mask. Quantized L1 candidate selection retains original alpha on ties. Control gray/stroke uses the same discrete response to retain displayed shades; an unnecessary continuous recompensation would introduce another1-gray shift.

Parent's frozen release is `outputs/05-linq/root-cash-plane-v20/release.json`; helper SHA256 `bb1fc04f7668c6ced347a3cc3487f69804b8a6818a928c4b95600ce6da2439e1`, measurements SHA256 `4deb5ba7d49e066e990497b4f6d03b7b1650e974703a0d27ecb6b1edb3da30a7`. Exactly32 native states improve:778–780,782,787–810,828–829,833–834. All 35 other controls remain pixel-identical. Continuous prototype data stays separate and is not applied.

## Restaurant: restore the complete static lower UI

The old bitmap's content cuts the price line before its 860px physical edge. A simple bottom append restores only the second line and Find a table, leaving the malformed first line. Recover one static component from the empty world820 gutter through 1000, using the two genuine original views1145/1146 projected into the same unchanged document coordinates. Undo the existing parent opacity once; animate the single static component only with the existing camera/opacity. Internal UI text is explicitly bitmap.

The full native check limits the actual visible component to1144–1148; a faint synthetic ghost at 1149 is rejected. All five frames improve and controls 1143/1149/1150 are pixel-identical. Payload SHA256 `8b0612250438c1a64c0e3bfe1bf4741c3eeaf3fe9e88dca62e458e4b7b164075`, with source and pixel bounds in `restaurant-bottom-v20-release.json` and provenance beside it. Existing document, photo rail and camera are unchanged.

## Freeze and propagate from actual baselines

Compose both releases once from immutable19. Verify the complete applied Cash subtree against the independently accepted branch by native properties and asset bytes. Preflight 368 assets with zero issues; validate 2,418 unique IDs. Full-scope proof leaves all 1,421 states outside the37-frame union identical. Snapshot `outputs/05-linq/final-v20/scene.json`, SHA256 `658184bb8d05c50633f37fa0ef0bfd8a943773076f249c7e0dbf02991e6e93c6`, preserves every property/material byte.

G actual19 refreshes 37; HTML actual18 needs 184; Remotion actual17 needs 351 including625; native actual13 needs 651 capture states(exact 648, with206–208 conservative guards). Run final PC709 encoding before the full1,458-frame scan and 24 native peak review. Only an accepted source/visual gate permits other method propagation. Then compare all 1,458 retained G/R frames separately from source fidelity and verify the older625 cached truncation is replaced.

Remaining photo, board and gallery material/resampling/optics differences stay explicit. Neither metrics nor renderer parity is a percentage of perfection, and exact 1:1 is not claimed.

## Final capture verification and minimal recovery

G20 passes all 1,458 source samples: mean MAE 1.310951, maximum 5.212960 at unchanged restaurant1100. All37 changed encoded frames improve; all24 separated peak previews are visually reviewed again. The final encoded828 has no broad halo;1145 contains the restored rows. The source gate permits method propagation with remaining material/resampling/camera/optics differences recorded, not a100%claim.

R20's complete native-cache comparison finds a single all-white607. Preserve the bad PNG/log/raw report. It is not a chunk boundary. A fresh606/607/608 same-process probe matches the exact original broad runtime chunk(174 frames,5,885,710 bytes) with SVG proofs.606/608 are exact guards;607 is populated with small image/text-edge raster differences(.001811/max24). No original cause is established. Only the genuine fresh Remotion607 is promoted, with all other1,457 cache file stats unchanged; no GSAP pixels are copied. Re-PC-encode and rerun all-frame parity. The earlier625 cached truncation is a separate incident and is also repaired.

Final R/G: mean .000537862, max channel49,1,366 pixel-identical frames. H/G: mean .000536407,max49,1,372 pixel-identical. All86 H/G differences also exactly match R's pixels. The initial H zero-pixel assertion is retained as a raw observation and replaced by an explicit measured material-anomaly guard; pixelIdentity remains false. This records real small raster differences without hiding a material blank. Allfive final sidecars identify immutable20 and full-range-bt709-v1. `verification/05-final-v20-release.json` binds all picture hashes and evidence; `quality.md` gives the readable fidelity/editability limits. Parent's final source/encoded/audio/package audit remains separate.
