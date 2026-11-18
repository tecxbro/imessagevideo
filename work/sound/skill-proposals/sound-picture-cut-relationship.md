# Skill proposal — sound: relationship to picture and cuts

Proposed addition to `references/ui-audio-workflow.md` (or a new
`sound-design.md` reference). Drafted from the sound agent's audit,
experiments and tool work in `work/sound/`.

## The contract

**Sound is a first-class deliverable tied to the delivered picture version —
the perceived event is the (frame, onset) pair, not either alone.**

1. Inventory *visible* actions on the accepted picture at native frames.
   Cue times are frame numbers, never wall-clock guesses. If the picture
   recuts, re-derive the cue map — do not nudge times by hand.
2. Emit sounds only for observed actions: composer typing (one key per
   visible batch, keep real pauses), sends, arrivals, taps, selections,
   panel moves. Controls appearing may stay silent *by recorded decision*
   (`silent_visual_state`), never by omission.
3. Align on the impact the viewer perceives: keys/clicks on dominant early
   attack peak, movement/whoosh on onset. Documented exception to keep:
   04-poke selection — source frame 633, accepted picture 645; sound
   follows the delivered frame.
4. Choose provenance per event: licensed effect (CC0 Kenney/keyboard packs
   in `library/prepared/` + license files + hashes), declared procedural
   synthesis, deliberate silence — never unlabeled reference-audio reuse.
5. Music is optional and subordinate: quiet bed ≈−6 dB under production UI,
   capped ducking (~1.2 dB max, never summed); sparse UI stems are never
   normalized to a program LUFS target. AI music = text-prompt only,
   pinned output file + request id — prompts don't reproduce, files do.
6. Verify in the ENCODED artifact:
   - duration/span: `frames/fps` sample count, `-movie_timescale 48000`,
     explicit `-map` so source-film audio can't leak into new mixes.
   - codec true peak: **measured** AAC failure — 112 kbps turned a
     −2.56 dBTP PCM master into +0.80 dBTP (2 clipped samples); 192k −0.98;
     256k −2.47. Encode hot stems ≥256k and re-measure decoded output.
   - cue integrity: expected-cue↔onset correlation on the decoded export
     (every event within ±~120 ms, no unexplained onsets, intentional
     silences whitelisted) + kind fingerprint (ZCR/crest/window-RMS per
     event vs declared family). Loudness/duration alone CANNOT catch a
     shifted or wrong sound — proven by planted-defect test.
7. Report heard-vs-measured separately. A spectrogram is not listening.
   Where no human endpoint exists, say so; machine classification
   (SNClassifySoundRequest) is admissible evidence *labelled as such*.
8. Keep stems, cue sheet, code snapshot and hashes editable/verifiable;
   immutable accepted exports are never regenerated to hide earlier
   decisions.

## Editorial evidence worth citing in the skill

- Same-picture treatment test (`work/sound/treatment-experiment.md`):
  removing cues felt bigger than a 10-frame recut — but **stale cues over a
  recut felt worst of all, worse than silence**. A shifted cue turns
  "designed tactility" into a sync bug.
- Cue-integrity test (`work/sound/cue-integrity-test.md`): a +200 ms
  shifted cue and a whoosh→click swap each passed LUFS/TP/duration; the
  onset-correlation + kind-fingerprint checks caught both.
- Six-film audit (`work/sound/sound-map.md`): originals are music-led
  (several clipped above 0 dBTP); recreated deliverables are UI-led with
  optional quiet bed — do not copy source loudness.

## Tools donated (work/sound/bin/)

- `stem_build.py` — frame-exact asset placement → s24 stem + placement
  report (attack/onset alignment, pure stdlib).
- `onsets.py` — onset/envelope detection on any audio (ffmpeg decode +
  stdlib analysis).
- `cue_check.py` — cue-sheet↔export correlation checker (exit 1 on fail).
- `classify` (Swift/SNClassifySoundRequest) — local machine-listening dump.
