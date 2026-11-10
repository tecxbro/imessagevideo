from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np
import json
import copy

root = Path('/workspace/imessage-recreations')
ref = root/'references/02-danieltian'
review = root/'verification/fidelity-review/02-capsule-collapse'
assets = ref/'assets/capsule-collapse-review'
assets.mkdir(parents=True, exist_ok=True)
base = root/'outputs/02-danieltian/final-v12'
scene = json.load(open(base/'scene.json'))
measurements = json.load(open(review/'measurements-refined.json'))
poses = {row['frame']: row['providers'] for row in measurements['frames']}


def find(layer, identifier):
    if layer['id'] == identifier:
        return layer
    for child in layer.get('children', []):
        match = find(child, identifier)
        if match:
            return match


def rename_absolute(layer, prefix):
    layer['id'] = prefix + layer['id']
    if layer.get('src') and not layer['src'].startswith(('/', 'data:', 'http:')):
        layer['src'] = str((base/layer['src']).resolve())
    for child in layer.get('children', []):
        rename_absolute(child, prefix)


def picture(identifier, source, x, y, width, height):
    return dict(id=identifier, type='image', src=str(source), x=x, y=y, width=width, height=height)


parts = {}
provenance = []
for provider in ['lyft', 'airbnb', 'resy']:
    group = next(layer for layer in scene['layers'] if layer['id'] == 'pb-capsule-'+provider)
    body_layer = find(group, 'pb-'+provider+'-body')
    body_path = base/body_layer['src']
    body = np.array(Image.open(body_path).convert('RGB'))
    # Isolate logo material and neutral name glyphs from the accepted static UI.
    logo = Image.fromarray(body[12:108, 12:108]).convert('RGBA')
    mask = Image.new('L', (384, 384), 0)
    ImageDraw.Draw(mask).ellipse((17, 17, 367, 367), fill=255)
    logo.putalpha(mask.resize((96, 96), Image.Resampling.LANCZOS))
    logo_path = assets/(provider+'-logo-material.png')
    logo.save(logo_path)
    pixels = body[12:108, 120:430].astype(float)
    alpha = np.clip((253-pixels.mean(axis=2))/253, 0, 1)
    alpha[alpha < .015] = 0
    name = np.zeros((96, 310, 4), dtype='uint8')
    name[:,:,3] = np.uint8(alpha*255+.5)
    name_path = assets/(provider+'-name-glyph-material.png')
    Image.fromarray(name).save(name_path)
    check = find(group, 'pb-'+provider+'-check')
    parts[provider] = dict(logo=str(logo_path), name=str(name_path), check=str((base/check['src']).resolve()))
    provenance.append(dict(provider=provider, source=str(body_path), sourceFrame=525, logo_crop=[12,12,108,108], name_crop=[120,12,430,108], notice='Static accepted provider UI material only; new border/clip/camera are native. Name is a bitmap alpha glyph mask, not live text.'))

# Check circles keep growing after the first check state; do not freeze525's
# small material size. Once clipping begins, retain the last full diameter.
check_sizes = {}
max_sizes = {provider: [0, 0] for provider in ['lyft', 'airbnb', 'resy']}
for frame in range(525, 548):
    source = np.array(Image.open(review/'source'/f'{frame-521:04d}.png').convert('RGB'))
    check_sizes[frame] = {}
    for provider, y0, y1 in [('lyft',410,570),('airbnb',570,720),('resy',720,900)]:
        crop = source[y0:y1,1120:1280]
        mask = (crop[:,:,0]<120)&(crop[:,:,1]>160)&(crop[:,:,2]<150)
        yy, xx = np.where(mask)
        if len(xx):
            max_sizes[provider][0] = max(max_sizes[provider][0], int(np.ptp(xx)+1))
            max_sizes[provider][1] = max(max_sizes[provider][1], int(np.ptp(yy)+1))
        check_sizes[frame][provider] = max_sizes[provider].copy()

frames = []
for frame in range(526, 548):
    children = []
    for provider in ['lyft', 'airbnb', 'resy']:
        pose = poses[frame][provider]
        if pose['bodyY'] is None:
            continue
        width = max(117, min(604, pose['curveWidth']))
        x, y = pose['bodyX'], pose['bodyY']
        prefix = f'capsule-review-{frame}-{provider}-'
        contents = [
            dict(id=prefix+'border', type='rect', x=2.25, y=2.25, width=width-4.5, height=112.5, radius=56.25, fill='#fdfdfd', stroke='#e6e6e6', strokeWidth=3.5),
            picture(prefix+'name', parts[provider]['name'], 120, 12, 310, 96),
            picture(prefix+'check', parts[provider]['check'], 540.5-37*check_sizes[frame][provider][0]/67, 58.5-37.5*check_sizes[frame][provider][1]/68, 78*check_sizes[frame][provider][0]/67, 79*check_sizes[frame][provider][1]/68)
        ]
        if frame < 540:
            bounds = measurements['canonical_logo_bounds'][provider]
            bx, by, bw, bh = pose['logo_bbox']
            scale_x = (bw-1)/(bounds['maxX']-bounds['minX'])
            scale_y = (bh-1)/(bounds['maxY']-bounds['minY'])
            logo_x = bx-(bounds['minX']-12)*scale_x
            logo_y = by-(bounds['minY']-12)*scale_y
            contents.append(picture(prefix+'logo', parts[provider]['logo'], logo_x-x, logo_y-y, 96*scale_x, 96*scale_y))
        children.append(dict(id=prefix+'capsule', type='group', x=x, y=y, clip=dict(width=width,height=117,radius=58.5), children=contents))
    if children:
        frames.append(dict(id=f'capsule-review-frame-{frame}', type='group', start=frame/30, end=(frame+1)/30, children=children))

# These measured logo tracks already exist but their original parent suppresses
# 540–547. Continue the same actors early, then hand back to original548+.
fly = next(layer for layer in scene['layers'] if layer['id']=='group-1068')
logos = copy.deepcopy([layer for layer in fly['children'] if layer['id'] in ['middle-fly-lyft','middle-fly-airbnb','middle-fly-resy']])
for logo in logos:
    rename_absolute(logo, 'capsule-review-early-')
frames.append(dict(id='capsule-review-early-orbit-540-547', type='group', start=540/30, end=548/30, children=logos))
query_tracks = {
    'x': [dict(t=row['frame']/30, value=row['x'], ease='linear') for row in measurements['searches']],
    'y': [dict(t=row['frame']/30, value=row['y'], ease='linear') for row in measurements['searches']]
}
spec = dict(
    changed_frame_ranges=[[526,550]],
    gate_ends={f'pb-capsule-{name}':526/30 for name in ['lyft','airbnb','resy']},
    insert_before={'pb-capsule-lyft': frames},
    query_id='pb-result-search', query_child='middle-query-before-18', query_tracks=query_tracks,
    provenance=dict(static_parts=provenance, check_growth=check_sizes, native_camera='Exact per-frame measured source capsule border/width and logo pose526–539; native rounded clips and independent static name/check material.', early_orbit='Clone accepted measured native inner logo tracks540–547 only, original548+ remains untouched; stale capsule ghosts548–550 removed.', search='Native original query material with measured position526–539; NCC .9875–.9998. Settled525/outside states preserved.', limitations='Bitmap material AA/compression and native vector border differences remain; no complete source-frame/video asset.')
)
(ref/'capsule-collapse-review-elements.json').write_text(json.dumps(spec, indent=2))
print('Native capsule groups', len(frames), 'scope', spec['changed_frame_ranges'])
