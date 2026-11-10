# Acquisition steps

1. Checked /workspace for AGENTS.md; none found.
2. Confirmed ffmpeg, ffprobe, and Pillow are installed.
3. Initial acquisition script failed because requests was not installed; diagnosed locally and replaced it with urllib from Python standard library.
4. Fetched supplied URL with urllib, preserving inherited proxy and TLS trust. Status: 200.
5. Parsed real media URL from public page metadata and downloaded source.mp4.
7. Ran ffprobe: 48.6s. Extracted frame at 2s intervals and assembled labeled contact sheet. Note fps filter samples center of each 2s bin (labels t=1,3,...).
8. Scene-change detection at threshold 0.12 saved to scene-detection.log; extracted 2fps inspection frames and split 30-per-sheet for finer timing.
9. Visually inspected all 2fps contact sheets. Wrote timed graphic scene inventory, visual system notes, reconstruction constraints, and genuine-vs-inferred measurements in analysis.md.
10. Extracted selected native-resolution keyframes for implementation and QA.
