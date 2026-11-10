"""Apply the independently measured short reply/card corrections to accepted V14."""
from pathlib import Path
import argparse,copy,json
DEFAULT_SPEC=Path(__file__).resolve().parent/'final-midstate-fix/elements-final.json'
def apply_midstate(scene,spec_path=None):
    spec=json.loads(Path(spec_path or DEFAULT_SPEC).read_text())
    result=copy.deepcopy(scene)
    found=set()
    additions=spec['insertAfter']
    edits=spec['originalPropertyEdits']
    def walk(layers):
        output=[]
        for node in layers:
            identity=node['id']
            if identity.startswith('post-v14-'):
                raise ValueError('Midstate helper already applied')
            if identity in edits:
                for property_name,track in edits[identity].items():
                    assert property_name.endswith('Track')
                    node.setdefault('keyframes',{})[property_name[:-5]]=copy.deepcopy(track)
                found.add(identity)
            if 'children'in node:
                node['children']=walk(node['children'])
            output.append(node)
            if identity in additions:
                output.extend(copy.deepcopy(additions[identity]))
                found.add(identity)
        return output
    result['layers']=walk(result['layers'])
    assert found==set(edits)|set(additions),('Missing expected authored identities',found^(set(edits)|set(additions)))
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
        if node.get('src')and not node['src'].startswith(('/','data:','http:','https:')):
            node['src']=str((source.parent/node['src']).resolve())
        for child in node.get('children',[]):
            absolute(child)
    for node in scene['layers']+scene.get('fonts',[]):
        absolute(node)
    target=apply_midstate(scene,args.spec)
    Path(args.output).write_text(json.dumps(target,separators=(',',':')))
