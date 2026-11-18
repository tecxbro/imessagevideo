# Faithful sound reconstruction workflow (reference → verified export)

For: given a reference film **with sound**, rebuild a soundtrack that serves
the *delivered* picture. Written for agents working in this environment
(ffmpeg/ffprobe, python3 stdlib, no numpy assumed; optional Apple
SNClassifySoundRequest tool at `work/sound/bin/classify`).

The governing question is not "does it measure like the reference" but
"does each audible moment land on the visible action the viewer sees."

## 0. Honesty contract (read first)

- A spectrogram is not listening. Report **heard** (human or machine
  classification, labelled) separately from **measured** (numbers).
- Never mux the original reference soundtrack into a "recreated" export.
  `reference_film_samples_reused` must stay `false` in your reports unless
  the source license explicitly allows reuse and the user wants it.
- Hash everything: source, picture file, cue sheet, code, stems, exports.

## 1. Inventory the reference's audio events

1. Decode the reference audio once to a working WAV (mono 16 kHz for
   detection, stereo 48 kHz for spectral checks). `ffprobe` the real stream:
   codec, rate, duration vs picture duration (AAC tails can exceed picture).
2. Measured pass:
   - `ebur128=peak=true` → integrated LUFS / LRA / true peak of the source
     (note: sources 01–03 here master *above* 0 dBTP — loudness is not a
     target to copy).
   - `silencedetect=n=-45dB:d=0.3` → intentional quiet holds and tails
     (02 ends silent 1.8 s; 03 holds 4.45 s silent; 06 last 0.5 s).
   - `work/sound/bin/onsets.py` (or astats-metadata pass) → transient times.
   - Spectrogram (`showspectrumpic`) for band structure only — describe what
     is seen, not heard.
3. Machine-listened pass: `bin/classify <wav>` → per-window class labels.
   In these films the sources classify ~90 %+ as music/percussion; isolated
   `typing`, `whoosh`, `chime`, `tap`, `speech`-ish labels mark candidate
   diegetic cues. Keep label + confidence + time; low-confidence labels are
   hypotheses, not facts.
4. Sort every candidate event into: **music bed**, **percussion/beat**
   (recurring grid — see `analysis/sfx-summary.json`: most of ~180
   transients/film were music), **UI/diegetic effect**, **voice**,
   **ambience**, **intentional silence**. A transient on a beat grid is
   percussion until proven otherwise.

## 2. Map each event to a visible action — on the DELIVERED picture

- Inventory visible actions at *native frame indices* of the accepted
  picture file (frame-exact, from scene descriptions or frame stepping):
  typing batches, sends (composer clears), arrivals (bubble animates in),
  taps, selections, panel opens/closes, control appearances.
- Apply the picture edit map BEFORE writing cue times. The library lesson:
  04-poke's restaurant selection sits at source frame 633 but delivered
  frame 645 — **sound follows the delivered frame**, preserving the
  documented 12-frame discrepancy. 06-gallery removes source 34.9667–41 s:
  subtract the cut from post-cut cues and never leave a sound for removed
  picture.
- Rules that kept the canonical schedules honest (from
  `references/ui-audio-workflow.md`): keys only for visible composer text
  changes, keep real pauses, one key per observed batch, no keys for
  titles/AI replies/caret blinks, a selected-phrase delete is one action,
  controls merely appearing can stay silent.

## 3. Decide per event: lift / license / synthesize / silence

| decision | when | provenance duty |
|---|---|---|
| lift reference audio | almost never — only if the reference itself is yours/licensed for reuse | keep source hash, license text, edit points |
| licensed library effect | a real UI sound exists (click/tap/key/drop/select/tick) | keep source URL, license file, original+prepared sha256 — a public download is not itself a license |
| licensed field recording | physical actions (keys) — here: unicaegames pack, CC0, Cherry KC1000/SM7B | filename-level categories only; no "physical key = letter" claims |
| procedural synthesis | movement/transitions/sends/whooshes | code-pinned (`synthesis/ui_synth.py` sha), seeded params |
| deliberate silence | control appearances, quiet holds the picture already sells | record it in the cue sheet as `silent_visual_state` |

