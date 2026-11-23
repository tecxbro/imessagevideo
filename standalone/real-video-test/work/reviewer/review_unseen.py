"""Independently compare visible tracks and sound in the unseen fixture and reconstruction."""
import argparse
import json
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


def decode(path):
    raw = subprocess.check_output(['ffmpeg', '-nostdin', '-v', 'error', '-xerror', '-i', str(path), '-an',
                                   '-map', '0:v:0', '-fps_mode', 'passthrough', '-pix_fmt', 'rgb24',
                                   '-c:v', 'rawvideo', '-threads', '1', '-f', 'rawvideo', 'pipe:1'])
    return np.frombuffer(raw, dtype=np.uint8).reshape(-1, 270, 480, 3).astype(np.int16)


def audio(path):
    probe = subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'a:0', '-show_entries',
                                     'stream=sample_rate,start_time,duration,channels', '-of', 'json', str(path)])
    streams = json.loads(probe)['streams']
    if not streams:
        return {'stream': None, 'cues': []}
    raw = subprocess.check_output(['ffmpeg', '-nostdin', '-v', 'error', '-xerror', '-i', str(path), '-map', '0:a:0',
                                   '-ac', '1', '-ar', '48000', '-f', 'f32le', 'pipe:1'])
    s = np.frombuffer(raw, dtype='<f4')
    rate = 48000
    width = 240
    rms = np.sqrt((s[:len(s) // width * width].reshape(-1, width) ** 2).mean(axis=1))
    active = np.flatnonzero(rms > .02).tolist()
    groups = []
    for sample in active:
        if not groups or sample - groups[-1][-1] > 1:
            groups.append([sample])
        else:
            groups[-1].append(sample)
    cues = []
    for group in groups:
        start, stop = group[0] * width, (group[-1] + 1) * width
        x = s[start:stop]
        frequency = int(abs(np.fft.rfft(x * np.hanning(len(x)), n=48000)).argmax())
        cues.append({'start_seconds': start / rate, 'end_seconds': stop / rate, 'peak_hz': frequency})
    return {'stream': streams[0], 'cues': cues}


def centroids(masks):
    positions = []
    for frame in masks:
        y, x = np.where(frame)
        positions.append([x.mean(), y.mean()] if x.size else [float('nan')] * 2)
    return np.array(positions)


def tracks(frames):
    r, g, b = frames.transpose(3, 0, 1, 2)
    shuttle = (r > 150) & (b > 130) & (r - g > 35) & (b - g > 45)
    anchor = (g[:, 160:190, 80:130] > 150) & (r[:, 160:190, 80:130] < 125) & (g[:, 160:190, 80:130] > b[:, 160:190, 80:130] + 12)
    tether = (b > 130) & (g > 105) & (b - r > 45) & (g - r > 23) & (b - g > 18)
    return {'shuttle': centroids(shuttle), 'fixed_anchor': centroids(anchor) + [80, 160], 'tether': centroids(tether)}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('input', type=Path)
    p.add_argument('output', type=Path)
    p.add_argument('evidence', type=Path)
    args = p.parse_args()
    args.evidence.mkdir(parents=True, exist_ok=True)
    a, b = decode(args.input), decode(args.output)
    at, bt = tracks(a), tracks(b)
    count = min(len(a), len(b))
    frames = [0, 14, 22, 32, 34, 41, 43, 52, 60, 62, 72, count - 1]
    comparison = {'decoded_frames': [len(a), len(b)], 'visible_points': {},
                  'audio': {'source': audio(args.input), 'output': audio(args.output)}}
    for key, coord in at.items():
        delta = np.linalg.norm(coord[:count] - bt[key][:count], axis=1)
        comparison['visible_points'][key] = {
            'worst_frame': int(np.nanargmax(delta)), 'max_center_error_px': round(float(np.nanmax(delta)), 3),
            'sample_source': coord[frames].round(2).tolist(), 'sample_output': bt[key][frames].round(2).tolist()}
    cmp = np.abs(a[:count] - b[:count])
    comparison['rgb_mae_first_frame'] = {name: float(cmp[0, y, x].mean()) for name, (y, x) in {
        'fixed_panel': (slice(222, 228), slice(120, 365)), 'fixed_bright_bar': (slice(56, 63), slice(53, 100)),
        'fixed_muted_bar': (slice(56, 63), slice(103, 132)), 'fixed_baseline': (slice(207, 216), slice(52, 428)),
    }.items()}
    comparison['sample_frames'] = frames
    comparison['mean_rgb_at_frame_89'] = float(np.abs(a[-1] - b[-1]).mean())
    (args.evidence / 'observations.json').write_text(json.dumps(comparison, indent=2) + '\n')
    row_length = 6
    board = Image.new('RGB', (240 * row_length, 600), '#202731')
    font = ImageDraw.Draw(board)
    for idx, frame in enumerate(frames):
        x, y = (idx % row_length) * 240, (idx // row_length) * 300
        font.text((x + 6, y + 1), f'FRAME {frame} | source ↑, reconstruction ↓', fill='white')
        for row, video in enumerate((a, b)):
            sample = Image.fromarray(video[frame].astype(np.uint8)).resize((240, 135), Image.Resampling.LANCZOS)
            board.paste(sample, (x, y + 16 + row * 140))
    board.save(args.evidence / 'frame-pairs.jpg', quality=94)


if __name__ == '__main__':
    main()
