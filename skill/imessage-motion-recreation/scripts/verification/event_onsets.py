"""Local temporal review gate. Frames are zero-based; boxes are normalized xyxy."""
import argparse
import csv
import json
from pathlib import Path
import subprocess
import time

import numpy as np


def decode(path):
    probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_streams', '-of', 'json', str(path)]))['streams'][0]
    n, d = map(int, probe['avg_frame_rate'].split('/'))
    width = min(480, int(probe['width']))
    height = max(1, round(int(probe['height']) * width / int(probe['width'])))
    process = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', str(path), '-vf', f'scale={width}:{height}', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    frames = []
    size = width * height * 3
    while True:
        data = process.stdout.read(size)
        if not data:
            break
        if len(data) != size:
            raise ValueError('Truncated decoded frame')
        frames.append(np.frombuffer(data, np.uint8).reshape(height, width, 3))
    process.stdout.close()
    if process.wait() or not frames:
        raise ValueError(f'Could not decode {path}')
    return np.stack(frames), {'path': str(path), 'fps': n / d, 'width': int(probe['width']), 'height': int(probe['height']), 'frames': len(frames)}


def regions(mask):
    remaining = set(map(tuple, np.argwhere(mask)))
    while remaining:
        pending = [remaining.pop()]
        group = []
        while pending:
            y, x = pending.pop()
            group.append((y, x))
            for neighbor in [(y-1, x), (y+1, x), (y, x-1), (y, x+1)]:
                if neighbor in remaining:
                    remaining.remove(neighbor)
                    pending.append(neighbor)
        ys, xs = zip(*group)
        yield min(xs), min(ys), max(xs)+1, max(ys)+1


def scan_frames(frames, meta, threshold=5., stable=3, grid=32):
    _, h, w, _ = frames.shape
    ny, nx = max(1, round(h/grid)), max(1, round(w/grid))
    edges_y, edges_x = np.linspace(0, h, ny+1, dtype=int), np.linspace(0, w, nx+1, dtype=int)
    changes = np.zeros((len(frames), ny, nx))
    for f in range(1, len(frames)):
        delta = np.abs(frames[f].astype(float)-frames[f-1].astype(float)).mean(2)
        for y in range(ny):
            for x in range(nx):
                changes[f,y,x] = delta[edges_y[y]:edges_y[y+1],edges_x[x]:edges_x[x+1]].mean()
    active = changes > threshold
    events = []
    last_cut = -stable
    def append(f, box, kind, magnitude):
        events.append({'frame': f, 'time': f/meta['fps'], 'bbox': box, 'kind': kind, 'magnitude': round(float(magnitude), 3)})
    quiet = changes < threshold * .3
    for f in range(stable, len(frames)-stable):
        if active[f].mean() > .65:
            if f-last_cut >= stable:
                append(f, [0,0,1,1], 'cut', changes[f].mean())
            last_cut = f
            continue
        prior = changes[f-stable:f].max(0)
        onset = active[f] & ((prior < threshold*.3) | (changes[f] > 3*prior)) & quiet[f+1:f+stable+1].all(0)
        for kind, mask in [('local-onset', onset), ('settle', quiet[f:f+stable].all(0) & active[f-stable:f].all(0))]:
            if f-last_cut < stable:
                continue
            for x0,y0,x1,y1 in regions(mask):
                box = [edges_x[x0]/w, edges_y[y0]/h, edges_x[x1]/w, edges_y[y1]/h]
                magnitude = changes[f if kind=='local-onset' else f-1,y0:y1,x0:x1].max()
                append(f, box, kind, magnitude)
    return events


def crop(frames, box):
    h,w = frames.shape[1:3]
    x0,y0,x1,y1 = box
    return frames[:, max(0,int(y0*h)):max(1,int(np.ceil(y1*h))), max(0,int(x0*w)):max(1,int(np.ceil(x1*w)))]


