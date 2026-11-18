# Original scoring workflow — sound for NEW material (no reference track)

For: an agent given a picture-locked film with **no existing soundtrack**
(or told to replace one). Goal: decide what the film needs, source it
legally, keep it editable, and tie it to the exact delivered picture.

## 1. The five-layer decision — take them in this order

**UI/diegetic effects are never optional when the screen acts.** If fingers
type, messages send, bubbles arrive, sheets open — those moments need sound
or a deliberate, recorded silence. This layer carries the "the interface is
real" feeling; in the library films it is *the* soundtrack (see
treatment-experiment.md: stripping cues gutted the scene more than a recut).

Then decide the rest by what the picture is doing:

| layer | use when | skip when |
|---|---|---|
| **music** | the film is a *launch/promo* statement — motion itself is the content, energy arc sells the product | the film is a walkthrough/demo where clarity beats hype; or timing is dense — a bed over busy UI turns to mush |
| **voice** | narration/dialogue exists or is commissioned — script first, record/clear-rights, then cut picture to voice | you cannot produce a clean take with rights — never fake VO with unclean sources |
| **designed effects** | non-UI moments need identity: logo resolves, title slams, transition whooshes, the "brand" sounds | every whoosh on every cut — restraint is the difference between designed and noisy |
| **ambience** | scenes imply a place (live-action, room, outdoors) or a silence that feels dead needs air | pure-screen UI films — a room tone under an iMessage screen usually reads as noise floor, not depth |
| **silence** | as a *choice*: pre-drop hush, logo hold, a control appearing (see canonical `silent_visual_state`) | never as an accident — an unscored moment you didn't decide about is a bug, not a choice |

Practical rule that held up in the audit: the six original films are
music-led (continuous beds, LUFS −8…−19) with only sparse diegetic accents;
the library's recreated deliverables are **UI-led with an optional quiet
bed** (−6 dB music under production UI). For a *recreation skill*, UI-first
is the defensible default: it survives a missing-music request and never
needs the "why does the bed not match" apology.

## 2. Where sounds come from in this environment (verified this session)

| source | what | license status |
|---|---|---|
| `resources/complete-ui-audio-source-v1/.../library/prepared/` | 25 Kenney interface effects + 12 single-key recordings, 48 kHz trimmed | **CC0** — license texts + source-page evidence + hashes in `library/licenses/` |
| `resources/.../library/sources/`, `archives/` | original downloads | kept for provenance; prefer `prepared/` for clean boundaries |
| `resources/.../synthesis/bank/` | 10 procedural effects (whooshes, pops, confirms) | original synthesis, code-pinned — clean by construction |
| ffmpeg synthesis (`anoisesrc`, `sine`, `aevalsrc`, filters) | any transitional texture, UI ticks, simple beds | generated on the spot — clean; document the command |
| `work/sound/bin/classify` (Apple SNClassifySoundRequest) | machine-listening QA on your own stems | local, no network |
| paid/AI generation (e.g. music via fal/ElevenLabs) | optional beds | used by mixes line: **text-prompt only, never reference-conditioned**, pin the returned file + request id; a regenerated prompt is NOT reproducible — treat the output file as the master |
| the reference film's own audio | — | **not a source** unless its license is in hand; presence of a file ≠ permission to reuse |

If you must fetch new libraries: prefer CC0/PD sources with archived
license pages (kenney.nl, opengameart entries), record URL + license file +
sha256 + download date. A public download is not a license — the *license
text* is the license.

## 3. Build the score

1. **Lock the picture version.** Record file sha256, fps (rational), frame
   count, exact duration. Every cue is in *this* file's frame numbers.
   (`cue_check.py` uses the same sheet; if the picture changes, the sheet
   must move.)
2. **Inventory visible actions at native frames** — same rules as
   reconstruction: keys only for composer changes, one key per batch,
   sends/arrivals/taps/sheets from observed transitions, controls appearing
   may stay silent. Get onsets from the scene description or frame steps,
   not from audio (there is none yet).
3. **Assign each event a layer and a source**: licensed asset id /
   procedural effect / generated / silent — with gain, pan, alignment basis
   (keys/clicks: dominant early attack peak; movement: onset).
4. **Render stems separately**: `ui`, `design`, `music`, `voice`,
   `ambience` — 48 kHz stereo, exact picture span, finite PCM, zeroed
   endpoints. Stems stay editable: per-event placement metadata, not a
   flattened render, is the deliverable's source of truth.
5. **Mix restrained**: UI at production level (~-18 dBFS cue peaks), bed
   −6 dB-ish under, ducking capped ≤~1.2 dB, never normalize sparse stems
   to a loudness target. Label any boosted audition copy.
6. **Score transitions and holds deliberately**: a logo hold can take a
   soft resolve + tail or honest silence — decide, don't drift. The library
   kept 03's 4.45 s silent tail and it reads as intended.
7. **Mux explicitly** (`-map 0:v -map 1:a -c:v copy`,
   `-movie_timescale 48000`) and verify packets unchanged.

## 4. Verify like delivery depends on it (it does)

- `cue_check.py <export> <cue-sheet>` — every scored event lands within
  tolerance; unexplained onsets flagged; intentional silences whitelisted.
- Kind fingerprints (ZCR/crest/window-RMS) per event — wrong-asset and
  truncation bugs (see cue-integrity-test.md for real catches).
- `classify` the stems and the muxed export — texture sanity, and the only
  "listening" available when no human endpoint exists.
- True peak measured on the **encoded** artifact — 112 kbps AAC overshot a
  −2.56 dBTP master to +0.80 dBTP; use ≥256k for hot content and re-measure.
- Stems + cue sheet + code snapshot + hashes archived so the score can be
  rebuilt or edited after picture changes.

## 5. If the picture recuts after scoring

Re-derive the sheet, don't nudge it by hand: events are *attached to
frames*, so the map is (old frame → new frame) → new times. Anything you
can't map gets re-inventoried, not interpolated. Then re-verify. The stale-
audio variant in treatment-experiment.md shows what an unmapped cue sounds
like: a whoosh before the bubble — worse than silence.
