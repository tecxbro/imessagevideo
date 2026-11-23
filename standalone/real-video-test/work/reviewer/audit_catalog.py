"""Run the catalog's public export and fresh project renderer for independent review."""
import argparse
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


def execute(argv):
    return subprocess.run(argv, capture_output=True, text=True)


def open_video(movie, width=180, height=120):
    data = subprocess.check_output([
        'ffmpeg', '-nostdin', '-v', 'error', '-xerror', '-threads', '1', '-i', str(movie),
        '-map', '0:v:0', '-an', '-vf', f'scale={width}:{height}:flags=area',
        '-pix_fmt', 'rgb24', '-threads', '1', '-f', 'rawvideo', 'pipe:1',
    ])
    return np.frombuffer(data, dtype=np.uint8).reshape(-1, height, width, 3)


def filmstrip(reference, replay, row, path):
    a, b = open_video(reference), open_video(replay)
    if len(a) != len(b):
        raise ValueError(f'Expected a matching frame count, got {len(a)} and {len(b)}')
    n, h, w, _ = a.shape
    a16, b16 = a.astype(np.int16), b.astype(np.int16)
    source_motion = np.abs(a16 - a16[0]).mean(axis=(1, 2, 3))
    replay_motion = np.abs(b16 - b16[0]).mean(axis=(1, 2, 3))
    events = [e['frame'] for e in row.get('events', [])]
    dynamic = np.abs(a16[1:] - a16[:-1]).mean(axis=(1, 2, 3))
    peak_event = int(dynamic.argmax()) + 1
    frames = sorted(set([0, n // 3, n * 2 // 3, n - 1, max(0, peak_event - 1), peak_event, *events[:3]]))
    strip = Image.new('RGB', (w * len(frames), h * 2 + 42), '#232b37')
    draw = ImageDraw.Draw(strip)
    draw.text((6, 2), row['id'] + ' | bundled preview above, fresh output below', fill='white')
    for col, f in enumerate(frames):
        if f >= n:
            continue
        x = col * w
        draw.text((x + 4, 19), f'Frame {f}', fill='white')
        strip.paste(Image.fromarray(a[f]), (x, 39))
        strip.paste(Image.fromarray(b[f]), (x, 40 + h))
    strip.save(path)
    return {'source_peak_change': float(source_motion.max()), 'replay_peak_change': float(replay_motion.max()),
            'temporal_curve_mae': float(np.abs(source_motion - replay_motion).mean()),
            'temporal_difference_mae': float(np.abs((a16[1:] - a16[:-1]) - (b16[1:] - b16[:-1])).mean()),
            'sample_frames': frames}


def audit_one(skill, out, row):
    sid = row['id']
    target = out / sid
    target.mkdir(exist_ok=False)
    movie = target / 'project' / 'replay.mp4'
    preview = target / 'preview.mp4'
    commands = [
        [sys.executable, str(skill / 'scripts/recipes.py'), 'preview', sid, '--out', str(preview)],
        [sys.executable, str(skill / 'scripts/recipes.py'), 'export', sid, '--out', str(movie.parent)],
        [sys.executable, str(movie.parent / 'render_pillow.py'), '--scene', str(movie.parent / 'scene.json'), '--out', str(movie)],
        [sys.executable, str(skill / 'scripts/frames.py'), str(preview), str(movie), '--out', str(target / 'compare'),
         '--require-structure-match', '--max-pts-error-ms', '0', '--max-mae', '3'],
    ]
    result = {'id': sid, 'moves': row['moves'], 'fixed': row['fixed'], 'commands': commands}
    for cmd in commands:
        process = execute(cmd)
        with (target / 'commands.log').open('a') as log:
            log.write(f'$ {cmd!r} exit={process.returncode}\n{process.stdout}{process.stderr}\n')
        if process.returncode and cmd != commands[-1]:
            result.update(status='execution error', command=cmd, exit_code=process.returncode)
            return result
    try:
        report = json.loads((target / 'compare/report.json').read_text())
        result.update(frame_count=report['compared_frames'], structure_match=report['structure_match'],
                      errors=report['metrics'].get('full'), failures=report['failures'],
                      **filmstrip(preview, movie, row, target / 'strip.jpg'))
        result['status'] = 'comparison within limits' if report['limits_passed'] else 'comparison limits failed'
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        result.update(status='measurement error', error=str(error))
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('skill', type=Path)
    p.add_argument('out', type=Path)
    p.add_argument('--workers', type=int, default=3)
    p.add_argument('--ids', nargs='+')
    args = p.parse_args()
    skill, out = args.skill.resolve(), args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    rows = json.loads((skill / 'assets/seed/catalog.json').read_text())['entries']
    if args.ids is not None:
        rows = [row for row in rows if row['id'] in set(args.ids)]
    with ThreadPoolExecutor(max_workers=args.workers) as pool, (out / 'results.jsonl').open('w') as log:
        for result in pool.map(lambda row: audit_one(skill, out, row), rows):
            result.pop('commands')
            line = json.dumps(result)
            log.write(line + '\n')
            log.flush()
            print(result['id'], result['status'], flush=True)


if __name__ == '__main__':
    main()
