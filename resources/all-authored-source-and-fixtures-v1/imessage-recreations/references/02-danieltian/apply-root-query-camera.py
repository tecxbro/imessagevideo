from pathlib import Path
import json,copy,hashlib,argparse
REF=Path(__file__).resolve().parent

def apply_query(scene):
 s=copy.deepcopy(scene);file=REF/'root-query-camera-patch.json';spec=json.loads(file.read_text());group=next(l for l in s['layers'] if l['id']=='pb-result-search');child=next(c for c in group['children'] if c['id']=='middle-query-after-18');child['end']=570/30;group['end']=570/30
 child['keyframes']={key:[dict(t=r['frame']/30,value=r[key],ease='linear') for r in spec['rows'] if r['frame']<570] for key in ['blur','opacity']};child['editability']='One static bounded original search capsule UI material. Native measured blur, opacity and lifecycle; bitmap internal caption, magnifier and border. No per-frame raster sequence.'
 s['root_query_camera_patch']={'scope':[[540,569]],'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'notice':spec['notice']};return s
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();s=json.loads(a.input.read_text())
 def absolute(l):
  if l.get('src') and not l['src'].startswith(('/','data:','http:','https:')):l['src']=str((a.input.parent/l['src']).resolve())
  for c in l.get('children',[]):absolute(c)
 for l in s['layers']:absolute(l)
 for f in s.get('fonts',[]):
  if not f['src'].startswith(('/','data:','http:','https:')):f['src']=str((a.input.parent/f['src']).resolve())
 a.output.write_text(json.dumps(apply_query(s),indent=2));print(a.output)
