# Video comparison

`compare.py` compares native decoded frames at explicit reference/recreation times and creates a JSON report, CSV metrics and an HTML contact sheet. Each contact row shows reference, recreation, and absolute difference amplified 4×.

```sh
python3 verification/compare.py references/01-photonhq/source.mp4 renders/remotion.mp4 \
  --reference-start 4.0 --candidate-start 0 --duration 3 --fps 3 \
  --out verification/results/photonhq-remotion
```

For a recreation made from multiple graphic excerpts, pass `--segments segments.json`:

```json
[
  {"name":"opening","reference_start":0,"candidate_start":0,"duration":2.5},
  {"name":"app demonstration","reference_start":8.2,"candidate_start":2.5,"duration":4}
]
```

Default sampling is once per second. Use `--fps 5` for phase checks, `--times 0,0.1,0.2,0.5` for explicit offsets within every mapped segment, or `--all-frames` to request the reference frame rate. All-frames mode is intentionally expensive. Timing is exact requested timestamps, with FFmpeg selecting the first decoded presentation frame at or after each seek time. Match source cadence to avoid sampling the wrong animation phase.

Metrics are measured at native resolution unless `--width` explicitly scales both inputs using Lanczos. Native dimensions must agree. Global MAE/RMSE/PSNR, luma SSIM and changed-pixel percentage are recorded separately from foreground metrics. The foreground mask is the union of pixels in either image that differ from the reference border-median background by more than 12 channel levels, dilated by one pixel. This avoids a white background hiding a missing message. Override it for flat scenes with `--background 255,255,255`. The JSON records the inferred background and foreground coverage per frame; complex footage requires visual review.

SSIM uses valid 11×11 uniform windows, luma coefficients 0.2126/0.7152/0.0722, population variance, and standard 8-bit constants. It is diagnostic and may differ from tools using Gaussian windows or sample covariance. Identical frames have MAE/RMSE zero, SSIM one and infinite PSNR (`null` with `psnr_infinite: true`). No single percentage certifies perfection. A sampled-frame pass says only that those decoded samples match. Audio and editability need separate checks.

After structural corrections, `scan_timeline.py reference.mp4 candidate.mp4 --out timeline-scan` measures global native MAE for **every** aligned picture frame and ranks peaks at least half a second apart. Use `--segments` for the explicit Rene cut map. It writes a CSV covering all frames and `peak-segments.json` for a subsequent `compare.py --segments peak-segments.json --times 0` native visual/foreground review. A peak identifies a place to investigate, not its cause. It may represent timing, a missing state, camera geometry, antialiasing or legitimate encoding differences.
