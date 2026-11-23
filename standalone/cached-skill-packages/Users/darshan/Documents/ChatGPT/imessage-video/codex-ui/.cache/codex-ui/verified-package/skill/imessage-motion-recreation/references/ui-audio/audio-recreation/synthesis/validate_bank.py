"""Validate a generated UI bank and decode its audition using FFmpeg."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import wave
from pathlib import Path

import numpy as np

if __package__:
    from .ui_synth import SAMPLE_RATE, analyze
else:
    from ui_synth import SAMPLE_RATE, analyze


def read_pcm24(file: Path) -> np.ndarray:
    with wave.open(str(file), 'rb') as handle:
        if (handle.getframerate(), handle.getnchannels(), handle.getsampwidth()) != (SAMPLE_RATE, 2, 3):
            raise ValueError(f'Unexpected WAV format: {file}')
        raw = np.frombuffer(handle.readframes(handle.getnframes()), dtype=np.uint8).reshape(-1, 3)
    packed = raw[:, 0].astype(np.int32) | (raw[:, 1].astype(np.int32) << 8) | (raw[:, 2].astype(np.int32) << 16)
    signed = np.where(packed >= 2 ** 23, packed - 2 ** 24, packed)
    return signed.reshape(-1, 2).astype(np.float64) / (2 ** 23 - 1)


def validate(directory: Path) -> dict:
    manifest = json.loads((directory / 'manifest.json').read_text())
    code_sha = hashlib.sha256((Path(__file__).parent / 'ui_synth.py').read_bytes()).hexdigest()
    if code_sha != manifest['provenance']['code_sha256']:
        raise ValueError('Synthesis source differs from the source pinned by the bank manifest')
    assets = []
    for entry in manifest['assets']:
        file = directory / entry['file']
        if hashlib.sha256(file.read_bytes()).hexdigest() != entry['sha256']:
            raise ValueError(f'Hash mismatch: {file}')
        x = read_pcm24(file)
        stats = analyze(x)
        tail = float(np.max(np.abs(x[-24:])))
        if stats['clipped'] or not stats['endpoints_zero'] or max(abs(v) for v in stats['dc']) >= 1e-6 or tail >= .002:
            raise ValueError(f'Signal acceptance failed: {file}: {stats}, tail={tail}')
        if stats['frames'] != entry['analysis']['frames']:
            raise ValueError(f'Frame-count mismatch: {file}')
        assets.append({'file': entry['file'], 'sha256': entry['sha256'], **stats,
                       'last_half_ms_peak': tail,
                       'peak_time_ms': float(np.argmax(np.max(np.abs(x), axis=1)) / SAMPLE_RATE * 1000)})
    result = {'status': 'pass', 'sample_rate': SAMPLE_RATE, 'channels': 2,
              'assets': assets, 'source_audio_inputs': [],
              'synthesis_code_sha256': code_sha, 'source_provenance_matches': True,
              'manifest_sha256': hashlib.sha256((directory / 'manifest.json').read_bytes()).hexdigest()}
    if 'audition' in manifest:
        file = directory / manifest['audition']['file']
        if hashlib.sha256(file.read_bytes()).hexdigest() != manifest['audition']['sha256']:
            raise ValueError('Audition hash mismatch')
        decoded = subprocess.run(['ffmpeg', '-v', 'error', '-threads', '1', '-i', str(file),
                                  '-f', 'f32le', '-acodec', 'pcm_f32le', '-threads', '1', '-'],
                                 check=True, capture_output=True).stdout
        samples = np.frombuffer(decoded, dtype='<f4').reshape(-1, 2)
        stats = analyze(samples)
        if stats['clipped'] or abs(stats['duration'] - manifest['audition']['duration']) > 1 / SAMPLE_RATE:
            raise ValueError(f'Audition decode failed acceptance: {stats}')
        # Lossy MP3 has encoder padding in its container and small endpoint
        # leakage; WAVs, not the preview, are the timed mixing assets.
        result['audition_decoded'] = stats
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    result = validate(args.directory)
    document = json.dumps(result, indent=2) + '\n'
    if args.out:
        args.out.write_text(document)
    print(json.dumps({'status': result['status'], 'assets': len(result['assets']),
                      'audition_decoded': result.get('audition_decoded')}, indent=2))
