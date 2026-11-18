# Six-film sound map — what exists, where it lives, what it actually is

Compiled by the sound agent (branch `devin-agent-sound`). Paths are relative to
this worktree unless marked `AR=` (`resources/complete-ui-audio-source-v1/imessage-recreations/audio-recreation/`).

**Method honesty note.** No human audition endpoint exists in this session. Two
evidence classes are used throughout and kept separate:

- **Measured** — ffprobe/ebur128/silencedetect/astats numbers, decoded-PCM
  statistics, packet hashes.
- **Machine-listened** — Apple's `SNClassifySoundRequest` (version1) run over
  decoded 16 kHz mono WAVs (`work/sound/bin/classify`, results in
  `work/sound/analysis/classify-*.txt`). This is a ~300-class neural audio
  tagger: real content evidence, but still not a human ear. Class labels like
  "typing" or "speech" are classifier *opinions*, noted with confidence values.

## 1. Source-film audio (the reference sound)

All six `projects/*/imessage-recreations/references/*/source.mp4` carry an AAC
stereo stream (01/04/06 at 48 kHz, 02/03/05 at 44.1 kHz). These are the
**original launch-film soundtracks** — the only "reference sound" anywhere in
the checkout. Nothing else reuses them (`reference_film_samples_reused: false`
in every ui-mix report and preview manifest).

| film | dur (s) | measured I LUFS | true peak | notable measured facts |
|---|---|---|---|---|
| 01-photonhq | 21.83 | **-7.7 LUFS** | **+1.1 dBTP** | loud master, essentially no quiet sections |
| 02-danieltian | 45.49 | -10.1 LUFS | +1.0 dBTP | silence 43.67→45.49 (1.81 s tail) |
| 03-photon-mini | 42.17 | -14.2 LUFS | **+1.4 dBTP** | silence 37.72→42.17 (4.45 s end hold) |
| 04-poke | 42.86 | -16.8 LUFS | -1.3 dBTP | quietest conservative master of the six |
| 05-linq | 48.60 | -13.4 LUFS | -0.6 dBTP | even bed, fades to tail |
| 06-gallery | 55.51 | -19.0 LUFS | -6.0 dBTP | most dynamic (LRA 7.3); last 0.52 s silent |

Machine-listened (1.5 s windows, whole film):

- **All six classify overwhelmingly as `music`/`percussion`** — the sources are
  music-led launch films, not UI-sound-led films. Confirms the earlier
  signal-only pass (`analysis/sfx-summary.json`: ~180 transients/film, most
  "music_or_percussion_likely", cue confidence ≤0.46, `auditioned: false`).
- **01-photonhq**: pure music classification; `alarm_clock:0.25` blip at 4.5 s.
  Prior UI work found **one** visible click in this film (see §2).
