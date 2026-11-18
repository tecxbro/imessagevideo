"""Create a private seeded intervention key and damaged production UI PCM."""
import argparse
import json
from pathlib import Path
import numpy as np
from scipy import signal
from check_cues import SR, add, decode
import subprocess


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('stem', type=Path); p.add_argument('--receipt', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True); p.add_argument('--key', type=Path, required=True)
    p.add_argument('--seed', type=int, default=73129)
    a = p.parse_args()
    if a.output.exists() or a.key.exists():
        p.error('Refusing to overwrite an existing intervention or key')
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.key.parent.mkdir(parents=True, exist_ok=True)
    receipt = json.loads(a.receipt.read_text()); base = a.receipt.parent.parent
    x = decode(a.stem)
    rng = np.random.default_rng(a.seed)
    candidates = [c for c in receipt['cues'] if 140 < c['canonical_event']['frame'] < 800]
    chosen = rng.choice(len(candidates), 8, replace=False)
    changes = [('late', 1), ('late', 2), ('late', 4), ('late', 8), ('early', -3),
               ('attenuated', 0), ('lowpassed', 0), ('dropped', 0)]
    defects = []
    for index, (kind, frames) in zip(chosen, changes):
        c = candidates[index]; wave = np.load(base / c['reference'], allow_pickle=False)
        start = c['clip_start_sample_unclipped']; delta = round(frames * SR / receipt['fps'])
        add(x, wave, start, -1)
        if kind in {'late', 'early'}:
            add(x, wave, start + delta)
        elif kind == 'attenuated':
            add(x, wave, start, 10**(-12/20))
        elif kind == 'lowpassed':
            filtered = signal.sosfilt(signal.butter(6, 550, fs=SR, output='sos'), wave, axis=0)
            add(x, filtered, start)
        defects.append({'ordinal': c['ordinal'], 'kind': kind, 'expected_sample': c['event_sample'],
                        'offset_samples': delta, 'offset_frames': frames})
    extra = next(c for c in receipt['cues'] if c['canonical_event']['kind']=='tap')
    wave = np.load(base / extra['reference'], allow_pickle=False)
    sample = round(33.25 * SR)
    add(x, wave, sample)
    defects.append({'ordinal': None, 'kind': 'extra', 'sample': sample})
    subprocess.run(['ffmpeg', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-',
                    '-c:a', 'flac', '-sample_fmt', 's32', '-n', str(a.output)], input=x.astype('<f4').tobytes(), check=True)
    a.key.write_text(json.dumps({'seed': a.seed, 'defects': defects}, indent=2)+'\n')
    a.key.chmod(0o600)
    print(f'Wrote {a.output}; private intervention key: {a.key}; {len(defects)} interventions')


if __name__ == '__main__':
    main()
