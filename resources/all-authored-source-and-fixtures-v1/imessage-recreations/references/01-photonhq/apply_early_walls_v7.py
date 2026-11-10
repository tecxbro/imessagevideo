"""ID-scoped opaque SMS/mail state fix, preserving local component flip phases."""
from pathlib import Path
import json,copy,argparse
P=Path(__file__).parent;B=P/'early-walls-v7-measure'
def apply_early_walls(scene):
 s=copy.deepcopy(scene);changed=[]
 for l in s['layers']:
  if l['id'].startswith(('ocr-wall-','edge-restore-')):
   keys=l.setdefault('keyframes',{}).setdefault('opacity',[{'t':0,'value':1}]);keys[:]=[q for q in keys if abs(q['t']-8.3)>1e-7 and abs(q['t']-9.9)>1e-7];keys.extend([{'t':8.3,'value':0,'ease':'hold'},{'t':9.9,'value':0,'ease':'hold'}]);keys.sort(key=lambda q:q['t']);changed.append(l['id'])
 s['layers'].extend(json.load(open(B/'native-layers.json')));s['source']['notes']+=' V7 native opaque SMS249–281 and mail297–314 component state/pose tracks replace invented OCR-loss fades and vertical collapse. Existing authorized local 3D component poses282–296 and315–335 remain unchanged. Static original per-component UI artwork has declared bitmap internals; no source frame/video is an output layer.';return s,{'changed_frame_ranges':[[249,281],[297,314]],'gated_ids':changed}
def absolute_assets(s,base):
 def walk(ls):
  for l in ls:
   if l.get('src')and not l['src'].startswith(('data:','http:','https:','/')):l['src']=str((base/l['src']).resolve())
   walk(l.get('children',[]))
 walk(s['layers'])
 for f in s.get('fonts',[]):
  if not f['src'].startswith(('data:','http:','https:','/')):f['src']=str((base/f['src']).resolve())
 return s
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--input',type=Path,default=P.parents[1]/'outputs/01-photonhq/final-v6/scene.json');p.add_argument('--output',type=Path,default=P/'early-walls-v7.scene.json');a=p.parse_args();s=absolute_assets(json.load(open(a.input)),a.input.parent);s,scope=apply_early_walls(s);a.output.write_text(json.dumps(s,indent=2)+'\n');(B/'scope.json').write_text(json.dumps(scope,indent=2)+'\n');print(a.output)
