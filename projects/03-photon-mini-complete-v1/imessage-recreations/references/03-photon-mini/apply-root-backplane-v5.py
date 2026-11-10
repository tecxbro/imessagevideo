from pathlib import Path
import argparse,json,copy,hashlib
REF=Path(__file__).resolve().parent

def apply_backplane(scene):
 scene=copy.deepcopy(scene);specfile=REF/'root-backplane-patch-v5.json';spec=json.loads(specfile.read_text())
 def walk(ls):
  for l in ls:
   if l['id'] in ('measured-lunch-ui-v13','measured-lunch-display-dim-v13','menu13-p03-151'):l['start']=735/30
   walk(l.get('children',[]))
 walk(scene['layers']);scene['layers']=[l for l in scene['layers'] if not l['id'].startswith(('root-backplane-material-','root-backplane-ui-ink-','root-backplane-stencil-','root-backplane-black-display'))];index=next(i for i,l in enumerate(scene['layers']) if l['id']=='measured-menu-surface-v13');scene['layers'][index:index]=copy.deepcopy(spec['layers']);index=next(i for i,l in enumerate(scene['layers']) if l['id']=='measured-lunch-bezel-overlay-v13');scene['layers'][index:index]=copy.deepcopy(spec['stencilLayers']);scene['root_backplane_patch']={'scope':spec['scope'],'sha256':hashlib.sha256(specfile.read_bytes()).hexdigest(),'notice':spec['notice']};return scene
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();source=a.input.resolve();scene=json.loads(source.read_text())
 def absolute(l):
  if l.get('src') and not l['src'].startswith(('data:','http:','https:')):l['src']=str((source.parent/l['src']).resolve())
  for c in l.get('children',[]):absolute(c)
 for l in scene['layers']:absolute(l)
 for f in scene.get('fonts',[]):
  if not f['src'].startswith(('data:','http:','https:')):f['src']=str((source.parent/f['src']).resolve())
 scene=apply_backplane(scene);a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(scene,indent=2));print(a.output)
