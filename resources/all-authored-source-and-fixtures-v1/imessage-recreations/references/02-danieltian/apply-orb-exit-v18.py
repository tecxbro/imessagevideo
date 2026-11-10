"""Restore two independently measured Airbnb provider orbs1021–1022 only."""
from pathlib import Path
import json,copy,argparse
DEFAULT=Path(__file__).resolve().parent/'orb-exit-v18/patch-spec.json'
def apply_orbs(scene,spec_path=DEFAULT):
    spec=json.loads(Path(spec_path).read_text())
    parent=next(n for n in scene['layers']if n['id']=='group-1118')
    for identity,replacement in spec['replacements'].items():
        i=next(i for i,n in enumerate(parent['children'])if n['id']==identity)
        new=copy.deepcopy(parent['children'][i])
        for key in['x','y','scaleX','scaleY']:new['keyframes'][key]=copy.deepcopy(replacement['keyframes'][key])
        parent['children'][i]=new
    return scene
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--input',required=True);p.add_argument('--output',required=True);a=p.parse_args();scene=json.loads(Path(a.input).read_text());apply_orbs(scene);Path(a.output).write_text(json.dumps(scene,separators=(',',':')))
