from pathlib import Path
import copy,json
P=Path(__file__).parent

def apply_own(scene):
 s=copy.deepcopy(scene);data=json.loads((P/'mini-own-v14-components.json').read_text());r=data['replace_roots'];s['layers']=[copy.deepcopy(r.get(x['id'],x)) for x in s['layers']];ids={x['id'] for x in data['new_roots']};s['layers']=[x for x in s['layers'] if x['id'] not in ids];ix=next(i for i,x in enumerate(s['layers']) if x['id']=='measured-collage-v13');s['layers'][ix+1:ix+1]=copy.deepcopy(data['new_roots']);s['mini_own_v14']={'scope':data['declared_delta'],'notice':data['notice']};return s
