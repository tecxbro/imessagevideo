"""Correct only the observed physical chrome settle; preserve all UI cameras."""
from pathlib import Path
import copy,json
P=Path(__file__).resolve().parent

def apply_chrome(scene):
    scene=copy.deepcopy(scene)
    data=json.loads((P/'lunch-chrome-v16-aperture.json').read_text())['frames']
    root=next(layer for layer in scene['layers'] if layer['id']=='p03-204')
    owned={f'p03-{index}' for index in range(91,97)}
    originals=[layer for layer in root['children'] if layer['id'] in owned]
    if len(originals)!=6:
        raise ValueError('Expected six unique original physical material/hardware nodes')
    physical=copy.deepcopy(originals)
    for layer in physical:
        layer['id']='chrome16-'+layer['id']
    keys={key:[] for key in ['x','y','scaleX','scaleY']}
    poses=[]
    # Actual width has settled while the inherited camera still shrinks linearly.
    # A fully visible aperture givesY without the reflection-biased rim fit.
    for row in data:
        frame=row['frame']
        if not 497<=frame<=516:
            continue
        candidates=row['candidates']
        if len(candidates)!=1 or candidates[0]['top_censored']:
            raise ValueError('No unique uncensored physical aperture at'+str(frame))
        island=candidates[0]
        scale=row['hardware_fit']['scale']
        values=dict(x=island['center'][0]-400*scale,y=island['center'][1]-88*scale,scaleX=scale,scaleY=scale)
        for key,value in values.items():
            keys[key].append(dict(t=frame/30,value=float(value),ease='hold'))
        poses.append(dict(frame=frame,camera=values,aperture_bbox=island['bbox'],scale_evidence='Native dark outer-bezel modes; physical island center independently anchorsY',prior=row['prior']))
    for layer in originals:
        if layer.get('keyframes',{}).get('opacity'):
            raise ValueError('Unexpected existing physical opacity track')
        layer.setdefault('keyframes',{})['opacity']=[dict(t=0,value=1,ease='hold'),dict(t=497/30,value=0,ease='hold'),dict(t=517/30,value=1,ease='hold')]
    chrome=dict(id='independent-physical-lunch-chrome-v16',type='group',start=497/30,end=517/30,keyframes=keys,children=physical,semanticText='Physical iPhone hardware and display material',provenance=dict(kind='Observed outer-width and uncensored physical-aperture center; existing static genuine hardware artwork',measurement_file='lunch-chrome-v16-aperture.json',notice='Only physical material/rim/island move. Existing Messages/header/bubble/preview cameras and618+menu/backplane remain unchanged. Later rim photometricY fits were rejected by native comparisons; no correction is forced once the width has settled.'))
    scene['layers'].insert(scene['layers'].index(root),chrome)
    scene['lunch_chrome_v16']=dict(scope=[497,516],poses=poses,rejected_blanket_scope=[495,617],notice='The old coarse linear hardware settle lags actualsource width/aperture. Direct physical measurements replace only20 native poses. Native UI/header/preview remain on their already fitted cameras. Later photometric-only fits regressed and were rejected. No new image asset or whole-frame layer.')
    return scene

if __name__=='__main__':
    scene=json.loads((P/'final-v15.scene.json').read_text())
    (P/'lunch-chrome-v16-prototype.scene.json').write_text(json.dumps(apply_chrome(scene),indent=2))
    print('built directly observed20frame chrome settle')
