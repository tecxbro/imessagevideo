from pathlib import Path
import json,copy,argparse,hashlib
REF=Path(__file__).resolve().parent

def apply_birth(scene):
 s=copy.deepcopy(scene);file=REF/'root-header-birth-patch.json';p=json.loads(file.read_text());s['layers']=[l for l in s['layers'] if not l['id'].startswith('root-header-birth-pose-')];s['layers']+=copy.deepcopy(p['layers']);s['root_header_birth_patch']={'scope':p['scope'],'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'notice':p['notice']};return s
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();s=json.loads(a.input.read_text())
 def absolute(l):
  if l.get('src') and not l['src'].startswith(('/','data:','http:','https:')):l['src']=str((a.input.parent/l['src']).resolve())
  for c in l.get('children',[]):absolute(c)
 for l in s['layers']:absolute(l)
 for f in s.get('fonts',[]):
  if not f['src'].startswith(('/','data:','http:','https:')):f['src']=str((a.input.parent/f['src']).resolve())
 a.output.write_text(json.dumps(apply_birth(s),indent=2));print(a.output)
