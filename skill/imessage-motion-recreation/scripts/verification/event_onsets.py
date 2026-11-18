"""Local temporal review gate. Frames are zero-based; boxes are normalized xyxy."""
import argparse
import csv
from functools import lru_cache
import json
from pathlib import Path
import subprocess
import time

import numpy as np

try:
    from PIL import Image, ImageDraw
except ImportError:
    Image = ImageDraw = None


@lru_cache(maxsize=1)
def cadence_option():
    options = subprocess.check_output(['ffmpeg', '-hide_banner', '-h', 'full'], text=True, stderr=subprocess.STDOUT)
    return '-fps_mode' if any(line.split()[0].split('[')[0] == '-fps_mode' for line in options.splitlines() if line.split()) else '-vsync'


def decode(path):
    probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_streams', '-of', 'json', str(path)]))['streams'][0]
    n, d = map(int, probe['avg_frame_rate'].split('/'))
    width = min(480, int(probe['width']))
    height = max(1, round(int(probe['height']) * width / int(probe['width'])))
    process = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', str(path), '-map', '0:v:0', '-vf', f'scale={width}:{height}', cadence_option(), 'passthrough', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
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


def coalesce(events):
    merged = []
    for event in events:
        event = {**event, 'bbox': list(event['bbox'])}
        changed = True
        while changed:
            changed = False
            for other in merged:
                a, b = event['bbox'], other['bbox']
                if (event['frame'] == other['frame'] and event['kind'] == other['kind']
                        and min(a[2], b[2]) >= max(a[0], b[0])
                        and min(a[3], b[3]) >= max(a[1], b[1])):
                    event['bbox'] = [min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3])]
                    event['magnitude'] = max(event['magnitude'], other['magnitude'])
                    merged.remove(other)
                    changed = True
                    break
        merged.append(event)
    return sorted(merged, key=lambda e: (e['frame'], e['kind'], e['bbox']))


def spatial_transition(frames, grid=None):
    h, w = frames.shape[1:3]
    ny, nx = grid if grid is not None else (min(8, h), min(8, w))
    ys, xs = np.linspace(0, h, ny+1, dtype=int), np.linspace(0, w, nx+1, dtype=int)
    cells = np.stack([frames[:, y0:y1, x0:x1].mean((1, 2))
                      for y0, y1 in zip(ys, ys[1:]) for x0, x1 in zip(xs, xs[1:])], axis=1)
    return np.diff(cells, axis=0)


def compare_frames(source, candidate, sm, cm, events, tolerance=2, window=20, frame_map=None, candidate_events=None):
    rows = []
    events = coalesce(events)
    for event in events:
        f = event['frame']
        expected = float(np.interp(f, *zip(*frame_map))) if frame_map else f/sm['fps']*cm['fps']
        lo,hi = max(1,round(expected)-window),min(len(candidate)-1,round(expected)+window)
        first = max(0,lo-2)
        a = crop(source[max(0,f-1):f+1], event['bbox'])
        b = crop(candidate[first:min(len(candidate),hi+3)], event['bbox'])
        # Match the signed RGB state transition, not simply the largest nearby motion.
        signature = a[-1].mean((0,1))-a[0].mean((0,1))
        trajectory = b.mean((1,2))
        differences = np.diff(trajectory, axis=0)
        indices = np.arange(lo,hi+1)
        if event['kind']=='settle':
            strength = np.linalg.norm(differences,axis=1)
            matches = [i for i in indices if i>=2 and strength[i-2-first]>2 and strength[i-1-first:min(i+2-first,len(strength))].max()<2]
            found = int(min(matches,key=lambda i:abs(i-expected))) if matches else None
        else:
            norm = np.linalg.norm(signature)
            scores = np.linalg.norm(differences[indices-1-first]-signature,axis=1)
            valid = scores < max(3, norm*.65)
            valid &= np.linalg.norm(differences[indices-1-first],axis=1)>max(2,norm*.25)
            regional = {}
            for other in candidate_events or []:
                if other['kind'] != event['kind'] or not lo <= other['frame'] <= hi:
                    continue
                a0, b0 = event['bbox'], other['bbox']
                overlap = max(0, min(a0[2],b0[2])-max(a0[0],b0[0])) * max(0, min(a0[3],b0[3])-max(a0[1],b0[1]))
                union = (a0[2]-a0[0])*(a0[3]-a0[1])+(b0[2]-b0[0])*(b0[3]-b0[1])-overlap
                if overlap > 0:
                    regional[other['frame']] = max(regional.get(other['frame'], 0), overlap/union)
            if regional:
                peers = [e for e in events if e['frame'] == f and e['kind'] == event['kind']]
                support = {}
                for i in regional:
                    boxes = [e['bbox'] for e in candidate_events if e['frame'] == i and e['kind'] == event['kind']]
                    support[i] = sum(any(min(a['bbox'][2], b[2]) > max(a['bbox'][0], b[0])
                                         and min(a['bbox'][3], b[3]) > max(a['bbox'][1], b[1]) for b in boxes) for a in peers)
                valid = np.array([i in regional and support[i] == max(support.values()) for i in indices])
                valid &= differences[indices-1-first] @ signature > 0
            matches = indices[valid]
            if len(matches):
                grid = (min(8, a.shape[1], b.shape[1]), min(8, a.shape[2], b.shape[2]))
                target = spatial_transition(a, grid)[0]
                transitions = spatial_transition(b, grid)[matches-1-first]
                spatial_scores = np.linalg.norm(transitions-target, axis=(1,2)) / max(1, np.linalg.norm(target))
                combined = spatial_scores + scores[valid] / max(3, norm) + np.array([1-regional.get(i,1) for i in matches])
                found = int(min(zip(matches, combined), key=lambda item: (round(float(item[1]), 6), abs(item[0]-expected), item[0]))[0])
            else:
                found = None
        delta = None if found is None else round(found-expected,3)
        status = 'missing' if found is None else ('late' if delta>tolerance else 'early' if delta < -tolerance else 'pass')
        rows.append({**event, 'candidate_frame':found, 'expected_frame':round(expected,3), 'delta_frames':delta, 'status':status})
    return rows


