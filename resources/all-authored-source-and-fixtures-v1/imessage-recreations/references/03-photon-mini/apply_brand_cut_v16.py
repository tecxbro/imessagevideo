"""Use the measured hard CTA→Photon cut at native1185, not an invented fade."""
from pathlib import Path
import copy,json
P=Path(__file__).resolve().parent

def apply_brand_cut(scene):
    scene=copy.deepcopy(scene)
    cta=next(layer for layer in scene['layers'] if layer['id']=='p03-699')
    brand=next(layer for layer in scene['layers'] if layer['id']=='p03-705')
    cta['end']=1185/30
    brand['start']=1185/30
    brand['keyframes']['opacity']=[dict(t=1185/30,value=1,ease='hold')]
    brand['keyframes']['y']=[dict(t=1185/30,value=479,ease='hold')]
    scene['brand_cut_v16']=dict(scope=[1185,1198],source_last_cta_frame=1184,source_first_opaque_brand_frame=1185,notice='Source native hard cut at39.5s; prior implementation delayed39.6s then invented a350ms fade. Reuses unchanged native semantic Photon logo paths from the verified40s hold; no new artwork or whole-frame layer.')
    return scene

if __name__=='__main__':
    scene=json.loads((P/'final-v15.scene.json').read_text())
    (P/'brand-cut-v16-prototype.scene.json').write_text(json.dumps(apply_brand_cut(scene),indent=2))
