# PhotonHQ and Daniel: visual UI cue timing

Use **01-events.json** and **02-events.json** for mixing. Other files with these prefixes are analysis evidence, not additional cue lists. Both timelines use zero-based native frames at 30 fps. No soundtrack/transient detector supplied cue timestamps, and no sounds, scene, movie or sound library was edited.

- PhotonHQ V10: one observed cursor/button press at **frame 70, 2.333333333 s**. The pressed-state blend jumps from zero at 69 to 0.954 at 70; deepest press is 73. There is no visible human composer typing. Promotional titles, background message walls and the final URL/logo are excluded.
- Daniel V19: **32 visible composer-change events**, representing **51 normalized characters**, from **105 / 3.500 s** through **159 / 5.300 s**. Multi-character changes are `typing_burst`, with the actual `delta_count`; internal keystroke times are not invented. The cursor's visible advances at 143, 149 and 152 support three space inputs. Other interword spaces bundled with new letters cannot be isolated to a separate exact key time. Automatic line wrapping is not an asserted Return key.
- Daniel has a real text hold after `tmr.`: no character change across **128–142**. Cursor blinking is neither typing nor delete. The filled draft becomes an outgoing message at **175 / 5.833333333 s**; clearing on this transition is not backspace.
- Daniel's other two blue reply payloads hard-reveal at **770 / 25.666666667 s** and **920 / 30.666666667 s**. They have no visible composer or per-character keys. Their earlier three-dot status animations are excluded from typing cues.
- Ten incoming message/rich-link births are recorded at their canonical native activation frames: **640, 667, 677, 702, 734, 840, 866, 952, 972, 999**. The source-owner measured helpers and native source contact sheets support their roles. One arrival per message is emitted; spring growth, scrolling and settled holds do not create additional arrivals.
- Three optional `tap` events at **509, 517 and 519** describe green-check births for Airbnb, Lyft and Resy. The check-state change is observed, but no pointer/finger action is visible. These may be automated confirmations; the JSON explicitly labels the user gesture as inferred and keeps them outside the main events list.

Daniel's main list contains **45 events: 32 typing changes, 3 outgoing sends and 10 incoming arrivals**. There are **zero delete events**. Event confidence concerns visible state evidence; no physical keyboard telemetry exists in a rendered motion graphic.

## Evidence and failure diagnosis

The canonical scenes were read with dense vector path strings discarded, retaining about 4.9 MB / 10.5 MB of metadata in memory. The 395 MB Daniel scene was not copied to disk. Its final inventory reader hashes in 1 MiB chunks.

All native composer frames 90–174 were analyzed with OCR and manually checked in the two `02-composer-native-*.jpg` contact sheets. OCR caret artifacts (`cal`, `hell`, `help]`) were corrected against the source pixels and known readable prefix. The earlier composer-v5 helper interpolated a character schedule; it was deliberately not used as actual per-character timing.

One script syntax error was corrected before a decoder ran. The first decoding attempt then exposed FFmpeg's YUV420 crop rounding: an odd requested height of 275 produced 274 rows, corrupting fixed-size frame reads. That entire attempt was discarded. A byte-count proof in `02-crop-diagnosis.json` verifies that explicit RGB conversion before cropping retains exactly 275 rows; the corrected 85-frame producer completed successfully before its evidence was used.

The events cite canonical layer IDs, native source frames and original source-owner helpers. Source01's press is supported by `intro-review-elements.json`; Daniel's exact composer art comes from `root-copy-pose-N`, the send flight from `root-send-flight-pose-175`, and the two later hard-reveals from the accepted `final-midstate-fix/elements-final.json` paths. The scene/source evidence hashes are retained in the cue JSON and validation record.
