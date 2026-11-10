"""Repair semantic word associations; no complete picture/screen material."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json, copy, sys, importlib.util
import numpy as np
R = Path('/workspace/imessage-recreations')
D = R / 'verification/final/06-gallery/v22'
B = R / 'outputs/06-gallery/final-v21/scene.json'
s = json.loads(B.read_text())
sys.path.insert(0, str(R / 'engines'))
import render_pillow as rp
nodes = {}
def walk(ns):
    for n in ns:
        nodes[n['id']] = n
        walk(n.get('children', []))
walk(s['layers'])
before = copy.deepcopy(nodes)
records = []
insertions = []
def out(f):
    return f if f < 1230 else f - 181
def tm(f):
    return out(f) / 30

def put(ident, prop, values):
    n = nodes[ident]
    desired = dict(values)
    lo, hi = min(desired), max(desired)
    old = n.setdefault('keyframes', {}).get(prop, [])
    # Keep original sub-ulp key times at untouched boundaries. Insert an exact
    # integer-frame guard beside them instead of replacing a nearly equal key.
    times = [tm(f) for f in desired]
    keys = [k for k in old if all(abs(k['t'] - t) > 1e-7 for t in times)]
    for f, v in desired.items():
        keys.append({'t':tm(f), 'value':v, 'ease':'linear'})
    for f in [lo - 1, hi + 1]:
        t = tm(f)
        v = rp.state(before[ident], t).get(prop, 0)
        keys = [k for k in keys if k['t'] != t]
        keys.append({'t':t, 'value':v, 'ease':'linear'})
    n['keyframes'][prop] = sorted(keys, key=lambda k:k['t'])

def gray(f):
    return np.asarray(Image.open(D / f'source-late/{f:06d}.png').convert('RGB')).mean(2)
def bbox(m, x0=200, y0=300):
    y, x = np.where(m)
    if len(x) < 20:
        return None
    return [int(x.min() + x0), int(y.min() + y0), int(x.max() + 1 + x0), int(y.max() + 1 + y0)]
def groups(m, gap=20):
    xx = np.where(m.any(0))[0]
    gg = []
    for x in xx:
        if not gg or x - gg[-1][-1] > gap:
            gg.append([x])
        else:
            gg[-1].append(x)
    return [bbox(m[:,g[0]:g[-1]+1], int(g[0]+200)) for g in gg if m[:,g[0]:g[-1]+1].sum() >= 100]
fontboxes = {}
def fontbox(n):
    key = (n['text'], n['fontSize'])
    if key in fontboxes:
        return fontboxes[key]
    f = ImageFont.truetype(str(R / 'shared/fonts/SF-Pro-Display-Medium.otf'), n['fontSize'])
    im = Image.new('L', (1800, 300))
    ImageDraw.Draw(im).text((0,0), n['text'], font=f, fill=255)
    fontboxes[key] = im.getbbox()
    return fontboxes[key]
def poses(ident, rows):
    n = nodes[ident]
    bb = fontbox(n)
    tracks = {k:{} for k in ['x','y','scaleX','scaleY','fill']}
    for f, b, c in rows:
        sx = (b[2] - b[0]) / (bb[2] - bb[0])
        sy = (b[3] - b[1]) / (bb[3] - bb[1])
        vals = [b[0] - bb[0] * sx, b[1] - bb[1] * sy, sx, sy, '#' + f'{c:02x}' * 3]
        for k, v in zip(tracks, vals):
            tracks[k][f] = v
    for k,v in tracks.items():
        put(ident, k, v)

# Same neutral-copy glyphs, independently measured; gap35 merged these words.
provider_rows = {'already':[], 'text':[]}
for f in range(1358, 1374):
    a = np.asarray(Image.open(D / f'source-late/{f:06d}.png').convert('RGB'))
    neutral = (a.max(2) - a.min(2) < 20) & (a.max(2) < 140)
    bb = groups(neutral, 20)
    if len(bb) != 2:
        raise ValueError(('Provider association needs review', f, bb))
    for label,b in zip(['already','text'], bb):
        n = before['rene-v16-provider-' + label]
        fb = fontbox(n)
        st = rp.state(n, tm(f))
        old = [st['x'] + fb[0] * st['scaleX'], st['y'] + fb[1] * st['scaleY'], st['x'] + fb[2] * st['scaleX'], st['y'] + fb[3] * st['scaleY']]
        if max(abs(v-w) for v,w in zip(b, old)) > 1.01:
            provider_rows[label].append((f,b,0))
            records.append({'sourceFrame':f,'element':label,'cause':'gap35 merged independent already/text','beforeBox':old,'box':b})
for label,rows in provider_rows.items():
    if rows:
        poses('rene-v16-provider-' + label, rows)

# Correct the fade-in, without moving the already correctly registered Done ink.
put('rene-final11-group-37', 'opacity', {f:v for f,v in [(205,0),(206,0),(207,0),(208,1/3),(209,2/3)]})
records.append({'sourceFrames':[205,209],'element':'Done actor','cause':'old fade204–209 precedes measured fade207–210','fit':'native font registration dy=0; independent least squares alpha .335663 at208/.668476 at209; retain exact210+ control','values':[0,0,0,1/3,2/3]})

# Source1298 crossfade contains TWO semantic lines. Incoming Lives was mislabeled Does.
for ident in ['rene-final11-text-98','rene-final11-text-99','rene-final11-text-100','rene-final11-text-101','rene-final11-text-102']:
    n = nodes[ident]
    st = rp.state(before[ident], tm(1297))
    for prop in ['x','scaleX','scaleY']:
        put(ident, prop, {1298:st[prop]})
    put(ident, 'y', {1298:st['y'] - 12})
    put(ident, 'fill', {1298:'#1b1b1b'})
    put(ident, 'blur', {1298:5})
    n['end'] = tm(1299)
# The small isolated briefcase also remains a faint independent actor for one frame.
ident = 'rene-final11-image-106'
st = rp.state(before[ident], tm(1297))
for prop in ['x','scaleX','scaleY']:
    put(ident, prop, {1298:st[prop]})
put(ident,'y',{1298:st['y']-12})
put(ident,'opacity',{1298:.07})
put(ident,'blur',{1298:5})
nodes[ident]['end'] = tm(1299)
bb = groups(gray(1298) > 30, 18)
if len(bb) != 3:
    raise ValueError(('Lives association', bb))
for ident,b in zip(['rene-final11-text-103','rene-final11-text-104','rene-final11-text-105'],bb):
    ar = gray(1298)
    roi = ar[b[1]-300:b[3]-300,b[0]-200:b[2]-200]
    col = round(float(np.percentile(roi[roi>30],95)))
    poses(ident,[(1298,b,col)])
    nodes[ident]['start'] = tm(1298)
records.append({'sourceFrame':1298,'element':'outgoing Does… and incoming Lives…','cause':'first-N-label cluster assignment confused two simultaneously visible lines','newBoxes':bb,'nativeWords':True})

# The mascot top lies above every letter, giving an unambiguous independent camera.
mascot = nodes['rene-final11-image-107']
asset = np.asarray(Image.open(B.parent / mascot['src']).convert('RGBA'))
y,x = np.where(asset[:,:,3] > 25)
ib = [int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)]
mascot_tracks = {k:{} for k in ['x','y','scaleX','scaleY']}
brand_words = {}
for f in range(1437, 1445):
    ar = gray(f)
    m = ar < 230
    top = m.copy()
    top[180:,:] = False
    yy,xx = np.where(top)
    left = int(xx.min()) - 26
    face = m.copy()
    face[:,left+171:] = False
    fb = bbox(face)
    sx = (fb[2]-fb[0]) / (ib[2]-ib[0])
    sy = (fb[3]-fb[1]) / (ib[3]-ib[1])
    vals = [fb[0]-ib[0]*sx,fb[1]-ib[1]*sy,sx,sy]
    for k,v in zip(mascot_tracks,vals):
        mascot_tracks[k][f] = v
    wm = (ar < 140)
    wm[:,:left+171] = False
    wb = bbox(wm)
    if wb:
        brand_words[f] = wb
for k,v in mascot_tracks.items():
    put(mascot['id'],k,v)
# Preserve the authentic settled bitmap at1443+, but fit1444's full reveal exactly.
put('rene-final11-group-110','x',{1444:brand_words[1444][0]-3,1445:rp.state(before['rene-final11-group-110'],tm(1446))['x']})
put('rene-final11-rect-108','x',{1444:brand_words[1444][2]-brand_words[1444][0]+3,1445:rp.state(before['rene-final11-rect-108'],tm(1446))['x']})
put('rene-final11-rect-108','width',{1444:max(0,367-(brand_words[1444][2]-brand_words[1444][0]+3)),1445:rp.state(before['rene-final11-rect-108'],tm(1446))['width']})
# A bounded genuine wordmark is traced once to editable native letter contours.
word_img = nodes['rene-final11-image-109']
im = np.asarray(Image.open(B.parent / word_img['src']).convert('RGB'))
alpha = 1-im.mean(2)/255
spec = importlib.util.spec_from_file_location('tracer',R/'references/02-danieltian/trace_glyphs.py')
tracer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tracer)
path, stats = tracer.trace_alpha(alpha)
reveal = {'id':'rene-v22-brand-letter-reveal','type':'group','start':tm(1440),'end':tm(1443),'children':[{'id':'rene-v22-brand-letter-contours','type':'path','d':path,'fill':'#000000'},{'id':'rene-v22-brand-letter-mask','type':'rect','x':0,'y':-3,'width':370,'height':128,'fill':'#ffffff','keyframes':{'x':[],'width':[]}}], 'keyframes':{'x':[],'y':[]}}
for f in range(1440,1443):
    b = brand_words[f]
    w = b[2]-b[0]+3
    for key,val in [('x',b[0]-3),('y',485)]:
        reveal['keyframes'][key].append({'t':tm(f),'value':val,'ease':'linear'})
    for key,val in [('x',w),('width',370-w)]:
        reveal['children'][1]['keyframes'][key].append({'t':tm(f),'value':val,'ease':'linear'})
insertions.append(reveal)
s['layers'].append(reveal)
records.append({'sourceFrames':[1437,1444],'element':'mascot/brand reveal','cause':'merged entering R stretched mascot; wordmark native node began3frames late','wordBoxes':brand_words,'trace':stats,'material':'one static genuine wordmark traced into native letter contours; native per-frame camera/cover'})

# Word identity is tied to its own held-layout aperture, never to first N surviving clusters.
ctas = [('Just',610,820,1510),('like',820,975,1511),('a',975,1040,1513),('friend',1040,1310,1514)]
for label,x0,x1,last in ctas:
    rows = []
    for f in range(1510,last+1):
        ar = gray(f)
        m = ar[:,x0-200:x1-200] < 252
        bb = bbox(m,x0)
        if bb is None:
            continue
        crop = ar[bb[1]-300:bb[3]-300,bb[0]-200:bb[2]-200]
        vals = crop[crop < 252]
        c = int(np.percentile(vals,5))
        rows.append((f,bb,c))
        records.append({'sourceFrame':f,'element':label,'box':bb,'fill':c,'cause':'retained word identity after preceding word fade'})
    poses('source-measured-final-word-'+label, rows)
    nodes['source-measured-final-word-'+label]['end'] = tm(last+1)
# Start is already visible before the old first-N routine assigns its own label.
rows = []
for f in [1515,1516]:
    ar = gray(f)
    m = ar < 252
    bb = bbox(m)
    crop = ar[bb[1]-300:bb[3]-300,bb[0]-200:bb[2]-200]
    rows.append((f,bb,int(np.percentile(crop[crop<252],5))))
poses('source-measured-final-word-Start',rows)
nodes['source-measured-final-word-Start']['start'] = tm(1515)

# The final 'now' survives Start for one additional measured source frame.
ar = gray(1547)
m = ar[:,980-200:1220-200] < 252
bb = bbox(m,980)
roi = ar[bb[1]-300:bb[3]-300,bb[0]-200:bb[2]-200]
poses('source-measured-final-word-now',[(1547,bb,int(np.percentile(roi[roi<252],5)))])
nodes['source-measured-final-word-now']['end'] = tm(1548)
records.append({'sourceFrame':1547,'element':'now','cause':'last suffix survives previous word but shared old end omitted one native frame','box':bb})

updates = {}
for ident,n in nodes.items():
    orig = before[ident]
    dd = {k:copy.deepcopy(v) for k,v in n.items() if k != 'children' and v != orig.get(k)}
    if dd:
        updates[ident] = dd
payload = {'definition':'Source06 final22 fixes measured semantic text association and independent reveal lifecycles, plus Done native opacity. Native glyphs/cameras/clips; no source scene/screen/frame playback.', 'baseSceneSHA256':__import__('hashlib').sha256(B.read_bytes()).hexdigest(),'node_updates':updates,'insertions':insertions,'records':records}
P = R/'references/06-gallery/late-review-v22-elements.json'
P.write_text(json.dumps(payload,indent=2))
for n in s['layers']:
    pass
# Normalize all existing relative assets for this independent authoring location.
def normalize(ns):
    for n in ns:
        if n.get('src') and not n['src'].startswith(('/','data:','http:','https:')):
            n['src'] = str((B.parent/n['src']).resolve())
        normalize(n.get('children',[]))
normalize(s['layers'])
for f in s.get('fonts',[]):
    if not f['src'].startswith(('/','data:','http:','https:')):
        f['src'] = str((B.parent/f['src']).resolve())
s['source']['notes'] += ' ' + payload['definition']
C = R/'references/06-gallery/scene-late-review-v22.json'
C.write_text(json.dumps(s,indent=2))
(D/'measurements.json').write_text(json.dumps(records,indent=2))
print(json.dumps({'nodes':len(updates),'insertions':len(insertions),'scene':str(C),'providerChanged':{k:len(v) for k,v in provider_rows.items()}},indent=2))
