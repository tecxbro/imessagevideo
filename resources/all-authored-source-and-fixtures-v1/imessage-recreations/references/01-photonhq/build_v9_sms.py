"""Measured missing SMS material and native rolling-number alpha outlines."""
from pathlib import Path
import json,sys,re,hashlib
import numpy as np
from PIL import Image
p=Path(__file__).parent;root=p.parents[1];sys.path.insert(0,str(root/'engines'));sys.path.insert(0,str(p.parent/'02-danieltian'));from render_pillow import state
from trace_glyphs import trace_alpha
sourcePath=root/'outputs/01-photonhq/final-v8/scene.json';scene=json.load(open(sourcePath));byid={n['id']:n for n in scene['layers']};obs=json.load(open(p/'early-walls-v7-measure/observations-all.json'));assets=p/'assets/v9-sms-material';assets.mkdir(exist_ok=True);nodes=[];ledger=[]
# Repair only source-observed material outside the actually painted old bitmap.
# The existing known lower/right card art is kept; source260 remains untouched.
for f in range(250,260):
 image=Image.open(p/'early-walls-v7-measure'/f'frame-{f-248:03}.png').convert('RGB')
 for index in (0,1,2,4):
  t=obs[index];r=next((r for r in t['records'] if r['frame']==f),None)
  if r is None:continue
  n=byid[t['id']];q=state(n,f/30);x0,y0,x1,y1=r['box'];x0=0 if x0<=2 else x0;y0=0 if y0<=2 else y0;x1=1920 if x1>=1918 else x1;y1=1080 if y1>=1078 else y1
  left,top=q['x'],q['y'];right=left+q['width']*q['scaleX'];bottom=top+q['height']*q['scaleY'];regions=[]
  # Two disjoint strips cover the missing L, with a1px measured seam overlap.
  if top>y0+.5:regions.append([x0,y0,x1,min(y1,int(np.ceil(top))+1)])
  if left>x0+.5:regions.append([x0,max(y0,int(np.floor(top))),min(x1,int(np.ceil(left))+1),y1])
  if right<x1-.5:regions.append([max(x0,int(np.floor(right))-1),max(y0,int(np.floor(top))),x1,y1])
  for j,box in enumerate(regions):
   if box[2]<=box[0] or box[3]<=box[1]:continue
   file=assets/f'{index:02d}-{f:03d}-{j}.png';image.crop(box).save(file);meta={'sourceNativeFrame':f,'sourceBox':box,'cardId':t['id'],'oldPaintedBox':[left,top,right,bottom],'kind':'Only previously unpainted, independently bounded original card material; internal bitmap copy.','noNeighborComponents':True,'sha256':hashlib.sha256(file.read_bytes()).hexdigest()};ledger.append(meta)
   nodes.append({'id':f'v9-sms-missing-material-{index}-{f}-{j}','type':'image','src':str(file.resolve()),'x':box[0],'y':box[1],'width':box[2]-box[0],'height':box[3]-box[1],'start':f/30,'end':(f+1)/30,'provenance':meta})
# The rolling state is reconstructed from isolated source-number masks as native
# alpha contours. Nested opacity weights reproduce a32-level alpha staircase.
numberNodes=[];numberLedger=[];N=32;unit=4;box=(680,450,1036,640)
for f in range(250,258):
 a=np.array(Image.open(p/'early-walls-v7-measure'/f'frame-{f-248:03}.png').convert('RGB').crop(box),dtype=float);alpha=np.clip((255-a.mean(2))/255,0,1);children=[]
 for level in range(1,N+1):
  threshold=(level-.5)/N;d,stats=trace_alpha(alpha,threshold=threshold)
  if not d:continue
  d=re.sub(r'-?\d+(?:\.\d+)?',lambda m:f'{float(m.group())*unit:.5f}',d)
  children.append({'id':f'v9-sms-number-{f}-alpha-{level}','type':'path','d':d,'fill':'#000000','opacity':1/(N-level+1),'scaleX':1/unit,'scaleY':1/unit,'semanticText':'10,000+ measured rolling reveal','alphaContourLevel':threshold})
 numberNodes.append({'id':f'v9-sms-number-state-{f}','type':'group','x':box[0],'y':box[1],'start':f/30,'end':(f+1)/30,'children':children,'provenance':{'sourceNativeFrame':f,'sourceBox':list(box),'kind':'Native editable alpha-contour glyph paths; semantic final copy10,000+, measured rolling geometry; not live font text.'}});numberLedger.append({'frame':f,'contours':len(children),'sourceBox':list(box),'maximumAlpha':float(alpha.max())})
# The gray card's hue-threshold extraction had also deleted dark letter pixels.
# Restore only alpha holes strictly between opaque row boundaries; RGB is genuine
# original card material and stays byte-identical. Scope still ends before260.
original=byid['early-wall-native-v7-sms-000'];originalFile=sourcePath.parent/original['src'];rgba=np.array(Image.open(originalFile).convert('RGBA'));fixed=rgba.copy();holes=0
for row in range(rgba.shape[0]):
 xs=np.where(rgba[row,:,3]>200)[0]
 if len(xs)<2:continue
 inner=np.arange(xs[0],xs[-1]+1);missing=inner[rgba[row,inner,3]<200];holes+=len(missing);fixed[row,missing,3]=255
file=assets/'sms-000-alpha-restored.png';Image.fromarray(fixed).save(file)
alphaRepair={'originalId':original['id'],'src':str(file.resolve()),'frames':[250,259],'changedAlphaPixels':int(np.sum(fixed[:,:,3]!=rgba[:,:,3])),'rgbBytesIdentical':bool(np.array_equal(fixed[:,:,:3],rgba[:,:,:3])),'kind':'Restored genuine existing card glyph RGB removed by the prior hue-threshold alpha mask; row-interior alpha only. Static bitmap UI copy, native camera unchanged.','sha256':hashlib.sha256(file.read_bytes()).hexdigest()}
assert alphaRepair['rgbBytesIdentical']
spec={'alphaRepair':alphaRepair,'baseline':str(sourcePath),'scope':[[250,259]],'materialNodes':nodes,'numericNodes':numberNodes,'numericOriginalId':'source-heading-word-sms-0','numericOriginalResume':258/30,'materialLedger':ledger,'numberLedger':numberLedger};(p/'v9-repair/sms-spec-working.json').write_text(json.dumps(spec,indent=2)+'\n');(assets/'provenance.json').write_text(json.dumps(ledger,indent=2)+'\n');print('material',len(nodes),'number states',len(numberNodes),flush=True)
