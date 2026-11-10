"""Measure each short Order! glyph box and its separate gray native capsule."""
from pathlib import Path
import sys,json,math
sys.path.insert(0,'/tmp/imessage-food-cv')
import cv2,numpy as np
from scipy import ndimage
R=Path('/workspace/imessage-recreations/references/03-photon-mini');D=R/'food-orbit-measure';records=json.loads((D/'order-ocr-refined.json').read_text());out={};cv2.setNumThreads(1)
for ns,items in records.items():
 n=int(ns);a=cv2.imread(str(R/'lunch-native'/f'{n-609:03d}.png')).astype(float);found=[]
 for rec in items:
  l,t,r,b=rec['bbox'];w=r-l;h=b-t;px=max(10,int(w*.5));py=max(10,int(h*1.4));x0=max(0,l-px);x1=min(1920,r+px);y0=max(0,t-py);y1=min(1080,b+py);roi=a[y0:y1,x0:x1];neutral=(roi.max(2)-roi.min(2)<12)&(roi.min(2)>210)&(roi.max(2)<249);strip=neutral.copy();strip[:max(0,t-y0-max(2,int(h*.35)))]=False;strip[max(0,t-y0):]=False;strip[:,:max(0,l-x0+int(w*.1))]=False;strip[:,min(x1-x0,r-x0-int(w*.1)):]=False
  pixels=roi[strip]
  if not len(pixels):pixels=roi[neutral]
  if not len(pixels):continue
  v,ct=np.unique(pixels.astype('uint8'),axis=0,return_counts=True);color=v[ct.argmax()];mask=np.max(np.abs(roi-color),2)<=2;lab,num=ndimage.label(mask,np.ones((3,3)));candidates=[]
  for li,sl in enumerate(ndimage.find_objects(lab),1):
   yy,xx=sl;ww=xx.stop-xx.start;hh=yy.stop-yy.start
   if ww<w*.8 or hh<h*.7:continue
   overlap=np.sum(lab[max(0,t-y0):min(y1-y0,b-y0),max(0,l-x0):min(x1-x0,r-x0)]==li);candidates.append((overlap,li,sl))
  body=None;reliable=False
  if candidates:
   _,li,sl=max(candidates,key=lambda q:q[0]);yy,xx=sl;solid=ndimage.binary_fill_holes(lab==li);column=int((xx.start+xx.stop)*.5);ys=np.flatnonzero(solid[:,column]);coreT=int(ys.min()) if len(ys) else yy.start;coreB=int(ys.max()+1) if len(ys) else yy.stop;bb=[xx.start+x0,coreT+y0,xx.stop+x0,coreB+y0];bw,bh=bb[2]-bb[0],bb[3]-bb[1]
   if 1.1<bw/max(1,w)<2.5 and 1.35<bh/max(1,h)<4.5 and bb[0]>x0 and bb[2]<x1 and bb[1]>y0 and bb[3]<y1:body=bb;reliable=True
  if body is None:
   # Measured canonical735 word/body ratios, used only when optical/UI overlap prevents an isolated gray component.
   sx=w/43;sy=h/12;body=[l-11*sx,t-8*sy,l-11*sx+64*sx,t-8*sy+30*sy]
  # Source centerline is horizontal throughout this billboard UI. Estimate tilt from the lower black-glyph envelope as evidence.
  glyph=a[t:b,l:r];bm=(glyph.max(2)<120)&(glyph.max(2)-glyph.min(2)<20);xs=[];ys=[]
  for x in range(w):
   yy=np.flatnonzero(bm[:,x])
   if len(yy):xs.append(x);ys.append(yy.max())
  angle=0.
  if len(xs)>8:
   # Lower half of letter bottoms removes ascender/interior-counter samples.
   high=np.asarray(ys)>=np.quantile(ys,.6);xx=np.asarray(xs)[high];yy=np.asarray(ys)[high]
   if len(xx)>4:angle=float(np.degrees(np.arctan(np.polyfit(xx,yy,1)[0])))
  # Conservative filtering of faint/rotated OCR artifacts; retain measured bbox/projection evidence.
  found.append({**rec,'bodyBounds':body,'bodyReliable':reliable,'bodyRGB':color[::-1].tolist(),'baselineAngleEstimate':angle,'rotation':0 if abs(angle)<2 else angle})
 out[ns]=found
(D/'order-body-measurements.json').write_text(json.dumps(out,indent=2));print('Measured Order bodies',sum(map(len,out.values())),'isolated',sum(q['bodyReliable'] for v in out.values() for q in v))