def write_sheets(directory, source_path, candidate_path, rows):
    if Image is None:
        raise ValueError('--sheets requires Pillow')
    directory.mkdir(parents=True, exist_ok=True)
    failures = [r for r in rows if r['status'] != 'pass']
    images = {}
    for label, path, key in [('source', source_path, 'frame'), ('candidate', candidate_path, 'expected_frame')]:
        probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'v:0',
                                                  '-count_frames', '-show_entries', 'stream=nb_read_frames', '-of', 'json', str(path)]))
        count = int(probe['streams'][0]['nb_read_frames'])
        indices = sorted({max(0, min(count-1, round(r[key])+d)) for r in failures for d in range(-2, 3)} |
                         {max(0, min(count-1, r['candidate_frame']+d)) for r in failures if label == 'candidate' and r['candidate_frame'] is not None for d in range(-2, 3)})
        if not indices:
            continue
        ranges = []
        for f in indices:
            if ranges and f == ranges[-1][1]+1:
                ranges[-1][1] = f
            else:
                ranges.append([f, f])
        expression = '+'.join(f'between(n\\,{a}\\,{b})' for a, b in ranges)
        folder = directory / label
        folder.mkdir(exist_ok=True)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(path), '-map', '0:v:0', '-vf', f'select={expression}',
                        cadence_option(), 'passthrough', '-start_number', '0', str(folder/'extract-%06d.png')], check=True)
        for i, f in enumerate(indices):
            target = folder / f'frame-{f:06d}.png'
            (folder/f'extract-{i:06d}.png').replace(target)
            images[label, f] = target
        images[label, 'count'] = count
    for i, r in enumerate(failures):
        centers = [round(r['expected_frame'])]
        if r['candidate_frame'] is not None and r['candidate_frame'] != centers[0]:
            centers.append(r['candidate_frame'])
        for center in centers:
            sheet = Image.new('RGB', (1280, 5*384), '#222222')
            draw = ImageDraw.Draw(sheet)
            for row, d in enumerate(range(-2, 3)):
                for col, label in enumerate(['source', 'candidate']):
                    f = max(0, min(images[label, 'count']-1, (r['frame'] if col == 0 else center)+d))
                    with Image.open(images[label, f]) as im:
                        im.thumbnail((640, 360))
                        sheet.paste(im, (col*640, row*384+24))
                    draw.text((col*640+5, row*384+5), f'{label} native frame {f}', fill='white')
            sheet.save(directory/f'failure-{i:03d}-source-{r["frame"]}-candidate-{center}.jpg', quality=92)


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
            q.add_argument('--sheets',type=Path,help='Write paired failure context sheets and native PNG frames (requires Pillow)')
    args=p.parse_args(); started=time.monotonic()
    source,sm=decode(args.source)
    events=json.loads(args.events.read_text())['events'] if getattr(args,'events',None) else scan_frames(source,sm,args.threshold,args.stable)
    report={'source':sm,'events':events}
    if args.command=='compare':
        candidate,cm=decode(args.candidate)
        if args.roi_events:
            events+=json.loads(args.roi_events.read_text())['events']
        events=coalesce(events)
        mapping=json.loads(args.frame_map.read_text()) if args.frame_map else None
        candidate_events=coalesce(scan_frames(candidate,cm,args.threshold,args.stable))
        rows=compare_frames(source,candidate,sm,cm,events,args.tolerance,args.window,mapping,candidate_events)
        matched=[r for r in rows if r['candidate_frame'] is not None]
        only=[e for e in candidate_events if not any(abs(e['frame']-r['candidate_frame'])<=args.tolerance and all(abs(a-b)<.15 for a,b in zip(e['bbox'],r['bbox'])) for r in matched)]
        report.update(events=events,candidate=cm,results=rows,candidate_only=only,failures=sum(r['status']!='pass' for r in rows),tolerance=args.tolerance)
        fields=['frame','kind','candidate_frame','delta_frames','status','bbox']
        with args.out.with_suffix('.csv').open('w') as stream:
            writer=csv.DictWriter(stream,fields,extrasaction='ignore');writer.writeheader();writer.writerows(rows)
        lines=['| source | kind | candidate | delta | status |','|---|---|---|---|---|']
        lines += [f"| {r['frame']} | {r['kind']} | {r['candidate_frame']} | {r['delta_frames']} | {r['status']} |" for r in rows if r['status']!='pass']
        args.out.with_suffix('.md').write_text('\n'.join(lines)+'\n')
        if args.sheets:
            analysis_seconds=round(time.monotonic()-started,3)
            write_sheets(args.sheets,args.source,args.candidate,rows)
            report['analysis_seconds']=analysis_seconds
    report['seconds']=round(time.monotonic()-started,3)
    args.out.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ['events','results','candidate_only']},indent=2))
    print(f"events={len(events)} candidate_only={len(report.get('candidate_only',[]))}")
    return int(bool(report.get('failures')))


if __name__=='__main__':
    raise SystemExit(main())
