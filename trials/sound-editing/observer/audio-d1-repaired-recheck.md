# Job A: repaired-mix recheck

## Integrity

The repaired file decodes with return code **0 and empty stderr**. Its copied video-packet SHA256 is **fef5481d8bbb13c16a14d05ad846cdb72112ca876913b9f0c27d871dc393d62b**, matching the claim. 1283 frames, 30000/1001 fps. Audio is 48 kHz stereo and exactly 2,054,853 samples/channel, matching R. No global alignment or gain adjustment was applied.

## Nine-defect recheck

Offsets use full-band normalized cross-correlation against each original R cue, ±350 ms search, followed by stereo least-squares gain. Frame units use 30000/1001. Every one of the eight expected cue offsets is **0.000 ms / 0.000 frames**, hence passes the requested **±0.5 frame (±16.683 ms)** tolerance. Presence requires RMS >1e-5 and correlation >0.5 (extra-window presence uses energy only). For level/spectral restoration, the explicitly chosen screening limits are ±0.5 dB gain, centroid within 5% of R, and correlation ≥0.98. These additional limits were not supplied by the user; they prevent a zero-lag but still severely damaged cue from passing. Centroid here is stereo-summed **power-weighted FFT centroid of the same complete R cue window**, not the magnitude-weighted STFT centroid used for visual spectrograms. A change from a previous centroid number can result from different windows/definitions.

| Old defect / R time | Offset ms / frames | Gain dB | Power centroid R → repaired, Hz | Present? | Result |
|---|---|---|---|---|---|
| 3: shifted / 10.041 | 0.000 / 0.000 | -0.000 | 1587.8 → 1587.8 | yes | PASS |
| 4: damaged / 11.308 | 0.000 / 0.000 | -0.000 | 1545.8 → 1545.8 | yes | PASS |
| 5: damaged / 12.046 | 0.000 / 0.000 | -0.067 | 3988.8 → 3939.1 | yes | PASS |
| 6: shifted / 13.778 | 0.000 / 0.000 | 0.000 | 1588.2 → 1588.2 | yes | PASS |
| 7: shifted / 17.117 | 0.000 / 0.000 | 0.000 | 3944.7 → 3944.7 | yes | PASS |
| 9: shifted / 21.518 | 0.000 / 0.000 | 0.000 | 1542.2 → 1542.2 | yes | PASS |
| 10: missing / 22.153 | 0.000 / 0.000 | 0.000 | 1588.5 → 1588.5 | yes | PASS |
| 12: shifted / 24.288 | 0.000 / 0.000 | 0.000 | 1589.3 → 1589.3 | yes | PASS |
| 14: extra / extra at 33.247 | N/A / N/A | N/A | N/A → 36.3 | yes | FAIL |

**8/9 pass the stated screening rules; not a bit-identical restoration.** The repaired 12.046 s cue has correlation 0.9895, gain −0.067 dB and centroid −1.25% relative to R: the severe low-pass defect is repaired, but a residual remains (cue-window RMS 0.007559, max 0.044632). Its PASS is conditional on the declared restoration thresholds, not proof that every sample was restored.

The original extra click is largely removed, but its **33.247–33.296 s window is not silent**: RMS **0.000592802** (−64.54 dBFS), peak **0.00141324**, power centroid **36.3 Hz**. The strongest residual is around **33.28–33.31 s / f997–998**. This is low-frequency residual energy, not proof the original click remains intact. Under a strict above-noise absence test this row fails; offset/gain versus R are undefined because R has no cue there. Broad 33.20–33.35 s inspection is included in residual screening, so shifted residue outside the old short cue window is not hidden.

## New-difference scan and codec-floor limits

Whole-file repaired-minus-R residual: **RMS 0.001002520 / max 0.102319948**, linear full scale. The maximum occurs at **4.069292 s / f122**, inside the already ambiguous opening composite.

The screening floor is **2.11926956e-05 RMS per 10 ms**: 99th percentile of nonzero old D−R residual in otherwise clean, non-defect regions, excluding the five previously ambiguous codec-heavy composite regions. This is an **empirical codec/coding baseline, not a proven universal codec noise floor**. Including those five high-residual composites would inflate it to roughly 0.012 and hide small new changes; that alternative was rejected. Every window is retained in `difference_energy.csv`; above-floor windows separated by ≤50 ms are grouped in `residual_regions.csv`.

| New or increased region, s | Repaired−R RMS | Max | Old D−R RMS | Interpretation |
|---|---|---|---|---|
| 3.61–4.34 | 0.00249372 | 0.10231995 | 0.00198734 | previously ambiguous composite; coding versus change unresolved |
| 4.74–4.78 | 0.00008730 | 0.00035632 | 0.00000051 | new/increased numeric residual above baseline; not automatically audible damage |
| 5.85–6.06 | 0.00249737 | 0.01897039 | 0.00194456 | previously ambiguous composite; coding versus change unresolved |
| 7.73–7.76 | 0.00016132 | 0.00078455 | 0.00000043 | new/increased numeric residual above baseline; not automatically audible damage |
| 8.94–8.98 | 0.00007121 | 0.00026190 | 0.00000028 | new/increased numeric residual above baseline; not automatically audible damage |
| 9.35–9.4 | 0.00006690 | 0.00027355 | 0.00001355 | new/increased numeric residual above baseline; not automatically audible damage |
| 12.06–12.19 | 0.00787252 | 0.04463243 | 0.05251222 | old-defect/tail window; inspect recheck above |
| 12.51–12.56 | 0.00002587 | 0.00008575 | 0.00001965 | old-defect/tail window; inspect recheck above |
| 18.31–18.36 | 0.00005340 | 0.00045359 | 0.00000308 | new/increased numeric residual above baseline; not automatically audible damage |
| 19.18–19.41 | 0.00304863 | 0.02044485 | 0.00210165 | previously ambiguous composite; coding versus change unresolved |
| 22.92–23.08 | 0.00887607 | 0.06340519 | 0.00683066 | previously ambiguous composite; coding versus change unresolved |
| 25.22–25.27 | 0.00010297 | 0.00066925 | 0.00001586 | new/increased numeric residual above baseline; not automatically audible damage |
| 26.69–26.85 | 0.00947217 | 0.05433043 | 0.00787523 | previously ambiguous composite; coding versus change unresolved |
| 28.45–28.5 | 0.00005061 | 0.00022261 | 0.00000382 | new/increased numeric residual above baseline; not automatically audible damage |
| 33.28–33.31 | 0.00077552 | 0.00141324 | 0.00087688 | old-defect/tail window; inspect recheck above |

Thus there **are new/increased numerical differences**, including around 4.74, 7.73, 8.94, 9.35, 18.31, 25.22 and 28.45 s outside the previously damaged cues. Their largest listed RMS is 0.000161321 and peak 0.000784554 (7.73–7.76 s); these are much smaller than the unresolved composite residuals. Re-encoding can produce such differences. Without lossless provenance or repeated-encode controls, they cannot honestly be called either proven intentional new damage or guaranteed codec noise. The residual table is the exhaustive above-baseline screen, rather than a claim that no new differences exist.

## Reproduction

`new_jobs_extract.py`, then `repaired/recheck.py`, using `/Users/devin/observer/groundtruth/.venv/bin/python`. Hash/decode/probe/ebur128 logs, WAV, detailed recheck CSV, all-window difference energy and residual summaries are local beside this report. No audition, upload or publication.
