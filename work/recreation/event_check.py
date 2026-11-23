#!/usr/bin/env python3
"""Event-onset alignment check between a reference film and a candidate render.

Whole-frame averages (global MAE/SSIM) cannot see a small discrete UI element
appearing a few frames early or late: the affected pixels are <0.2% of the
frame and the error lasts only a handful of frames, so it hides inside the
codec/motion noise floor. This was the Poke restaurant-selection defect: the
blue check popped at source frame 633 but candidate frame 645 while the
per-frame MAE there stayed *below* the film's own mean.

This check builds an *event map* per film on a coarse spatial grid and
compares event TIMES directly, not pixel averages:

  Tier 1 (color onsets): saturated-ink pixel count per hue bin per grid cell.
    An onset = cell crossing --ink-frac upward. Catches taps, selection
    checks, send buttons, toggles, colored bubbles.

  Tier 2 (change onsets): |F(t)-F(t-1)| hot-cells whose region returns to
    quiet within --persist frames = a new stable state (a pop), as opposed
    to sustained motion. Catches neutral pops (gray bubbles, keyboards).

Events (kind, frame, cell-cluster bbox) are matched between films by
kind+hue+location within --max-offset frames; a time offset > --tolerance
or an unmatched reference event is flagged.

Exit 0 = PASS, 1 = flagged. mp4 input needs ffmpeg; numpy+PIL afterwards.
Usage:
  event_check.py --ref source.mp4 --cand render.mp4 [--tolerance 2]
  event_check.py --ref-frames 'dir/*.png' --cand render.mp4
"""
import argparse, glob, json, subprocess, sys
from collections import deque
import numpy as np

FPS_NOMINAL = 30000 / 1001
CELL = 24          # px per grid cell (1440x1080 -> 60x45 grid)
HUES = 12


def probe(path):
    out = subprocess.check_output([
        'ffprobe', '-v', 'error', '-select_streams', 'v:0',
        '-show_entries', 'stream=width,height,avg_frame_rate',
        '-of', 'json', path])
    st = json.loads(out)['streams'][0]
    fr = st['avg_frame_rate'].split('/')
    fps = float(fr[0]) / float(fr[1]) if len(fr) == 2 else float(fr[0])
    return int(st['width']), int(st['height']), fps


def frames_mp4(path, w, h):
    cmd = ['ffmpeg', '-v', 'error', '-i', path,
           '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-']
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=w * h * 3 * 4)
    i = 0
    while True:
        buf = proc.stdout.read(w * h * 3)
        if len(buf) < w * h * 3:
            break
        yield i, np.frombuffer(buf, np.uint8).reshape(h, w, 3).copy()
        i += 1
    proc.wait()


def frames_png(pattern):
    from PIL import Image
    for i, f in enumerate(sorted(glob.glob(pattern))):
        yield i, np.asarray(Image.open(f).convert('RGB'))


