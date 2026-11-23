# Acquisition and analysis log

1. Checked workspace for AGENTS.md and existing media/tooling. No AGENTS.md and no preinstalled yt-dlp found.
2. Probed original X page, cdn.syndication.twimg.com, and api.fxtwitter.com public metadata with inherited proxy/TLS settings. Raw responses and headers saved.
3. Syndication returned `{}` and cannot provide media. Root cause: that public endpoint did not return this post metadata. Switched to fxtwitter, which returned status 200 and original video CDN URLs; no identical retry.
4. Downloaded highest-resolution original MP4 from video.twimg.com. ffprobe confirms actual media stream fps, dimensions, frame count, and duration. Stored original + source.json + ffprobe.json.
5. Generated first 1fps contact sheet at 384px. Failure: 5×5 tile with one output covered only 25 seconds, insufficient for 45-second source; captions absent. Corrected by extracting all whole-second samples and creating timestamped sheets in 20-frame chunks.
6. Inspected the complete labelled sheets; every observed scene is graphic content and in scope. Wrote scenes.json and analysis.md with clear estimated timing boundaries.
7. Extracted selected full-resolution keyframes for later measurements. Ran FFmpeg scene-score diagnostics as supplementary evidence; smooth transitions still need manual frame analysis.
8. Initial whole-second scene boundaries proved too coarse for matching. Generated quarter-second contact sheets in one FFmpeg pass and inspected all samples; corrected boundary estimates in scenes.json. Diagnosed an anomalous fully assembled frame-zero title before intro reset, rather than mistaking it for intended initial state. Added measured isolated-title bboxes in measurements.json.
