"""Native cart capsule/control reconstruction from bounded semantic glyph contours."""
from pathlib import Path
from PIL import Image
from scipy import ndimage
import numpy as np,json,copy,importlib.util,hashlib
P=Path(__file__).parent
sp=importlib.util.spec_from_file_location('glyph_trace',P.parent/'02-danieltian/trace_glyphs.py');mod=importlib.util.module_from_spec(sp);sp.loader.exec_module(mod)

def build():
 records=json.loads((P/'cart-v14-measurements.json').read_text());frames=[];proof=[]
 for r in records:
  f=r['frame'];q=r['chosen']
  if not q or not 668<=f<=725:continue
  x,y,x2,y2=q['bbox'];w=x2-x;h=y2-y;a=np.array(Image.open(P/'lunch-native'/f'{f-609:03}.png').convert('RGB'))[y:y2,x:x2].mean(2);bg=float(np.median(a[(a>225)&(a<249)]));children=[{'id':f'cart14-{f}-body','type':'rect','width':w,'height':h,'radius':h/2,'fill':'#'+f'{round(bg):02x}'*3}]
  # Glyphs are traced separately from the independently editable native capsule.
  # The split follows semantic cart-icon vs counter rather than whole-control pixels.
  for role,left,right in [('cart symbol',8,min(w,round(h*.90))),('item count',min(w,round(h*.90)),w-7)]:
   if right<=left:continue
   ink=np.clip((bg-a[7:h-6,left:right])/bg,0,1);gain=float(np.quantile(ink,.98))
   if gain<.012:continue
   mask=ink/gain;mask[mask<.12]=0;d,meta=mod.trace_alpha(mask,x0=left,y0=7,threshold=.5)
   if not d:continue
   children.append({'id':f'cart14-{f}-{role.replace(" ","-")}','type':'path','d':d,'fill':'#000000','opacity':min(1,gain),'semanticText':{'cart symbol':'Shopping cart','item count':str(1 if f<682 else 2 if f<711 else 3)}[role],'provenance':{'kind':'bounded original glyph outlines','source_frame':f,'source_box':[x+left,y+7,x+right,y2-6],'role':role,'notice':'Source glyph shape is native SVG outline, not live font text; capsule remains native geometry. SourceAA is re-rasterized by each engine.'}})
  frames.append({'id':f'measured-cart-frame-{f}-v14','type':'group','x':x,'y':y,'start':f/30,'end':(f+1)/30,'children':children});proof.append({'frame':f,'bbox':q['bbox'],'gray':bg,'semantic_count':1 if f<682 else 2 if f<711 else 3})
 # The final few projected/defocused poses use native geometry plus blur and explicit
 # opacity. Their late trajectory is refined from visible digit locations.
 last=copy.deepcopy(frames[-1]);last.pop('start');last.pop('end')
 for f,x,y,alpha,blur in [(726,1287,357,1,1.3),(727,1273,354,.98,2.4),(728,1253,350,.86,4.0),(729,1223,345,.59,6.3),(730,1179,339,.22,9.0)]:
  q=copy.deepcopy(last);q.update(id=f'measured-cart-frame-{f}-v14',x=x,y=y,opacity=alpha,blur=blur,start=f/30,end=(f+1)/30)
  def rename(n):
   n['id']=n['id'].replace('725',str(f))
   for c in n.get('children',[]):rename(c)
  rename(q);frames.append(q)
 data={'scope':[668,730],'root':{'id':'measured-cart-v14','type':'group','start':668/30,'end':731/30,'children':frames},'measurements':proof,'notice':'Native gray capsule geometry and separately traced semantic cart/count glyph paths. Counts reveal/fade independently as source1→2→3. Final five defocused exit poses remain a measured native blur/trajectory approximation; no source bitmap or fullframe is embedded.'};f=P/'cart-v14-components.json';f.write_text(json.dumps(data,indent=2));print(hashlib.sha256(f.read_bytes()).hexdigest())

def apply_cart(scene):
 scene=copy.deepcopy(scene);data=json.loads((P/'cart-v14-components.json').read_text());ids={'p03-211','late-menu-cart-two-v10','late-menu-cart-v10','measured-cart-v14'};scene['layers']=[x for x in scene['layers'] if x['id'] not in ids];scene['layers'].append(copy.deepcopy(data['root']));scene['cart_v14']={'scope':data['scope'],'notice':data['notice']};return scene
if __name__=='__main__':build()
