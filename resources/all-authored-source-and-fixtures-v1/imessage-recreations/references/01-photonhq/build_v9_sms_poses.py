"""Repair only six incomplete SMS actors with observed bounded component poses.
The source has a brief 3D/rolling entrance: a clipped rest image cannot recover
its local material warp using the old axis camera. Preserve independent native
lifecycle/box and explicit bitmap internals rather than invent perspective.
"""
from pathlib import Path
import json,hashlib
from PIL import Image
p=Path(__file__).parent;root=p.parents[1];folder=p/'assets/v9-sms-card-poses';folder.mkdir(exist_ok=True);obs=json.load(open(p/'early-walls-v7-measure/observations-all.json'));nodes=[];ledger=[];scopes={}
for f in range(250,260):
 source=Image.open(p/'early-walls-v7-measure'/f'frame-{f-248:03}.png').convert('RGB')
 for index in (0,1,2,3,4,5):
  track=obs[index];r=next((r for r in track['records']if r['frame']==f),None)
  if r is None:continue
  x0,y0,x1,y1=r['box'];box=[max(0,x0-3),max(0,y0-3),min(1920,x1+3),min(1080,y1+3)];file=folder/f'{index:02}-{f:03}.png';source.crop(box).save(file);meta={'sourceNativeFrame':f,'sourceBox':box,'sourceDetectedComponentBox':r['box'],'originalActor':track['id'],'kind':'Individually bounded original SMS card material for the short observed3D entrance pose; internal copy/corner shading are bitmap. Camera, box and lifecycle are independent native properties. No neighbor components or source frame/video layer.','sha256':hashlib.sha256(file.read_bytes()).hexdigest()};ledger.append(meta);scopes.setdefault(track['id'],[]).append(f);nodes.append({'id':f'v9-sms-expanded-pose-{index}-{f}','type':'image','src':str(file.resolve()),'x':box[0],'y':box[1],'width':box[2]-box[0],'height':box[3]-box[1],'start':f/30,'end':(f+1)/30,'semanticText':'Original separate SMS UI component','bitmapLimitation':'Static original per-card pose contains the local perspective/lighting and internal glyph pixels. Editable native card box/camera/lifetime; not live internal UI text.','provenance':meta})
spec=json.load(open(p/'v9-repair/sms-spec-working.json'));spec['rejectedStripIteration']={'materialNodes':len(spec['materialNodes']),'reason':'Dense254 proved the clipped front image also distorts the painted region during the3D entrance; filling only missing strips was insufficient.'};spec.pop('alphaRepair',None);spec['materialNodes']=nodes;spec['materialLedger']=ledger;spec['replacementScopes']=scopes;(p/'v9-repair/sms-spec-expanded.json').write_text(json.dumps(spec,indent=2)+'\n');(folder/'provenance.json').write_text(json.dumps(ledger,indent=2)+'\n');print(len(nodes),'component poses',flush=True)
