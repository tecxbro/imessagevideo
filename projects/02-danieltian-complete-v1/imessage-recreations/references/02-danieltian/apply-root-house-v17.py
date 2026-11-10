"""A measured independent house actor; original text-row transforms are intact."""
from pathlib import Path
import json
D = Path(__file__).resolve().parent

def find(layer, identity):
    if layer['id'] == identity:
        return layer
    for child in layer.get('children', []):
        result = find(child, identity)
        if result is not None:
            return result

def apply_house(scene):
    root = next(layer for layer in scene['layers'] if layer['id'] == 'reason-v5-measured-camera')
    original = find(root, 'early-reason-emoji-full-3-0')
    if original is None or find(root, 'root-house-world-v17') is not None:
        raise ValueError('Missing or already patched house actor')
    poses = json.loads((D / 'root-house-v17/measured-world-poses.json').read_text())['poses']
    poses = [pose for pose in poses if 289 <= pose['frame'] <= 363]
    # The original291 pose is already stronger than a refitted static image.
    # Retain its exact row transform and material for that one native picture.
    original['start'] = 291/30
    original['end'] = 292/30
    house = {
        'id': 'root-house-world-v17', 'type': 'image', 'src': original['src'],
        'start': 289/30, 'end': 364/30,
        'x': 0, 'y': 0, 'width': 69, 'height': 68,
        'semanticText': 'House emoji — a place to stay',
        'editability': 'Original static69×68 Apple house artwork with independent measured world x/y/width/height/fade. Text-row motion is preserved. The iris transition occludes it from364.',
        'keyframes': {name: [{'t': pose['frame']/30, 'value': (0 if name == 'opacity' and pose['frame'] == 291 else pose[name]), 'ease': 'linear'} for pose in poses] for name in ['x','y','width','height','opacity']}
    }
    root['children'].append(house)
    return scene
