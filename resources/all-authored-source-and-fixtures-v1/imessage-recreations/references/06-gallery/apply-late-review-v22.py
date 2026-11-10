"""Apply independently measured source06 semantic word/reveal corrections by ID."""
from pathlib import Path
import argparse, copy, json
p = argparse.ArgumentParser()
p.add_argument('--input', type=Path, required=True)
p.add_argument('--output', type=Path, required=True)
p.add_argument('--elements', type=Path, default=Path(__file__).with_name('late-review-v22-elements.json'))
a = p.parse_args()
s = json.loads(a.input.read_text())
e = json.loads(a.elements.read_text())
counts = dict.fromkeys(e['node_updates'], 0)
all_ids = set()
def walk(ns):
    for n in ns:
        if n['id'] in all_ids:
            raise ValueError('Duplicate original ID: ' + n['id'])
        all_ids.add(n['id'])
        if n.get('src') and not n['src'].startswith(('/', 'data:', 'http:', 'https:')):
            n['src'] = str((a.input.parent / n['src']).resolve())
        if n['id'] in e['node_updates']:
            counts[n['id']] += 1
            n.update(copy.deepcopy(e['node_updates'][n['id']]))
        walk(n.get('children', []))
walk(s['layers'])
if any(v != 1 for v in counts.values()):
    raise ValueError(('Expected unique scoped IDs', counts))
for n in e['insertions']:
    if n['id'] in all_ids:
        raise ValueError('New native reveal already exists: ' + n['id'])
    s['layers'].append(copy.deepcopy(n))
for f in s.get('fonts', []):
    if not f['src'].startswith(('/', 'data:', 'http:', 'https:')):
        f['src'] = str((a.input.parent / f['src']).resolve())
s['source']['notes'] += ' ' + e['definition']
a.output.parent.mkdir(parents=True, exist_ok=True)
a.output.write_text(json.dumps(s, indent=2))
print(json.dumps({'ids':counts, 'insertions':len(e['insertions']), 'output':str(a.output)}))
