# Editable Messages Motion trial

This laboratory clip applies draft send, typing and reply to one editable
contact thread. The send appears at frame 38, typing starts at 56, and the
reply appears at 88 on a 24 fps clock. The 114-frame clip runs 4.75 seconds.

Edit copy and event frames in conversation.json. After changing it, regenerate
the editable composition from the iMessage skill directory.

```sh
FONTCONFIG_FILE=/path/to/this/project/fontconfig.xml \
  python3 upstream/film.py recompile-messages /path/to/this/project
python3 upstream/film.py render /path/to/this/project /tmp/contact-motion.mp4
```

With Node 22.19+, FFmpeg and Chrome installed, the existing composition can also
render directly from this folder. The final optional argument names an output
outside the project.

```sh
npm ci
HYPERFRAMES_NO_TELEMETRY=1 HYPERFRAMES_NO_UPDATE_CHECK=1   ./node_modules/.bin/hyperframes render . --output /tmp/contact-motion.mp4 --quality high
```

The delivery sample in evidence includes an original send cue. The editable
plan, cue asset, audio verify report, and silent picture allow an independent
sync check. The contact appearance is stylized and its portrait is original.
The package includes DejaVu font notices and the bundled GSAP license notice.
