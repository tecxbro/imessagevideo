# Source acquisition steps

1. Checked workspace for AGENTS.md; none found.
2. Queried public X syndication endpoint with tweet id, lang=en, token=1. Succeeded, no authentication needed.
3. Read video variants; chose highest-resolution official MP4.
4. Downloaded source.mp4 and ran ffprobe; raw probe saved.
5. Extracted two-second overview contact sheet and one-second labeled diagnostic sheets. Both videos are all graphic/UI animation, with no live-action segments to omit.
6. Reviewed every one-second diagnostic frame. Transcribed observed text, identified camera movements, mock phone geometry, interface states, asset dependencies and provisional scene ranges in analysis.md.
7. Failure: attempted to inspect Poke dense sheet while its extraction process was still running. Cause: yielded shell process had not completed. Correction: waited for that exact process to finish; did not start duplicate extraction. Future image inspection must follow successful generation completion.
8. Ran automatic scene-change candidate detection at threshold 0.10 and saved times to scene-cuts.json. These candidates must be visually confirmed at native fps.
