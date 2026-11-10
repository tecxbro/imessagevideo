"""Apply only ID-scoped early-query + Uber refinements to any phonebook revision.
Inputs remain immutable; bitmap internal copy is explicitly declared in patch metadata.
"""
from pathlib import Path
import argparse, json, copy, hashlib
import numpy as np
from PIL import Image
from scipy import ndimage
ROOT=Path('/workspace/imessage-recreations'); REF=ROOT/'references/02-danieltian'; E=ROOT/'verification/fidelity-review/02-phonebook-branch'; AS=REF/'assets/phonebook-review'; AS.mkdir(exist_ok=True)
BG=253.; assets=[]
def save(name,a,frame,box,purpose):
 p=AS/(name+'.png');Image.fromarray(a).save(p);assets.append(dict(file=str(p.relative_to(REF)),source_frame=frame,source_bounds=box,purpose=purpose,sha256=hashlib.sha256(p.read_bytes()).hexdigest()));return str(p.relative_to(REF))
def track(p):return [dict(t=f/30,value=float(v),ease='linear') for f,v in p]
def img(id,src,w,h,**kw):return dict(type='image',id='pbr-'+id,src=src,width=w,height=h,**kw)
def arr(kind,frame):return np.array(Image.open(E/f'{kind}-{frame}.png').convert('RGB'))
qdata=json.loads((E/'query-dense.json').read_text());qd={x['frame']:x for x in qdata};states=[('full-three-early',390,394,390),('full-three',394,404,399),('full-two',404,406,404),('tail-two',406,408,406),('tail-one',408,412,411),('tail-none',412,413,412),('short',413,416,413)]
query=[]
for name,first,end,sourcef in states:
 box=qd[sourcef]['text_box'];x0,y0,x1,y1=box;offset=300,430
 # Anchor to the letter bbox; trailing dots are artwork outside that bbox.
 if 'three' in name:padright=48
 elif 'two' in name:padright=33
 elif 'one' in name:padright=19
 else:padright=3
 crop=[x0-3,y0-3,x1+padright,y1+3];a=arr('query',sourcef)[crop[1]-430:crop[3]-430,crop[0]-300:crop[2]-300].astype(float);ink=np.clip(BG-a.mean(2),0,253);peak=qd[sourcef]['peak'];rgba=np.zeros((*ink.shape,4),np.uint8);rgba[:,:,3]=np.uint8(np.clip(ink/peak,0,1)*255)
 src=save('query-'+name,rgba,sourcef,crop,'Isolated original query glyph state; bitmap internal copy, native measured translation/scale/opacity.')
 ks={k:[] for k in ['x','y','scaleX','scaleY','opacity']}
 for f in range(first,end):
  if f==415:bb=[786,514,1276,568];p=24.
  else:bb=qd[f]['text_box'];p=qd[f]['peak']
  sx=(bb[2]-bb[0])/(x1-x0);sy=(bb[3]-bb[1])/(y1-y0)
  vals=[bb[0]-3*sx,bb[1]-3*sy,sx,sy,p/BG]
  for k,v in zip(ks,vals):ks[k].append((f,v))
 query.append(img('query-'+name,src,crop[2]-crop[0],crop[3]-crop[1],start=first/30,end=end/30,keyframes={k:track(v) for k,v in ks.items()}))
# Source ring is one static stroke split into caps + a stretchable central strip;
# its native width/height contract independently of the text state.
a=arr('query',399);g=a.mean(2);lab,n=ndimage.label((g>180)&(g<252));chosen=None
for j,s in enumerate(ndimage.find_objects(lab),1):
 if s is None:continue
 yy,xx=s
 if xx.stop-xx.start>700 and 100<yy.stop-yy.start<160:chosen=(j,s);break
