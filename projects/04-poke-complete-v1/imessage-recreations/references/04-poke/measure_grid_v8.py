"""Fit independent native logo-layer positions/opacity at every grid frame.

Known static brand artwork is the template; no complete source frame is a scene layer.
FFT correlation finds position, normalized spatial correlation rejects other logos,
and the least-squares color deficit gives opacity on white.
"""
from pathlib import Path
import json,hashlib,math
import numpy as np
from PIL import Image
from scipy import ndimage
from scipy.fft import rfft,irfft,next_fast_len

p=Path(__file__).parent;decoded=p/'measurements-v8/decoded';out=p/'measurements-v8';out.mkdir(exist_ok=True);fps=30000/1001
reference=Image.open(p/'native/39.0.png').convert('RGB');entry=Image.open(p/'measurements-v8/decoded/001152.png').convert('RGB')
base_x=[-70,201,472,744,1015,1286];base_y=[22,292,564,836]
names=[['sonos','github','banana','asana','hex','strava'],['spiral','webflow','canva','todoist','oura','sonos'],['outlook','cube','vercel','notion','gmail','spiral'],['netlify','linear','calendar','sonos','github','outlook']]
whole={'sonos':reference.crop((744,836,969,1061)),'spiral':entry.crop((3,310,212,519)).resize((225,225),Image.Resampling.LANCZOS),'netlify':entry.crop((3,814,212,1023)).resize((225,225),Image.Resampling.LANCZOS),'strava':entry.crop((1228,59,1437,268)).resize((225,225),Image.Resampling.LANCZOS),'outlook':Image.open(p/'assets/brand-outlook-auth-composite.png').convert('RGB').resize((225,225),Image.Resampling.LANCZOS)}
templates=[];provenance=[]
for row in range(4):
 for col in range(6):
  name=names[row][col];i=row*6+col
  if col in [0,5]:image=whole[name].copy();source={'kind':'genuine complementary brand artwork','name':name,'entry_frame':1152 if name in ['spiral','netlify','strava']else None}
  else:image=reference.crop((base_x[col],base_y[row],base_x[col]+225,base_y[row]+225));source={'frame':1169,'crop':[base_x[col],base_y[row],base_x[col]+225,base_y[row]+225]}
  file=p/'assets'/f'grid-native-v8-{i:02}-{name}.png';image.save(file);templates.append(image);provenance.append({'index':i,'name':name,'asset':'assets/'+file.name,'source':source,'purpose':'Genuine individual static service-logo artwork; affine position/scale/opacity remain independent native layers. No whole-frame bitmap or video replacement.','sha256':hashlib.sha256(file.read_bytes()).hexdigest()})

def blue_box(a):
 v=255-a.astype(float);direction=np.array([223,145,15.]);cos=(v*direction).sum(2)/(np.linalg.norm(v,axis=2)*np.linalg.norm(direction)+1e-9);mask=(cos>.98)&(v.max(2)>25);mask[:180]=False;mask[680:]=False
 labels,_=ndimage.label(mask);choices=[]
 for sl in ndimage.find_objects(labels):
  if sl is None:continue
  yy,xx=sl;w,h=xx.stop-xx.start,yy.stop-yy.start
  if 90<w<400 and 90<h<400 and .8<w/h<1.2:choices.append((w*h,[xx.start,yy.start,xx.stop,yy.stop]))
 return max(choices)[1] if choices else None

ref_box=blue_box(np.array(reference));rest_sum=(ref_box[2]-ref_box[0])+(ref_box[3]-ref_box[1]);frames=list(range(1125,1219));geometry=[]
for n in frames:
 a=np.array(Image.open(decoded/f'{n:06}.png').convert('RGB'));bb=blue_box(a);colored=int(((a.max(2).astype(int)-a.min(2).astype(int)>30)&(a.min(2)<230)).sum());geometry.append({'frame':n,'time':n/fps,'blue_bbox':bb,'colored_pixels':colored})
cut=next(r['frame']for r in geometry if r['frame']>1190 and r['colored_pixels']<1000)
valid=[r for r in geometry if r['blue_bbox']and r['frame']<cut]
for r in valid:
 b=r['blue_bbox'];r['scale']=((b[2]-b[0])+(b[3]-b[1]))/rest_sum;r['row1_y']=b[1]-(ref_box[1]-base_y[1])*r['scale']
