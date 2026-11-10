# Linq05 / Rene06 visual UI cue sheets

These files target UI micro-sounds only. They use accepted visual states, independently measured glyph/component timing, and semantic scene data. Source music transients are not treated as keyboard, tap, send, or arrival evidence. No audio, library asset, source scene, movie, cache, site, Git or paid service was changed.

The canonical inputs are Linq `outputs/05-linq/final-v20/scene.json` and Rene `outputs/06-gallery/final-v23/scene.json`; their SHA256 fingerprints and supporting builder fingerprints are in `05-06-evidence-and-validation.json`. All event frames are zero-based **OUTPUT native frames**. Both videos use 30 fps. `time` is `frame / 30`, and `sample_offset_48000` is an exact 48 kHz placement aid, not a rendered audio file.

## Files and recommended defaults

- `05-linq-ui-cues.json`: 41 recommended visual cues — 23 typing, six taps, four sends, eight arrivals. Three navigation/touch interpretations are separate optional inferred events.
- `05-linq-keypress-schedule.csv`: only the 23 observed human draft glyph events, ready for individual keyboard UI effects.
- `06-gallery-ui-cues.json`: 18 recommended visible message cues — five sends and 13 arrivals. Two opening/camera-reveal interpretations are separate optional inferred events.
- `06-gallery-keypress-schedule.csv`: header only, deliberately. A visible static keyboard/empty composer does not establish keystrokes.

Use `events` by default. Do not automatically mix `optional_inferred_events`. Their action/contact timing is not independently shown, and each includes a confidence, evidence and timing bracket. No sound is claimed to have been directly observed in the original audio; “observed” refers to visual UI state. A sound aligned to that state is a reconstruction decision.

## Exact Linq typing observations

The human composer reads `Yo i'm bored, chess battle?`. Its 23 non-space original glyph paths are independently revealed at frames:

`23, 25, 30, 31, 34, 39, 40, 43, 45, 48, 50, 54, 56, 59, 61, 64, 69, 70, 73, 75, 78, 80, 83`.

The generator reads the actual canonical `v19-type-glyph-*` start/semantic data and verifies that the concatenated glyphs equal the full draft without spaces. These are first visible character frames with one-frame visual precision, not physically filmed key-downs. The four spaces have no independently visible ink onset. Their surrounding visible-frame windows are recorded under `unresolved_input_operations`; no extra exact space keystrokes are invented. `draft_after` retains the actual spacing so the input state is reviewable.

The completed draft held/moved after frame83 is not typed again. Composer retirement/send is not backspace. There are no observed delete events. The first chess attachment/copy bundle is one send cue around frames149–151, avoiding two artificial sends for one visual message bundle.

## Grounded tap responses

Linq's chess selection becomes strong at frame216 (selection alpha about .017→.980), and its corrected white pawn/selected-cell transition begins at228. These are UI-response clicks; no finger/pointer contact is shown.

Cash has four distinct plus-control gray/pulse responses at frames786,791,796,802, followed by amount-rail jumps at787,792,797,803. The amount advances `$162.89 → $163.89 → $164.89 → $165.89 → $166.89`. Each cue records the response-to-amount one-frame bracket, actual fill values, and both canonical control/rail node evidence. These are taps, not typed digits. Opponent chess moves, rolling amount material, caret blinks and general camera motion are not extra UI keystrokes.

## Rene message and typing limits

Rene's visible initial composer/keyboard is a static empty iMessage UI bitmap. “Book it,” “Yes plz,” birthday reactions/orders and “LETS GOOOO” enter as outgoing bubbles; their prior human draft changes are not shown. No fake character schedule or invented typing burst is emitted. Incoming AI message bodies receive arrival cues only, not keyboard sounds. Marketing titles, email/photo motion, provider icons and end-copy animation are excluded from typing and taps.

The five birthday message entrances at714,734,745,770,781 come directly from the accepted23 source-measured UI birth data (half-opacity first picture then full). The preexisting Emma bubble travels with the entering phone and is not asserted as a new arrival. Likewise, the landlord notification is already in a moving lockscreen: an optional inferred reveal cue425 is separate, and the same content's thread reframe461 is explicitly suppressed to avoid a double ping. Rene's later comparison, Yes and draft-ready messages have distinct visible births485,499,512.

Rene omits original source frames1049–1229. Output0–1048 maps identically; output1049 onward maps to source frame `output + 181`. Thus output1049 is source1230, and output1482 is source1663. This mapping is stored and validated even though all recommended interactive-message cues occur before the live-action cut. No event uses original source time in place of output time.

## Derivation and validation steps

1. Read and fingerprint both immutable accepted scenes; index node IDs, JSON pointers, global lifetimes and opacity starts.
2. Read Linq's actual per-glyph semantic/start data. Reconstruct the draft, preserve whitespace uncertainty, and emit one event per observed visible glyph.
3. Match incoming/outgoing bubble entries to their canonical semantic component lifetimes and first nonzero visual opacity. Group a card plus copy where a second cue would double the same send.
4. Cross-check Cash's real control response and amount rail; use the accepted corrected pawn transition and selection data rather than older mistaken trajectories.
5. Inspect retained native frames for Rene's empty composer, actual birthday text, notification carried by camera and completed message states. Treat camera-only reveals separately from an observed UI birth.
6. Exclude AI/body/title typing, duplicated static drafts, blinks, amount rolls and clears around sends. Keep low-confidence navigation cues outside the default event list.
7. Validate kind vocabulary, frame/time bounds, source mapping, typing count/draft reconstruction and canonical input hashes after generation.

`05-06-build-cues.py` is deterministic and writes only these owned cue files. It does not load an audio track. The outputs distinguish measured visible alignment from inferred physical action and unobserved original sound.
