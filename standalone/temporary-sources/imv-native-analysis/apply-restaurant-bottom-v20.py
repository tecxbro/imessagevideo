"""Restore the one static lower restaurant UI component exposed during exit."""
from pathlib import Path
import json,copy,hashlib
P=Path(__file__).resolve().parent/'restaurant-bottom-v20-frozen-elements.json'
SHA='8b0612250438c1a64c0e3bfe1bf4741c3eeaf3fe9e88dca62e458e4b7b164075'
def apply_restaurant_bottom(scene):
    assert hashlib.sha256(P.read_bytes()).hexdigest()==SHA
    node=json.loads(P.read_text())
    group=next(q for q in scene['layers']if q['id']=='rich-group-14')
    assert all(q['id']!=node['id']for q in group['children'])
    index=next(i for i,q in enumerate(group['children'])if q['id']=='v10-restaurant-document')
    group['children'].insert(index+1,copy.deepcopy(node))
    return scene
