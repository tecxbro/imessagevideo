# Question C: V5 overlap correction

## Conclusion

**The previous f109 correlation-based ranking argument does not survive.** It compared a dense composite R typing window with a sparser V5 typing window and treated the composite mismatch as if it were single-cue damage. After separating scheduled neighbours, the retained first key matches an independently available source-derived R atom extremely well. The old 0.57 statistic and 9.558 dB aggregate gain span must not be used as evidence of a defective first key or uniform per-cue inconsistency. The original third-place ranking is therefore not established by that argument.

## Test, including an attempt to disprove the overlap explanation

First, I attempted to find overlap by correlating later *consolidated* decoded R cue regions with the opening. Those later regions did not match (best correlations <0.26), because the old onset CSV had **collapsed the entire opening typing sequence into one region**. “Cues 4 and 6” are not rows 4 and 6 of that CSV. Inspection of the local Poke source receipt identifies **zero-based ordinals 4 and 6, at frames 113 and 116**, whose 250 ms keyboard clips overlap the f109 clip. These are real scheduled overlaps, not an unconstrained lag search chosen to maximize the result.

For this non-blind Poke-only question I additionally used the already local source receipt and prepared keyboard assets under `/Users/devin/repos/imessagevideo/resources/complete-ui-audio-source-v1/imessage-recreations/audio-recreation/`. **No Check In source schedules, treatment identities, stems or reference mix were used for Job B.** The new source access makes this a source-assisted audit, not a claim that decoded R alone supplies clean isolated stems.

`overlap_recheck.py` places 14 independent key atoms at receipt sample offsets, solves their gains jointly against R and V5 (condition number 1.751), and subtracts the two overlapping V5 neighbours before comparing f109 over its 250 ms source window in the same 1–5 kHz band as the old matching method. Coefficient estimates are source-constrained; the known source shapes are not learned from the V5 target window. Whole-opening model correlations are R **0.99124**, V5 **0.99923**; the imperfect R fit explicitly limits claims based on decoded-R residual cancellation.

| Measurement | Result |
|---|---|
| Raw full-opening R/V5 correlation | 0.572787 |
| After subtracting ordinal 4/f113 and 6/f116; source-assisted isolated reference | 0.999206 |
| f109 gain relative to common V5/R scale | -0.0007 dB |
| Common V5/R gain, not a cue defect | -1.5679 dB |
| Decoded-R residual cancellation, all other fitted atoms removed | 0.979917 |
| Retained typing-cue relative coefficient gain span | 0.1683 dB |
| All remaining R cue classes plus corrected retained typing, gain span | 5.2568 dB |

V5 retains typing atoms at **f109, f113, f116, f120 and f124**; nine other dense R typing atoms are essentially absent in the source-constrained fit. This explains why correlating the entire R opening with V5 was not a valid isolated-cue test. The new result supports the specialist's **overlap explanation** and approximately 0.998 / near-zero relative gain result. It does **not reproduce that exact number using decoded R alone**: retaining codec/model residuals gives about 0.980 rather than 0.998. Report both, not just the favourable source-assisted value.

The retained-typing gain span **0.168 dB** supports the narrower claim of roughly 0.3 dB uniformity for those retained keys. The **blanket all-cue 0.3 dB claim is not reproduced versus this decoded R**: non-overlapping panel and send cues remain about 5.09 and 3.04–3.15 dB lower relative to the common arrival/click scale. These can be intentional class-level mix choices, not damage. Across these classes the new span is **5.257 dB**, not the old spurious 9.558 dB. No new overall preference ranking is asserted from class-level gain choices alone.

## Environment note

The task venv was loaded, but NumPy 2.0.2's Apple Accelerate matmul emitted spurious `divide by zero encountered in matmul`, `overflow encountered in matmul`, and `invalid value encountered in matmul` even for an all-ones finite matrix. A single-thread check did not fix it. The analysis-only venv was safely changed to **NumPy 1.26.4**; the same finite-matrix sanity test then emitted no warning, and this overlap analysis was rerun with identical finite results. No source repository/configuration was changed.

Artifacts: `overlap_recheck.py`, `.csv`, `.json`, `.log`. The historical treatment report now points to this correction. No audition or publication.
