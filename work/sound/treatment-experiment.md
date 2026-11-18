# Treatment experiment — same picture, different sound; then a recut

**Scene:** 04-poke "Indian option" exchange, frames 315–420 of the accepted
picture (`ui-previews/04-poke-ui.mp4`, 29.97 fps, 3.54 s segment):
tap selects "Indian" (f339/t0.80s) → outgoing selected-option card (f361/t1.54s)
→ incoming "want me to find a spot?" (f375/t2.00s) → second arrival at t3.27s.
Verified visually: `analysis/frames/poke-exchange-strip.png`.

**Variants** (all in `exports/exp04/`, AAC 256k, `-movie_timescale 48000`):

| file | picture | audio |
|---|---|---|
| v1-full-cues.mp4 | original cut | production UI stem (4 cues) |
| v2-sparse.mp4 | original cut | same minus the tap click (window t0.75–1.20 silenced) |
| v3-silence.mp4 | original cut | **no audio stream** |
| v4-music-only.mp4 | original cut | −6 dB AI bed alone |
| v5-ui-plus-music.mp4 | original cut | full mix |
| v6-hold-retimed.mp4 | +10-frame hold after the settled card (f370) | UI stem spliced: part1 + 0.334 s silence + part2 — cues retimed to the new picture |
| v7-hold-stale.mp4 | same +10-frame hold | **unretimed** segment audio — cues keep old times |
| v8-hold-silent.mp4 | same +10-frame hold | **no audio stream** |

## What was measured

Onsets (`bin/onsets.py`, ≥12 dB rise over floor):

- v1: 0.80, 1.56, 2.00, 3.27 — the four events, frame-accurate.
- v2: 1.56, 2.00, 3.27 — tap cue verifiably removed, others untouched.
- v4: floor −48 dBFS (bed present); onsets every ≈0.49 s — the music's own
  beat grid (~122 BPM groove), independent of picture events.
- v6: 0.80, 1.56, **2.33**, 3.60 — the arrival correctly shifted +0.334 s.
- v7: 0.80, 1.56, **2.00**, 3.27 — audio identical to v1; but the picture now
  reveals the bubble at ≈2.33 s. The whoosh/drop lands **0.33 s before the
  bubble exists on screen**.

Loudness: v1 −29.0, v4 −21.9, v5 −21.6, v6 −28.8 LUFS integrated (segment).

## What was machine-heard (SNClassifySoundRequest, labelled inference)

- v1: `click:0.40` across the tap window; `whoosh_swoosh_swish` 0.23–0.28 at
  send and arrival windows — event-shaped texture over silence.
- v4/v5: `music:0.83–0.92` every window — the bed reads as one continuous
  designed layer; UI clicks inside v5 are masked by the bed at production
  level (classifier no longer separates them).
- v6 vs v7: at window 1.5–2.5 s v6 shows a low-confidence gap then the
  retimed whoosh at ~2.33 s; v7 shows the whoosh a window earlier — the
  classifier tracks the retime. (No stream on v3/v8 — silence is the literal
  absence of a soundtrack, not "quiet".)

## What the cut change did to the picture (viewed frames)

At output frame 63 (≈2.1 s): v1 already shows the reply mid-arrival; v6
(`analysis/frames/v6-at-2.2.png`) still shows the settled card — 10 extra
frames of "sent and waiting". The reply then arrives at frame 70. The hold
reads as a deliberate beat of anticipation: *sent → pause → answer*.

## Verdict — which changed the felt scene more?

**The sound change, in this beat — but only clean sound change.**
Ordering by felt magnitude (reasoned from the evidence above; no human
audition available, so this is labelled judgment, not certification):

1. **v7 (stale cues over recut) feels worst** — worse than v8 silence.
   A whoosh/drop arriving 0.33 s before the bubble appears converts "designed
   tactility" into a visible sync bug: sound now *contradicts* causality.
   This is the core lesson: a recut invalidates the cue map; unchanged audio
   is not neutral, it's wrong.
2. **v1→v3 (cues→silence) is the next-largest change.** The exchange goes
   from "the interface is a physical thing that clicks and sends" to muted
   screen recording. Music-only (v4) keeps a designed feel but loses all
   action specificity — it reads as a promo bed, not a living UI.
3. **v1→v6 (the 10-frame hold, correctly retimed) is the smallest clean
   change** — a rhythmic nuance (anticipation weight), not a changed event.
   The same cue set lands identically relative to their actions.

So: **a small cut change matters less than a small sound change — until the
cut desynchronizes the sound, at which point the *combination* dominates
everything.** Cut and cue are not independent variables; the perceived event
is the pair. An editor may hold a frame for feel, but the sound must be
re-scored to the new picture version (v6) — never left stale (v7) — or
dropped deliberately (v8, clean but thinner).

## Artifacts

- Variants: `work/sound/exports/exp04/v*.mp4`
- Frame evidence: `work/sound/analysis/frames/{poke-exchange-strip,hold-check,v6-at-2.2}.png`
- Classifier dumps: `work/sound/analysis/classify-exp-*.txt`
- Segment stems: `exports/exp04/seg-*.wav`, `hold-ui.wav`
