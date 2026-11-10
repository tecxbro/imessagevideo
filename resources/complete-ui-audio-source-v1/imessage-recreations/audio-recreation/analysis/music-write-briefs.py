#!/usr/bin/env python3
"""Build concise original-score briefs from the adjacent completed measurements."""
from pathlib import Path
import hashlib
import json

OUT = Path(__file__).resolve().parent
DIRECTIONS = {
    '01-photonhq': {
        'working_bpm': 109,
        'rhythm': 'Compact syncopated electronic pulse; keep the strong approximately0.55s recurring accent, with occasional dotted figures rather than a dense fill at every UI move.',
        'palette': ['syncopated rounded synth bass', 'crisp kick and snare/clap', 'short bright synth chord stabs', 'small original percussive detail'],
        'arc': 'Start clean and immediately legible; add body around5s, sustain the lift through19s, resolve around19.8–20s and let the tail fade to21.833s.',
        'anchors': [1.869, 4.8622, 8.1348, 13.5924, 17.4037, 18.2318],
        'prompt': 'Compose a NEW21.833-second instrumental electronic product-launch cue at approximately109BPM. Use a new syncopated synth-bass idea, crisp compact kick and snare/clap, short bright chord stabs and small original percussive details. Bright, nimble and controlled is the requested creative direction. Build gently after5s, keep the strongest momentum in the middle, then resolve around20s with a short clean tail. Leave room for separate UI sound effects. No voice, humming, lyrics, recognizable borrowed tune or reference-audio sampling.',
    },
    '02-danieltian': {
        'working_bpm': 123,
        'rhythm': 'A123BPM grid with some dotted-quarter accents produces an approximately82BPM accent stream, near the measured81.27BPM period; preserve that metrical ambiguity as a spacious groove rather than declaring an exact source meter.',
        'palette': ['deep pulsing synth bass', 'punchy electronic kick', 'sharp snare/clap and crisp hi-hat', 'short original non-tonal percussive motif', 'sparse synth harmony'],
        'arc': 'Keep0–11s restrained, build11–22s, use the fullest body22–34s, then thin out after40–41s and decay to45.333s.',
        'anchors': [2.6173, 6.7978, 13.9316, 20.3271, 24.2581, 32.6191, 38.2763, 40.2418],
        'prompt': 'Compose a NEW45.333-second instrumental technology-demo cue on an approximately123BPM grid with spacious dotted-quarter accents. Start with a sparse filtered pulse and deep controlled bass, gradually add a punchy kick, sharp snare/clap, crisp hats and a new non-tonal percussive motif, reach a fuller middle around22–34s, then strip the rhythm near41s and resolve into a clean tail. Make a new motif and harmonic form. Keep melody subordinate to the motion and allow separate UI effects. No voice, lyrics, humming or reference-audio samples.',
    },
    '03-photon-mini': {
        'working_bpm': 118,
        'rhythm': 'A clear approximately118BPM pulse with light syncopation and occasional three-against-two/dotted accents; this is the strongest bass-and-broadband agreement of the six measurements.',
        'palette': ['tight rounded synth bass', 'crisp electronic drums and shaker-like percussion', 'small staccato pluck motif', 'airy synthetic chords', 'brief original transition fills'],
        'arc': 'Introduce lightly, lift after8–10s, maintain an active middle through36s, resolve37–39s and reserve39–42s for a very quiet tail or final hold.',
        'anchors': [4.4332, 8.0849, 16.1566, 20.5665, 27.9697, 30.7434, 34.7842, 36.3008],
        'prompt': 'Compose a NEW42-second instrumental mini-app launch cue around118BPM. Use tight rounded bass, short tactile percussion, a playful original bell/pluck idea and soft synthetic chords. Keep it buoyant but uncluttered. Lift after8s, maintain an active pulse through the demonstrations, resolve around38s and leave a very quiet tail for the final39–42s hold. All notes and sound design must be newly created. No voice, singing, humming, lyrics or borrowed source samples.',
    },
    '04-poke': {
        'working_bpm': 123,
        'rhythm': 'A123BPM electronic grid with a relaxed half-time61.5BPM weight; both periodicities are strong, so do not force a busy fast beat.',
        'palette': ['bouncy rounded synth bass', 'compact electronic kick and clap', 'light shaker/hi-hat', 'short synth plucks', 'new formant-filtered oscillator pulses with no voice source'],
        'arc': 'Keep a steady understated bed across0–32s, allow a small late lift around32–38s, then soften41–42.809s.',
        'anchors': [8.1448, 12.0758, 19.9479, 27.82, 31.8708, 38.1466, 40.1121],
        'prompt': 'Compose a NEW42.809-second instrumental launch cue around123BPM with a relaxed half-time feel. Favor bouncy rounded synth bass, compact electronic kick and clap, a light shaker/hat pattern and short synth plucks. Add a few newly synthesized formant-filtered oscillator pulses for rhythmic color, using no voice or vocal sample. Understated, friendly and precise is the requested creative direction. Keep the groove consistent rather than building to a cinematic drop; add only a modest late lift, then taper over the last2s. Leave space for message and interface sounds. No voice, humming, lyrics, recognizable tune or reference-audio samples.',
    },
    '05-linq': {
        'working_bpm': 96,
        'rhythm': 'A relaxed approximately96BPM pulse with gentle syncopation; approximately64BPM dotted/metric alternative remains plausible from the mixed audio.',
        'palette': ['rounded low synth bass', 'dry soft kick/snare', 'mellow keyboard chords', 'brief light pluck detail', 'subtle stereo texture'],
        'arc': 'Establish the pulse quickly, keep a modest middle lift around12–36s, then reduce density after43–44s and fade to48.6s.',
        'anchors': [6.1693, 13.0736, 18.0722, 26.8223, 32.7588, 39.3239, 42.7561],
        'prompt': 'Compose a NEW48.6-second instrumental product-demo cue around96BPM. Use rounded low synth bass, restrained dry drums, mellow keyboard chords and a small original pluck detail. Make the creative feel confident, warm and lightly syncopated. Maintain a smooth middle lift without a huge drop, begin reducing layers near44s, and end with a clean fading cadence at48.6s. Keep upper frequencies restrained and leave space for UI effects. Entirely new motif and harmony; no voice, lyrics, humming or reference-audio samples.',
    },
    '06-gallery': {
        'working_bpm': 134,
        'rhythm': 'A134BPM light pulse with a spacious67BPM half-time feel; the approximately0.45s and0.90s periodicities are both strongly measured.',
        'palette': ['rounded rhythmic synth bass', 'clean drum-machine kick and snare/clap', 'bright original plucked arpeggio', 'filtered airy pads', 'new formant-filtered oscillator pulses with no voice source'],
        'arc': 'For the cut49.433s picture, build gently through12s, use the fullest body12–30s, simplify30–44s, then resolve and decay44–49.433s. Compose continuously across output34.9667s; do not insert a gap for the removed source section.',
        'anchors': [9.4019, 13.4327, 21.4944, 28.6581, 30.4541, 36.0643, 39.4067, 43.8965],
        'prompt': 'Compose a NEW49.433-second instrumental product-story cue around134BPM with a spacious67BPM half-time feel. Use rounded rhythmic synth bass, clean drum-machine kick and snare/clap, a new bright plucked arpeggio and filtered airy pads. Replace any vocal-chop character with newly synthesized formant-filtered oscillator pulses, using no voices or vocal samples. A warm, considered and lightly optimistic character is the creative direction. Grow into12–30s, simplify after30s, and resolve with a taper over44–49.433s. Keep it one continuous composition; the picture has already removed a6.033s live-action segment. No voice, humming, lyrics, borrowed melody or source-audio samples.',
    },
}


