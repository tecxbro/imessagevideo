#!/usr/bin/env python3
"""Read-only audio footprint analysis. Writes only sibling music-* analysis files.
No separation, transcription, audio generation or perceptual listening is claimed.
"""
from pathlib import Path
import hashlib
import json
import math
import platform
import subprocess
import sys
from datetime import datetime, timezone
from fractions import Fraction

import numpy as np
import scipy
from scipy import ndimage, signal

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
IDS = ['01-photonhq', '02-danieltian', '03-photon-mini', '04-poke', '05-linq', '06-gallery']
SR = 22050
HOP = 220
NFFT = 1024
CUT = (1049 / 30, 41.0)


def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def mapped_time(identifier, seconds):
    if identifier != '06-gallery' or seconds < CUT[0]:
        return round(float(seconds), 4)
    if seconds < CUT[1]:
        return None
    return round(float(seconds - (CUT[1] - CUT[0])), 4)


def db(value):
    return float(20 * np.log10(max(float(value), 1e-8)))


def tempo_candidates(envelope, hop_seconds):
    """Normalized onset-envelope autocorrelation, explicitly not beat transcription."""
    if len(envelope) < 300 or float(np.std(envelope)) < 1e-8:
        return []
    centered = np.asarray(envelope, dtype=np.float64)
    centered = np.maximum(centered - ndimage.median_filter(centered, size=101), 0)
    limit = np.quantile(centered, .99)
    centered = np.minimum(centered, limit)
    centered -= centered.mean()
    lags = np.arange(math.ceil(60 / (180 * hop_seconds)), math.floor(60 / (60 * hop_seconds)) + 1)
    scores = []
    for lag in lags:
        left, right = centered[:-lag], centered[lag:]
        denominator = np.linalg.norm(left) * np.linalg.norm(right)
        scores.append(float(np.dot(left, right) / denominator) if denominator else 0.0)
    scores = np.asarray(scores)
    peaks, _ = signal.find_peaks(scores, distance=3)
    peaks = list(peaks)
    if scores[0] > scores[1]:
        peaks.append(0)
    if scores[-1] > scores[-2]:
        peaks.append(len(scores) - 1)
    order = sorted(peaks, key=lambda index: scores[index], reverse=True)
    result = []
    for index in order:
        bpm = 60 / (float(lags[index]) * hop_seconds)
        if all(abs(bpm - item['bpm']) > 3 for item in result):
            result.append({'bpm': round(bpm, 2), 'normalized_autocorrelation': round(float(scores[index]), 5), 'lag_seconds': round(float(lags[index] * hop_seconds), 5)})
        if len(result) == 5:
            break
    return result