- **02-danieltian**: music + `tap` hits at 3.75/11.25/12.0/39.75 s, strong
  `finger_snapping:0.94` at 39.0 s, `whoosh_swoosh_swish` at 41.25 s, and a
  `sigh:0.62`/`breathing` segment at ~42 s (into the silent tail — likely the
  music fade's noisy decay; flag as ambiguous, not as dialogue).
- **03-photon-mini**: `glass_clink:0.50` + `whoosh` at 36.75 s, then
  `writing`/`typing`/`typewriter` at 37.5 s — this coincides with the source's
  visible typing block; plausible real typing SFX in the source mix. `chime` at
  31.5 s. Classifier confidence moderate; treat as "probable source UI sounds".
- **04-poke**: `whale_vocalization`/`whoosh`/`water` at 0.0 s (filtered sweep
  intro), `speech:0.14–0.24` at 16.5/24.0 s — consistent with the fal model's
  "nonlexical vocal-like chops" note; not certified speech. A `whoosh` at
  ~5.25 s may be a send sound.
- **05-linq**: no non-music classes cleared threshold; `firecracker`/
  `person_shuffling` hits are percussion misreads. Source UI sounds, if any,
  are buried in the music mix.
- **06-gallery**: `chime`/`bell` at ~21 s; `foghorn`/`didgeridoo` labels on the
  low pad sections. The removed live-action stretch (34.97–41.0 s) sits inside
  the music bed.

**What the source sound design is (best supported reading):** continuous
produced music tracks (genre per `analysis/music-briefs.md`: funk-pop, minimal
tech-house, chill-hop, etc.) with *sparse* diegetic UI accents in at least 03
(probable typing+clink) and 02 (taps/whoosh); the other four show no separable
UI layer above the music — either absent or fully masked.

## 2. Recreated audio deliverables (independent, no reference samples)

Two production lines exist, both **original** — nothing was lifted from the
source soundtracks:

### A. `AR/ui-mixes/<id>/` — frame-grounded UI sound (primary per skill)

- `ui.flac` / `ui.m4a` — UI-only stem at production levels, cues placed on
  *observed action frames* (canonical schedules, `AR/ui-cues/canonical-*.json`,
  hashed). 48 kHz stereo, exact picture sample count.
- `ui_preview.m4a` — the same stem boosted +4.7…+9.0 dB purely for audition
  (`audio_audition_boost: true`); production files keep designed gain.
- `music.flac` / `full_mix.flac` — optional AI-music bed at −6 dB and its
  union with UI; full mixes are deliberately **not** re-normalized to −16 LUFS.
- `report.json` — per-event routing: asset, license, gain, pan, sample offset,
  alignment (`dominant_early_attack_peak` for keys/clicks, onset for movement),
  `alignment_error_samples` (0 observed).
- `AR/ui-previews/<id>-ui.mp4` (boosted UI over accepted picture) and
  `<id>-recreated.mp4` (full mix over picture) — muxed review exports; video
  packets copied untouched, packet-hash-verified in the sidecar `.json`s.

### B. `AR/mixes/<id>/` — "-16 LUFS music-led mix" line

- Only `music.flac` (the AI-generated bed at final gain) is present in this
  checkout per film; the `full_mix.flac`/`sfx.flac`/`.m4a` exports are
  described in `mix-report.json` but are not in the bundle (delivered
  separately; bundle audit notes it). This line uses sparse *procedural*
  accents (10–23 events/film chosen from proposal cue sheets) rather than the
  canonical UI schedules — a different, earlier recipe.

### Cue routing observed across all six ui-mixes (measured from report.json)

| canonical kind | rendered as | provenance |
|---|---|---|
| typing / typing_burst / delete | `key_*.wav` single-key recordings | unicaegames Keyboard Soundpack #1, CC0 (Cherry KC1000, SM7B; filename-level categories only — no physical-key claim) |
| message_arrival | `kenney_drop_001.wav` | Kenney Interface Sounds, CC0 |
| tap / text_select / cart_update | `kenney_click_001`, `kenney_select_001`, `kenney_tick_001` | Kenney, CC0 |
| message_send, panel_open/close | `original_procedural_fallback` | new synthesis (ui_synth.py), no samples |
| control_appear | `silent_visual_state` | deliberately silent (2 events: 03, 04) |

Events: 01=1 tap; 02=45 (22 typing,10 burst,3 send,10 arrival); 03=45 (44
audible); 04=35 (34 audible); 05=41; 06=18 (13 arrival,5 send). Total 185
visual events, 183 rendered, 2 intentionally silent.

Music inputs: `AR/ai/<id>/music.mp3` + `provenance.json` — ElevenLabs Music
v2.5 via fal, text-prompt-only generation (`reference_audio_used_as_generation_input:
false`), one pinned file per film, sha256'd in mix reports.

Procedural bank: `AR/synthesis/bank/` — 10 declared effects (air_whoosh,
bubble_pop, card_swoosh, digital_sparkle, glass_confirm, key_tap, low_impact,
touch_click + audition file), code-pinned.

Licenses: `AR/library/licenses/` (Kenney-License.txt, Keyboard-CC0-evidence.txt
with source-page hash b078a1da…); original archives in `library/archives/`;
prepared 48 kHz stems in `library/prepared/` with original+prepared sha256.

## 3. Export inventory — reference vs independent vs silent

| material | contains reference sound? | status in checkout |
|---|---|---|
| `references/*/source.mp4` audio | yes — it IS the reference | present (6/6) |
| `AR/ui-mixes/*/ui.flac/.m4a` | no — new stems | present (6/6) |
| `AR/ui-mixes/*/music.flac`, `full_mix.flac` | no | present (6/6) |
| `AR/mixes/*/music.flac` | no | present; sfx/full_mix stems absent from bundle (report-described) |
| `AR/ui-previews/*-ui.mp4` | no (boosted UI) | present (6/6) |
| `AR/ui-previews/*-recreated.mp4` | no (UI+music) | present (6/6) |
| `LOCAL-LIBRARY.json` deliverables (`deliverables/*/{remotion,gsap,html,motion-canvas,pillow}.mp4`) | n/a | **not synced** — only source.mp4 files are on disk (6 files total under projects/) |
| silent masters | none — every export with a stream has signal; `control_appear` events are intentional per-cue silences inside stems | — |

## 4. Known limits carried forward (from the library's own audits)

- The canonical schedules describe the *recreated* picture's frames, which are
  accepted as matching the source's motion; a documented 12-frame discrepancy
  exists for 04-poke's restaurant selection (source 633 vs accepted 645 — new
  sound follows the delivered picture).
- The `mixes/` line predates the frame-grounded UI line; its SFX timings were
  model-proposal transients at ≤0.46 confidence, not observed actions.
- AAC codec overshoot documented (see reconstruction-workflow.md §8):
  112 kbps turned a −2.56 dBTP PCM master into +0.80 dBTP with 2 clipped
  samples; 256 kbps stayed −2.47 dBTP. Always measure the encoded artifact.
- Sources 01–03 master above 0 dBTP (+1.0…+1.4) — the originals themselves
  clip inter-sample. Do not treat "match the reference loudness" as a target.
