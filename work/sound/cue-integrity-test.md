# Cue-integrity test — does a fresh-agent review catch a damaged export?

**Delivered export under review:** `ui-previews/04-poke-ui.mp4` (accepted
picture + boosted UI stem, AAC 192k). Canonical schedule:
`ui-cues/canonical-04-poke.json` (35 events; 1 intentionally silent).

**Planted defects** (files in `work/sound/integrity/`):

- **D1 — shifted cue.** The tap at 11.311 s (frame 339, "Indian option")
  moved +200 ms → 11.511 s. Surgery: carve 11.27–11.85 to a gap, re-insert
  0.2 s later, drop 0.2 s of the following inter-cue silence so every other
  cue stays put. Result: onset at 11.51, hole at 11.31, all other onsets
  bit-identical in time. Encoded AAC 192k, video stream-copied
  (`integrity/d1-shifted.mp4`, audio 42.809396 s vs picture 42.809433 s).
- **D2 — wrong-category swap.** The send whoosh body (12.05–12.35) replaced
  with the tap click recording (same ~level) — a plausible authoring bug:
  right time, right loudness, wrong sound (`integrity/d2-swapped.mp4`).

## Review path & results

| check | clean | D1 (shift +200 ms) | D2 (whoosh→click) |
|---|---|---|---|
| ebur128 I LUFS | −23.3 | −23.5 | −24.7 |
| true peak | −5.0 dBTP | −5.0 dBTP | −5.0 dBTP |
| stream/duration | ok | ok | ok |
| machine classify (1 s windows) | click@11.0, whoosh@11.5–12.0 | same labels — **miss** | whoosh stays top label but `click` rises at 11.5–12.0 — **weak signal only** |
| **cue_check.py vs canonical sheet** | 34/35 (1 = intentional silence) | **CAUGHT**: `tap` FAIL (rise 0 dB) + unexpected onset at t=11.495 (+184 ms measured) | passes — attack present at right time (not its job) |
| **kind fingerprint** (ZCR/crest/window-RMS in [t, t+0.4 s]) | matches declared kinds | tap slot: click fingerprint, still present — consistent w/ D1 once onset is flagged | **CAUGHT**: send slot shows ZCR 0.018 / crest 33 / −38.5 dB vs whoosh class ZCR ≈0.15 / crest ≈8 / ≈−25 dB |

## What caught what — honest summary

- **Loudness/peaks/duration caught nothing.** Content-identical defects are
  invisible to delivery stats. This is expected — a shifted cue is not a
  loudness defect.
- **The machine classifier alone missed the 200 ms shift.** At 1 s windows
  a late click is still a click in the same window. It gave only a weak,
  easy-to-miss hint for D2 (label ordering change).
- **cue_check (action↔onset correlation) caught D1 decisively**: the
  expected slot shows zero rise (a hole), and an unexplained onset appears
  +184 ms later. Two independent flags from one measurement.
- **cue_check passed D2** — timing/presence is blind to timbre. The kind
  fingerprint (zero-crossing rate, crest factor, window RMS in a 0.4 s
  window) is the designed complement: three declared classes separate by an
  order of magnitude (whoosh ZCR≈0.15 / click≈0.012 / drop≈0.054; crest
  ≈8 / ≈33 / ≈18). D2's swapped slot reads click on every metric.
- The one standing "failure" on the clean file is `control_appear@15.18` —
  the intentionally silent control. Cue sheets must mark intentional
  silence (`silent_visual_state`) so the check whitelists it rather than
  training reviewers to ignore failures.

## Measured limit — the check under a continuous music bed

Same test run on `04-poke-recreated.mp4` (UI + −6 dB music bed, not the
boosted UI): floor rises to −54.5 dBFS and the detector still resolves
**32/35** cues, but (a) two mid-burst typing events and one quiet arrival
are masked below threshold, and (b) ~8 music-beat transients report as
"unexpected onsets" (they're the bed's ~0.49 s percussion grid, not
defects). **Verdict: run cue-integrity on the isolated UI stem — that is
what stems are for — and treat full-mix checks as advisory unless
thresholds are kind/level-adapted or beats are whitelisted.** A
music-led export cannot certify frame-exact cue timing by this check alone;
the stem can, and the stem is an editable deliverable.

## The check a fresh agent should run (now encoded in the workflow)

1. `cue_check.py <export-audio> <canonical-cue-sheet>` → every declared cue
   produces an attack within ±120 ms, no unexplained onsets; silent-flagged
   events must show silence.
2. Kind fingerprint per declared event: ZCR + crest factor + RMS in the
   post-onset window vs the kind's expected envelope family (whoosh/click/
   drop/key measured above). Catches wrong-asset and decay-truncation bugs.
3. Machine-listened pass (`bin/classify`) over the export → texture sanity
   (typing reads typing, sends read whoosh, no music where none was
   designed) — complements, cannot replace, 1+2.
4. Standard delivery stats (LUFS/TP on the DECODED export) for codec damage
   only — see the 112 kbps AAC +0.80 dBTP evidence; never as a sync check.
5. Human listening when an endpoint exists — none in this session.

## Artifacts

`integrity/delivered-audio.wav` (decoded delivered audio),
`integrity/d1-shifted.{wav,mp4}`, `integrity/d2-swapped.{wav,mp4}`,
tools `bin/onsets.py`, `bin/cue_check.py` (exit 1 on fail),
`bin/classify` (Swift/SNClassifySoundRequest).
