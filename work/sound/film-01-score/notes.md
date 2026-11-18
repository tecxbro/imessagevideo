# film-01-score — status

## PLACEHOLDER/DEMO: creative film not yet delivered

`../creative/handoffs/out/creative/` exists but was empty at last check
(creative agent in reference-study + film-01 build). Per my brief, this
directory currently holds a **clearly-labeled demonstration score on a
library picture**: `04-poke-demo`. When creative's picture-locked film +
cue sheet lands, this same pipeline scores it under `film-01-score/`
(`stems/`, `cue-sheet-<film>.json`, muxed export, this notes file).

## Demo: 04-poke re-scored from its action inventory

**Picture:** `AR/ui-previews/04-poke-ui.mp4` video stream, 1283 frames @
30000/1001 (42.8094 s), file sha256
`ff84fd86efa6220dbe716b9d9e327fb6de3b755d27e5c03a5054c442fde8c987`.
Canonical action inventory reused as *observed-action evidence*; every
asset, gain, pan and layering decision is new.

**Layer decisions (mine):**

- typing burst f109–125 (14 observed key events) → rotating CC0 single-key
  recordings (`key_001/011/023/029`), −13 dB, dominant-attack aligned, ±8 %
  pan spread — physical keys, not a loop.
- message_arrival ×11 → `kenney_drop_001` (CC0), −14 dB.
- message_send ×3 → procedural `air_whoosh`, −10 dB, onset-aligned.
- send f800 (voice-message bubble) → `bubble_pop` — a bubble, not a whoosh.
- taps f232/f339 → `kenney_click_001`; **selection f645 →
  `kenney_confirmation_001`** — the payoff choice gets a distinct confirm.
- panel_open f175/f575 → procedural `card_swoosh`, onset-aligned.
- control_appear f455 → **deliberate silence** (suggestion bar, recorded
  in the sheet as `silence: true`).
- logo cut f1215 (verified by scene-detect + frames) → `glass_confirm`
  −16 dB on a separate `design` stem; the 2.27 s `Poke.com` hold then plays
  honest silence — a decided hush, matching the library's own tail choice.
- No music, no ambience: UI-led deliverable per skill default. The option
  of a −6 dB bed is documented in original-scoring.md.

## What was measured

- Stems: `stems/ui.wav`, `stems/design.wav` — s24 48 kHz stereo,
  exactly 2,054,853 samples (= 1283 fr / 29.97). UI peak −18.51 dBFS,
  design −24.51, full mix −18.51, **0 clipped samples**.
- `04-poke-demo-scored.mp4`: video packets stream-copied; AAC 192k;
  `-movie_timescale 48000`; audio duration 42.809396 s vs video 42.809433 s.
- `cue_check.py` on the **encoded** export vs merged cue sheet: **35/36
  pass, 0 unexpected onsets**; sole fail = the intentional silence
  (whitelist semantics working as designed).
- Export loudness −35.2 LUFS / −18.4 dBTP (production UI level — sparse by
  design). Labelled audition copy `*-AUDITION-BOOST-9dB.mp4` at −26.2
  LUFS / −9.5 dBTP; production gain is the unboosted file.

## What was machine-heard (SNClassifySoundRequest; not human audition)

Typing stretch reads `typing/typewriter/typing_computer_keyboard` 0.71–0.90
at 3.0–3.75 s; sends/panels read `whoosh_swoosh_swish`; the confirmation
at 21.5 s reads `beep`/`telephone` (Kenney confirm tone — plausible);
silent regions sit at low-confidence mush. No stray music or voice labels.
`analysis/classify-score-04-demo.txt`.

Side-by-side vs the library production stem (`classify-04-prod-ui.txt`):
identical texture except the f645 selection — production's plain click
registers only weak `click`/`writing` labels around 21 s, while my
`kenney_confirmation_001` registers `beep:0.77`/`telephone:0.64` at
20.25–21.75. The classifier heard the editorial upgrade: the payoff
selection now *sounds* like a confirm, not a tick. Both files share the
odd 15.75 s `gunshot` misread (send-whoosh edge bleed into the window —
kept as honest classifier noise, not a cue claim).

## Files

`cue-sheet-04-poke-demo.json` (UI events), `cue-sheet-design.json`,
`stems/{ui,design,full_mix}.wav` + placement reports,
`04-poke-demo-scored.mp4`, `04-poke-demo-scored-AUDITION-BOOST-9dB.mp4`.
Tools: `work/sound/bin/stem_build.py`, `onsets.py`, `cue_check.py`.
