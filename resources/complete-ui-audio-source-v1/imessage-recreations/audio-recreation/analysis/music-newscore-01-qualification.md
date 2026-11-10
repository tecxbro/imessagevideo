# New PhotonHQ score: computational check

The newly generated draft has a strong recurring pulse compatible with the requested approximately **109 BPM**. Broadband and bass analyses both peak in the **109.34 BPM candidate bin**; all three 8-second broadband windows agree. The broadband normalized autocorrelation is **0.87496**, compared with **0.60712** for the original mix. This is a periodicity check, not proof of musical meter or an audible feel match; lag quantization near this tempo spaces candidate bins by roughly 2 BPM.

The decoded draft is **21.864036 s**, versus the picture's **21.833333333 s**. The approximately 30.7 ms excess can be an encoded tail/padding span; trim the final mix to the picture duration rather than assuming a generator timing failure.

Quarter RMS levels are **−14.99 / −14.86 / −14.72 / −17.94 dBFS**. The draft is nearly level through its first three quarters, then fades. The original measured **−12.51 / −10.68 / −10.62 / −12.03 dBFS**, with a larger middle lift. The new one-second RMS falls sharply across **19–20 s**; the original's large decline starts across **20–21 s**. Thus the new ending settles about one second earlier. This difference is documented, not treated as a failed rhythm direction.

Whole-draft mono RMS is **-15.44 dBFS**. Its decoded float sample peak is **+0.08 dBFS**; a small MP3-decoder overshoot alone does not establish hard clipping. Set final gain/headroom after adding the independently produced effects.

No human listening, new-score content model, vocal/instrument classifier or subjective similarity pass was performed here. Original timbre, clean-instrumental status, mix balance and final picture sync still require the separate content/audition checks. No audio was written or modified by this check.

Input: `audio-recreation/ai/01-photonhq/music.mp3`; SHA256 `bf30bc60ebe17dde7db9f1d75727cc50273bac49083ae7620cc38e8556662f92`. Reproducible measurements and settings are in `music-newscore-01.json` and `music-newscore-01-measure.py`.
