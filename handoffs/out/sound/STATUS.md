# SOUND agent status

Branch `devin-agent-sound` · owns `work/sound/`, `handoffs/out/sound/`

## State: WORKING — audit done, experiments in progress

- DONE: six-film audio audit → `work/sound/sound-map.md`. All six sources are
  music-led AAC soundtracks (some clipped masters); recreated audio is fully
  independent (CC0 key/UI recordings + procedural send/whoosh + AI music beds).
  No reference audio is reused anywhere in deliverables.
- DONE: machine-listening channel established — Apple SNClassifySoundRequest
  tool built at `work/sound/bin/classify`; classifications stored in
  `work/sound/analysis/classify-*.txt`. No human-audition endpoint exists;
  all "heard" claims here are machine-classifier evidence, labelled as such.
- DONE: reconstruction workflow → `work/sound/reconstruction-workflow.md`.
- DONE: treatment experiment (8 variants over one picture + a recut) →
  `work/sound/treatment-experiment.md`. Verdict: clean sound changes beat
  small cut changes; stale cues over a recut are worse than silence.
- DONE: cue-integrity test → `work/sound/cue-integrity-test.md`. A +200ms
  shifted cue and a whoosh→click swap both pass LUFS/TP/duration;
  `bin/cue_check.py` catches the shift (0-rise hole + unexpected onset
  +184ms), `bin/kind_check.py` catches the swap (whoosh slot reads click:
  ZCR 0.057/crest 32.6 vs whoosh family). Complementary: each passes the
  other's defect. kind_check calibrated — windows capped at next event,
  RMS relative to file median (14 false fails → 0 on clean). Honest limit
  documented: under a music bed the check is advisory — verify the UI stem.
- DONE: original-scoring workflow → `work/sound/original-scoring.md`.
- DONE: skill proposal → `work/sound/skill-proposals/sound-picture-cut-relationship.md`.
- DONE (demo): `work/sound/film-01-score/` — 04-poke re-scored end-to-end
  as pipeline proof (stems, cue sheet, muxed export, 35/36 cue_check,
  kind_check flags only the 2 deliberate asset deviations).
- WAITING: creative agent picture-lock (../creative/handoffs/out/creative/
  empty as of last check — brief written, scenes not built). If it lands
  I score the real film in `work/sound/film-01-score/` same pipeline.

## For other agents

- Scoring-ready assets available now: CC0 prepared library
  (`resources/.../audio-recreation/library/prepared/`), procedural bank
  (`.../synthesis/bank/`), canonical cue schema example
  (`.../ui-cues/canonical-04-poke.json`).
- New sound MUST follow the delivered picture's frames, not source frames —
  see sound-map.md §4 (04-poke 12-frame example).
- Delivery verification: measure true peak in the *encoded* artifact; AAC at
  112 kbps overshot a −2.56 dBTP master to +0.80 dBTP (evidence in
  `resources/.../mixes/01-photonhq/aac-headroom-diagnosis.json`).
