"""Apply two immutable native composer shadow calibrations."""
from pathlib import Path
import json,hashlib,copy
P=Path(__file__).resolve().parent/'intro-shadow-v19-frozen.json'
SHA='7689e8ee864de911574879dc3ff1164600b7c2647934402396d42124c5764989'
def apply_shadow(scene):
    assert hashlib.sha256(P.read_bytes()).hexdigest()==SHA
    data=json.loads(P.read_text())
    intro=next(q for q in scene['layers']if q['id']=='v19-intro-composer')
    body=next(q for q in intro['children']if q['id']=='v19-composer-white-body')
    for node in body['children']:
        node['shadow']=copy.deepcopy(data['patches'][node['id']])
    return scene
