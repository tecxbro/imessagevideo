from pathlib import Path
import argparse
import copy
import json

parser = argparse.ArgumentParser()
parser.add_argument('--input', type=Path, required=True)
parser.add_argument('--output', type=Path, required=True)
parser.add_argument('--elements', type=Path, default=Path(__file__).with_name('capsule-collapse-review-elements.json'))
args = parser.parse_args()
scene = json.loads(args.input.read_text())
spec = json.loads(args.elements.read_text())
counts = dict.fromkeys([*spec['gate_ends'], spec['query_id']], 0)

def absolute(layer):
    if layer.get('src') and not layer['src'].startswith(('/', 'data:', 'http:', 'https:')):
        layer['src'] = str((args.input.parent/layer['src']).resolve())
    for child in layer.get('children', []):
        absolute(child)

layers = []
for layer in scene['layers']:
    absolute(layer)
    identifier = layer['id']
    layers.extend(copy.deepcopy(spec['insert_before'].get(identifier, [])))
    if identifier in spec['gate_ends']:
        layer['end'] = spec['gate_ends'][identifier]
        counts[identifier] += 1
    if identifier == spec['query_id']:
        matches = [child for child in layer['children'] if child['id']==spec['query_child']]
        if len(matches) != 1:
            raise ValueError('Expected unique before18 query')
        matches[0].setdefault('keyframes', {}).update(copy.deepcopy(spec['query_tracks']))
        counts[identifier] += 1
    layers.append(layer)
if any(count != 1 for count in counts.values()):
    raise ValueError('Expected unique capsule/query IDs: '+str(counts))
for font in scene.get('fonts', []):
    if not font['src'].startswith(('/', 'data:', 'http:', 'https:')):
        font['src'] = str((args.input.parent/font['src']).resolve())
scene['layers'] = layers
scene['source']['notes'] += ' Scoped capsule collapse526–550: measured rounded widths, row camera, check clipping, search pose, early orbit540–547 and no stale548–550 capsules. All reserved and outside states preserved.'
args.output.parent.mkdir(exist_ok=True, parents=True)
args.output.write_text(json.dumps(scene, indent=2))
print(json.dumps(dict(counts=counts, ranges=spec['changed_frame_ranges'], output=str(args.output))))