def spaced(text):
    # These fixed authoring strings deliberately contain compact values; normalize prose.
    import re
    text = re.sub(r'(?<=[A-Za-z])(?=\d)', ' ', text)
    text = re.sub(r'(?<=\d)(?=(?:BPM|s\b|Hz\b|second\b))', ' ', text)
    return text


def main():
    result = []
    model_file = OUT / 'music-model-notes.json'
    model_notes = {item['id']: item for item in json.loads(model_file.read_text())['entries']} if model_file.exists() else {}
    md = [
        '# Original instrumental score briefs',
        '',
        'These are directions for newly composed music, not reconstructions or extracted stems. No source audio, melody, voice or samples may be reused. No perceptual listening was performed in this analysis. Source observations are computational measurements of the mixed soundtrack unless separately attributed to a content model; exact instruments, meter and vocal presence remain unverified. The suggested palettes and moods are creative choices, not claims about what was heard.',
        '',
        'Tempo candidates come from onset-envelope autocorrelation, which can follow percussion, speech, interface sounds or subdivisions. Timings below are prominent mixed-audio transients, not identified musical downbeats. Treat them as optional sync windows; compose new transitions around the picture instead of copying each source accent.',
        '',
    ]
    for identifier, direction in DIRECTIONS.items():
        data = json.loads((OUT / f'music-{identifier}.json').read_text())
        mix = data['measured_mix']
        bass_fraction = mix['frequency_band_energy_fractions']['sub_20_80'] + mix['frequency_band_energy_fractions']['bass_80_250']
        candidates = data['tempo']['broadband_candidates'][:3]
        bpm_line = ', '.join(f"{item['bpm']:.1f}" for item in candidates)
        quarters = data['target_timeline_mix']['quarter_rms_dbfs']
        evidence = {
            'mixed_audio_broadband_tempo_candidates_bpm': candidates,
            'bass_energy_below_250hz_percent': round(bass_fraction * 100, 2),
            'active_frame_spectral_centroid_median_hz': mix['active_frame_spectral_centroid_hz_median'],
            'quarter_rms_dbfs_on_target_timeline': quarters,
            'candidate_tempo_confidence': 'Moderate for recurring onset periods; unresolved for musical meter or exact downbeat.',
            'palette_inference_limit': 'Low-frequency weighting and spectral center are measured; exact instruments are not established.',
        }
        item = {
            'id': identifier,
            'target_picture_duration_seconds': data['target_duration_seconds'],
            'measured_evidence': evidence,
            'vocal_presence': data['vocal_presence'],
            'proposed_new_instrumental': {
                'working_bpm_editorial_choice': direction['working_bpm'],
                'rhythm': spaced(direction['rhythm']),
                'suggested_timbral_palette_not_source_identification': direction['palette'],
                'energy_arc': spaced(direction['arc']),
                'optional_transient_sync_windows_output_seconds': direction['anchors'],
                'timing_tolerance_note': 'Analysis hop is 9.977 ms; spectral window is 46.44 ms. Round anchors to nearby picture frames and place new musical gestures by ear after generation.',
                'generation_brief': spaced(direction['prompt']),
            },
            'provenance': {'measurement_file': f'music-{identifier}.json', 'source_sha256': data['source_sha256'], 'listening_performed': False, 'paid_calls': 0},
        }
        if identifier in model_notes:
            item['separately_attributed_content_model_summary'] = model_notes[identifier]
        if identifier == '06-gallery':
            item['source_to_output_time_map'] = {'omitted_source_seconds': [1049 / 30, 41], 'omitted_source_frames_inclusive': [1049, 1229], 'omitted_duration_seconds': 181 / 30, 'rule': 'source t <1049/30 => output t;1049/30 <=t <41 => omitted; t >=41 => output t−181/30.', 'post_cut_anchor_source_seconds': [42.0976, 45.44, 49.9298], 'post_cut_anchor_output_seconds': [36.0643, 39.4067, 43.8965]}
        result.append(item)
        md.extend([
            f'## {identifier} — {data["target_duration_seconds"]:.3f} s',
            '',
            f'**Measured:** onset-period candidates {bpm_line} BPM; {bass_fraction *100:.1f}% of analyzed spectral energy lies below 250 Hz, with median active-frame centroid {mix["active_frame_spectral_centroid_hz_median"]:.0f} Hz. Equal-duration quarter RMS levels are {", ".join(str(value) for value in quarters)} dBFS. These are mixed-audio descriptors, not instrument or genre identification.',
            '',
            f'**New-score brief:** {spaced(direction["prompt"])}',
            '',
            f'**Rhythm and arc:** {spaced(direction["rhythm"])} {spaced(direction["arc"])}',
            '',
            f'**Optional accent windows:** {", ".join(f"{value:.2f}" for value in direction["anchors"])} s on the output timeline. **Vocal evidence:** the signal pass did not classify speech or singing; the separate model report follows. Generate an instrumental score regardless.',
            '',
        ])
        if identifier in model_notes:
            note = model_notes[identifier]
            md.extend([
                f'**Separate model evidence:** `{note["model_endpoint"]}`, request `{note["request_id"]}`, describes {note["model_style_description"][0].lower() + note["model_style_description"][1:]} {note["model_timbre_description"]} It reports no intelligible speech or sung words' + (' but identifies nonlexical vocal-like music chops.' if note['model_reported_nonlexical_vocal_like_texture'] else '.'),
                '',
                f'**Model qualification:** {note["model_tempo_description"]} {note["working_tempo_decision"]} {note["timing_or_identity_qualification"]} {note["new_instrumental_voice_policy"]} These are model descriptions, not a human audition. Exact saved-result paths and hashes are in `music-model-notes.json`.',
                '',
            ])
        if identifier == '06-gallery':
            md.extend(['The Rene picture omits source 34.9666667–41.0000000 s (frames 1049–1229 inclusive). Its target is 1483 frames at 30 fps, 49.4333333 s. Post-cut measured anchors source 42.10/45.44/49.93 s map to output 36.06/39.41/43.90 s. These are timing references only; do not reuse or cut the original audio.', ''])
    md.extend([
        '## Method, corrections and limits',
        '',
        '1. Probed the six original MP4 audio streams and hashed every source. Decoded stereo float32 audio to memory at 22050 Hz; no temporary audio file or generated score was written.',
        '2. The first exploratory pass included short AAC tails beyond the picture. Those tails are not meaningful score duration. The final pass trims to native frame count / nominal frame rate; all briefs use the exact picture length, including the fractional Poke cadence and the Rene cut.',
        '3. Measured RMS/peaks, one-second and quarter energy, spectral bands/centroid/rolloff, stereo correlation and a median-filter harmonic-energy proxy. None of these identifies vocals or exact instruments.',
        '4. Estimated recurring rhythms with normalized autocorrelation of positive log-spectral changes; retained competing periodicities. A single source BPM is not certified. Detected transient timings can include percussion, UI sounds and other mixed content.',
        '5. Wrote new instrumental directions from measured energy and timing, with explicit creative palettes. Generation, listening, musical edit decisions, voice exclusion checks, loudness and final sync remain separate validation steps. A generated cue should be auditioned against the actual picture; a numerical match alone cannot certify a similar feel.',
        '',
        '6. Inspected all six saved content-model outputs as text and appended attributable timbre/speech summaries with endpoint, request ID and raw-result hashes. Instrument and vocal-like identities remain model interpretations. Conflicting model tempos/endings do not replace the independent signal data. Poke and Rene use newly synthesized formant-filtered pulses instead of any voice or vocal sample.',
        '',
        'All commands/settings, source hashes and software versions are in `music-provenance.json`; reproducible measurement code is `music-measure.py`. Six per-reference JSON files retain the detailed values and time maps. `music-briefs.json` is the structured generation handoff. This analysis agent made no paid request, melody transcription or audio sampling; the coordinator obtained the separately attributed model results.',
        '',
    ])
    text = '\n'.join(md)
    import re
    (OUT / 'music-briefs.md').write_text(text)
    (OUT / 'music-briefs.json').write_text(json.dumps({'purpose': 'New instrumental score generation; no copied original audio', 'listening_performed': False, 'briefs': result}, indent=2) + '\n')
    print(json.dumps({'briefs': len(result), 'markdown_bytes': len(text.encode()), 'json_bytes': (OUT / 'music-briefs.json').stat().st_size}))


if __name__ == '__main__':
    main()
