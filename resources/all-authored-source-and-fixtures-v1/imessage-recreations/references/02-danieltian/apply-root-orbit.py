from pathlib import Path
import json,copy,argparse,hashlib
REF=Path(__file__).resolve().parent

def apply_orbit(scene):
 s=copy.deepcopy(scene);file=REF/'root-orbit-patch.json';p=json.loads(file.read_text());s['layers']=[l for l in s['layers'] if not l['id'].startswith('root-orbit-pose-')];g=next(l for l in s['layers'] if l['id']=='group-1068');g['end']=548/30;index=s['layers'].index(g)+1;s['layers'][index:index]=copy.deepcopy(p['layers']);s['root_orbit_patch']={'scope':p['scope'],'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'notice':p['notice']};return s
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();s=json.loads(a.input.read_text())
 def absolute(l):
  if l.get('src') and not l['src'].startswith(('/','data:','http:','https:')):l['src']=str((a.input.parent/l['src']).resolve())
  for c in l.get('children',[]):absolute(c)
 for l in s['layers']:absolute(l)
 for f in s.get('fonts',[]):
  if not f['src'].startswith(('/','data:','http:','https:')):f['src']=str((a.input.parent/f['src']).resolve())
 a.output.write_text(json.dumps(apply_orbit(s),indent=2));print(a.output)
