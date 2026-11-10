"""Small helpers for deterministic, bounded revisions of the frozen native scene."""
import copy


def sample(keys, time):
    keys = sorted(keys, key=lambda key: key['t'])
    if time <= keys[0]['t']:
        return keys[0]['value']
    for left, right in zip(keys, keys[1:]):
        if time > right['t']:
            continue
        fraction = (time - left['t']) / (right['t'] - left['t'])
        ease = right.get('ease', 'linear')
        if ease == 'hold':
            fraction = 1 if fraction >= 1 else 0
        elif ease == 'easeInOut':
            fraction = 4 * fraction**3 if fraction < .5 else 1 - (-2 * fraction + 2)**3 / 2
        elif ease == 'easeIn':
            fraction = fraction**3
        elif ease == 'easeOut':
            fraction = 1 - (1 - fraction)**3
        a, b = left['value'], right['value']
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            return a + (b - a) * fraction
        return b if fraction >= 1 else a
    return keys[-1]['value']


def at(layer, prop, time):
    keys = layer.get('keyframes', {}).get(prop)
    if keys:
        return sample(keys, time)
    return layer.get(prop, 1 if prop in ['scaleX', 'scaleY', 'opacity'] else 0)


def amend(layer, prop, values, first, last):
    prior = layer.get('keyframes', {}).get(prop, [])
    kept = [key for key in prior if key['t'] < first or key['t'] > last]
    layer.setdefault('keyframes', {})[prop] = sorted(kept + values, key=lambda key: key['t'])


def track(layer, prop, rows, field=None):
    field = field or prop
    values = [{'t': row['time'], 'value': row[field], 'ease': 'linear'} for row in rows]
    amend(layer, prop, values, rows[0]['time'], rows[-1]['time'])


def flat(layers):
    result = []
    for layer in layers:
        result.append(layer)
        result.extend(flat(layer.get('children', [])))
    return result


def resolved(layer, time, prefix=''):
    output = copy.deepcopy(layer)
    for prop in output.pop('keyframes', {}):
        output[prop] = at(layer, prop, time)
    output.pop('start', None)
    output.pop('end', None)
    if prefix:
        output['id'] = prefix + output['id']
    output['children'] = [resolved(child, time, prefix) for child in layer.get('children', [])
                          if child.get('start', 0) <= time < child.get('end', float('inf'))]
    if not layer.get('children'):
        output.pop('children', None)
    return output
