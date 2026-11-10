"""Read-only coarse whole-image identity search on bounded static disc templates."""
from pathlib import Path
import json
import numpy as np
from PIL import Image,ImageFilter
from scipy.signal import fftconvolve
from scipy.ndimage import minimum_filter
P=Path(__file__).parent;S=json.load(open(P/'scene.json'));F=P/'native-transition-v18';B=P/'portrait-helper-v18';B.mkdir(exist_ok=True);A=P/'assets/portrait-helper-v18';A.mkdir(exist_ok=True)
# Both isolated original discs are sampled at624. The foliage woman's left
# edge788 is clear of the larger Asian portrait's measured right edge772.5.
new=[]
for id,f,box in [('new-blond-male',624,(531,562,681,712)),('new-foliage-woman',624,(788,743,912,867))]:
 im=Image.open(F/f'{f:06d}.png').convert('RGBA').crop(box);w,h=im.size;yy,xx=np.mgrid[:h,:w];alpha=np.uint8(np.clip((.5-np.sqrt(((xx+.5)/w-.5)**2+((yy+.5)/h-.5)**2))*min(w,h)/1.3,0,1)*255);im.putalpha(Image.fromarray(alpha));p=A/(id+'.png');im.save(p);new.append({'id':id,'src':str(p),'source_frame':f,'source_bounds':list(box),'kind':'Isolated original photographed disc, static image with circle alpha. Native camera/depth/blur remain editable.'})
(B/'new-portrait-provenance.json').write_text(json.dumps(new,indent=2)+'\n')
faces={g['id'].split('-')[-1]:P/g['children'][0]['src']for g in S['layers']if g['id'].startswith('rene-final11-group-')and g.get('start')==20.5};faces.update({x['id']:Path(x['src'])for x in new});scale=6;pad=160

def find(f,id):
 src=np.array(Image.open(F/f'{f:06d}.png').convert('RGB').resize((320,180),Image.Resampling.LANCZOS)).astype(np.float32);src=np.pad(src,((pad,pad),(pad,pad),(0,0)));valid=np.pad(np.ones((180,320),np.float32),((pad,pad),(pad,pad)));ar=Image.open(faces[id]).convert('RGBA');bg=Image.new('RGBA',ar.size,'white');bg.alpha_composite(ar);orig=bg.convert('RGB');candidates=[]
 for diameter in np.geomspace(55,1100,25):
  size=round(diameter/scale);y,x=np.mgrid[:size,:size];mask=(((x+.5)/size-.5)**2+((y+.5)/size-.5)**2<.42**2).astype(np.float32);photo=orig.resize((size,size),Image.Resampling.LANCZOS);den=fftconvolve(valid,mask[::-1,::-1],mode='same');good=den>mask.sum()*.24;energy=sum(fftconvolve(src[:,:,c]**2,mask[::-1,::-1],mode='same')for c in range(3))
  for frac in [0,.025,.06]:
   tpl=np.array(photo.filter(ImageFilter.GaussianBlur(frac*size))).astype(np.float32);cross=sum(fftconvolve(src[:,:,c],(tpl[:,:,c]*mask)[::-1,::-1],mode='same')for c in range(3));te=fftconvolve(valid,(np.sum(tpl**2,axis=2)*mask)[::-1,::-1],mode='same');cost=np.maximum(0,energy-2*cross+te)/np.maximum(1,den*3);cost[~good]=1e8
   # Several local minima make the ambiguity visible, rather than silently
   # snapping a missing identity to a similar neighboring face.
   minima=(cost==minimum_filter(cost,size=max(5,size//3)))&good;ys,xs=np.where(minima);ix=np.argsort(cost[ys,xs])[:3]
   for k in ix:candidates.append({'cx':float((xs[k]-pad)*scale),'cy':float((ys[k]-pad)*scale),'diameter':float(diameter),'blurFraction':frac,'mse':float(cost[ys[k],xs[k]]),'visibleFraction':float(den[ys[k],xs[k]]/mask.sum())})
 return sorted(candidates,key=lambda x:x['mse'])[:12]
results=json.load(open(B/'coarse-identity-search.json')) if (B/'coarse-identity-search.json').exists() else {}
for f,id in [(615,'73'),(618,'73'),(615,'83'),(618,'83'),(618,'75'),(624,'new-blond-male'),(618,'new-foliage-woman'),(615,'85'),(616,'85'),(617,'85'),(618,'85'),(624,'75'),(630,'new-blond-male'),(645,'new-blond-male'),(630,'new-foliage-woman'),(645,'new-foliage-woman'),(660,'new-foliage-woman'),(681,'new-foliage-woman'),(660,'new-blond-male'),(681,'new-blond-male'),(609,'87'),(612,'87'),(609,'95'),(612,'95')]:
 if f'{id}-{f}' in results:continue
 rows=find(f,id);results[f'{id}-{f}']=rows;print(id,f,rows[:4],flush=True);(B/'coarse-identity-search.json').write_text(json.dumps(results,indent=2)+'\n')