times=np.array([r['frame']for r in valid]);scales=np.array([r['scale']for r in valid]);ys=np.array([r['row1_y']for r in valid]);cache={};cache_size=None;measurements=[]

def correlation(source_state,template_state,xmin,xmax):
 fa,energy_source,width,size=source_state;fb,energy_template,w=template_state;corr=irfft((fa*np.conj(fb)).sum(axis=(0,2)),n=size,workers=1)
 xs=np.arange(math.floor(xmin),math.ceil(xmax)+1);left=np.maximum(0,xs);right=np.minimum(width,xs+w);tl=np.maximum(0,-xs);tr=np.minimum(w,width-xs);visible=right-left
 keep=(visible>=25)&(tr>tl);xs=xs[keep];left=left[keep];right=right[keep];tl=tl[keep];tr=tr[keep]
 en_t=energy_template[tr]-energy_template[tl];en_s=energy_source[right]-energy_source[left];c=corr[np.mod(xs,size)];scores=np.where(en_t*en_s>1,c/np.sqrt(np.maximum(1,en_t*en_s)),0);i=int(scores.argmax());x=float(xs[i]);score=float(scores[i]);alpha=float(np.clip(c[i]/max(1,en_t[i]),0,1))
 if 0<i<len(xs)-1 and xs[i-1]+1==xs[i] and xs[i]+1==xs[i+1]:
  denom=scores[i-1]-2*scores[i]+scores[i+1]
  if abs(denom)>1e-9:x+=float(np.clip(.5*(scores[i-1]-scores[i+1])/denom,-.5,.5))
 if score<.6 or alpha<.02:alpha=0
 return x,alpha,score

for r in geometry:
 n=r['frame']
 if n>=cut:continue
 scale=float(np.interp(n,times,scales));row1_y=float(np.interp(n,times,ys));size=max(1,round(225*scale));actual_scale=size/225;a=np.array(Image.open(decoded/f'{n:06}.png').convert('RGB'));rows=[]
 if size!=cache_size:cache.clear();cache_size=size
 for row in range(4):
  y=row1_y+(base_y[row]-base_y[1])*scale;iy=round(y);strip=np.full((size,1440,3),255,dtype=np.uint8);lo=max(0,iy);hi=min(1080,iy+size)
  if hi>lo:strip[lo-iy:hi-iy]=a[lo:hi]
  deficit=255-strip.astype(np.float32);fft_size=next_fast_len(1440+size-1);source_state=(rfft(deficit,n=fft_size,axis=1,workers=1),np.r_[0,np.cumsum((deficit*deficit).sum((0,2)),dtype=np.float64)],1440,fft_size)
  for col in range(6):
   i=row*6+col;key=(i,size)
   if key not in cache:
    template=255-np.array(templates[i].resize((size,size),Image.Resampling.LANCZOS)).astype(np.float32);cache[key]=(rfft(template,n=fft_size,axis=1,workers=1),np.r_[0,np.cumsum((template*template).sum((0,2)),dtype=np.float64)],size)
   target=720+(base_x[col]-720)*scale;low,high=(target-450,target+15)if row%2==0 else(target-15,target+450)
   x,alpha,score=correlation(source_state,cache[key],low,high);rows.append({'index':i,'x':x,'y':float(iy),'scaleX':actual_scale,'scaleY':actual_scale,'opacity':alpha,'ncc':score})
 measurements.append({'frame':n,'time':n/fps,'camera_scale_measurement':scale,'tiles':rows});print(n,'scale',round(scale,4),'visible',sum(v['opacity']>0 for v in rows),flush=True)
report={'source':'source.mp4','source_frame_cadence':'30000/1001','method':'Native RGB template spatial correlation, source row/y/scale measured from Webflow body; per-tile horizontal position and opacity independently fitted. Alternating row direction only limits the search region, not the measured result. Integer template size is native measured scale; horizontal NCC peak has quadratic subpixel refinement.','cut_frame':cut,'cut_time':cut/fps,'reference_blue_bbox':ref_box,'geometry':geometry,'measurements':measurements};(out/'grid-pose-fit.json').write_text(json.dumps(report,indent=2));(p/'assets/grid-native-v8-provenance.json').write_text(json.dumps(provenance,indent=2));print('CUT',cut,cut/fps)
