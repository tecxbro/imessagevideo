"""Review decoded delivery audio against frozen, independently supplied cue references.

No production stem is opened. FFmpeg applies MP4 edit lists/skip-sample metadata;
we report that metadata and measured common alignment, never silently remove a
global soundtrack shift. Correlation measures waveform similarity, not listening.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import numpy as np
from scipy import signal
from scipy.ndimage import maximum_filter1d

SR = 48000
PACKET_HASH_METHOD = 'SHA-256 of concatenated first-video-stream encoded packet payloads; ffmpeg -map 0:v:0 -c copy -f hash -hash sha256; excludes container metadata and audio; not decoded frames'


def packet_hash(path):
    return subprocess.check_output(['ffmpeg', '-v', 'error', '-i', str(path), '-map', '0:v:0',
                                    '-c', 'copy', '-f', 'hash', '-hash', 'sha256', '-'], text=True).strip()


def decode(path):
    raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-i', str(path), '-map', '0:a:0',
                                   '-ar', str(SR), '-ac', '2', '-f', 'f32le', '-'])
    return np.frombuffer(raw, '<f4').reshape(-1, 2).astype(float)


def add(target, wave, start, gain=1):
    lo, hi = max(0, start), min(len(target), start + len(wave))
    if hi > lo:
        target[lo:hi] += gain * wave[lo-start:hi-start]


def locate(audio, wave, expected, radius):
    lo = max(0, expected - radius)
    hi = min(len(audio), expected + radius + len(wave))
    region = audio[lo:hi]
    dot = sum(signal.correlate(region[:, c], wave[:, c], mode='valid', method='fft') for c in range(2))
    cumulative = np.concatenate(([0.], np.cumsum(np.sum(region ** 2, axis=1))))
    energy = np.maximum(0., cumulative[len(wave):] - cumulative[:-len(wave)])
    ref_energy = np.sum(wave ** 2)
    corr = np.clip(dot / np.sqrt(np.maximum(energy * ref_energy, 1e-25)), -1, 1)
    corr[energy < ref_energy * 1e-6] = 0
    index = int(np.argmax(corr))
    return lo + index, float(corr[index]), float(dot[index] / ref_energy)


def stamp(sample, fps):
    seconds = sample / SR
    return f'{int(seconds//60):02}:{seconds%60:06.3f} f{round(seconds*fps)}'


def outside_tolerance(offset, frames, fps):
    return abs(offset) > round(frames * SR / fps)


def background_codec_floor(wave, block=240):
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / 'reference.m4a'
        subprocess.run(['ffmpeg', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-',
                        '-c:a', 'aac', '-b:a', '192k', '-movie_timescale', str(SR), str(path)],
                       input=wave.astype('<f4').tobytes(), check=True)
        encoded = decode(path)[:len(wave)]
    error = encoded - wave
    error = np.pad(error, ((0, (-len(error)) % block), (0, 0)))
    rms = np.sqrt(np.mean(error.reshape(-1, block, 2)**2, axis=(1, 2)))
    return maximum_filter1d(rms, size=21) * 2 + .001


def review(video, receipt_path, tolerance=1, window=12, correlation=.8, level=6):
    receipt = json.loads(receipt_path.read_text())
    actual = packet_hash(video)
    if actual != receipt['picture_packet_sha256']:
        return {'status': 'fail', 'picture_match': False, 'expected_picture': receipt['picture_packet_sha256'],
                'actual_picture': actual, 'cues': [], 'extras': []}
    base = receipt_path.parent.parent
    waves = []
    for cue in receipt['cues']:
        path = base / cue['reference']
        if hashlib.sha256(path.read_bytes()).hexdigest() != cue['reference_sha256']:
            raise ValueError(f'Reference hash mismatch: {path}')
        waves.append(np.load(path, allow_pickle=False))
    audio = decode(video)
    if not np.isfinite(audio).all():
        raise ValueError('Nonfinite decoded PCM')
    background = None
    codec_floor = None
    if 'background_reference' in receipt:
        ref = receipt['background_reference']
        path = base / ref['reference']
        if hashlib.sha256(path.read_bytes()).hexdigest() != ref['reference_sha256']:
            raise ValueError('Background reference hash mismatch')
        wave = np.load(path, allow_pickle=False)
        if wave.shape != audio.shape:
            raise ValueError('Background reference span differs from decoded delivery')
        gain = float(np.sum(audio * wave) / np.sum(wave ** 2))
        corr = float(np.sum(audio * wave) / np.sqrt(np.sum(audio ** 2) * np.sum(wave ** 2)))
        background = {'correlation_with_full_delivery': corr, 'gain_delta_db': float(20*np.log10(max(gain, 1e-10))),
                      'reference_sha256': ref['reference_sha256'], 'subtraction_gain': 1.,
                      'status': 'pass' if .5 < gain < 2 else 'fail'}
        codec_floor = background_codec_floor(wave)
        background['residual_floor_method'] = 'max(0.003, 2x independently AAC-192k-encoded reference residual RMS, local 105ms maximum, +0.001); no delivery-derived noise fitting'
        audio -= wave
    fps = receipt['fps']; radius = round(window * SR / fps)
    starts = [c['clip_start_sample_unclipped'] for c in receipt['cues']]
    gains = [1.] * len(starts)
    residual = audio.copy()
    for wave, start in zip(waves, starts):
        add(residual, wave, start, -1)
    measurements = [None] * len(starts)
    # Coordinate descent isolates overlapping keys rather than treating their
    # neighbors as distortion. Every iteration reads only decoded delivery PCM.
    for _ in range(4):
        for i, (cue, wave) in enumerate(zip(receipt['cues'], waves)):
            add(residual, wave, starts[i], gains[i])
            start, corr, gain = locate(residual, wave, cue['clip_start_sample_unclipped'], radius)
            starts[i], gains[i] = start, max(0., gain)
            measurements[i] = (start, corr, gain)
            add(residual, wave, start, -gains[i])
    rows = []
    for cue, (start, corr, gain) in zip(receipt['cues'], measurements):
        offset = start - cue['clip_start_sample_unclipped']
        db = 20 * np.log10(max(abs(gain), 1e-10))
        flags = []
        if corr < .25 or db < -35:
            flags.append('missing')
        else:
            if corr < correlation or abs(db) > level:
                flags.append('damaged')
            if outside_tolerance(offset, tolerance, fps):
                flags.append('late' if offset > 0 else 'early')
        rows.append({'ordinal': cue['ordinal'], 'frame': cue['canonical_event']['frame'],
                     'expected_sample': cue['event_sample'], 'timestamp': stamp(cue['event_sample'], fps),
                     'offset_samples': offset, 'offset_ms': offset/SR*1000, 'offset_frames': offset/SR*fps,
                     'correlation': corr, 'level_delta_db': float(db), 'flags': flags})
    # Residual energy on 5 ms blocks, merged over 50 ms. AAC noise floor is
    # bounded by a fixed production-level threshold, not the damaged file's peak.
    block = 240
    padded = np.pad(residual, ((0, (-len(residual)) % block), (0, 0)))
    rms = np.sqrt(np.mean(padded.reshape(-1, block, 2)**2, axis=(1, 2)))
    threshold = np.maximum(.003, codec_floor) if codec_floor is not None else .003
    active = np.flatnonzero(rms > threshold)
    groups = np.split(active, np.flatnonzero(np.diff(active) > 10) + 1) if len(active) else []
    extras = []
    for group in groups:
        sample = int(group[0] * block)
        # Distortion attached to an identified cue is already a cue defect.
        if any(abs(sample - (start + c['clip_alignment_offset_samples'])) < .15*SR
               for start, c in zip(starts, receipt['cues'])):
            continue
        extras.append({'sample': sample, 'timestamp': stamp(sample, fps), 'rms': float(max(rms[group])), 'flags': ['extra']})
    packets = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'a:0',
        '-read_intervals', '%+#1', '-show_packets', '-of', 'json', str(video)], text=True))
    good = [r['offset_samples'] for r in rows if r['correlation'] > .9 and abs(r['level_delta_db']) < 3]
    return {'status': 'fail' if extras or any(r['flags'] for r in rows) or (background and background['status'] != 'pass') else 'pass', 'picture_match': True,
            'picture_packet_sha256': actual, 'decoded_samples': len(audio), 'fps': fps,
            'picture_packet_hash_method': PACKET_HASH_METHOD, 'background_reference_review': background,
            'priming': {'first_audio_packet': packets['packets'][0], 'decoder': 'FFmpeg edit-list/skip_samples applied',
                        'measured_common_offset_samples': float(np.median(good)) if good else None,
                        'additional_alignment_correction_samples': 0},
            'thresholds': {'timing_frames': tolerance, 'search_frames': window, 'correlation': correlation, 'level_db': level},
            'cues': rows, 'extras': extras}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('mp4', type=Path); p.add_argument('--receipt', required=True, type=Path)
    p.add_argument('--json', required=True, type=Path); p.add_argument('--tolerance-frames', type=float, default=1)
    p.add_argument('--window-frames', type=float, default=12); p.add_argument('--correlation', type=float, default=.8)
    p.add_argument('--level-db', type=float, default=6)
    a = p.parse_args()
    r = review(a.mp4, a.receipt, a.tolerance_frames, a.window_frames, a.correlation, a.level_db)
    a.json.write_text(json.dumps(r, indent=2)+'\n')
    print('id  expected           offset(ms/frames)   corr    level(dB)  result')
    for c in r['cues']:
        print(f'{c["ordinal"]:2}  {c["timestamp"]:18} {c["offset_ms"]:8.2f}/{c["offset_frames"]:6.2f}  {c["correlation"]:.3f}  {c["level_delta_db"]:9.2f}  {",".join(c["flags"]) or "ok"}')
    for e in r['extras']:
        print(f' -  {e["timestamp"]:18} extra transient rms={e["rms"]:.5f}')
    print(f'{r["status"]}: picture_match={r["picture_match"]}, cues={len(r["cues"])}, defective={sum(bool(c["flags"]) for c in r["cues"])}, extras={len(r["extras"])}')
    raise SystemExit(0 if r['status']=='pass' else 1)


if __name__ == '__main__':
    main()
