from pathlib import Path
import json,copy,hashlib,argparse
REF=Path(__file__).resolve().parent

def apply_query(scene):
 scene=copy.deepcopy(scene);file=REF/'root-query-fade-patch.json';spec=json.loads(file.read_text());scene['layers']=[l for l in scene['layers'] if not l['id'].startswith('root-query-fade-')]
 group=next(l for l in scene['layers'] if l['id']=='pb-result-search');child=next(c for c in group['children'] if c['id']=='middle-query-after-18');child['end']=18.;index=scene['layers'].index(group)+1;scene['layers'][index:index]=copy.deepcopy(spec['layers']);scene['root_query_fade_patch']={'scope':spec['scope'],'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'notice':spec['notice']};return scene
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();s=json.loads(a.input.read_text())
 def absolute(l):
  if l.get('src') and not l['src'].startswith(('/','data:','http:','https:')):l['src']=str((a.input.parent/l['src']).resolve())
  for c in l.get('children',[]):absolute(c)
 for l in s['layers']:absolute(l)
 for f in s.get('fonts',[]):
  if not f['src'].startswith(('/','data:','http:','https:')):f['src']=str((a.input.parent/f['src']).resolve())
 a.output.write_text(json.dumps(apply_query(s),indent=2));print(a.output)
