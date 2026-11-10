from pathlib import Path
import argparse,json,copy,hashlib
REF=Path(__file__).resolve().parent

def apply_copy(scene):
 scene=copy.deepcopy(scene);specfile=REF/'root-copy-patch.json';spec=json.loads(specfile.read_text());remove={'group-1177','group-1184','group-1191','group-1198','group-1205','text-1206-outlined'};kept=[]
 for l in scene['layers']:
  if l['id']=='group-801':
   for c in l.get('children',[]):
    if c['id']=='rect-800':c['end']=95/30
  if l['id']=='group-857':l['end']=95/30
  if l['id'] in remove or l['id'].startswith(('composer-v5-char-','root-copy-pose-','root-composer-material-','root-composer-send-')):continue
  if l['id'].startswith('text-') and l['id'][5:].isdigit() and 802<=int(l['id'][5:])<=853 and l.get('end',scene['duration'])>95/30:
   l['end']=95/30
   if l.get('start',0)>=l['end']:continue
  if l['id']=='text-1207-outlined':l['start']=1251/30
  kept.append(l)
 material=json.loads((REF/'root-composer-material-patch.json').read_text());scene['layers']=kept+copy.deepcopy(material['layers'])+copy.deepcopy(spec['layers']);scene['root_copy_patch']={'scope':spec['scope'],'sha256':hashlib.sha256(specfile.read_bytes()).hexdigest(),'materialSHA256':hashlib.sha256((REF/'root-composer-material-patch.json').read_bytes()).hexdigest(),'notice':spec['notice']};return scene
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();source=a.input.resolve();scene=json.loads(source.read_text())
 def absolute(l):
  if l.get('src') and not l['src'].startswith(('data:','http:','https:')):l['src']=str((source.parent/l['src']).resolve())
  for c in l.get('children',[]):absolute(c)
 for l in scene['layers']:absolute(l)
 for f in scene.get('fonts',[]):
  if not f['src'].startswith(('data:','http:','https:')):f['src']=str((source.parent/f['src']).resolve())
 scene=apply_copy(scene);a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(scene,indent=2));print(a.output)
