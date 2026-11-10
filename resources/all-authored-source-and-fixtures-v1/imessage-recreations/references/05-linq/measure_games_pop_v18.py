"""Measure actual per-tile coverage and independent label positions; no camera fit."""
from pathlib import Path
import json,sys,copy,hashlib
import numpy as np,cv2
from scipy import ndimage
from PIL import Image
P=Path(__file__).parent;ROOT=P.parents[1];M=P/'games-pop-v18-measure';OUT=P/'assets/games-pop-v18';OUT.mkdir(exist_ok=True);sys.path.insert(0,str(ROOT/'engines'));import render_pillow as rp
src=ROOT/'outputs/05-linq/final-v17/scene.json';s=json.load(open(src));g=next(n for n in s['layers']if n['id']=='g-138');nodes={n['id']:n for n in g['children']};cv2.setNumThreads(1)
# The world camera is identity. Original source material pixels already map1:1.
# A saturation-only extent can omit dark/desaturated image edges; use the whole
# nonwhite connected image component, excluding independent text by area.
material=[];ledger=[];labelUpdates={};measurements=[];templates={}
for i in range(6):
 n=copy.deepcopy(nodes[f'root-games-label-{i}']);n.pop('keyframes',None);n.update(start=0,end=s['duration'],x=0,y=0,opacity=1);im=rp.render({**s,'layers':[n],'background':'#ffffff'},0,str(src.parent));a=np.array(im,dtype=float);ink=np.array(rp.rgba(n['fill'])[:3],dtype=float).mean();alpha=np.clip((255-a.mean(2))/(255-ink),0,1);yy,xx=np.where(alpha>.08);box=[int(xx.min())-2,int(yy.min())-2,int(xx.max())+3,int(yy.max())+3];templates[i]=(alpha[box[1]:box[3],box[0]:box[2]].astype('float32'),box,ink)
for f in range(130,146):
 source=np.array(Image.open(M/'source'/f'{f:06}.png').convert('RGB'));base=np.array(Image.open(ROOT/f'outputs/05-linq/frames-gsap/{f:06}.png').convert('RGB'));records=[]
 for i in range(6):
  n=nodes.get(f'root-games-tile-{i}-pose-{f}')
  if n is None:continue
  x,y,w,h=[int(n[k])for k in ('x','y','width','height')];col=i%3;row=i//3;left=max(0,[120,360,595][col]);right=min(960,[365,600,845][col]);top=95 if row==0 else 390;bottom=405 if row==0 else 680
  mask=source[top:bottom,left:right].min(2)<245;labels,count=ndimage.label(mask,np.ones((3,3)));comps=[]
  for lab,sl in enumerate(ndimage.find_objects(labels),1):
   if sl is None:continue
   yy,xx=sl;area=int((labels[sl]==lab).sum())
   if area>10000 and xx.stop-xx.start>150 and yy.stop-yy.start>150:comps.append((area,[left+xx.start,top+yy.start,left+xx.stop,top+yy.stop]))
  if not comps:raise ValueError((f,i,'No complete tile component'))
  full=max(comps)[1];r={'frame':f,'tile':i,'oldPaintedBox':[x,y,x+w,y+h],'observedFullBox':full}
  if full[3]>y+h+2:
   box=[max(0,full[0]-1),y+h-1,min(960,full[2]+1),min(720,full[3]+1)];before=float(abs(source[box[1]:box[3],box[0]:box[2]].astype(float)-base[box[1]:box[3],box[0]:box[2]].astype(float)).mean());r['missingStripSourceMae']=before
   if before>.1:
    file=OUT/f'tile-{i}-{f}-lower.png';Image.fromarray(source).crop(box).save(file);meta={'sourceFrame':f,'sourceBounds':box,'originalActor':n['id'],'kind':'Only source-observed lower material omitted by saturation-only bounds. Original known pixels/camera retained; internal animated UI is original bounded bitmap.','sha256':hashlib.sha256(file.read_bytes()).hexdigest()};material.append({'id':f'games-pop-v18-lower-{i}-{f}','type':'image','src':str(file.resolve()),'x':box[0],'y':box[1],'width':box[2]-box[0],'height':box[3]-box[1],'start':f/30,'end':(f+1)/30,'provenance':meta});ledger.append(meta)
  if f>=131:
   template,tbox,ink=templates[i];bx,by,bx1,by1=tbox;sl=nodes[f'root-games-label-{i}'];st=rp.state(sl,f/30);sx0=max(0,bx-8);sx1=min(960,bx1+8);sy0=max(0,full[3]+2,by-26);sy1=min(720,by1+36)
   patch=source[sy0:sy1,sx0:sx1].astype(float);alpha=np.clip((255-patch.mean(2))/(255-ink),0,1);alpha[(patch.max(2)-patch.min(2))>30]=0
   if alpha.shape[0]<template.shape[0]:r['labelRejected']='Insufficient below-tile source room'
   else:
    score=cv2.matchTemplate(alpha.astype('float32'),template,cv2.TM_CCOEFF_NORMED);_,ncc,_,loc=cv2.minMaxLoc(score);dx=sx0+loc[0]-bx;dy=sy0+loc[1]-by;oldx=float(st['x']);oldy=float(st['y']);r['labelFit']={'ncc':ncc,'x':dx,'y':dy,'oldX':oldx,'oldY':oldy}
    def loss(tx,ty):
     W=np.array([[1,0,bx+tx-sx0],[0,1,by+ty-sy0]],dtype='float32');pred=cv2.warpAffine(template,W,(alpha.shape[1],alpha.shape[0]),flags=cv2.INTER_LINEAR);return float(abs(pred-alpha).mean())
    before=loss(oldx,oldy);after=loss(dx,dy);r['labelFit'].update(beforeAlphaMae=before,afterAlphaMae=after)
    if ncc>.8 and after<before-.003 and max(abs(dx-oldx),abs(dy-oldy))>=1:
     labelUpdates.setdefault(sl['id'],[]).append({'frame':f,'x':dx,'y':dy,'ncc':ncc,'beforeAlphaMae':before,'afterAlphaMae':after})
  records.append(r)
 measurements.append({'frame':f,'tiles':records});print(f,'strips',sum(x['sourceFrame']==f for x in ledger),'label updates',[(i,r['labelFit']['oldY'],r['labelFit']['y'])for i,r in enumerate(records)if r.get('labelFit')and any(x['frame']==f for x in labelUpdates.get(f'root-games-label-{i}',[]))],flush=True)
spec={'baseline':str(src),'baselineSha256':hashlib.sha256(src.read_bytes()).hexdigest(),'groupId':'g-138','cameraUnchanged':True,'scope':[[130,145]],'materialNodes':material,'materialLedger':ledger,'labelUpdates':labelUpdates,'measurements':measurements};(M/'spec-working.json').write_text(json.dumps(spec,indent=2)+'\n');(OUT/'provenance.json').write_text(json.dumps(ledger,indent=2)+'\n');print('TOTAL',len(material),'strips',sum(len(v)for v in labelUpdates.values()),'label offsets',flush=True)