Music: prefer **new** material (see original-scoring.md). Do not recreate the
reference's tune or sample its bed; a text-only generation prompt with
measured tempo/arc guidance is what the mixes line used (ElevenLabs v2.5 via
fal, one pinned file per film, `reference_audio_used_as_generation_input:
false`).

## 4. Build the stems

- 48 kHz stereo, exactly `picture_frames / fps` long — derive sample count
  from rational fps (`frames * 48000 * fps_den // fps_num`).
- Alignment: keys/clicks align **dominant early attack peak** to the action
  frame; movement/whoosh align **onset**. Record `event_sample`,
  `clip_alignment_offset_samples`, `alignment_error_samples` per event
  (the accepted reports show error 0).
- Prepare single events, not loops: decode licensed sources to 48 k stereo,
  trim, declick boundaries, remove DC, leave headroom (~-18 dBFS cue peaks
  in accepted UI stems).
- Keep stems separate: `ui`, `music`, (`voice`, `ambience` if present) —
  editable, version-tied: record picture sha256 + fps + frame count in the
  cue sheet and every report.

## 5. Mix

- UI-first: render the UI stem before any loudness talk; sparse stems are
  never normalized to program LUFS targets.
- Music bed quiet and optional: accepted full mixes sit ≈ -22 LUFS
  (music −6 dB under the older -16 LUFS line) with overlap-capped ducking
  (max ≈1.2 dB, never summed).
- Provide a **labelled** boosted UI-only audition (ui_preview +4.7–9 dB) —
  never ship the boost as production gain.

## 6. Encode — then measure THE ENCODED FILE, not the PCM master

Documented failure kept honest: a FLAC music stem measuring **−2.56 dBTP**
re-encoded to **+0.80 dBTP at 112 kbps AAC (2 clipped samples)**. Same
encode at **256 kbps: −2.47 dBTP**; 192 kbps: −0.98 dBTP. Loudness barely
moved (−15.9 LUFS all) — only true peak betrayed the codec overshoot.
Evidence: `AR/mixes/01-photonhq/aac-headroom-diagnosis.json`,
`mixer-steps.md` entry 4. Also entry 5: MP4's default 1000 Hz movie
timescale rounded 21.833333 s → 21.833 s (16 samples short); use
`-movie_timescale 48000` (or audio rate) so container duration is exact.
Rules:

- Encode hot content at ≥256 kbps AAC (or accept the measured margin);
  quiet SFX stems are empirically fine at 112–192 kbps — but measure anyway.
- Always re-measure integrated LUFS **and true peak** on the decoded
  artifact; allow codec-driven correction only as one bounded, recorded
  gain (e.g., `common_peak_guard_gain_db`).
- Mux with explicit stream mapping (`-map 0:v -map 1:a -c:v copy`) so no
  source-film audio leaks in; verify video and AAC packet hashes survive
  muxing (see `ui-previews/*.json` for the proof format).

## 7. Verify in the delivered export

Ordered checks a reviewer can run (tools in `work/sound/bin/`):

1. `ffprobe`/`ebur128` on the decoded export — duration, LUFS, TP in bounds.
2. **Action↔onset correlation**: `cue_check.py <export-audio> <cue-sheet>`
   — every expected event must show an attack within tolerance
   (default ±120 ms window, >10 dB over floor), and no unexpected onset may
   appear. Whitelist events marked `silent_visual_state` — the check flags
   them (correctly: silence fails an attack test) so tag, don't waive, them.
3. Machine-listened spot check: `classify` the export — typing stretches
   should classify as typing-ish, sends as whoosh-ish, silence as low-
   confidence mush; music-bed exports classify as music. A wrong label or
   a missing stretch is a review finding.
4. Human listening when an endpoint exists — state plainly when it does not.
5. Packet hashes + `finite PCM + endpoints_zero + no clipped samples` stats.

## 8. Deliver & document

- Cue sheet = event list w/ frame, time, kind, routing, license/synth
  provenance, alignment basis, picture sha256+fps.
- Report = measured stems, measured encoded exports, ducking/normalization
  actuals, validation list, and a plain-language "what you will hear"
  section written from the classifier/listening pass.
- Immutable acceptance: keep prior accepted exports; new work goes to a new
  folder; log observed failure → likely cause → changed variable → evidence.
