"""Keep genuine physical bezel above all UI/paper, respecting special close-up gates."""
from pathlib import Path
import copy,json
from apply_blue_arrival_v14 import sample
P=Path(__file__).resolve().parent

def apply_bezel(scene,start_frame=211,end_frame=413,identifier='early-top-bezel-v17'):
    scene=copy.deepcopy(scene)
    root=next(layer for layer in scene['layers'] if layer['id']=='p03-86')
    if any(layer['id']==identifier for layer in root['children']):
        raise ValueError('Early bezel helper was already applied')
    original=next(layer for layer in root['children'] if layer['id']=='p03-10')
    hardware=copy.deepcopy(original)
    opacity=copy.deepcopy(original.get('keyframes',{}).get('opacity',[dict(t=0,value=original.get('opacity',1))]))
    keys=[key for key in opacity if key['t']<start_frame/30]
    keys.append(dict(t=start_frame/30,value=0,ease='hold'))
    keys.append(dict(t=(end_frame+1)/30,value=sample(opacity,(end_frame+1)/30),ease='hold'))
    keys.extend(key for key in opacity if key['t']>(end_frame+1)/30)
    original.setdefault('keyframes',{})['opacity']=keys
    hardware.update(id=identifier,start=start_frame/30,end=(end_frame+1)/30,semanticText='Physical bezel above receding page and foreground Mail paper',provenance=dict(kind='Existing alpha-isolated genuine hardware, same existing measured physical camera',notice='UI and foreground paper cannot paint over physical bezel. Existing opacity gates suppress this generic texture during the separately measured310–334close-up; no sourceUI pixels have nonzero alpha.'))
    root['children'].append(hardware)
    scene['early_bezel_v17']=dict(scope=[start_frame,end_frame],notice='Physical occlusion ownership only: One original genuine bezel moves above paper/UI; its old lower copy is gated off, with original camera and original special-closeup opacity gates. No new image asset or full-frame layer.')
    return scene

if __name__=='__main__':
    for name,out in [('final-v15.scene.json','early-bezel-only-v17-prototype.scene.json'),('early-entry-v17-composite-prototype.scene.json','early-entry-bezel-v17-prototype.scene.json')]:
        scene=json.loads((P/name).read_text())
        (P/out).write_text(json.dumps(apply_bezel(scene),indent=2))
    print('built isolated and joint bezel occlusion prototypes')
