# Check In v1 blind audio-treatment review (Job B)

## Ranking and scope

**This is an objective, conditional technical ranking, not a listening judgment. Audio was not auditioned.** Criterion: comparable detected transient-cue coverage/timing, then lower non-cue sustained energy and greater peak headroom. A travel texture may be artistically desirable; its presence is not intrinsically a defect. Under a criterion favouring continuous travel sonification, the order need not be the same. There is no reference mix and no assertion that every picture change must sound.

| Rank | Treatment | LUFS / dBTP / LRA | Cue clusters / aligned | Objective evidence |
|---|---|---|---|---|
| 1 | T-V2 | −40.3 / −19.9 / 12.0 | 11 / 11 | Same transient cue-cluster coverage; no sustained background in 7.2–13.7 s; 2.5 dB more true-peak headroom. |
| 2 | T-M8 | −40.2 / −17.4 / 11.9 | 11 / 11 | Same timing coverage; adds sustained 7.093–13.897 s travel texture, band RMS −49.60 dBFS; no demonstrated masking of a concurrent transient cue. |

## Picture identity, decode and loudness

Silent original, T-M8 and T-V2 all copied-video-packet hash to **782119ce82a1cb231fa9d1ea0576174d36108d374cbefd40f3ab1d5fd4197799** and all full-file decode checks return **0 with empty stderr**. Picture: **720 frames / 30 fps / 1920×1080 / 24.000 s**. Original has no audio stream. Treatments decode to 48 kHz stereo, exactly 1,152,000 samples/channel each. Hashing is over `-map 0:v -c copy -f data` bytes, not decoded image hashes. LUFS/dBTP/LRA were measured with ffmpeg `ebur128=peak=true`; printed precision is 0.1 LU/dB. These treatments are nearly matched in displayed integrated loudness, but no stricter matching precision is claimed.

## Detected clusters and onset-to-picture sync

**Counts are detected clusters, not individual authored sounds or keystrokes.** Stereo RMS in 1 ms windows at −65 dBFS supplies activity starts with a 2 ms pre-roll; spectral-flux detection at 10 ms hop supplies attack grouping. Adjacent flux attacks separated by ≤250 ms form one transient cue cluster; near-silent gaps within a typing phrase therefore do not inflate the count. Both mixes yield **30 raw flux attacks → 11 transient cue clusters (0.458/s)**. A separate >2 s sustained region in M8 is classified as a background texture, not a twelfth transient cue. Raw amplitude-only regions (13 in M8, 15 in V2) are retained in `*_clusters.csv` as intermediate activity segmentation; those are **not the final cue counts**. Final counts/starts are in `*_onset_sync.csv` and `*_final_summary.json`.

Picture annotations use only the silent original: every-frame mean absolute RGB change at 480×270; spikes height 0.12, prominence 0.06, distance 3; plus actual frame inspection of named UI events. Native-resolution crops were inspected for small ETA text and late UI states. Timing uses zero-based frame `round(t*30)`. Negative error means audio before the first annotated visual frame; a small negative activity-start error can be a legitimate pre-attack. Association threshold is ≤2 rounded frames, not proof of perceived sync. Visually faint beginnings carry about one-frame annotation uncertainty.

| Cluster / event | M8 start s / f | V2 start s / f | Visual frame | M8 / V2 error ms |
|---|---|---|---|---|
| 1: incoming message first appears | 0.431 / 13 | 0.431 / 13 | 13 | -2.33 / -2.33 |
| 2: app drawer starts entering | 3.449 / 103 | 3.453 / 104 | 104 | -17.67 / -13.67 |
| 3: Check In row selected | 4.396 / 132 | 4.396 / 132 | 132 | -4.00 / -4.00 |
| 4: Check In card send begins | 6.2 / 186 | 6.201 / 186 | 186 | 0.00 / 1.00 |
| 5: right-phone conversation enters view | 14.829 / 445 | 14.829 / 445 | 445 | -4.33 / -4.33 |
| 6: right composer typing begins | 15.628 / 469 | 15.629 / 469 | 469 | -5.33 / -4.33 |
| 7: right composer typing update | 16.373 / 491 | 16.373 / 491 | 491 | 6.33 / 6.33 |
| 8: arrival cards become green | 16.995 / 510 | 16.995 / 510 | 510 | -5.00 / -5.00 |
| 9: right heart-reply composition update | 17.39 / 522 | 17.39 / 522 | 522 | -10.00 / -10.00 |
| 10: right heart bubble starts sending | 19.167 / 575 | 19.167 / 575 | 575 | 0.33 / 0.33 |
| 11: left heart bubble starts appearing | 19.664 / 590 | 19.664 / 590 | 590 | -2.67 / -2.67 |

**All 11 cluster starts in both treatments have a detected event within two frames; no unmatched transient cluster start.** For every raw flux attack, a separate association CSV is supplied too: internal key attacks need not correspond to a new high-contrast frame spike. They must not be called extra cues merely because the global visual detector misses small composer text changes.

### Key moments not reducible to onset counts

| Picture moment | Frame / time s | Audio association |
|---|---|---|
| Check In preview card appears | 138 / 4.600 | No independent start; preceding selection click at 4.396 s is 204 ms earlier. Not a reference-proven missing cue. |
| Check In send | 186 / 6.200 | Both have cluster start at 6.200/6.201 s. |
| ETA 18 → 15 → 12 → 9 → 6 → 3 → 1 min | 18 already visible at card reveal; steps approximately f250/280/310/340/370/400 = 8.333/9.333/10.333/11.333/12.333/13.333 s | No distinct detected transient cluster at any ETA step. M8 sustains travel texture across these steps; V2 is silent there. |
| Arrival / green state | 510 / 17.000 | Both start a short cue at 16.995 s (−5 ms). |
| Heart composition | 522 / 17.400 and 542 / 18.067 | Both are inside a multi-attack typing cluster beginning 17.390 s; second composition is not counted as a separate onset cluster. |
| Heart send / appearance | 575 / 19.167; 590 / 19.667 | Both aligned to 19.167 and 19.664 s starts. |
| End card | First visible caption around 628 / 20.933; fully legible by 640 / 21.333 and held through 22 s | No new detected cue; both audio tails finish before caption reveal. |

