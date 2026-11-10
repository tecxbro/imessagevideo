"""Apply measured phonebook frames436–524; preserve accepted525+ holds."""
from pathlib import Path
import argparse,copy,hashlib,json
REF=Path(__file__).resolve().parent
DEFAULT=REF/'phonebook-v14/elements-final.json'

def apply_phonebook(scene,elements=None):
    spec=json.loads(Path(elements or DEFAULT).read_text())
    result=copy.deepcopy(scene)
    capsules={'pb-capsule-lyft','pb-capsule-airbnb','pb-capsule-resy','pb-uber-eats'}
    seen=set()
    for node in result['layers']:
        id=node['id']
        if id.startswith('pb-number-'):
            node['end']=436/30;seen.add('field')
        if id in capsules:
            if id=='pb-uber-eats':
                node['end']=node['start']
            else:
                if abs(node.get('end',0)-526/30)>1e-10:
                    raise ValueError('Unexpected original capsule hold boundary: '+id)
                node['start']=525/30
            seen.add(id)
        if id=='pb-result-search':
            for child in node.get('children',[]):
                if child['id']=='middle-query-before-18':
                    child['start']=525/30;seen.add('query')
    if not {'field','query',*capsules}.issubset(seen):
        raise ValueError('Expected phonebook stable IDs were not all present: '+str(sorted(seen)))
    ids={n['id'] for n in result['layers']}
    if any(n['id'] in ids for n in spec['layers']):
        raise ValueError('Phonebook review already applied or inserted ID conflict')
    result['layers']+=copy.deepcopy(spec['layers'])
    result['phonebook_grid_review']={'specSha256':hashlib.sha256(Path(elements or DEFAULT).read_bytes()).hexdigest(),'scope':spec['scope'],'editability':spec['notes']}
    return result

def absolute_assets(node,base):
    if node.get('src') and not node['src'].startswith(('/','data:','http:','https:')):
        node['src']=str((base/node['src']).resolve())
    for c in node.get('children',[]):absolute_assets(c,base)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--elements',type=Path,default=DEFAULT);a=p.parse_args();scene=json.loads(a.input.read_text())
    for n in scene['layers']+scene.get('fonts',[]):absolute_assets(n,a.input.resolve().parent)
    result=apply_phonebook(scene,a.elements);a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,separators=(',',':')));print(a.output)
