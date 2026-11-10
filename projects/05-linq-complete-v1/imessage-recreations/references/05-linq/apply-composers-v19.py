"""Apply immutable measured intro/Cash input data to an asset-normalized V18 scene."""
from pathlib import Path
import json,copy,hashlib
D=Path(__file__).resolve().parent
P=D/'composer-v19-frozen-elements.json'
SHA='b7d9d68318a6e3f8778722d5fc8479164494fe743274a31509e2759898485c1a'
def apply_composers(scene):
 assert hashlib.sha256(P.read_bytes()).hexdigest()==SHA
 p=json.loads(P.read_text());ids=set(p['removedIntroRootIDs']);old=[q for q in scene['layers']if q['id']in ids];assert len(old)==len(ids);first=min(scene['layers'].index(q)for q in old);scene['layers']=[q for q in scene['layers']if q['id']not in ids];scene['layers'].insert(first,copy.deepcopy(p['intro']));cash=next(q for q in scene['layers']if q['id']=='linq-measured-v6-group-36');i=next(i for i,q in enumerate(cash['children'])if q['id']=='v10-cash-composer');cash['children'][i]=copy.deepcopy(p['cashComposer']);return scene
