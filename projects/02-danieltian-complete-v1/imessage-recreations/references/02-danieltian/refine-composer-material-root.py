"""Measure the text-free composer material and independent original send control."""
from pathlib import Path
import json,subprocess
import numpy as np
from scipy import ndimage
from PIL import Image
REF=Path(__file__).resolve().parent;AS=REF/'assets/root-composer-material';AS.mkdir(exist_ok=True);layers=[];records=[]
proc=subprocess.Popen(['ffmpeg','-v','error','-threads','1','-filter_threads','1','-i',str(REF/'source.mp4'),'-vf',"select='between(n,95,174)'",'-fps_mode','passthrough','-threads','1','-pix_fmt','rgb24','-f','rawvideo','pipe:1'],stdout=subprocess.PIPE)
for n in range(95,175):
 raw=proc.stdout.read(1920*1080*3);a=np.frombuffer(raw,np.uint8).reshape(1080,1920,3);rgb=a[390:690,180:1740].astype(float);g=rgb.mean(2);neutral=rgb.max(2)-rgb.min(2)<15;blue=(rgb[:,:,2]-rgb[:,:,0]>25)&(rgb[:,:,1]-rgb[:,:,0]>15);blue[:,:1250]=False;labels,_=ndimage.label(blue,np.ones((3,3)));options=[]
 for i,sl in enumerate(ndimage.find_objects(labels)):
  if sl is not None:
   yy,xx=sl;count=int((labels[sl]==i+1).sum())
   if count>500:options.append((count,i+1,sl))
 _,label,sl=max(options);circle=ndimage.binary_fill_holes(labels==label);avoid=ndimage.binary_dilation((neutral&(g<230))|circle,iterations=5);valid=neutral&~avoid
 # Only neutral non-UI material samples enter this interpolated scalar field.
 # No text/caret/control pixels survive the sample mask.
 den=ndimage.gaussian_filter(valid.astype(float),sigma=8);material=np.stack([np.divide(ndimage.gaussian_filter(rgb[:,:,c]*valid,sigma=8),den,out=np.full_like(den,253.),where=den>.01) for c in range(3)],axis=2);material=np.clip(np.rint(material),0,255).astype(np.uint8);asset=AS/f'material-{n}.png';Image.fromarray(material).save(asset);layers.append({'id':f'root-composer-material-{n}','type':'image','src':str(asset),'x':180,'y':390,'width':1560,'height':300,'start':n/30,'end':(n+1)/30,'semanticText':'Measured smooth composer material only','editability':'Procedurally drawn low-contrast material field from neutral non-UI samples; glyphs, caret and colored controls excluded. Not a source UI/frame playback layer.'})
 yy,xx=sl;bx0=max(0,180+xx.start-9);bx1=min(1920,180+xx.stop+9);by0=max(0,390+yy.start-9);by1=min(1080,390+yy.stop+9);arrow=AS/f'send-{n}.png';Image.fromarray(a[by0:by1,bx0:bx1]).save(arrow);layers.append({'id':f'root-composer-send-{n}','type':'image','src':str(arrow),'x':bx0,'y':by0,'width':bx1-bx0,'height':by1-by0,'start':n/30,'end':(n+1)/30,'sourceFrame':n,'semanticText':'Original iMessage send control','editability':'Strictly bounded original send-control artwork with independent native placement/lifetime; no typed copy or other scene content.'});records.append({'frame':n,'sendBounds':[bx0,by0,bx1,by1],'materialInput':'Neutral RGB samples excluding dilated glyph/caret and complete blue control silhouette','materialKernelSigma':8})
proc.stdout.close();assert proc.wait()==0
(REF/'root-composer-material-patch.json').write_text(json.dumps({'scope':[[95,174]],'layers':layers,'measurements':records},indent=2));print({'frames':len(records),'layers':len(layers)})