def analyze(identifier):
    source = ROOT / 'references' / identifier / 'source.mp4'
    probe_command = ['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(source)]
    probe = json.loads(subprocess.check_output(probe_command))
    audio_streams = [item for item in probe['streams'] if item.get('codec_type') == 'audio']
    if not audio_streams:
        raise RuntimeError(f'No audio stream: {identifier}')
    stream = audio_streams[0]
    video_stream = next(item for item in probe['streams'] if item.get('codec_type') == 'video')
    visual_duration = int(video_stream['nb_frames']) / float(Fraction(video_stream['r_frame_rate']))
    decode_command = ['ffmpeg', '-v', 'error', '-i', str(source), '-map', '0:a:0', '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-']
    raw = subprocess.check_output(decode_command)
    stereo = np.frombuffer(raw, dtype='<f4').reshape(-1, 2)
    decoded_audio_duration = len(stereo) / SR
    stereo = stereo[:round(visual_duration * SR)]
    mono = stereo.mean(axis=1)
    duration = len(mono) / SR
    frequencies, times, stft = signal.stft(mono, fs=SR, window='hann', nperseg=NFFT, noverlap=NFFT-HOP, nfft=NFFT, boundary=None, padded=False)
    magnitude = np.abs(stft).astype(np.float32)
    power = magnitude ** 2
    sum_power = power.sum(axis=0) + 1e-18
    centroid = (power * frequencies[:, None]).sum(axis=0) / sum_power
    cumulative = np.cumsum(power, axis=0)
    rolloff = frequencies[np.argmax(cumulative >= .85 * cumulative[-1], axis=0)]
    flatness = np.exp(np.mean(np.log(power + 1e-16), axis=0)) / np.mean(power + 1e-16, axis=0)
    framed = np.lib.stride_tricks.sliding_window_view(mono, NFFT)[::HOP]
    rms = np.sqrt(np.mean(framed ** 2, axis=1))
    activity = rms > max(10 ** (-45 / 20), float(np.quantile(rms, .95) * .02))
    logs = np.log1p(magnitude * 1000)
    flux = np.r_[0, np.maximum(np.diff(logs, axis=1), 0).mean(axis=0)]
    low_select = (frequencies >= 40) & (frequencies <= 220)
    low_flux = np.r_[0, np.maximum(np.diff(logs[low_select], axis=1), 0).mean(axis=0)]
    harmonic_median = ndimage.median_filter(magnitude, size=(1, 31))
    percussive_median = ndimage.median_filter(magnitude, size=(31, 1))
    harmonic_mask = harmonic_median ** 2 / (harmonic_median ** 2 + percussive_median ** 2 + 1e-18)
    harmonic_fraction = float(np.sum(power * harmonic_mask) / np.sum(power))
    bands = {}
    for name, lower, upper in [('sub_20_80', 20, 80), ('bass_80_250', 80, 250), ('low_mid_250_1000', 250, 1000), ('mid_1000_4000', 1000, 4000), ('high_4000_11025', 4000, 11026)]:
        selected = (frequencies >= lower) & (frequencies < upper)
        bands[name] = round(float(np.sum(power[selected]) / np.sum(power)), 5)
    broad_tempo = tempo_candidates(flux, HOP / SR)
    bass_tempo = tempo_candidates(low_flux, HOP / SR)
    segment_tempos = []
    for start in range(0, max(1, math.floor(duration) - 7), 6):
        selected = (times >= start) & (times < start + 8)
        segment_tempos.append({'source_start': start, 'source_end': min(round(duration, 4), start + 8), 'broadband_candidates': tempo_candidates(flux[selected], HOP / SR)[:2], 'bass_candidates': tempo_candidates(low_flux[selected], HOP / SR)[:2]})
    peak_indices, properties = signal.find_peaks(flux, distance=round(.08 * SR / HOP), prominence=max(float(np.std(flux) * .3), 1e-8))
    order = sorted(range(len(peak_indices)), key=lambda index: float(properties['prominences'][index]), reverse=True)
    selected_peaks = []
    for index in order:
        frame = int(peak_indices[index])
        seconds = float(times[frame])
        if all(abs(seconds - other['source_time']) >= .65 for other in selected_peaks):
            selected_peaks.append({'source_time': round(seconds, 4), 'output_time': mapped_time(identifier, seconds), 'spectral_flux': round(float(flux[frame]), 5), 'prominence': round(float(properties['prominences'][index]), 5), 'local_rms_dbfs': round(db(rms[frame]), 2), 'classification': 'unseparated broadband transient; may be percussion, speech consonant, UI sound or mix change'})
        if len(selected_peaks) == 14:
            break
    selected_peaks.sort(key=lambda item: item['source_time'])
    distributed_transients = []
    for section_start in range(0, math.ceil(duration), 8):
        local_order = [index for index in order if section_start <= times[int(peak_indices[index])] < section_start + 8]
        local = []
        for index in local_order:
            frame = int(peak_indices[index])
            seconds = float(times[frame])
            if all(abs(seconds - other['source_time']) >= .65 for other in local):
                local.append({'source_time': round(seconds, 4), 'output_time': mapped_time(identifier, seconds), 'prominence': round(float(properties['prominences'][index]), 5)})
            if len(local) == 3:
                break
        distributed_transients.append({'source_start': section_start, 'source_end': min(round(duration, 4), section_start + 8), 'representative_transients': sorted(local, key=lambda item: item['source_time'])})
    if identifier == '06-gallery':
        target_mono = np.concatenate([mono[:round(CUT[0] * SR)], mono[round(CUT[1] * SR):]])
    else:
        target_mono = mono
    target_quarters = []
    for index in range(4):
        start, end = int(index * len(target_mono) / 4), int((index + 1) * len(target_mono) / 4)
        target_quarters.append(round(db(np.sqrt(np.mean(target_mono[start:end] ** 2))), 2))
    energy = []
    for start in range(math.ceil(duration)):
        left = int(start * SR)
        right = min(len(mono), int((start + 1) * SR))
        section = mono[left:right]
        if not len(section):
            continue
        energy.append({'source_start': start, 'source_end': round(right / SR, 4), 'output_start': mapped_time(identifier, start), 'rms_dbfs': round(db(np.sqrt(np.mean(section ** 2))), 2), 'peak_dbfs': round(db(np.max(np.abs(section)))),})
    quarter_energy = []
    for index in range(4):
        start, end = int(index * len(mono) / 4), int((index + 1) * len(mono) / 4)
        quarter_energy.append(round(db(np.sqrt(np.mean(mono[start:end] ** 2))), 2))
    active_centroid = centroid[activity]
    active_rolloff = rolloff[activity]
    active_flatness = flatness[activity]
    correlation = float(np.corrcoef(stereo.T)[0, 1])
    result = {
        'id': identifier,
        'source_path': str(source.relative_to(ROOT)),
        'source_sha256': sha256(source),
        'source_file_bytes': source.stat().st_size,
        'format_duration_seconds': float(probe['format']['duration']),
        'audio_stream': {key: stream.get(key) for key in ['index', 'codec_name', 'sample_rate', 'channels', 'channel_layout', 'duration', 'bit_rate']},
        'decoded_audio_duration_seconds': round(decoded_audio_duration, 6),
        'analyzed_audio_duration_seconds': round(duration, 6),
        'native_picture_duration_seconds': round(visual_duration, 9),
        'native_picture_frames': int(video_stream['nb_frames']),
        'native_picture_frame_rate': video_stream['r_frame_rate'],
        'target_duration_seconds': round(visual_duration - 181 / 30 if identifier == '06-gallery' else visual_duration, 9),
        'target_audio_timing_note': 'Timing map only: omit source frames1049–1229 inclusive, [1049/30, 41) seconds; no audio export created.' if identifier == '06-gallery' else 'Unchanged source timeline; final score must use exact final visual duration.',
        'measured_mix': {'rms_dbfs': round(db(np.sqrt(np.mean(mono ** 2))), 2), 'peak_dbfs': round(db(np.max(np.abs(stereo))), 2), 'crest_factor_db': round(db(np.max(np.abs(mono))) - db(np.sqrt(np.mean(mono ** 2))), 2), 'active_frame_fraction': round(float(np.mean(activity)), 5), 'stereo_correlation': round(correlation, 5), 'quarter_rms_dbfs': quarter_energy, 'frequency_band_energy_fractions': bands, 'active_frame_spectral_centroid_hz_median': round(float(np.median(active_centroid)), 1), 'active_frame_85_percent_rolloff_hz_median': round(float(np.median(active_rolloff)), 1), 'active_frame_spectral_flatness_median': round(float(np.median(active_flatness)), 5), 'hpss_harmonic_energy_proxy_fraction': round(harmonic_fraction, 5)},
        'tempo': {'method': 'Normalized autocorrelation of positive log-spectral flux; 60–180 BPM search; unseparated soundtrack, aliases and speech/UI contamination unresolved.', 'broadband_candidates': broad_tempo, 'bass_candidates': bass_tempo, 'segments': segment_tempos},
        'target_timeline_mix': {'quarter_rms_dbfs': target_quarters, 'rms_dbfs': round(db(np.sqrt(np.mean(target_mono ** 2))), 2), 'purpose': 'Energy map only; this source audio must not be reused in the new score.'},
        'distributed_detected_transients': distributed_transients,
        'onset_density_per_second': round(len(peak_indices) / duration, 3),
        'major_detected_transients': selected_peaks,
        'one_second_energy': energy,
        'vocal_presence': {'established': False, 'confidence': 'unresolved', 'reason': 'No perceptual listening, source separation, or speech/singing model was used. Harmonic energy and onsets cannot identify vocals reliably.'},
        'observational_limits': ['Measurements describe the original mixed soundtrack, not a separated music stem.', 'No exact instrument, chord progression, melody, key, emotion, vocal language or sound-effect identity is established.', 'Suggested new-score timbres and BPM are editorial choices guided by these measurements, not assertions of an exact source match.'],
    }
    destination = OUT / f'music-{identifier}.json'
    destination.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'id': identifier, 'duration': duration, 'mix': result['measured_mix'], 'tempo_broad': broad_tempo[:3], 'tempo_bass': bass_tempo[:3], 'hits': [item['source_time'] for item in selected_peaks]}, separators=(',', ':')), flush=True)
    return result


