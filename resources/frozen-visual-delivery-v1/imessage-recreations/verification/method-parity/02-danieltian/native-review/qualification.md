# Source02 final19 renderer qualification

Read-only review of the lowest encoded method-parity frames: Pillow528, MotionCanvas890, Remotion/HTML854. All five masters and cache sidecars bind canonical SHA`729c783aa3a13f87c2e61d9a409a492adff9d27208ae6e092c3edfc2c2e8abee`; movie hashes stayed unchanged during acquisition. No scene, master or cache was written.

| Frame/method | Decoded RGB MAE vs G19 | Lossless PNG MAE vs G19 | Error energy on edges | Pixels>8 on edges |
|---|---:|---:|---:|---:|
|528Pillow|.301113|.225135|93.97%|99.75%|
|890MotionCanvas|.258197|.017433|80.23%|99.52%|
|854Remotion|.266213|.0000865|78.59%|99.19%|
|854HTML|.266213|.0000865|78.59%|99.19%|

The edge mask uses G19decoded luma Sobel gradient>8, dilated2pixels. Foreground interior excludes these edges; background excludes3pixels around foreground. Full measurements, source comparisons, masks and PNG/movie hashes are in `metrics.json`.

Pillow528: the complete search field/magnifier/copy, all three Lyft/Airbnb/Resy capsules, original logos and three green checks are present. Native-sized source/G/Pillow crop confirms matching state and layout. Differences concentrate on glyph/capsule/check/logo edges, consistent with native coverage/resampling plus small tone-rounding and encoding residuals. Foreground-interior MAE1.288 and background.0075 mean this is not described as exclusively an edge or encoding difference. Source-to-Pillow MAE.4811 versus source-to-G19.3617; no omitted asset or literal-copy state was observed.

MotionCanvas890: the cabin photograph, interior title/details, caption panel, Airbnb badges, floating multi-app header, outgoing budget bubble and “How about this one?” reply are complete. Lossless method difference is only.0174, while decoded difference is.2582, so separate encoding magnifies small image/vector sampling differences. Source-to-MC MAE1.7840 is slightly lower than source-to-G19 at1.7958; this is a worst *method-parity* frame, not evidence of worse source fidelity. Fine photo/rim/edge material differences remain; no missing scene layer was observed.

Remotion/HTML854: all card artwork and text, Resy/Budget, floating header, budget bubble and Airbnb provider state are complete. Lossless difference.0000865 is negligible compared with decoded.2662; this supports an encoded residual over nearly identical native pictures, rather than a layout/timing/asset omission. Source-to-method1.0023 and source-to-G19 1.0000 are close. Small interior/flat-background byte residuals remain as shown in the metrics, so these outputs are not called pixel-identical.

These samples qualify the reported method minima as resampling/coverage/encoding residuals with complete observed artwork. They do not certify full source identity or100% perfection. Existing source19glass/backdrop, silhouette/pose, original-art/AA and source-coding qualifications remain unchanged. Initial review-script parsing failed before acquisition because a compressed conditional lacked a space; it was replaced by an explicit branch, compiled, and the successful acquisition completed without touching protected inputs.