def grid_maps(f, prev, gh, gw):
    """Return (changed_cell_frac[gh,gw], ink_count[HUES,gh,gw])."""
    a = f.astype(np.int16)
    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    mx = np.maximum(np.maximum(r, g), b)
    mn = np.minimum(np.minimum(r, g), b)
    d = mx - mn
    ink = (d > 60) & (mx > 120)
    dd = np.where(d == 0, 1, d)
    hr = np.where(mx == r, (60 * ((g - b) / dd) + 360) % 360,
        np.where(mx == g, 60 * ((b - r) / dd) + 120,
                 60 * ((r - g) / dd) + 240))
    hb = (hr / 30).astype(np.int32) % HUES
    H, W = f.shape[:2]
    cell_area = CELL * CELL
    yid = (np.arange(H) // CELL)[:, None]
    xid = (np.arange(W) // CELL)[None, :]
    cell = (yid * gw + xid)
    cell = np.broadcast_to(cell, (H, W))
    ink_counts = np.bincount((hb[ink] * gh * gw + cell[ink]),
                             minlength=HUES * gh * gw).reshape(HUES, gh, gw)
    if prev is None:
        chg = np.zeros((gh, gw), np.float32)
    else:
        dm = (np.abs(a - prev.astype(np.int16)).max(2) > 45)
        chg = np.bincount(cell[dm], minlength=gh * gw).reshape(gh, gw) / cell_area
    return chg.astype(np.float32), ink_counts


def clusters(hot):
    """8-connected clusters on a coarse hot-cell grid -> bboxes in px."""
    H, W = hot.shape
    lab = np.zeros_like(hot, np.int32)
    out = []
    cid = 0
    for sy, sx in zip(*np.where(hot)):
        if lab[sy, sx]:
            continue
        cid += 1
        q = deque([(sy, sx)]); lab[sy, sx] = cid
        xs = [sx]; ys = [sy]
        while q:
            y, x = q.popleft()
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < H and 0 <= nx < W and hot[ny, nx] and not lab[ny, nx]:
                        lab[ny, nx] = cid
                        q.append((ny, nx)); xs.append(nx); ys.append(ny)
        out.append((min(xs) * CELL, min(ys) * CELL,
                    (max(xs) + 1) * CELL, (max(ys) + 1) * CELL, len(xs) * CELL * CELL))
    return out


def collect(frame_iter, ink_frac, change_frac, persist):
    """Single pass -> event lists with persistence qualification.

    An 'appear' onset is kept only if the ink stays on for >=persist frames
    after onset (a real new element, not codec flicker). A 'change' onset
    requires quiet before AND after (a pop to a new stable state).
    """
    color_ev, change_ev = [], []
    prev = None
    ink_hist = deque(maxlen=persist + 1)   # recent ink counts (HUES,gh,gw)
    chg_hist = deque(maxlen=persist + 1)   # recent changed-cell fractions
    ink_pend = []                          # appear candidates: (frame,hue,cells)
    off_pend = []                          # disappear candidates
    chg_pend = []                          # change candidates
    last = -1
    for idx, f in frame_iter:
        last = idx
        H, W = f.shape[:2]
        gh, gw = -(-H // CELL), -(-W // CELL)
        chg, inkc = grid_maps(f, prev, gh, gw)
        hot = chg >= change_frac
        ink_hist.append(inkc)
        chg_hist.append(chg)
        prev_ink = ink_hist[-2] if len(ink_hist) > 1 else np.zeros_like(inkc)
        prev_chg = chg_hist[-2] if len(chg_hist) > 1 else np.zeros_like(chg)

        if idx > 0:
            # --- tier 1: per-(hue,cell) appear/disappear onsets
            for hb_ in range(HUES):
                now = inkc[hb_] >= ink_frac * CELL * CELL
                was = prev_ink[hb_] >= ink_frac * CELL * CELL
                for (x1, y1, x2, y2, area) in clusters(now & ~was):
                    if area < 3 * CELL * CELL:
                        continue
                    ev = {'kind': 'appear', 'frame': idx, 'hue': int(hb_),
                          'bbox': (x1, y1, x2, y2), 'area': area,
                          'cells': [(y, x) for y in range(y1 // CELL, -(-y2 // CELL))
                                    for x in range(x1 // CELL, -(-x2 // CELL))],
                          'stay': 0}
                    # was the cell region quiet BEFORE onset?
                    if len(ink_hist) > persist:
                        before = np.mean([ink_hist[j][hb_][y, x] >= ink_frac * CELL * CELL
                                          for j in range(0, len(ink_hist) - 1)
                                          for (y, x) in ev['cells']])
                        if before > 0.3:
                            continue
                    ink_pend.append(ev)
                for (x1, y1, x2, y2, area) in clusters(was & ~now):
                    if area < 3 * CELL * CELL:
                        continue
                    off_pend.append({'kind': 'disappear', 'frame': idx, 'hue': int(hb_),
                                     'bbox': (x1, y1, x2, y2), 'area': area,
                                     'cells': [(y, x) for y in range(y1 // CELL, -(-y2 // CELL))
                                               for x in range(x1 // CELL, -(-x2 // CELL))],
                                     'stay': 0})
            # --- tier 2: persistent localized change
            for (x1, y1, x2, y2, area) in clusters(hot & ~(prev_chg >= change_frac)):
                if area < 3 * CELL * CELL:   # require >=3 cells contiguous
                    continue
                ev = {'frame': idx, 'bbox': (x1, y1, x2, y2), 'area': area,
                      'cells': [(y, x) for y in range(y1 // CELL, -(-y2 // CELL))
                                for x in range(x1 // CELL, -(-x2 // CELL))],
                      'quiet_before': 0, 'quiet_after': 0}
                if len(chg_hist) > persist:
                    before = np.mean([chg_hist[j][y, x] >= change_frac
                                      for j in range(0, len(chg_hist) - 1)
                                      for (y, x) in ev['cells']])
                    if before > 0.3:
                        continue
                chg_pend.append(ev)
        # persistence qualification
        for p in list(ink_pend):
            k = idx - p['frame']
            if k > persist:
                if p['stay'] >= persist - 1:
                    color_ev.append({kk: p[kk] for kk in ('kind', 'frame', 'hue', 'bbox', 'area')})
                ink_pend.remove(p)
            elif k >= 1:
                on = sum(1 for (y, x) in p['cells']
                         if inkc[p['hue']][y, x] >= ink_frac * CELL * CELL)
                if on >= 0.7 * len(p['cells']):
                    p['stay'] += 1
        for p in list(off_pend):
            k = idx - p['frame']
            if k > persist:
                if p['stay'] >= persist - 1:
                    color_ev.append({kk: p[kk] for kk in ('kind', 'frame', 'hue', 'bbox', 'area')})
                off_pend.remove(p)
            elif k >= 1:
                off = sum(1 for (y, x) in p['cells']
                          if inkc[p['hue']][y, x] < ink_frac * CELL * CELL)
                if off >= 0.7 * len(p['cells']):
                    p['stay'] += 1
        for p in list(chg_pend):
            k = idx - p['frame']
            if k > persist:
                if p['quiet_after'] >= persist - 1:
                    change_ev.append({'kind': 'change', 'frame': p['frame'],
                                      'bbox': p['bbox'], 'area': p['area']})
                chg_pend.remove(p)
            elif k >= 1:
                hot_now = sum(1 for (y, x) in p['cells'] if chg[y, x] >= change_frac)
                if hot_now <= 0.3 * len(p['cells']):
                    p['quiet_after'] += 1
        prev = f
    # dedupe change events (same frame, overlapping bbox)
    dedup = []
    for e in sorted(change_ev, key=lambda e: -e['area']):
        if not any(o['frame'] == e['frame'] and iou(o['bbox'], e['bbox']) > 0.3
                   for o in dedup):
            dedup.append(e)
    return color_ev, sorted(dedup, key=lambda e: e['frame']), last


def iou(a, b):
    x1, y1 = max(a[0], b[0]), max(a[1], b[1])
    x2, y2 = min(a[2], b[2]), min(a[3], b[3])
    if x2 <= x1 or y2 <= y1:
        return 0.0
    inter = (x2 - x1) * (y2 - y1)
    return inter / ((a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter)


def center_dist(a, b):
    return (((a[0] + a[2] - b[0] - b[2]) / 2) ** 2 +
            ((a[1] + a[3] - b[1] - b[3]) / 2) ** 2) ** 0.5


def best_match(e, pool, max_offset):
    best, bs = None, 1e18
    for i, c in enumerate(pool):
        if c['kind'] != e['kind']:
            continue
        if e.get('hue') is not None and c.get('hue') != e['hue']:
            continue
        dt = abs(c['frame'] - e['frame'])
        if dt > max_offset or center_dist(e['bbox'], c['bbox']) > 5 * CELL:
            continue
        score = dt * 10 + center_dist(e['bbox'], c['bbox'])
        if score < bs:
            best, bs = i, score
    return best


def match_events(ref_ev, cand_ev, max_offset):
    """Mutual-best-match: a pair counts only if each prefers the other."""
    cand_best = {}
    for j, c in enumerate(cand_ev):
        cand_best[j] = best_match(c, ref_ev, max_offset)
    for i, e in enumerate(sorted(ref_ev, key=lambda e: e['frame'])):
        b = best_match(e, cand_ev, max_offset)
        if b is not None and cand_best.get(b) is not None and \
                ref_ev.index(e) == cand_best[b]:
            e['match_frame'] = cand_ev[b]['frame']
            e['offset'] = cand_ev[b]['frame'] - e['frame']
        else:
            e['match_frame'] = None
            e['offset'] = None
    return ref_ev


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ref'); ap.add_argument('--cand')
    ap.add_argument('--ref-frames'); ap.add_argument('--cand-frames')
    ap.add_argument('--tolerance', type=int, default=2)
    ap.add_argument('--ink-frac', type=float, default=0.15)
    ap.add_argument('--change-frac', type=float, default=0.15)
    ap.add_argument('--persist', type=int, default=5)
    ap.add_argument('--max-offset', type=int, default=60)
    ap.add_argument('--out')
    a = ap.parse_args()

    def load(video, pngglob):
        if pngglob:
            return frames_png(pngglob)
        w, h, _ = probe(video)
        return frames_mp4(video, w, h)

    r_color, r_change, r_last = collect(load(a.ref, a.ref_frames),
                                      a.ink_frac, a.change_frac, a.persist)
    c_color, c_change, c_last = collect(load(a.cand, a.cand_frames),
                                      a.ink_frac, a.change_frac, a.persist)
    report = {'ref': a.ref or a.ref_frames, 'cand': a.cand or a.cand_frames,
              'ref_frames': r_last + 1, 'cand_frames': c_last + 1,
              'tolerance_frames': a.tolerance}
    flagged = []
    for tier, ev_r, ev_c in (('color', r_color, c_color), ('change', r_change, c_change)):
        rows = []
        for e in match_events(ev_r, ev_c, a.max_offset):
            row = {'tier': tier, 'kind': e['kind'], 'ref_frame': int(e['frame']),
                   'cand_frame': (int(e['match_frame'])
                                  if e['match_frame'] is not None else None),
                   'offset': (int(e['offset'])
                              if e['offset'] is not None else None),
                   'bbox': [int(v) for v in e['bbox']], 'area': int(e['area'])}
            if e.get('hue') is not None:
                row['hue_bin'] = int(e['hue'])
            flag = e['offset'] is not None and abs(e['offset']) > a.tolerance
            row['flag'] = 'offset' if flag else ('unmatched' if e['offset'] is None else None)
            rows.append(row)
            if flag:
                flagged.append(row)
        report[tier + '_events'] = rows
    report['flags'] = flagged
    unmatched = [r for r in report['color_events'] + report['change_events']
                 if r['flag'] == 'unmatched']
    report['unmatched_reference_events'] = len(unmatched)
    report['verdict'] = ('FAIL: %d event(s) offset > %d frames'
                         % (len(flagged), a.tolerance)) if flagged else 'PASS'
    if a.out:
        open(a.out, 'w').write(json.dumps(report, indent=1) + '\n')
    print(report['verdict'])
    for f in flagged:
        print(' FLAG %s/%s ref=%s cand=%s offset=%s bbox=%s area=%s' % (
            f['tier'], f['kind'], f['ref_frame'], f['cand_frame'],
            f['offset'], f['bbox'], f['area']))
    big = sorted(unmatched, key=lambda r: -r['area'])[:10]
    print(' warnings: %d reference events unmatched in candidate '
          '(independent artwork/content differences; largest below)' % len(unmatched))
    for f in big:
        print(' WARN %s/%s ref=%s bbox=%s area=%s' % (
            f['tier'], f['kind'], f['ref_frame'], f['bbox'], f['area']))
    sys.exit(1 if flagged else 0)


if __name__ == '__main__':
    main()
