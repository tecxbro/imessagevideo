"""Apply measured semantic fixes for isolated Mini peaks; all other states retained."""
from pathlib import Path
import argparse,copy,json

parser=argparse.ArgumentParser()
parser.add_argument('--input',type=Path,required=True)
parser.add_argument('--output',type=Path,required=True)
parser.add_argument('--elements',type=Path,default=Path(__file__).with_name('remaining-peaks-review-elements.json'))
args=parser.parse_args()
scene=json.loads(args.input.read_text())
spec=json.loads(args.elements.read_text())
expected=set(spec.get('node_updates',{}))|set(spec.get('insert_before',{}))|set(spec.get('insert_after',{}))|set(spec.get('append_children',{}))
counts=dict.fromkeys(expected,0)
def walk(layers):
    result=[]
    for layer in layers:
        identifier=layer['id']
        if identifier in expected:counts[identifier]+=1
        if layer.get('src') and not layer['src'].startswith(('/','data:','http:','https:')):
            layer['src']=str((args.input.parent/layer['src']).resolve())
        updates=copy.deepcopy(spec.get('node_updates',{}).get(identifier,{}))
        keyframes=updates.pop('keyframes',None)
        layer.update(updates)
        if keyframes:layer.setdefault('keyframes',{}).update(keyframes)
        if 'children'in layer:layer['children']=walk(layer['children'])
        if identifier in spec.get('append_children',{}):layer.setdefault('children',[]).extend(copy.deepcopy(spec['append_children'][identifier]))
        result.extend(copy.deepcopy(spec.get('insert_before',{}).get(identifier,[])))
        result.append(layer)
        result.extend(copy.deepcopy(spec.get('insert_after',{}).get(identifier,[])))
    return result
scene['layers']=walk(scene['layers'])
if any(count!=1 for count in counts.values()):raise ValueError('Expected unique Mini IDs: '+str(counts))
for font in scene.get('fonts',[]):
    if not font['src'].startswith(('/','data:','http:','https:')):font['src']=str((args.input.parent/font['src']).resolve())
scene['source']['notes']+=' Isolated measured Mini peak review: semantic Mail-plane/visible subject, independent first title/Alice camera, and early montage UI. Only declared native frames change; no whole-source-frame/video playback.'
args.output.parent.mkdir(exist_ok=True,parents=True)
args.output.write_text(json.dumps(scene,indent=2))
print(json.dumps(dict(ids=counts,ranges=spec['changed_ranges'],output=str(args.output))))
