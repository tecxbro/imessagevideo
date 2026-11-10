"""Independent bounded optical poses for Cash's pulsing plus control."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
D = Path(__file__).resolve().parent
ROOT = D.parent.parent
OUT = D / 'root-cash-control-v19'

def find(layers, identity):
    for layer in layers:
        if layer['id'] == identity:
            return layer
        result = find(layer.get('children', []), identity)
        if result is not None:
            return result

def source_path(frame):
    path = D / 'measurements/composer-v19/native' / f'source-{frame:06}.png'
    return path if path.exists() else D / 'measurements/native-transition' / f'{frame:06}.png'

def prepare():
    scene = json.loads((ROOT / 'outputs/05-linq/final-v18/scene.json').read_text())
    panel = find(scene['layers'], 'v10-cash-panel')
    ykeys = panel['keyframes']['y']
    akeys = panel['keyframes']['opacity']
    yy, xx = np.mgrid[345:455, 610:714]
    mask = (((xx-656)**2 + (yy-400)**2 <= 48**2) | ((xx-664)**2 + (yy-397)**2 <= 48**2))
    layers = []
    provenance = []
    for frame in range(773, 838):
        py = float(np.interp(frame/30, [q['t'] for q in ykeys], [q['value'] for q in ykeys]))
        alpha = float(np.interp(frame/30, [q['t'] for q in akeys], [q['value'] for q in akeys]))
        if 448+py < 0 or 349+py >= 720:
            continue
        if abs(py-round(py)) > 1e-7:
            raise ValueError('Unexpected noninteger panel registration')
        bounds = [610, 345+round(py), 714, 455+round(py)]
        raw = np.asarray(Image.open(source_path(frame)).convert('RGB').crop(bounds)).astype(float)
        # Recover local UI RGB so the existing panel's shared opacity is applied
        # once. Outside the visible source is offscreen for this exact pose.
        rgb = np.uint8(np.clip(np.rint((raw-255*(1-alpha))/alpha), 0, 255))
        rgba = np.dstack([rgb, np.uint8(mask)*255])
        file = OUT / f'control-{frame:06}.png'
        Image.fromarray(rgba).save(file)
        layers.append({'id':f'root-cash-plus-optical-v19-{frame}', 'type':'image', 'src':str(file.resolve()), 'x':610, 'y':345, 'width':104, 'height':110, 'start':frame/30, 'end':(frame+1)/30, 'sourceFrame':frame, 'sourceBounds':bounds, 'semanticText':'Cash plus control pulse/hover material', 'editability':'Independently bounded original104×110 UI optical pose, on the unchanged panel camera. Internal pixels are bitmap; amount geometry and input are unchanged.'})
        provenance.append({'frame':frame,'source':str(source_path(frame)), 'sourceBounds':bounds, 'panelY':py,'parentOpacity':alpha,'uncompositedParentOnce':True,'alphaMask':'Union of source and previous pressed-control support; drawn under the independent amount glyphs.'})
    (OUT / 'elements.json').write_text(json.dumps(layers,indent=2)+'\n')
    (OUT / 'asset-provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
    print(json.dumps({'poses':len(layers),'first':provenance[0]['frame'],'last':provenance[-1]['frame']}),flush=True)

def apply_cash_control(scene):
    panel = find(scene['layers'], 'v10-cash-panel')
    if any(child['id'].startswith('root-cash-plus-optical-v19-') for child in panel['children']):
        raise ValueError('Cash control already patched')
    elements = json.loads((OUT / 'elements.json').read_text())
    index = next(i for i,child in enumerate(panel['children']) if child['id']=='v10-cash-amount')
    panel['children'][index:index] = elements
    return scene

if __name__ == '__main__':
    prepare()
    source = ROOT / 'outputs/05-linq/final-v18/scene.json'
    scene = json.loads(source.read_text())
    def absolutize(layers):
        for layer in layers:
            if layer.get('src') and not layer['src'].startswith('data:'):
                layer['src'] = str((source.parent/layer['src']).resolve())
            absolutize(layer.get('children', []))
    absolutize(scene['layers'])
    for font in scene.get('fonts', []):
        font['src'] = str((source.parent/font['src']).resolve())
    apply_cash_control(scene)
    target = ROOT / 'outputs/05-linq/root-cash-control-v19'
    target.mkdir(exist_ok=True)
    (target/'scene.json').write_text(json.dumps(scene)+'\n')