def compare_frames(source, candidate, sm, cm, events, tolerance=2, window=20, frame_map=None):
    rows = []
    for event in events:
        f = event['frame']
        expected = float(np.interp(f, *zip(*frame_map))) if frame_map else f/sm['fps']*cm['fps']
        a, b = crop(source, event['bbox']), crop(candidate, event['bbox'])
        # Match the signed RGB state transition, not simply the largest nearby motion.
        signature = a[min(f,len(a)-1)].mean((0,1))-a[max(0,f-1)].mean((0,1))
        trajectory = b.mean((1,2))
        differences = np.diff(trajectory, axis=0)
        lo,hi = max(1,round(expected)-window),min(len(b)-1,round(expected)+window)
        indices = np.arange(lo,hi+1)
        if event['kind']=='settle':
            strength = np.linalg.norm(differences,axis=1)
            matches = [i for i in indices if i>=2 and strength[i-2]>2 and strength[i-1:min(i+2,len(strength))].max()<2]
            found = int(min(matches,key=lambda i:abs(i-expected))) if matches else None
        else:
            norm = np.linalg.norm(signature)
            scores = np.linalg.norm(differences[indices-1]-signature,axis=1)
            valid = scores < max(3, norm*.65)
            valid &= np.linalg.norm(differences[indices-1],axis=1)>max(2,norm*.25)
            matches = indices[valid]
            found = int(matches[np.argmin(scores[valid])]) if len(matches) else None
        delta = None if found is None else round(found-expected,3)
        status = 'missing' if found is None else ('late' if delta>tolerance else 'early' if delta < -tolerance else 'pass')
        rows.append({**event, 'candidate_frame':found, 'expected_frame':round(expected,3), 'delta_frames':delta, 'status':status})
    return rows


def main():
    p=argparse.ArgumentParser(description=__doc__)
    sub=p.add_subparsers(dest='command',required=True)
    for name in ['scan','compare']:
        q=sub.add_parser(name); q.add_argument('source'); q.add_argument('--out',type=Path,required=True)
        q.add_argument('--threshold',type=float,default=5); q.add_argument('--stable',type=int,default=6)
        if name=='compare':
            q.add_argument('candidate'); q.add_argument('--events',type=Path); q.add_argument('--roi-events',type=Path)
            q.add_argument('--frame-map',type=Path,help='JSON array of [source_frame,candidate_frame] anchors, linearly interpolated')
            q.add_argument('--tolerance',type=int,default=2); q.add_argument('--window',type=int,default=20)
    args=p.parse_args(); started=time.monotonic()
    source,sm=decode(args.source)
    events=json.loads(args.events.read_text())['events'] if getattr(args,'events',None) else scan_frames(source,sm,args.threshold,args.stable)
    report={'source':sm,'events':events}
    if args.command=='compare':
        candidate,cm=decode(args.candidate)
        if args.roi_events:
            events+=json.loads(args.roi_events.read_text())['events']
        mapping=json.loads(args.frame_map.read_text()) if args.frame_map else None
        rows=compare_frames(source,candidate,sm,cm,events,args.tolerance,args.window,mapping)
        candidate_events=scan_frames(candidate,cm,args.threshold,args.stable)
        matched=[r for r in rows if r['candidate_frame'] is not None]
        only=[e for e in candidate_events if not any(abs(e['frame']-r['candidate_frame'])<=args.tolerance and all(abs(a-b)<.15 for a,b in zip(e['bbox'],r['bbox'])) for r in matched)]
        report.update(candidate=cm,results=rows,candidate_only=only,failures=sum(r['status']!='pass' for r in rows),tolerance=args.tolerance)
        fields=['frame','kind','candidate_frame','delta_frames','status','bbox']
        with args.out.with_suffix('.csv').open('w') as stream:
            writer=csv.DictWriter(stream,fields,extrasaction='ignore');writer.writeheader();writer.writerows(rows)
        lines=['| source | kind | candidate | delta | status |','|---|---|---|---|---|']
        lines += [f"| {r['frame']} | {r['kind']} | {r['candidate_frame']} | {r['delta_frames']} | {r['status']} |" for r in rows if r['status']!='pass']
        args.out.with_suffix('.md').write_text('\n'.join(lines)+'\n')
    report['seconds']=round(time.monotonic()-started,3)
    args.out.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ['events','results','candidate_only']},indent=2))
    print(f"events={len(events)} candidate_only={len(report.get('candidate_only',[]))}")
    return int(bool(report.get('failures')))


if __name__=='__main__':
    raise SystemExit(main())