ETA boundaries are first legible sampled native-frame changes, approximately ±1 frame; `eta_steps.jpg` preserves the before/after evidence. `*_event_coverage.csv` distinguishes “start nearby” from “already inside an existing cluster,” so merged typing does not falsely appear absent from later actions.

## Background bed, BPM, masking and spectral character

- **M8:** sustained nonperiodic band-limited travel/noise texture approximately **7.093–13.897 s / f213–417**. In its stable 7.2–13.7 s interior, full-band RMS **−46.74 dBFS**, 1–5 kHz RMS **−49.60 dBFS**, power centroid **1101 Hz**. It has no stable musical pulse demonstrated by the onset detector; **bed BPM is not estimable / N/A**, not 122 BPM.
- **V2:** no sustained bed detected; selected 7.2–13.7 s samples are exactly zero. **Bed BPM N/A.**
- Both raw full-mix beat trackers return 122.45 BPM on sparse UI/typing patterns. This is **not a valid bed-tempo estimate** and is expressly rejected. Counts are not beat counts.
- There is **no detected transient cue cluster overlapping M8's sustained texture**: the preceding cue ends about 6.338 s and the next begins 14.829 s. Thus this analysis finds **no demonstrated simultaneous cue/bed masking**; it would be wrong to label the −49.60 dBFS travel-band energy as masking an absent cue. At transient cue onsets, measured nearby cue-excluded background is at numerical zero/very low decode residue; a finite cue/bed ratio is **not meaningful** and is reported N/A, rather than a fictitious +100–160 dB. `*_clusters.csv` retains uncorrected raw context calculations as diagnostics, not stem separation.
- No isolated stems exist, so hidden within-cluster masking between layered sounds cannot be independently measured. No treatment-source assets or schedule were consulted for this blind comparison.

`*_centroid.csv` gives full-mix magnitude-weighted STFT centroid every 10 ms. Silence has no meaningful centroid. `T-M8_spectrogram.png` and `T-V2_spectrogram.png` use identical absolute −100 to −20 dBFS colour scales, logarithmic 30 Hz–20 kHz, FFT 2048 / hop 480; both were actually viewed. Their sparse transients are similar; only M8 has the conspicuous sustained mid-band region at 7–14 s. This signal-picture inspection is not an audition.

## Clipping, abrupt edits, fades and tails

Both contain **zero full-scale sample/channel values**. Sample peaks M8 **0.132487**, V2 **0.101218**. Largest adjacent-sample steps occur at the same **17.000292 s / f510**, amplitudes **0.140397 / 0.109152**, inside the arrival cue. This is consistent with a sharp UI transient, not enough evidence to assert an audible click. Strongest sample-step candidates are saved; no nonzero file-boundary step or full-scale clipping was observed.

Both begin with silence until **0.432 s / f13**, then the incoming-message cue; there is no sustained music fade-in to measure. M8's travel region ramps on/off rather than extending to the file boundary: RMS rises from **−71.15 dBFS (7.05–7.10 s)** through **−60.59 (7.10–7.20 s)** to **−50.81 (7.20–7.40 s)**, then decays from **−47.15 (13.30–13.50 s)** through **−55.18 (13.70–13.90 s)** to **−78.75 (13.90–14.10 s)**. These are measured envelope windows, not a claimed single fade constant. Boundary-window energies are preserved in the final summary JSON. Both last exceed −70 dBFS at **19.777 s / f593**, leaving **4.223 s** below that threshold through the end card. Actual file endpoints are exactly zero; there is **no observed endpoint tail truncation**. M8's last threshold-defined cluster ends 19.723 s and V2's 19.715 s, but low-level cue tails continue until 19.777 s; activity thresholds must not be mistaken for source clip lengths. No end-card sound is detected around 22 s, which is a descriptive coverage result, not an error without a reference specification.

## Artifacts, reproduction and limitations

Local scripts: `../new_jobs_extract.py`, `visual.py`, `detail.py`, `analyze.py`, `final_metrics.py`, `../write_new_reports.py`. Use `/Users/devin/observer/groundtruth/.venv/bin/python`. Native-frame crops, overview/spike sheets, measured frame differences, onset and visual coverage CSVs, loudness/hash/decode/probe logs, extracted WAVs, spectral centroid/envelope/step tables and PNG spectrograms remain in this directory.

No subjective listening, no externally identified treatment names, no reference mix, and no published/uploaded artifacts. The only source-assisted work was **Question C on Poke**, documented separately and not used to time or identify Check In sounds.

## Other requested jobs

- **Job A:** `../repaired/report.md` and `../repaired/defect_recheck.csv`. Eight expected cues have zero offset vs R; strict removal of residual energy in the old extra-click window fails. All above-baseline numerical differences are tabulated, not hidden as codec noise.
- **Question C:** `../treatments/overlap_report.md`. The old V5 opening-correlation ranking argument is withdrawn; source-assisted f109 correlation after neighbour subtraction is 0.9992, while decoded-R residual cancellation gives 0.9799. Retained typing gain span is 0.168 dB, but an all-class 0.3 dB claim is not reproduced.
