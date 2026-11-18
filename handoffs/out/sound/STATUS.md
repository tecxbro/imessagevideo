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
- IN PROGRESS: reconstruction workflow doc, treatment experiment, cue-integrity
  test, original-scoring doc.
- WAITING: creative agent picture-lock (../creative/handoffs/out/creative/
  not present as of last check). If it lands, I will score that film under
  `work/sound/film-01-score/`; otherwise I'll score a library scene as demo.

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
