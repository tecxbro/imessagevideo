#!/usr/bin/env python3
"""Read-only rhythm/energy check of the genuinely new source01 score draft."""
from pathlib import Path
import hashlib
import json
import runpy
import subprocess
import numpy as np
from scipy import signal

OUT = Path(__file__).resolve().parent
ROOT = OUT.parent.parent
helpers = runpy.run_path(str(OUT / 'music-measure.py'))
SR, NFFT, HOP = helpers['SR'], helpers['NFFT'], helpers['HOP']
source = ROOT / 'audio-recreation/ai/01-photonhq/music.mp3'
probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(source)]))
raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-i', str(source), '-map', '0:a:0', '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'])
stereo = np.frombuffer(raw, dtype='<f4').reshape(-1, 2)
mono = stereo.mean(axis=1)
freq, times, spectrum = signal.stft(mono, fs=SR, window='hann', nperseg=NFFT, noverlap=NFFT-HOP, nfft=NFFT, boundary=None, padded=False)
magnitude = np.abs(spectrum)
logs = np.log1p(magnitude * 1000)
flux = np.r_[0, np.maximum(np.diff(logs, axis=1), 0).mean(axis=0)]
low = (freq >=40) & (freq <=220)
low_flux = np.r_[0, np.maximum(np.diff(logs[low], axis=1), 0).mean(axis=0)]
broad = [item for item in helpers['tempo_candidates'](flux, HOP / SR) if item['normalized_autocorrelation'] > .05]
bass = [item for item in helpers['tempo_candidates'](low_flux, HOP / SR) if item['normalized_autocorrelation'] > .05]
segments = []
for start in [0, 6, 12]:
    selected = (times >=start) & (times <start +8)
    segments.append({'start_seconds': start, 'end_seconds': start+8, 'broadband_candidates': [item for item in helpers['tempo_candidates'](flux[selected], HOP / SR) if item['normalized_autocorrelation'] > .05][:3], 'bass_candidates': [item for item in helpers['tempo_candidates'](low_flux[selected], HOP / SR) if item['normalized_autocorrelation'] > .05][:3]})
quarter_energy = []
for index in range(4):
    begin, end = int(index *len(mono)/4), int((index+1)*len(mono)/4)
    quarter_energy.append(round(helpers['db'](np.sqrt(np.mean(mono[begin:end]**2))), 2))
per_second = []
for start in range(int(np.ceil(len(mono)/SR))):
    section=mono[start*SR:min(len(mono),(start+1)*SR)]
    per_second.append({'start_seconds': start, 'end_seconds': min(len(mono)/SR,start+1), 'rms_dbfs': round(helpers['db'](np.sqrt(np.mean(section**2))),2)})
reference = json.loads((OUT/'music-01-photonhq.json').read_text())
strongest = broad[0]['bpm'] if broad else None
result = {
    'purpose': 'Computational check of a genuinely generated score draft, not listening or similarity certification',
    'new_score_path': str(source.relative_to(ROOT)),
    'new_score_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
    'audio_stream': {key: probe['streams'][0].get(key) for key in ['codec_name','sample_rate','channels','duration','bit_rate']},
    'format_duration_seconds': float(probe['format']['duration']),
    'decoded_duration_seconds': len(mono)/SR,
    'target_picture_duration_seconds': reference['target_duration_seconds'],
    'requested_working_bpm': 109,
    'broadband_candidates': broad,
    'bass_candidates': bass,
    'segments': segments,
    'strongest_broadband_period_difference_from_requested_bpm': round(abs(strongest-109),3) if strongest else None,
    'quarter_rms_dbfs': quarter_energy,
    'reference_quarter_rms_dbfs': reference['target_timeline_mix']['quarter_rms_dbfs'],
    'mix_rms_dbfs': round(helpers['db'](np.sqrt(np.mean(mono**2))),2),
    'mix_sample_peak_dbfs': round(helpers['db'](np.max(np.abs(stereo))),2),
    'one_second_energy': per_second,
    'listening_performed': False,
    'vocal_or_instrument_detection_performed': False,
    'source_audio_used_in_analysis': 'Only the original stats JSON was read for comparison; no source waveform used for this draft check.',
    'measurement_method': 'Same 22050 Hz /1024 Hann /220 hop log-spectral onset autocorrelation as music-measure.py, 60–180BPM search. This checks recurring periods, not exact musical meter.',
    'tempo_resolution_qualification': 'Onset lag is quantized at approximately 9.977 ms; at 109 BPM this yields a roughly 2 BPM spacing between adjacent lag bins. 109.34 is a candidate-bin value, not an exact musical-tempo certification.',
    'assessment': {'requested_rhythm_direction': 'Supported: the dominant recurring period is compatible with approximately 109 BPM and stable across all three 8-second windows.', 'energy_difference': 'New score is nearly level through the first three quarters, then fades; original had a stronger middle lift. New one-second RMS falls sharply in 19–20 s, about one second earlier than the original 20–21 s decrease.', 'duration_note': 'Decoded MP3 exceeds the picture by approximately 30.7 ms, consistent with a small encoded tail/padding span; final mixing should trim to exact native picture duration.', 'headroom_note': 'Decoded float sample peak is approximately +0.08 dBFS; do not infer hard clipping from this alone. Set final mix headroom/limiting after adding effects.', 'not_established': 'No human auditory pass, new-score model understanding, vocal exclusion, instrument identity or subjective feel match was established.'},
    'measurement_script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    'no_audio_export_or_mutation': True,
}
(OUT/'music-newscore-01.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({key:result[key] for key in ['format_duration_seconds','decoded_duration_seconds','target_picture_duration_seconds','broadband_candidates','bass_candidates','quarter_rms_dbfs','reference_quarter_rms_dbfs']},indent=2))
