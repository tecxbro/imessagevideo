"""Reusable bounded native UI component extraction; extracted from measured v10 builder."""
from pathlib import Path
import importlib.util,numpy as np
from PIL import Image
from scipy.ndimage import label,find_objects,binary_fill_holes
ROOT=Path(__file__).resolve().parent;A=ROOT/'assets';provenance=[]
spec=importlib.util.spec_from_file_location('trace',ROOT.parent/'02-danieltian/trace_glyphs.py');trace=importlib.util.module_from_spec(spec);spec.loader.exec_module(trace)
def asset(name, ar, box=None, frame=None, notes='bounded static app UI artwork; internal copy is raster'):
    path = A / (name + '.png')
    Image.fromarray(ar).save(path)
    provenance.append({'path': 'assets/' + path.name, 'source_frame': frame, 'box': box, 'kind': notes})
    return str(path)

def image(name, src, x, y, w, h):
    return {'type': 'image', 'id': 'v10-' + name, 'src': src, 'x': x, 'y': y, 'width': w, 'height': h}

def rect(name, x, y, w, h, fill, r=0):
    return {'type': 'rect', 'id': 'v10-' + name, 'x': x, 'y': y, 'width': w, 'height': h, 'fill': fill, 'radius': r}

def group(name, ch, **kw):
    return dict(type='group', id=name, children=ch, **kw)

def native_bubble(name, ar, semantic):
    """Isolate shape and ink at the original component's local coordinates."""
    ar = ar.astype(float)
    h, w = ar.shape[:2]
    blue = np.median(ar[:, :, 2] - ar[:, :, 0]) > 30
    if blue:
        mask = (ar[:, :, 2] - ar[:, :, 0] > 70) & (ar[:, :, 0] < 150)
    else:
        mask = (ar.max(2) - ar.min(2) < 4) & (ar.mean(2) > 210) & (ar.mean(2) < 242)
    vals = np.round(ar[mask]).astype(np.uint8)
    colors, cnt = np.unique(vals, axis=0, return_counts=True)
    bg = colors[cnt.argmax()].astype(float)
    outer = np.clip((255 - ar[:, :, 0]) / (255 - bg[0]), 0, 1)
    core = binary_fill_holes(outer > 0.7)
    outer[core] = 1
    colored = (ar.max(2) - ar.min(2) > 20) & core if not blue else np.zeros((h, w), bool)
    emojis = []
    labels, n = label(colored)
    slices = find_objects(labels)
    for sl in slices:
        if sl is None:
            continue
        yy, xx = sl
        if (labels[sl] > 0).sum() < 12:
            continue
        emojis.append([max(0, xx.start - 7), max(0, yy.start - 7), min(w, xx.stop + 7), min(h, yy.stop + 7)])
    if name == 'gotit':
        emojis.append([367, 16, 420, 72])
    changed = True
    while changed:
        changed = False
        for i, b in enumerate(emojis):
            for j in range(i):
                a = emojis[j]
                if b[0] <= a[2] + 4 and b[2] >= a[0] - 4 and (b[1] <= a[3] + 4) and (b[3] >= a[1] - 4):
                    emojis[j] = [min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3])]
                    emojis.pop(i)
                    changed = True
                    break
            if changed:
                break
    if blue:
        ink = np.clip((ar[:, :, 0] - bg[0]) / (255 - bg[0]), 0, 1) * core
    else:
        ink = np.clip((bg[0] - ar.mean(2)) / max(bg[0], 1), 0, 1) * core
    for b in emojis:
        ink[b[1]:b[3], b[0]:b[2]] = 0
    od, stats = trace.trace_alpha(outer)
    gd, gstats = trace.trace_alpha(ink)
    color = '#' + ''.join((f'{int(v):02x}' for v in bg))
    parts = [{'type': 'path', 'id': 'v10-' + name + '-body', 'd': od, 'fill': color}, {'type': 'path', 'id': 'v10-' + name + '-letters', 'd': gd, 'fill': '#ffffff' if blue else '#000000', 'semanticText': semantic}]
    for i, b in enumerate(emojis):
        src = asset(name + '-genuine-emoji-' + str(i), np.uint8(ar[b[1]:b[3], b[0]:b[2]]), notes='individual genuine colored emoji, static bounded crop')
        parts.append(image(name + '-emoji-' + str(i), src, b[0], b[1], b[2] - b[0], b[3] - b[1]))
    provenance.append({'component': name, 'kind': 'editable native body and glyph outlines', 'semanticText': semantic, 'bodyTrace': stats, 'inkTrace': gstats, 'backgroundRGB': bg.tolist()})
    return parts