j,(yy,xx)=chosen;ringbox=[xx.start+298,yy.start+428,xx.stop+302,yy.stop+432] # source x/y minus2 padding
mask=ndimage.binary_dilation(lab==j,iterations=2);ink=np.clip(BG-g,0,253)*mask;peak=float(ink.max());rgba=np.zeros((*g.shape,4),np.uint8);rgba[:,:,3]=np.uint8(np.clip(ink/peak,0,1)*255);rb=rgba[ringbox[1]-430:ringbox[3]-430,ringbox[0]-300:ringbox[2]-300];h,w=rb.shape[:2];cap=66
ringkeys={n:[] for n in ['leftx','rightx','middlex','y','sy','middlew','opacity']}
for f in range(390,416):
 if f==415:x,y,rw,rh=718,479,625,121
 else:x,y,rw,rh=qd[f]['rings'][0]
 # Ring detection bbox excludes2padding from template; add matching padding scaled by height.
 sy=rh/(h-4);pad=2*sy;x-=pad;y-=pad;rw+=2*pad
 source=arr('query',min(f,414)).mean(2)
 # Top straight stroke is unoccluded by text, gives independent ring fade.
 if f==415:ratio=.01
 else:
  yc=int(round(y+pad));xc=int(round(x+rw*.5));v=253-source[max(0,yc-430):min(source.shape[0],yc-430+5),xc-300-40:xc-300+40];ratio=float(np.percentile(v,90)/BG)
 for k,v in zip(ringkeys,[x,x+rw-cap*sy,x+cap*sy,y,sy,rw-2*cap*sy,min(1,ratio)]):ringkeys[k].append((f,v))
