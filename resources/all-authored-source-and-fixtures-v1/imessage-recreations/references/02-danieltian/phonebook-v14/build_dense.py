"""Measured layered native phonebook. Bounded semantic outlines; static original logo and number artwork."""
from pathlib import Path
import sys,json,copy,math,importlib.util,time
sys.path.insert(0,'/tmp/imessage-food-cv')
import cv2,numpy as np
from PIL import Image
from scipy import ndimage
R=Path(__file__).resolve().parent;P=R.parent.parent.parent/'outputs/02-danieltian/final-v13';cv2.setNumThreads(1);BG=253.;scene=json.loads((P/'scene.json').read_text());data=json.loads((R/'dense-measurements.json').read_text());spec=importlib.util.spec_from_file_location('trace',R.parent/'trace_glyphs.py');trace=importlib.util.module_from_spec(spec);spec.loader.exec_module(trace);spec=importlib.util.spec_from_file_location('measure',R/'measure_dense.py');measure=importlib.util.module_from_spec(spec);spec.loader.exec_module(measure)
def absolute(n):
 if n.get('src') and not n['src'].startswith(('/','data:','http:','https:')):n['src']=str((P/n['src']).resolve())
 for c in n.get('children',[]):absolute(c)
for n in scene['layers']:absolute(n)
for n in scene.get('fonts',[]):absolute(n)
def affine_group(id,M,W,H,children,opacity=1):
 M=np.array(M);U,s,V=np.linalg.svd(M[:,:2]);
 if np.linalg.det(U)<0:U[:,1]*=-1;s[1]*=-1
 if np.linalg.det(V)<0:V[1,:]*=-1;s[1]*=-1
 center=M@np.array([W/2,H/2,1]);return dict(id=id,type='group',x=float(center[0]),y=float(center[1]),rotation=math.degrees(math.atan2(U[1,0],U[0,0])),scaleX=float(s[0]),scaleY=float(s[1]),opacity=float(opacity),children=[dict(id=id+'-inner',type='group',rotation=math.degrees(math.atan2(V[1,0],V[0,0])),children=children)])
def paths(alpha,x,y,id,levels=5,color='#000000'):
 peak=float(np.max(alpha));out=[]
 if peak<.003:return out
 previous=0.
 for j,t in enumerate(np.linspace(.1,.9,levels) if levels>1 else[.5]):
  d,stats=trace.trace_alpha(alpha,x,y,threshold=float(t*peak));level=min(1,peak*(j+1)/levels);opacity=(level-previous)/(1-previous) if previous<1 else 0;previous=level
  if d:out.append(dict(id=id+'-'+str(j),type='path',d=d,fill=color,opacity=float(opacity)))
 return out
logo_specs=json.loads((R/'frame486-layered-details.json').read_text());logos={q['id']:q for q in logo_specs};lifetimes={n['id']:n['start'] for n in scene['layers'] if n['id'] in logos};new=[];ledger=[];started=time.monotonic()
for n in scene['layers']:
 if n['id'].startswith('pb-number-'):n['end']=436/30
 if n['id'] in logos:n['end']=n['start']
 if n['id']=='pb-result-search':
  for c in n.get('children',[]):
   if c['id']=='middle-query-before-18':c['start']=526/30
births={}
for ftext,frame in data.items():
 for q in frame['caps']:births[q['id']]=min(int(ftext),births.get(q['id'],9999))
