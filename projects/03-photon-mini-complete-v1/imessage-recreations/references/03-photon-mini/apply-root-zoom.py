from pathlib import Path
import argparse,json,copy,hashlib
REF=Path(__file__).resolve().parent

def apply_zoom(scene):
 specfile=REF/'root-zoom-patch.json';spec=json.loads(specfile.read_text());scene=copy.deepcopy(scene)
 def walk(ls):
  for l in ls:
   if l['id'] in ('p03-475','collage13-p03-475'):l['start']=903/30
   if l['id']=='p03-650':l['start']=899/30
   walk(l.get('children',[]))
 walk(scene['layers']);google=json.loads((REF/'root-google-exit-patch.json').read_text());scene['layers']=[l for l in scene['layers'] if not l['id'].startswith(('root-zoom-ui-','root-zoom-native-pose-','root-google-phone-exit'))]+[copy.deepcopy(google['layer'])]+copy.deepcopy(spec['layers']);scene['root_google_exit']=google['poses'];scene['root_zoom_patch']={'scope':spec['scope'],'sha256':hashlib.sha256(specfile.read_bytes()).hexdigest(),'measurements':spec['measurements'],'notice':spec['notice']};return scene
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();source=a.input.resolve();scene=json.loads(source.read_text())
 def absolute(l):
  if l.get('src') and not l['src'].startswith(('data:','http:','https:')):l['src']=str((source.parent/l['src']).resolve())
  for c in l.get('children',[]):absolute(c)
 for l in scene['layers']:absolute(l)
 for f in scene.get('fonts',[]):
  if not f['src'].startswith(('data:','http:','https:')):f['src']=str((source.parent/f['src']).resolve())
 scene=apply_zoom(scene);a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(scene,indent=2));print(a.output)
