from pathlib import Path
import sys,json,copy
import numpy as np
from PIL import Image
p=Path(__file__).parent;sys.path.insert(0,str(p.parent.parent/'engines'));sys.path.insert(0,str(p))
import render_pillow as rp
from apply_collage_cameras_v15 import build_spec,apply_collage_cameras
out=p/'collage-v15-measure';src=(p.parent.parent/'outputs/03-photon-mini/final-v14/scene.json').resolve();source=json.load(open(src));before=json.load(open(out/'rejected-singleton/camera-spec-before-temporal-guard.json'));before['artRefinements'][4]['src']=str((out/'rejected-singleton/04-before-temporal-guard.png').resolve());rows=json.load(open(out/'source-feature-tracks.json'));after=build_spec(source,rows);(out/'camera-spec-working.json').write_text(json.dumps(after,indent=2));old=apply_collage_cameras(source,before);new=apply_collage_cameras(source,after);oldcard=next(x for x in old['layers'] if x['id']=='native-affine-collage-cameras-v15')['children'][4];newcard=next(x for x in new['layers'] if x['id']=='native-affine-collage-cameras-v15')['children'][4];s0={**source,'layers':[oldcard]};s1={**source,'layers':[newcard]};rp.register_fonts(source,str(src.parent));affected=[];report=[]
for f in range(903,975):
 a=np.array(rp.render(s0,f/30,str(src.parent)));b=np.array(rp.render(s1,f/30,str(src.parent)));delta=np.abs(a.astype(int)-b.astype(int));n=int(np.any(delta,2).sum());report.append({'frame':f,'cardChangedPixels':n,'maxDelta':int(delta.max())})
 if n:affected.append(f)
print('affected',affected,flush=True)
metrics=json.load(open(out/'all72-metrics.json'))
for f in affected:
 image=rp.render(new,f/30,str(src.parent));image.save(out/'native-combined-frames'/f'{f:04}.png');a=np.array(Image.open(p/'collage-native'/f'{f-890:03}.png').convert('RGB'),dtype=float);m=next(q for q in metrics if q['frame']==f);m['beforeTemporalGuard']=m['new'];m['new']=float(np.abs(a-np.array(image,dtype=float)).mean());print(m,flush=True)
(out/'all72-metrics.json').write_text(json.dumps(metrics,indent=2));(out/'temporal-guard-native-proof.json').write_text(json.dumps({'rejected':'Card4 singleton source970 after an unsupported23-frame absence; correspondences were repeated UI typography from another app, not a verified Mail reentry.','checkedFrames':72,'affectedCardFrames':affected,'frames':report},indent=2));
# Keep a source-relative canonical-branch candidate with absolute dependency paths for scope verification.
def norm(node):
 if node.get('src') and not node['src'].startswith(('data:','http:','https:','/')):node['src']=str((src.parent/node['src']).resolve())
 for child in node.get('children',[]):norm(child)
for layer in new['layers']:norm(layer)
for f in new.get('fonts',[]):
 if f.get('src') and not f['src'].startswith(('data:','http:','https:','/')):f['src']=str((src.parent/f['src']).resolve())
(out/'combined-prototype.scene.json').write_text(json.dumps(new,indent=2));print('guard proof complete',flush=True)
