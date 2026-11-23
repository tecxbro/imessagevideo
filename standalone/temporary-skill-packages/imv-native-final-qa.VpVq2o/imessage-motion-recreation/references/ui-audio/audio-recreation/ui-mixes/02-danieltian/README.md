# 02-danieltian: frame-grounded UI sound

Primary clear-listening file: `ui_preview.m4a`, with a disclosed whole-UI boost of 7.000 dB. It measures -4.510 dBFS sample peak / -4.44 dBTP after AAC.

`ui.flac` / `ui.m4a` preserve the designed production UI levels. `music.flac` / `music.m4a` are the existing newly generated music-only stem attenuated6dB. `full_mix.flac` / `full_mix.m4a` combine this production UI with the quiet music bed; they are not raised to−16LUFS. Lossless stems add within independent24-bit quantization.

Canonical events: 45; rendered: 45; silent controls: 0. Actual single-key recordings are aligned by the dominant early transient to observed glyph-update frames. Observed batches receive one key; no physical key timing, title typing, AI-response typing or subframe character times are invented. Sends and panel movement use declared generated onset-aligned whooshes; stock samples retain CC0 provenance per event.

`report.json` preserves every raw canonical event and the stock/recording/procedural routing, levels, pitch, pan, attack alignment, file hashes and codec measurements. `schedule.snapshot.json` and `render_ui.source.py.txt` retain the actual executed inputs/source. `final-audit.json` independently verifies all7audio hashes and recomputes the production UI against its PCM24 export. No reference-film audio is read.

For future UI work without any score or AI generation: `python audio-recreation/scripts/render_ui.py --id 02-danieltian --no-music`. This writes separately under `02-danieltian/no-music/`, uses a silent bed, and makes no AI-music provenance claim. The accepted outputs above keep their actual earlier source snapshot; `renderer-api-compatibility.json` documents the optional API addition without relabelling them.
