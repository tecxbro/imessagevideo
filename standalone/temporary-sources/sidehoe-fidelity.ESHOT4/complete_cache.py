from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import sys
from itertools import groupby
import subprocess

if __name__=='__main__':
    project,cache = map(Path,sys.argv[1:3])
    frames=[f for f in range(778) if not (cache/f"{f:06d}.png").exists()]
    def fill(g):
        for a,b in g:
            subprocess.run([sys.executable, str(project/'render.py'), '--cache', str(cache),
                            '--frames', f'{a}:{b}'], check=True,stdout=subprocess.DEVNULL)
    from concurrent.futures import ThreadPoolExecutor
    ranges = []
    for _,g in groupby(enumerate(frames), key=lambda q:q[1]-q[0]):
        values=[f for _,f in g]
        ranges.append((values[0],values[-1]))
    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(fill,[ranges[i::4] for i in range(4)]))
    assert len(list(cache.glob('*.png')))==778
    print('Complete frame cache:',len(list(cache.glob('*.png'))))
