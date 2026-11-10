"""Measured command reaction continuation816–821. Preserves all other actor objects."""
from pathlib import Path
import json,copy,argparse
DEFAULT=Path(__file__).resolve().parent/'v17-refinement/reaction-clip-final.json'
def apply_reaction(scene,spec_path=DEFAULT):
    spec=json.loads(Path(spec_path).read_text())
    def walk(nodes):
        for index,node in enumerate(nodes):
            if node.get('id')==spec['id']:
                replacement=copy.deepcopy(node)
                replacement['keyframes']=copy.deepcopy(spec['replacement']['keyframes'])
                replacement['end']=spec['replacement']['end']
                nodes[index]=replacement
                return True
            if walk(node.get('children',[])):return True
        return False
    if not walk(scene['layers']):raise ValueError('Missing reaction actor')
    return scene
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--input',required=True);parser.add_argument('--output',required=True);parser.add_argument('--spec',default=str(DEFAULT));args=parser.parse_args()
    scene=json.loads(Path(args.input).read_text());apply_reaction(scene,args.spec);Path(args.output).write_text(json.dumps(scene,separators=(',',':')))
