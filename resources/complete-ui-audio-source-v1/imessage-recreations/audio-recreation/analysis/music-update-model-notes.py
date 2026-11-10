#!/usr/bin/env python3
"""Attribute saved content-model descriptions without changing signal measurements."""
from pathlib import Path
import hashlib
import json

OUT = Path(__file__).resolve().parent
FIRST = OUT / 'model-01-photonhq.json'
REST = OUT / 'model-analyses.json'
raw = [('01-photonhq', json.loads(FIRST.read_text()), FIRST)] + [(item['id'], item, REST) for item in json.loads(REST.read_text())]
SUMMARY = {
    '01-photonhq': {
        'style': 'Upbeat modern funk-pop / nu-disco.',
        'timbre': 'Funky slap or emulated synth bass; crisp four-floor electronic drums and snare/clap; sparse bright synthesizer stabs.',
        'tempo': 'Approximately 125 BPM, described as confident by the model.',
        'decision': 'Working 109 BPM follows the independent 109.34 BPM onset period, strongest in every 8-second window. The model tempo guess is retained as a contradiction, not silently accepted.',
        'limits': 'The model describes constant high energy and a clean ending, while measured RMS shows a modest middle lift and a substantial 20–21.833 s fade. Retain the measured timing envelope.',
        'vocal_like': False,
    },
    '02-danieltian': {
        'style': 'Upbeat minimalist electronic / clean technology-ad music.',
        'timbre': 'Punchy drum-machine kick, sharp snare/clap, slightly open hi-hat pattern and a low pulsing synth-bass root.',
        'tempo': 'Approximately 125 ±5 BPM.',
        'decision': 'Working 123 BPM is close to measured 122.73 BPM and within the model range; the strongest 81.27 BPM onset stream can be represented by dotted-quarter accents on that grid.',
        'limits': 'The model reports constant energy and an abrupt stop around 40 s. Measurements instead show a strong first-to-middle energy rise and a diminishing tail after approximately 41 s. Use the measured arc and exact picture duration.',
        'vocal_like': False,
    },
    '03-photon-mini': {
        'style': 'Modern upbeat electronic / technology-demo or nu-disco.',
        'timbre': 'Crisp drum-machine kick and clap/snare, steady hats and shaker-like percussion, driving synth bass, a melodic pluck synth and atmospheric pads.',
        'tempo': 'Approximately 125 ±5 BPM.',
        'decision': 'Working 118 BPM follows the 117.91 BPM signal period and bass/broadband agreement; the model tempo guess is approximate and does not replace the measurements.',
        'limits': 'The model claims an abrupt end around 36 s; measured mixed audio remains active later and is near-silent across the 39–42 s hold. Retain the measured ending window.',
        'vocal_like': False,
    },
    '04-poke': {
        'style': 'Minimal electronic / technology-house or clean dance-pop.',
        'timbre': 'Four-floor kick, shaker/hi-hat texture, bouncy synth bass, short percussive plucks and heavily processed nonlexical vocal-like chops.',
        'tempo': 'Approximately 120–125 BPM.',
        'decision': 'Working 123 BPM agrees with the 122.73 BPM measured period and model range; retain half-time weight suggested by the competing 60.74 BPM period.',
        'limits': 'The model reports a rapid fade beginning around 41 s, consistent with the measured late decline. Its instrument and chop identities remain model interpretations, not a human audition.',
        'vocal_like': True,
    },
    '05-linq': {
        'style': 'Relaxed chill-hop / low-fidelity electronic pop.',
        'timbre': 'Processed drums with clap/snap-like snare and shaker-like hats; rounded synth bass; warm pad or electric-piano-style chords; a short-decay plinky synth lead.',
        'tempo': 'Approximately 95–105 BPM.',
        'decision': 'Working 96 BPM agrees with the measured 95.45 BPM dominant period and model range; the approximately 64 BPM metrical alternative remains recorded.',
        'limits': 'The model describes a fade around 43 s followed by an ambient logo-like sting. The measured late decrease supports the fade timing but does not independently identify the sting or instrument.',
        'vocal_like': False,
    },
    '06-gallery': {
        'style': 'Upbeat electronic pop / lounge.',
        'timbre': 'Four-floor drum machine, crisp snare/clap, rhythmic clean synth bass, bright plucked arpeggios, filtered pads and processed nonlexical vocal-like chops.',
        'tempo': 'Approximately 125 ±5 BPM.',
        'decision': 'Working 134 BPM with a 67 BPM half-time feel follows the strong 133.64 / 66.82 BPM measured periods. The model tempo guess conflicts; exact source meter is not certified.',
        'limits': 'The model describes a quick source fade around 51 s, which maps to output approximately 44.967 s after the specified 6.033 s cut. Source-to-output mapping and measured energy take priority over an approximate model timestamp.',
        'vocal_like': True,
    },
}
entries = []
for identifier, response, path in raw:
    summary = SUMMARY[identifier]
    text = response['result']['output']
    entries.append({
        'id': identifier,
        'model_endpoint': response['endpoint_id'],
        'request_id': response['request_id'],
        'evidence_kind': 'Saved content-aware model description; text inspected directly, no human auditory listening pass',
        'raw_result_file': str(path.relative_to(OUT.parent.parent)),
        'raw_result_file_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        'raw_output_text_sha256': hashlib.sha256(text.encode()).hexdigest(),
        'direct_raw_model_result_reviewed_by_this_agent': True,
        'human_listening_performed': False,
        'source_path': f'references/{identifier}/source.mp4',
        'model_style_description': summary['style'],
        'model_timbre_description': summary['timbre'],
        'model_tempo_description': summary['tempo'],
        'working_tempo_decision': summary['decision'],
        'model_reported_intelligible_words': False,
        'model_reported_nonlexical_vocal_like_texture': summary['vocal_like'],
        'vocal_presence_qualification': 'The model reports no intelligible speech or sung words; this is not an independently verified absence of all vocal-like sound.',
        'new_instrumental_voice_policy': 'Use only newly synthesized formant-filtered pulses, not any voice or vocal sample, to supply a similar rhythmic texture.' if summary['vocal_like'] else 'Generate an instrumental score with no speech, singing, humming or vocal samples.',
        'timing_or_identity_qualification': summary['limits'],
        'source_audio_reused': False,
        'paid_calls_by_this_agent': 0,
    })
(OUT / 'music-model-notes.json').write_text(json.dumps({'purpose': 'Separately attributed actual saved model descriptions; signal-stat files remain immutable', 'entries': entries}, indent=2) + '\n')
print(f'Wrote {len(entries)} attributable model summaries.')
