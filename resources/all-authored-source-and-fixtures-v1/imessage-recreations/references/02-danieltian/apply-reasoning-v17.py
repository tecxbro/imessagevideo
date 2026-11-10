"""Measured semantic neutral glyphs and five independent static emoji actors272–374.
Stronger source373 is retained exactly. Apply root house helper afterward.
"""
from pathlib import Path
import json,copy,argparse
DEFAULT=Path(__file__).resolve().parent/'v17-refinement/reasoning-final.json'
def apply_reasoning(scene,spec_path=DEFAULT):
    spec=json.loads(Path(spec_path).read_text())
    i=next(i for i,n in enumerate(scene['layers'])if n['id']==spec['id'])
    old=scene['layers'][i]
    if any(n['id'].startswith('reason-neutral-native-')for n in old['children']):raise ValueError('Reasoning already patched')
    scene['layers'][i]=copy.deepcopy(spec['replacement'])
    return scene
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--input',required=True);p.add_argument('--output',required=True);p.add_argument('--spec',default=str(DEFAULT));a=p.parse_args()
    scene=json.loads(Path(a.input).read_text());apply_reasoning(scene,a.spec);Path(a.output).write_text(json.dumps(scene,separators=(',',':')))
