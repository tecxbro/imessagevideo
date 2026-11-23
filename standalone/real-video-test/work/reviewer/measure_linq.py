"""Independent per-frame content registration on the original Linq photo rail."""
import csv
import subprocess
import sys
from pathlib import Path

import numpy as np


def main(source, out):
    start, stop = 1065, 1135
    command = ['ffmpeg', '-nostdin', '-v', 'error', '-xerror', '-i', str(source), '-an',
               '-vf', f'trim=start_frame={start}:end_frame={stop},setpts=PTS-STARTPTS',
               '-fps_mode', 'passthrough', '-c:v', 'rawvideo', '-pix_fmt', 'gray', '-threads', '1', '-f', 'rawvideo', 'pipe:1']
    frames = np.frombuffer(subprocess.check_output(command), dtype=np.uint8).reshape(-1, 720, 960).astype(np.int16)
    if len(frames) != stop - start:
        raise RuntimeError('Source frame count changed')
    template = frames[1091 - start, 25:55, 194:410]
    records = []
    travel = 0
    for index, curr in enumerate(frames):
        error, x, y = min((float(np.abs(template - curr[25 + dy:55 + dy, 194 + dx:410 + dx]).mean()), dx, dy)
                          for dx in range(-5, 6) for dy in range(-5, 6))
        if index:
            # Both sides of the decoded strip show the same texture translated horizontally.
            # The crop is inside the rail, well clear of its fixed edge.
            prev = frames[index - 1]
            patch = curr[325:619:3, 216:564]
            rail_error, dx = min((float(np.abs(patch - prev[325:619:3, 216 + shift:564 + shift]).mean()), shift)
                                 for shift in range(-4, 190))
            travel += dx
        else:
            dx, rail_error = 0, 0
        records.append([start + index, x, y, round(error, 4), dx, travel, round(rail_error, 4)])
    with out.open('w') as fd:
        w = csv.writer(fd)
        w.writerow(['source_frame', 'heading_dx', 'heading_dy', 'heading_mae', 'rail_dx_from_prev', 'rail_total_dx', 'rail_mae'])
        w.writerows(records)


if __name__ == '__main__':
    main(Path(sys.argv[1]), Path(sys.argv[2]))
