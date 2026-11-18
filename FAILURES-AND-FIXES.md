# Failures, fixes and lessons used in the final build

These are documented development failures and the accepted improvements behind
the current production code. They are not new visual fixes made during this
completeness audit. The linked evidence keeps the measurements, controls and
limits. Read [FINAL-PRODUCTION.md](FINAL-PRODUCTION.md) for the code to use now;
you do not need to replay older builders to render the accepted scenes.

| Failure | Diagnosis and accepted change | Evidence and result |
|---|---|---|
| Poke's restaurant selection was twelve frames late despite modest full-frame error. | Blue/check overlays `p0249`/`p0250` retained `start: 21.5`, first visible at645 rather than source633. A separate trial moves both to `633*1001/30000`; add automatic local event-onset review before accepting exports. | [Trial and reports](trials/poke-selection-onset/): automatic detection measures633→645 (+12, late) before repair and633→633 (0, pass) after. Other heuristic flags remain; frozen scene, movies and audio are unchanged. |
| Later Remotion chunks were blank although the scene data existed. | Only `inputProps` changed; the selected Composition retained stale resolved props. Update both for each exact frame chunk, preserving the full scene as the authority. | [Playbook, transport lesson](skill/imessage-motion-recreation/references/reconstruction-playbook.md#L109); [full 1,360-frame Remotion/GSAP check](skill/imessage-motion-recreation/references/evidence/verification/remotion-v13-all-frames-parity.json): mean SSIM .999742. This measures renderer parity, not identity to the source. |
| Repeated Remotion browser launches timed out after successful captures. | Reuse one explicitly owned browser across chunks and close it in `finally`, instead of launching another browser for each chunk. | [Browser reuse controls](skill/imessage-motion-recreation/references/evidence/verification/remotion-browser-reuse-parity.json): all four recorded controls remained pixel-identical. |
| A Linq cached frame had white truncation despite good aggregate similarity. | A fresh render of the exact frozen scene matched the expected renderer. Refresh the bad cached state without changing geometry. The original cache defect's cause was not proven. | [Playbook, isolated outliers](skill/imessage-motion-recreation/references/reconstruction-playbook.md#L118) and retained [Linq diagnostic evidence](skill/imessage-motion-recreation/references/evidence/05-raster-parity-625/diagnostic.json). Do not label an unproven cause as a renderer or decoder bug. |
| Mini Apps briefly became flat rectangles in Pillow. | An extreme wrapper scale and inverse child scale collapsed the intermediate raster to 1×1 before the transforms cancelled. Condition local coordinates before rasterization, then use bounded supersampling. | [Coordinate-conditioning release](skill/imessage-motion-recreation/references/evidence/pillow-coordinate-conditioning/release-report.json): mean error over 53 affected frames fell from 18.7238 to .6007; outside controls stayed byte-identical. |
| Motion Canvas text moved vertically or changed shaping under transforms. | Removing DOM leading solved one error; transformed SVG font shaping needed font-size/metrics at the full transform's RMS scale with a compensating inverse paint transform. Test real rotated/scaled ancestors, anchors, fallback and blur. | [RMS release evidence](skill/imessage-motion-recreation/references/evidence/motion-canvas-text-inventory/rms-release-report.json) and [playbook](skill/imessage-motion-recreation/references/reconstruction-playbook.md#L120). The scene geometry was not changed to hide the engine discrepancy. |
| Shadows leaked through fading cards; a shadow-plus-blur revision made another control worse. | Applying opacity independently exposed the shadow through opaque content, while a world-space shadow inside a local Gaussian composite double-scaled its kernel. Composite shadow/content locally, then blur and apply the shared outer fade. | [Shadow/opacity release](skill/imessage-motion-recreation/references/evidence/shadow-opacity/release-report.json): combined-fixture MAE .716755 → .164742; retained neutral/opaque controls were unchanged. |
| A mathematically smoother Linq dark plane regressed held frames. | Continuous alpha fitting ignored Chromium's byte-quantized premultiplication. Fit the actual 8-bit compositing behavior, keep the original on ties and check each changed state. | [Quantized material release](skill/imessage-motion-recreation/references/evidence/root-cash-plane-v20/release.json): all 32 changed states improved, 35 other controls matched; mean source MAE 1.562636 → 1.342749. |
| Near-white colors changed between native captures, FFmpeg and Chrome. | A range flag alone was insufficient. Use coherent full-range BT.709 primaries, transfer and matrix metadata, and validate in both the decoder and real player. Preserve original capture hashes. | [Encoding experiment](skill/imessage-motion-recreation/references/evidence/encode-range/RECOMMENDATION.md): at frame 535, FFmpeg error to the native capture fell from 1.0700 to .1158 while the tested Chrome error also improved. |
| A safe lossless music mix overshot after AAC encoding. | The codec introduced peaks absent from the PCM. Compare the encoded outputs, increase music/full-mix AAC to 256 kbps and avoid forcing sparse UI effects to a music loudness target. | [Audio execution log, step 10](skill/imessage-motion-recreation/references/ui-audio/execution-steps.md#L12): 112 kbps reached +.80 dBTP; 256 kbps measured −2.47 dBTP on the same safe PCM. |

MAE values above are mean RGB error on a 0–255 channel scale unless the source
report defines a narrower control. SSIM is a similarity statistic. Neither is
a percentage of perfection. Historical releases can identify earlier engine
fingerprints; the current accepted renderer files and movies remain separately
pinned by the production registry and audit.

## What to do before retrying

1. Keep the input scene/asset hashes and the exact native frame or event time.
2. Determine whether the defect is geometry, UI state, typography, renderer,
   cache, encoding/player interpretation, or sound timing. A warning log is not
   proof that the producer failed, and a finished encoder is not proof of quality.
3. State the evidence-backed cause or bounded hypothesis, then change one causal
   variable. Do not hide a renderer problem by copying another engine's pixels.
4. Inspect the entire affected lifecycle plus unaffected control frames. A single
   good held frame or global average can miss a blank transition.
5. Promote only the actual newly rendered result and its matching evidence.
   Preserve the original source, accepted data, provenance and explicit limits.

## Remaining limits, not claimed fixes

- Poke's restaurant selection appears at source frame 633 but at accepted GSAP
  frame 645. The UI sound was intentionally aligned to the delivered picture at
  645; the 12-frame graphic discrepancy was not corrected by that audio work.
  See [audio step 17](skill/imessage-motion-recreation/references/ui-audio/execution-steps.md#L19).
- Figma Motion/export remains unvalidated. The five actual code renderers are
  the completed production methods.
- The final source comparisons have nonzero residual error. A complete upload
  and correct keyframe preservation do not certify exact visual identity.

The earlier development logs are evidence for these lessons. The normal editing
and rendering path uses only the accepted scenes, current engines and their
declared inputs, as shown in [the final-code guide](FINAL-PRODUCTION.md).