for name,art,keyx in [('left',rb[:,:cap],'leftx'),('middle',rb[:,w//2:w//2+1],'middlex'),('right',rb[:,-cap:],'rightx')]:
 src=save('query-ring-'+name,art,399,ringbox,'Original query border component; native cap-preserving geometry, not a frame sequence.')
 ks={'x':track(ringkeys[keyx]),'y':track(ringkeys['y']),'scaleY':track(ringkeys['sy']),'opacity':track(ringkeys['opacity'])}
 if name=='middle':ks['scaleX']=track(ringkeys['middlew'])
 else:ks['scaleX']=track(ringkeys['sy'])
 query.insert(0,img('query-ring-'+name,src,art.shape[1],art.shape[0],start=13,end=416/30,keyframes=ks))
# Magnifier is its own authentic bounded artwork and fades before the copy changes.
a=arr('query',390);box=[448,504,519,580];b=a[box[1]-430:box[3]-430,box[0]-300:box[2]-300].astype(float);ink=np.clip(BG-b.mean(2),0,253);rgba=np.zeros((*ink.shape,4),np.uint8);rgba[:,:,3]=np.uint8(ink/BG*255)
src=save('query-magnifier',rgba,390,box,'Original magnifier artwork, independently faded/translated.')
query.append(img('query-magnifier',src,71,76,x=448,y=504,start=13,end=13.3,keyframes={'x':track([(390,448),(393,439),(396,435),(399,437)]),'opacity':track([(390,1),(393,.55),(396,.08),(399,0)])}))
# Uber artwork is extracted BEFORE source fade, unlike the root prototype's16.5s texture.
# Independent vertical pose recreates the entry flip and camera settling; late alpha
# is measured only after geometry, so shrinking/fading are not conflated.
u=arr('uber',489);ud={q['frame']:q for q in json.loads((E/'uber-dense.json').read_text())};box=[1198,209,1796,329];art=u[box[1]-150:box[3]-150,box[0]-1160:box[2]-1160];src=save('uber-eats-full',art,489,box,'Bounded original full-opacity Uber Eats capsule, before fade. Bitmap internal copy and control; native camera/alpha.')
keys={k:[] for k in ['x','y','scaleX','scaleY','opacity']};baseink=np.clip(BG-art.mean(2),0,BG).sum();peakmass=ud[490]['ink_mass']
for f in range(475,501):
 if f==477:x,y,rw,rh=1196,218,591,89
 elif ud[f]['rings']:x,y,rw,rh=ud[f]['rings'][0]
 else:x,y,rw,rh=1203,210,595,115
 sx=rw/594;sy=rh/116
 op=0 if f<477 else (1 if f<=490 else max(0,(ud[f]['ink_mass']-84)/peakmass))
 for k,v in zip(keys,[x-2*sx,y-2*sy,sx,sy,op]):keys[k].append((f,v))
earlybox=[1195,219,1790,329];earlyart=arr('uber',480)[earlybox[1]-150:earlybox[3]-150,earlybox[0]-1160:earlybox[2]-1160];earlysrc=save('uber-eats-entry-pose',earlyart,480,earlybox,'Bounded original camera entry pose of Uber capsule; blended into settled artwork while native pose animates. Not full-frame playback.')
# Independent background stays opaque so an old field number cannot bleed through the
# fading capsule. Original prototype inadvertently depended on an opaque faded texture.
alpha_samples=keys.pop('opacity');fade=track([(f,a*(1-max(0,min(1,(f-490)/5)))) for f,a in alpha_samples]);keys={k:track(v) for k,v in keys.items()}
latebox=[1203,211,1800,328];lateart=arr('uber',495)[latebox[1]-150:latebox[3]-150,latebox[0]-1160:latebox[2]-1160];latesrc=save('uber-eats-late-faded-pose',lateart,495,latebox,'Original bounded late camera/fade pose retained to preserve the exact16.5s source anchor; independently blended/faded thereafter.')
latealpha=next(a for f,a in alpha_samples if f==495);latekeys=track([(f,max(0,min(1,(f-490)/5))*a/latealpha) for f,a in alpha_samples])
children=[dict(type='rect',id='pbr-uber-background',x=0,y=0,width=598,height=120,fill='#FDFDFD'),dict(type='group',id='pbr-uber-foreground',keyframes={'opacity':fade},children=[img('uber-entry',earlysrc,595*594/591,110*116/106,x=2-2*594/591,y=2-2*116/106,keyframes={'opacity':track([(475,1),(480,1),(489,0)])}),img('uber-settled',src,598,120,keyframes={'opacity':track([(475,0),(480,0),(489,1)])})])]
children.append(img('uber-late-pose',latesrc,597*594/596,117,x=2+594/596,y=3,keyframes={'opacity':latekeys}))
uber=dict(type='group',id='pb-uber-eats',start=475/30,end=17.05,keyframes=keys,children=children)

def apply(scene):
 scene=copy.deepcopy(scene);count=dict(query=0,uber=0);late=None
 for i,l in enumerate(scene['layers']):
  if l.get('id')=='group-1007':
   old=copy.deepcopy(l);old['end']=13.
   scene['layers'][i]=old;late=(i+1,dict(type='group',id='pbr-late-query',start=13,end=416/30,children=query));count['query']+=1
  elif l.get('id')=='pb-uber-eats':scene['layers'][i]=uber;count['uber']+=1
 if count!={'query':1,'uber':1}:raise ValueError(f'ID replacement mismatch: {count}')
 scene['layers'].insert(*late)
 scene['source']['notes']+=' Review patch: authentic bounded query glyph states/magnifier/border and full-opacity Uber capsule; native measured positions, dimensions and alpha. Internal copy artwork is bitmap and not live text. No full-source frames or video playback. Uber entrance perspective remains a 2D-scale approximation.'
 return scene
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--input',type=Path,default=REF/'scene-v6-phonebook-glyphs.json');p.add_argument('--output',type=Path,default=REF/'scene-v6-phonebook-review.json');a=p.parse_args();scene=apply(json.loads(a.input.read_text()));a.output.write_text(json.dumps(scene,indent=2));meta=dict(input=str(a.input),output=str(a.output),id_replacements=['group-1007','pb-uber-eats'],changed_frame_ranges=[[390,415],[463,511]],actual_node_lifetimes={'query':[390,415],'uber':[475,511]},assets=assets,notice='Reviewer branch; native sampled validation pending. Explicit bitmap copy limits; entry perspective remains approximate.');(REF/'phonebook-review-patch.json').write_text(json.dumps(meta,indent=2));print(json.dumps({k:v for k,v in meta.items() if k!='assets'},indent=2))