def main():
    results = [analyze(identifier) for identifier in IDS]
    provenance = {
        'created_utc': datetime.now(timezone.utc).isoformat(),
        'scope': 'Computational audio footprint analysis for original instrumental score generation; no listening or audio reuse.',
        'script_path': str(Path(__file__).resolve().relative_to(ROOT)),
        'script_sha256': sha256(Path(__file__).resolve()),
        'python': sys.version,
        'numpy_version': np.__version__,
        'scipy_version': scipy.__version__,
        'ffmpeg_version': subprocess.check_output(['ffmpeg', '-version'], text=True).splitlines()[0],
        'analysis_settings': {'decode': 'ffmpeg -v error -i SOURCE -map 0:a:0 -ac 2 -ar 22050 -f f32le -; decoded to memory, never written as audio', 'sample_rate': SR, 'analysis_span': 'Trim decoded audio tail to native picture duration (frame_count / nominal frame_rate). Rene spectral/tempo summary is uncut source; events additionally map to output time.', 'fft_samples': NFFT, 'hop_samples': HOP, 'window': 'Hann', 'tempo_search_bpm': [60, 180], 'hpss': '31-bin/31-time-frame median estimates; harmonic energy proxy only', 'transient_selection': 'Positive mean log-magnitude difference; local peaks >=80ms apart; top14 prominence peaks with >=650ms separation'},
        'source_audio_reused_in_generation': False,
        'paid_calls': 0,
        'listening_performed': False,
        'vocal_detection_performed': False,
        'originality_requirement': 'Generate new instrumental composition; do not reproduce source melody, harmony sequence, audio samples or voice.',
        'rene_omission_source_seconds': list(CUT),
        'files': [{'id': item['id'], 'path': f'music-{item["id"]}.json', 'sha256': sha256(OUT / f'music-{item["id"]}.json')} for item in results],
        'steps': ['Probed each original source audio stream with ffprobe.', 'Decoded original audio to in-memory stereo float32 at22050Hz, trimmed audio tail to native picture duration and analyzed a mono mix.', 'Measured whole-mix energy, spectrum, stereo correlation and onset timing.', 'Estimated candidate periodicities from broadband and low-band onset autocorrelation; retained ambiguities.', 'Mapped Rene event times across the explicitly omitted source interval.', 'Prepared original-score briefs separately from measured facts; no original audio sampling, model generation or paid request.'],
    }
    (OUT / 'music-provenance.json').write_text(json.dumps(provenance, indent=2) + '\n')


if __name__ == '__main__':
    main()
