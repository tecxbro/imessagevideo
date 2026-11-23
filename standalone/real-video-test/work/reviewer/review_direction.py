"""Decisive frames and decoded equality for the direction and donor-edit films."""
import argparse
import json
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def ffmpeg(input, *args):
    return subprocess.check_output(['ffmpeg', '-nostdin', '-v', 'error', '-xerror', '-i', str(input),
                                    '-map', '0:v:0', '-an', *args])


def hashes(movie):
    output = ffmpeg(movie, '-fps_mode', 'passthrough', '-pix_fmt', 'rgb24', '-c:v', 'rawvideo', '-threads', '1',
                    '-hash', 'sha256', '-f', 'framehash', 'pipe:1').decode()
    return [line.split(',')[-1].strip() for line in output.splitlines() if not line.startswith('#')]


def samples(movie, frames):
    expr = '+'.join(f'eq(n,{i})' for i in frames)
    data = ffmpeg(movie, '-vf', f"select='{expr}'", '-fps_mode', 'passthrough', '-pix_fmt', 'rgb24',
                  '-c:v', 'rawvideo', '-threads', '1', '-f', 'rawvideo', 'pipe:1')
    if len(data) != len(frames) * 720 * 480 * 3:
        raise ValueError(f'{movie} did not decode the requested frames')
    stride = 720 * 480 * 3
    return [Image.frombytes('RGB', (720, 480), data[i:i + stride]) for i in range(0, len(data), stride)]


def image_pair(primary, secondary, frames, path, prefix):
    cell_w, cell_h = 322, 220
    board = Image.new('RGB', (cell_w * len(frames), 2 * cell_h + 26), '#202731')
    w = ImageDraw.Draw(board)
    font = ImageFont.load_default(size=15)
    for index, frame in enumerate(frames):
        w.text((index * cell_w + 8, 1), f'{prefix} frame {frame}', font=font, fill='white')
        for row, image in enumerate((primary[index], secondary[index])):
            pic = image.resize((cell_w - 4, cell_h - 6), Image.Resampling.LANCZOS)
            board.paste(pic, (index * cell_w, 20 + row * cell_h))
    board.save(path, quality=94)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project', type=Path)
    parser.add_argument('evidence', type=Path)
    args = parser.parse_args()
    args.evidence.mkdir(parents=True, exist_ok=True)
    original, edit = (args.project / path for path in ('concert-tickets.mp4', 'meet-at-the-doors.mp4'))
    before, after = hashes(original), hashes(edit)
    changed = [i for i, (a, b) in enumerate(zip(before, after)) if a != b]
    original_plan = json.loads((args.project / 'plan-reply-approved.json').read_text())['plan']
    edited_plan = json.loads((args.project / 'plan-edit-approved.json').read_text())['plan']
    first, stop = original_plan['shots'][0]['frames'], sum(shot['frames'] for shot in original_plan['shots'][:2])
    evidence = {'frames_decoded': [len(before), len(after)], 'expected_changed_span': [first, stop],
                'actual_changed_span': [min(changed), max(changed) + 1], 'changed_frames': len(changed),
                'untouched_frames_equal': sum(1 for i in range(len(before)) if (i < first or i >= stop) and before[i] == after[i]),
                'unchanged_adjacent': {str(i): before[i] == after[i] for i in [first - 2, first - 1, stop, stop + 1]},
                'unchanged_shot_plans': [original_plan['shots'][i] == edited_plan['shots'][i] for i in (0, 2)]}
    fps = json.loads((args.project / 'plan-reply-approved.json').read_text())['plan']['fps']
    for label, frames in (('entry', [first - 2, first - 1, first, first + 1, first + 12]),
                          ('exit', [stop - 12, stop - 2, stop - 1, stop, stop + 1]),
                          ('gesture', [first + 5, first + 35, first + 43, first + 56, stop - 12])):
        a, b = samples(original, frames), samples(edit, frames)
        image_pair(a, b, frames, args.evidence / f'{label}.jpg', 'Cut')
        if label == 'gesture':
            b[2].save(args.evidence / 'edited-text-native.png')
    motions = [args.project / name / 'preview.mp4' for name in ('proof-browse', 'proof-reply')]
    frames = [0, fps // 2, fps, 45, 60, 95]
    image_pair(*(samples(x, frames) for x in motions), frames, args.evidence / 'pitch-gestures.jpg', 'Proof')
    (args.evidence / 'decoded-comparison.json').write_text(json.dumps(evidence, indent=2) + '\n')
    print(json.dumps(evidence))


if __name__ == '__main__':
    main()
