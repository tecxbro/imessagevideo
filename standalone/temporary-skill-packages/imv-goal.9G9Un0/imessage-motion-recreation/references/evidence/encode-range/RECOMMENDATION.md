# Encoding range experiment

Recommendation: validate a fully tagged full-range encode from the frozen lossless cache before any shared production change. A range flag alone causes a demonstrated Chrome regression.

| Native frame | FFmpeg MAE to native: current → proposed | FFmpeg MAE to reference: current → proposed | Chrome MAE to native: current → proposed |
|---|---:|---:|---:|
| 535 | 1.0700 → 0.1158 | 1.2582 → 0.3188 | 0.1338 → 0.1140 |
| 126 | 0.9931 → 0.0559 | 1.1165 → 0.2164 | 0.1164 → 0.0539 |
| 885 | 1.1186 → 0.2746 | 2.8979 → 2.0850 | 0.3045 → 0.2520 |

At535, 1,948,862 pixels are exactly gray253 in both native PNG and reference. Current limited-range encodes Y233; FFmpeg extracts RGB252, while Chrome displays253. Full-range encodes Y253. With incomplete P/T tags Chrome incorrectly displays255 in this test; with coherent P/T/M=1/1/1 and full-range VUI=1 it displays253.

A metadata-only remux and explicit setparams encoding have exactly the same decoded YUV SHA256 as plain full-range. The Chrome difference therefore comes from metadata interpretation, not changed picture samples. Codec color_primaries/color_trc options alone left SPS P/T=2/2 in this FFmpeg pipeline; setparams made P/T=1/1.

The proposed profile retains BT.709 matrix coefficients, 8-bit4:2:0, H.264 High, CRF16 and30fps. FFmpeg calls a full-range decoded4:2:0 stream yuvj420p; this does not mean4:4:4. All24frames and0.8s survive, and the candidate has zero playback-only drops/corruption in both tested Chrome flag sets. Candidate RGB pixels match across default and forced-sRGB/software-decode flags.

Palette gray exact medians: FFmpeg133/256 →256/256; Chrome220/256 →256/256. Palette flat color MAE: FFmpeg.7396 →.3542; Chrome1.3229 →.1354. Actual colored-content chromatic MAE also improves at all three measured checkpoints in Chrome. Accurate rounding alone leaves gray252 in FFmpeg and gives mixed content results. Zscale works when fully tagged but changes the chroma conversion and gives slightly worse measured native MAE at the three actual frames. CRF0 TV still extracts gray252, confirming that CRF adjustment alone cannot fix this bias.

Proposed filter (read-only recommendation):

```text
scale=in_range=full:out_range=full:out_color_matrix=bt709,setparams=range=full:color_primaries=bt709:color_trc=bt709:colorspace=bt709
```

Retain the existing encoder options and set `-color_range pc -colorspace bt709 -color_primaries bt709 -color_trc bt709 -pix_fmt yuv420p`. The filter-level setparams is necessary in the tested pipeline to keep coherent VUI tags.

Validation plan: after the combined source02 scene is frozen, hash the retained native PNG cache and encode it once to a separate gsap-fullrange-review.mp4. Do not rerender or overwrite production. Verify1360frames/30fps, dimensions/pixel format and actual SPS+container color tags after audio muxing. Run the every-frame native/reference comparison and inspect the24ranked peaks, including126/535/885 plus dark/color edge samples. Seek/play the review file in both tested Chrome modes, compare flat and chromatic pixels and playback-only timing counters, then decide whether to move all encoders to one shared encode-only profile. Preserve original native cache and actual capture/encoding fingerprints.

Limit: the source has unspecified color metadata. Its535 background is254 in Chrome but253 in the established FFmpeg reference PNG. This experiment improves faithful native RGB transport under the measured decoders; it does not prove source-perfect appearance across players.

All exact commands, profile/probe metadata, RGB measurements, VUI traces, browser flags/callback times, input hashes and failure diagnoses are in this folder. No production encoder or output was changed.
