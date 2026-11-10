"""Restore the measured pre-reply typing entrance and true viewport-clipped label."""
from pathlib import Path
import copy,json,argparse
DEFAULT_SPEC=Path(__file__).resolve().parent/'final-midstate-fix/late-state-elements-final.json'
def apply_late_state(scene,spec_path=None):
    spec=json.loads(Path(spec_path or DEFAULT_SPEC).read_text())
    result=copy.deepcopy(scene)
    assert not any(n['id']==spec['layer']['id']for n in result['layers'])
    assert not any(g['id']==spec['gradient']['id']for g in result.get('gradients',[]))
    result.setdefault('gradients',[]).append(copy.deepcopy(spec['gradient']))
    found=False
    def walk(nodes):
        nonlocal found
        output=[]
        for node in nodes:
            if 'children'in node:node['children']=walk(node['children'])
            output.append(node)
            if node['id']==spec['label']['id']:
                keys=node.setdefault('keyframes',{}).get('opacity',[])
                assert not any(key['t']>904/30 for key in keys)
                node['keyframes']['opacity']=copy.deepcopy(keys)+[{'t':904/30,'value':1,'ease':'hold'},{'t':905/30,'value':0,'ease':'hold'},{'t':957/30,'value':0,'ease':'hold'},{'t':958/30,'value':1,'ease':'hold'}]
                output.extend(copy.deepcopy(spec['label']['clones']))
                found=True
        return output
    result['layers']=walk(result['layers'])
    assert found
    result['layers'].append(copy.deepcopy(spec['layer']))
    return result
if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--input',required=True)
    parser.add_argument('--output',required=True)
    parser.add_argument('--spec')
    args=parser.parse_args()
    source=Path(args.input).resolve()
    scene=json.loads(source.read_text())
    def absolute(node):
        if node.get('src')and not node['src'].startswith(('/','data:','http:','https:')):node['src']=str((source.parent/node['src']).resolve())
        for child in node.get('children',[]):absolute(child)
    for node in scene['layers']+scene.get('fonts',[]):absolute(node)
    Path(args.output).write_text(json.dumps(apply_late_state(scene,args.spec),separators=(',',':')))
