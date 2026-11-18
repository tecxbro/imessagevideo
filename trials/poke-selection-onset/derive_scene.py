"""Materialize the trial scene without modifying the accepted project."""
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ORIGINAL=HERE.parents[1]/'projects/04-poke-complete-v1/imessage-recreations/scenes/04-poke/scene.json'
EXPECTED='bf46102ecdc578cdadac244ba85dec7e5ab19fe07b80277a2fdcdb4c2b191df1'
if hashlib.sha256(ORIGINAL.read_bytes()).hexdigest()!=EXPECTED:
    raise ValueError('Original scene hash differs')
scene=json.loads(ORIGINAL.read_text())
patches={p['layer_id']:p for p in json.loads((HERE/'selection.patch.json').read_text())}
changed=[]


def walk(layers):
    for layer in layers:
        if layer['id'] in patches:
            patch=patches[layer['id']]
            if layer[patch['property']]!=patch['original']:
                raise ValueError('Original property differs')
            layer[patch['property']]=633*1001/30000
            changed.append(layer['id'])
        if 'src' in layer:
            layer['src']=str(ORIGINAL.parent/layer['src'])
        walk(layer.get('children',[]))


walk(scene['layers'])
if sorted(changed)!=sorted(patches):
    raise ValueError('Missing patch target')
for font in scene.get('fonts',[]):
    font['src']=str(ORIGINAL.parent/font['src'])
(HERE/'derived-scene.json').write_text(json.dumps(scene,indent=2)+'\n')
print(f'Derived scene: {changed}; start={633*1001/30000}')
