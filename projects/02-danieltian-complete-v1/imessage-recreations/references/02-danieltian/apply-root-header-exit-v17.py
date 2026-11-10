"""Restore the two measured header exit frames without altering its entrance."""
from pathlib import Path
import copy
import json
D = Path(__file__).resolve().parent
PATCH = D / 'root-header-exit-v17/camera-patch.json'

def find(layers):
    for layer in layers:
        if layer['id'] == 'group-1077':
            return layer
        result = find(layer.get('children', []))
        if result is not None:
            return result

def apply_header_exit(scene):
    group = find(scene['layers'])
    if group is None:
        raise ValueError('Expected independent header group-1077')
    patch = json.loads(PATCH.read_text())
    for name, values in patch['tracks'].items():
        keys = group['keyframes'][name]
        if any(key['t'] > 1027 / 30 for key in keys):
            raise ValueError('Unexpected later header keys or duplicate patch: ' + name)
        group['keyframes'][name] = keys + copy.deepcopy(values)
    return scene