slots={'pb-capsule-lyft':(1,1),'pb-capsule-airbnb':(3,2),'pb-capsule-resy':(6,2),'pb-uber-eats':(1,3)}
for ftext,frame in data.items():
 f=int(ftext);src=np.asarray(Image.open(R/'source-native'/f'{f:06d}.png').convert('RGB')).astype(float);gray=src.mean(2);lab,rings=measure.detect(src)
 # Original field textures are independently reposed with measured per-cell affine cameras.
 for q in frame['cells']:
  cell=tuple(map(int,q['id'].rsplit('-',2)[1:]));replaced=any(cell==slot and f>=births.get(id,9999) for id,slot in slots.items())
  if q['opacity']<=.001 or replaced:continue
  W,H=q['width'],q['height'];id='pb14-field-'+str(f)+'-'+q['id'];node=affine_group(id,q['matrix'],W,H,[dict(id=id+'-art',type='image',src=q['asset'],x=-W/2,y=-H/2,width=W,height=H)],q['opacity']);node.update(start=f/30,end=(f+1)/30);new.append(node)
 used=set()
 for q in frame['caps']:
  id=q['id'];
  if id in used:continue
  used.add(id);l,t,r,b=q['bbox'];bw,bh=r-l,b-t;W,H=(598,120) if id=='pb-uber-eats' else(604,117);rootid='pb14-card-'+str(f)+'-'+id;group=dict(id=rootid,type='group',start=f/30,end=(f+1)/30,children=[],semanticCopy={'pb-capsule-lyft':'Lyft','pb-capsule-airbnb':'Airbnb','pb-capsule-resy':'Resy','pb-uber-eats':'Uber Eats'}[id],provenance={'sourceFrame':f,'bounds':q['bbox'],'material':'independently measured native border, semantic glyph/control contours, original static logo artwork'});children=group['children'];children.append(dict(id=rootid+'-backdrop',type='rect',x=l+1,y=t+1,width=bw-2,height=bh-2,radius=(bh-2)/2,fill='#FDFDFD'))
  rawmask=ndimage.binary_dilation(lab==q['label'],iterations=2);a=np.clip((BG-gray)/BG,0,1)*rawmask;L,T,RR,B=max(0,l-3),max(0,t-3),min(1920,r+3),min(1080,b+3);children+=paths(a[T:B,L:RR],L,T,rootid+'-ring',5)
  # The label's projected black glyph silhouette is independent from the rounded container.
  L,T,RR,B=l+105,t+5,r-100,b-5;ar=src[T:B,L:RR];a=np.clip((BG-ar.mean(2))/BG,0,1)*(ar.max(2)-ar.min(2)<18);a[ndimage.binary_dilation(rawmask,iterations=3)[T:B,L:RR]]=0;children+=paths(a,L,T,rootid+'-semantic-label',5)
  L,T,RR,B=r-100,max(t,int((t+b)/2-42)),r-20,min(b,int((t+b)/2+42));ar=src[T:B,L:RR];a=np.clip((BG-ar.mean(2))/BG,0,1)*(ar.max(2)-ar.min(2)<18);a[ndimage.binary_dilation(rawmask,iterations=3)[T:B,L:RR]]=0;children+=paths(a,L,T,rootid+'-plus',5)
  # Green check controls are native colored contours, retaining their actual local morph silhouette.
  rr,gg,bb=ar[:,:,0],ar[:,:,1],ar[:,:,2];green=(gg>rr+25)&(gg>bb+20)&(gg>100);mask=ndimage.binary_dilation(ndimage.binary_fill_holes(green),iterations=2);a=np.clip((BG-rr)/(BG-49),0,1)*mask;children+=paths(a,L,T,rootid+'-check',7,'#31D652')
  logo=logos[id];cl,ct,cr,cb=logo['logoCrop'];asset=R/'assets'/(id+'-original-logo.png');M=np.array(q['matrix']);# Original static pictorial logo under its native measured content camera.
  node=affine_group(rootid+'-logo',M,W,H,[dict(id=rootid+'-logo-art',type='image',src=str(asset.resolve()),x=cl-W/2,y=ct-H/2,width=cr-cl,height=cb-ct)])
  # Measure actual colored/logo birth and fade; an empty ring must stay empty.
  z=src[t:b,l:min(r,l+130)];chroma=z.max(2)-z.min(2);count=int((chroma>25).sum());reference=np.asarray(Image.open(asset).convert('RGBA'));refchroma=reference[:,:,:3].max(2).astype(float)-reference[:,:,:3].min(2).astype(float);peak=float(np.percentile(chroma[chroma>5],97)) if np.count_nonzero(chroma>5)>5 else 0.;refpeak=float(np.percentile(refchroma[reference[:,:,3]>128],97));logoOpacity=float(np.clip(peak/max(1,refpeak),0,1)) if count>5 else 0.;node['opacity']=logoOpacity
  children.append(node);new.append(group);ledger.append(dict(frame=f,id=id,bounds=q['bbox'],cameraFit=q['fit'],quality=q['quality'],logoCamera=M.tolist(),logoOpacity=logoOpacity,coloredPixels=count))
 # Native search query optical reveal, bounded above the first selected card.
 if f>=510 and frame['caps']:
  top=min(q['bbox'][1] for q in frame['caps']);L,T,RR,B=350,230,1550,min(405,top-12)
  if B>T:
   ar=src[T:B,L:RR];a=np.clip((BG-ar.mean(2))/BG,0,1)*(ar.max(2)-ar.min(2)<12)
   if a.max()>.025:
    id='pb14-query-'+str(f);new.append(dict(id=id,type='group',start=f/30,end=(f+1)/30,semanticCopy='Searching the Agent Phone Book...',provenance={'sourceFrame':f,'bounds':[L,T,RR,B],'material':'native source-derived semantic outline and optical reveal'},children=paths(a,L,T,id+'-ink',9)))
 if f%5==0:print('built',f,'layers',len(new),'seconds',round(time.monotonic()-started,1),flush=True)
spec=dict(scope=[[436,525]],gates={'pb-number-*':{'end':436/30},'four original capsules':{'end':'start'},'middle-query-before-18':{'start':526/30}},layers=new,notes='No reference video/full-frame layer. Static genuine original number and logo art remain independently transformed. Text, rounded containers, controls and query reveal are bounded native source-derived contours; outline copy is not live editable typography. Optical antialias/compression and logo perspective residuals remain.');(R/'elements-candidate.json').write_text(json.dumps(spec,separators=(',',':')));scene['layers']+=new;scene['phonebook_v14']=dict(scope=spec['scope'],notice=spec['notes']);(R/'scene-candidate.json').write_text(json.dumps(scene,separators=(',',':')));(R/'caps-ledger.json').write_text(json.dumps(ledger,indent=2));print('DONE',len(new),'seconds',time.monotonic()-started,flush=True)
