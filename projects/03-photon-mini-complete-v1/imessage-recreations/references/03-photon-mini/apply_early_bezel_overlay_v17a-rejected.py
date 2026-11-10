"""Keep genuine physical bezel above all UI/paper, respecting special close-up gates."""
from pathlib import Path
import copy,json
P=Path(__file__).resolve().parent

def apply_bezel(scene):
    scene=copy.deepcopy(scene)
    root=next(layer for layer in scene['layers'] if layer['id']=='p03-86')
    if any(layer['id']=='early-top-bezel-v17' for layer in root['children']):
        raise ValueError('Early bezel helper was already applied')
    hardware=copy.deepcopy(next(layer for layer in root['children'] if layer['id']=='p03-10'))
    hardware.update(id='early-top-bezel-v17',start=211/30,end=414/30,semanticText='Physical bezel above receding page and foreground Mail paper',provenance=dict(kind='Existing alpha-isolated genuine hardware, same existing measured physical camera',notice='UI and foreground paper cannot paint over physical bezel. Existing opacity gates suppress this generic texture during the separately measured310–334close-up; no sourceUI pixels have nonzero alpha.'))
    root['children'].append(hardware)
    scene['early_bezel_v17']=dict(scope=[211,413],notice='Physical occlusion ownership only: original genuine bezel repeats above paper/UI, with original camera and original special-closeup opacity gates. No new image asset or full-frame layer.')
    return scene

if __name__=='__main__':
    for name,out in [('final-v15.scene.json','early-bezel-only-v17-prototype.scene.json'),('early-entry-v17-composite-prototype.scene.json','early-entry-bezel-v17-prototype.scene.json')]:
        scene=json.loads((P/name).read_text())
        (P/out).write_text(json.dumps(apply_bezel(scene),indent=2))
    print('built isolated and joint bezel occlusion prototypes')
