"""Reusable physical-camera measurement from original thin hardware pixels.

Input image is the 1920x1080 source frame (or proportional downsample). Return
poses for review, not automatic scene mutations. UI must be fitted separately.
"""
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage
_P=Path(__file__).parent
_a=np.asarray(Image.open(_P/'assets/phone-hardware.png').convert('RGBA')).astype(float)
_g=_a[:,:,:3].mean(2);_yy,_xx=np.mgrid[:_a.shape[0],:_a.shape[1]]
_mask=(_a[:,:,3]>245)&(_g<245)&((_xx<14)|(_xx>_a.shape[1]-15))&(abs(ndimage.sobel(_g,axis=0))/8>12)
_y,_x=np.where(_mask);_values=_g[_mask];_x=_x*800/_a.shape[1];_y=_y*1658/_a.shape[0]

def fit_hardware(image,initial,y_radius=300,edge_bands=None):
 """Return scale/x/y, residual and diagnostics from thin body/rim samples.

 `initial`: {scale or scaleX, x, y} in full1920 source pixels. `edge_bands`
 optionally gives two (left,right) x intervals in full source pixels to exclude
 floating artwork. Never infer the Messages UI transform from this result.
 """
 im=image.convert('RGB').resize((960,540),Image.Resampling.LANCZOS);gray=np.asarray(im).mean(2);dark=gray<75
 if edge_bands:
  masks=[]
  for lo,hi in edge_bands:
   mask=dark.copy();mask[:,:max(0,int(lo/2))]=False;mask[:,min(960,int(hi/2)):]=False;masks.append(mask)
  ld,rd=masks
 else:ld=rd=dark
 valid_l=ld.any(1);valid_r=rd.any(1);left=int(np.bincount(np.argmax(ld,1)[valid_l]).argmax())*2 if valid_l.any() else 0;right=int(np.bincount(959-np.argmax(rd[:,::-1],1)[valid_r]).argmax())*2 if valid_r.any() else 1918
 scale=float(initial.get('scale',initial.get('scaleX',1)));x=float(initial['x']);used_sides=False
 if left>0 and right<1918 and right-left>250:scale=(right-left)/768*1.002;x=(left+right)/2-400*scale;used_sides=True
 ys=np.arange(float(initial['y'])-y_radius,float(initial['y'])+y_radius+1,2.);xp=np.broadcast_to((x+scale*_x)[None,:]/2,(len(ys),len(_x)));yp=(ys[:,None]+scale*_y[None,:])/2;inside=(xp>1)&(xp<959)&(yp>1)&(yp<539);sample=ndimage.map_coordinates(gray,[yp,xp],order=1,mode='nearest');loss=np.minimum(abs(sample-_values[None,:]),90);scores=(loss*inside).sum(1)/np.maximum(15,inside.sum(1));scores[inside.sum(1)<15]=100;j=int(scores.argmin());y=float(ys[j])
 if 0<j<len(ys)-1:
  a,b,c=scores[j-1:j+2];den=a-2*b+c
  if den>0:y+=float(np.clip((a-c)/den,-1,1))
 result={'scale':scale,'x':x,'y':y,'hardware_cost':float(scores[j]),'visible_feature_samples':int(inside[j].sum()),'left_dark_mode':left,'right_dark_mode':right,'used_both_sides':used_sides,'review_required':bool(scores[j]>25 or inside[j].sum()<30),'scope':'Physical device only. Foreground occlusion/perspective and different hardware lighting can invalidate the fit.'}
 return result
