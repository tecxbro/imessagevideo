"""Isolate source hardware-only ring/sensor and native silhouette for send close-up."""
from pathlib import Path
import json,sys,hashlib
import numpy as np
from PIL import Image
P=Path(__file__).parent;B=P/'early-v13-measure';D=P/'assets/early-send-hardware-v13';D.mkdir(exist_ok=True);s=json.loads((P/'early-v13.scene.json').read_text());sys.path.insert(0,str(P.parents[1]/'engines'));from render_pillow import state
p=next(l for l in s['layers'] if l['id']=='p03-86');q=state(p,311/30);scale=q['scaleX'];cx=q['x'];cy=q['y'];im=Image.open(B/'validation-source/013.png').convert('RGB');a=np.asarray(im);gray=a.mean(2);fg=gray<245;ys,xs=np.where(fg);top=int(ys.min());right=np.full(1080,-1,int);valid=fg.any(1);right[valid]=1919-np.argmax(fg[valid,::-1],axis=1);mask=np.zeros(fg.shape,bool)
for y in np.where(valid)[0]:
 r=right[y];mask[y,max(0,r-40):r+2]=True
for x in range(int(right.max())+1):
 iy=np.where(fg[:,x])[0]
 if len(iy):t=int(iy[0]);mask[max(0,t-1):t+40,x]=True
mask &= np.indices(mask.shape)[1] <= (right[:,None]+1)
box=(0,max(0,top-1),int(right.max()+2),1080);rgba=np.dstack([a,(mask*255).astype('uint8')]);ring=Image.fromarray(rgba).crop(box);ring.save(D/'ring.png');sensorbox=(40,140,560,290);im.crop(sensorbox).save(D/'sensor.png')
points=[(-64,top)]+[(int(right[y])+1,y)for y in range(top,1080,2)if right[y]>=0]+[(int(right[-1])+1,1200),(-64,1200)];d='M'+' L'.join(f'{x} {y}'for x,y in points)+' Z';data={'reference_frame':311,'reference_camera':{'scale':scale,'x':cx,'y':cy},'silhouette_path':d,'ring':{'src':str((D/'ring.png').relative_to(P)),'x':(box[0]-cx)/scale,'y':(box[1]-cy)/scale,'width':(box[2]-box[0])/scale,'height':(box[3]-box[1])/scale},'sensor':{'src':str((D/'sensor.png').relative_to(P)),'x':(sensorbox[0]-cx)/scale,'y':(sensorbox[1]-cy)/scale,'width':(sensorbox[2]-sensorbox[0])/scale,'height':(sensorbox[3]-sensorbox[1])/scale},'path_transform':{'x':-cx/scale,'y':-cy/scale,'scaleX':1/scale,'scaleY':1/scale},'provenance':{'ring_bounds':list(box),'opaque_ring_pixels':int(mask.sum()),'sensor_bounds':list(sensorbox),'scope':'Only outer hardware ring and sensor island. UI text/pane/button are excluded. Native silhouette remains an editable vector path.','limitation':'Hardware lighting is original photo texture, independently transformed with native device camera.'}}
# The actual iOS panel uses a continuous corner. Preserve it as a native
# measured boundary instead of guessing another circular corner radius.
white=(gray[:,900:1140]>245);white[:350]=False;wr=np.full(1080,-1,int);wv=white.any(1);wr[wv]=1139-np.argmax(white[wv,::-1],axis=1);wt=int(np.where(wv)[0].min());wp=[(-64,wt)]+[(int(wr[y])+1,y) for y in range(wt,1080) if wr[y]>=0]+[(int(wr[-1])+1,1200),(-64,1200)];data['pane_path']='M'+' L'.join(f'{x} {y}' for x,y in wp)+' Z';pane=next(l for l in p['children'] if l['id']=='p03-77');e=state(pane,311/30);ox=cx+scale*e['x'];oy=cy+scale*e['y'];data['pane_transform']={'x':-ox/scale,'y':-oy/scale,'scaleX':1/scale,'scaleY':1/scale};data['provenance']['pane_shape']='Native vector boundary measured from actual continuous corner; no UI pixels/text embedded.'
# Higher-resolution original held title in the send-camera close-up. The
# partial offscreen heading remains a native semantic glyph path.
sys.path.insert(0,str(P.parent/'02-danieltian'));from trace_glyphs import trace_alpha
crop=np.asarray(im.crop((0,690,700,850))).astype(float);alpha=np.clip((253-crop.mean(2))/253,0,1);title,stats=trace_alpha(alpha,0,690);data['closeup_title_path']=title;data['provenance']['closeup_title']={'source_frame':311,'bounds':[0,690,700,850],'semantic_text':'Dinner This Week (visible This Week portion)','editability':'Native original glyph outlines',**stats}
(B/'send-hardware-geometry.json').write_text(json.dumps(data,indent=2)+'\n');print(data['provenance'])
