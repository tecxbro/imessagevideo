"""Local linear-light correction masks from STATIC app document, not source frames.
Native shutter/camera remains beneath each transparent per-component color mask.
"""
from pathlib import Path
import numpy as np,json
from PIL import Image,ImageDraw
from scipy.ndimage import gaussian_filter
R=Path('/workspace/imessage-recreations');P=R/'verification/fidelity-review/05-flight';REF=R/'references/05-linq';A=REF/'assets/flight-document-review';D=json.load(open(REF/'flight-document-camera-exposure-review.json'));cam={q['frame']:q for q in D['camera']};bg={q['frame']:q for q in D['background']};doc=np.array(Image.open(A/'diagnostic-doc-composite.png').convert('RGB'))/255;H,W=doc.shape[:2];mask=Image.new('L',(W*4,H*4),0);ImageDraw.Draw(mask).rounded_rectangle((0,0,W*4,2000*4),radius=64*4,fill=255);alpha=np.array(mask.resize((W,H),Image.Resampling.LANCZOS))/255;clean=np.array(Image.open(P/'pre-source/0002.png').convert('RGB'))/255
lin=lambda v:np.where(v<=.04045,v/12.92,((v+.055)/1.055)**2.4)
srgb=lambda v:np.where(v<=.0031308,v*12.92,1.055*np.maximum(v,0)**(1/2.4)-.055)
def sample(a,Y):
 z=np.arange(720)-Y;lo=np.floor(z).astype(int);fr=(z-lo).reshape((720,)+(1,)*(a.ndim-1));v=a[np.clip(lo,0,H-1)]*(1-fr)+a[np.clip(lo+1,0,H-1)]*fr;v[(lo<0)|(lo>=H-1)]=0;return v
layers=[];prov=[]
for f in range(370,380):
 q=cam[f];s=q['spread'];off=np.linspace(-s/2,s/2,41)if q['kernel']=='box'else np.linspace(-3*s,3*s,41);weights=np.ones(41)if q['kernel']=='box'else np.exp(-.5*(off/s)**2);weights/=weights.sum();
 if q.get('exposureSamples'):off=np.array([v['offset']for v in q['exposureSamples']]);weights=np.array([v['weight']for v in q['exposureSamples']]);
 C=np.zeros((720,W,3));L=C.copy();al=np.zeros((720,W));premul=doc*alpha[:,:,None];lpre=lin(doc)*alpha[:,:,None]
 for o,w in zip(off,weights):C+=w*sample(premul,q['y']+o);L+=w*sample(lpre,q['y']+o);al+=w*sample(alpha,q['y']+o)
 B=1-bg[f]['opacity']*(1-gaussian_filter(clean,(bg[f]['blur'],bg[f]['blur'],0)))[:,188:772];enc=C+B*(1-al[:,:,None]);linear=srgb(L+lin(B)*(1-al[:,:,None]));delta=np.maximum(0,linear-enc)
 native=np.array(Image.open(P/'check-v1'/f'{f/30:.3f}.png').convert('RGB'))/255 if(P/'check-v1'/f'{f/30:.3f}.png').exists()else None
 # Unrendered intermediate frames use the encoded analytical exposure only;
 # checkpoint-native mask adaptation has no source pixel input.
 Cn=enc;target=np.clip(Cn+delta,0,1);a=np.clip(np.max(delta/np.maximum(.005,1-Cn),axis=2),0,1);rgb=np.clip((target-Cn*(1-a[:,:,None]))/np.maximum(1e-6,a[:,:,None]),0,1);rgba=np.dstack((rgb,a));rgba[a<.001]=0;pixels=np.uint8(np.clip(rgba,0,1)*255+.5)
 split=int(np.clip(round(q['y']+550),0,720));parts=[('header',0,0,W,split),('basic',0,split,360,720),('economy',360,split,W,720)]
 for name,x0,y0,x1,y1 in parts:
  if y1<=y0:continue
  asset=A/f'shutter-linear-color-{f}-{name}.png';Image.fromarray(pixels[y0:y1,x0:x1]).save(asset);layers.append(dict(id=f'flight-review-shutter-color-{f}-{name}',type='image',src=str(asset),x=188+x0,y=y0,width=x1-x0,height=y1-y0,start=f/30,end=(f+1)/30));prov.append(dict(frame=f,semantic_component=name,path=str(asset),source='Computed transparent COLOR-ONLY linear-light correction from canonical static UI components, measured shutter offsets, clean351 backdrop and candidate raster. No source-frame pixels.',rect=[188+x0,y0,x1-x0,y1-y0],kernel=q['kernel'],spread=s))
# Authentic late summary-card tail, still one shared document camera.
late=Image.open(P/'source/0045.png').convert('RGB').crop((188,0,772,132));latepath=A/'flight-summary-tail-sharp.png';late.save(latepath)
(REF/'flight-shutter-color-review.json').write_text(json.dumps(dict(layers=layers,provenance=prov,late_tail=str(latepath)),indent=2));print('masks',len(layers),flush=True)
