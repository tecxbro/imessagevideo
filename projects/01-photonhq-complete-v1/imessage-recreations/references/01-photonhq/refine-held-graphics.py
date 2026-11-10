"""Reconstruct bounded source glyphs and brand artwork; never use a complete frame as a render layer."""
from pathlib import Path
from PIL import Image
from scipy import ndimage
import numpy as np,json,hashlib,sys,copy
sys.path.insert(0,'/workspace/imessage-recreations/references/02-danieltian')
from trace_glyphs import trace_alpha
R=Path('/workspace/imessage-recreations/references/01-photonhq');A=R/'assets/held-art';A.mkdir(exist_ok=True)
scene=json.loads((R/'scene-wall-v4.json').read_text());replacements={};ledger=[]
def frame(n):
 names={15:'00.50',60:'02.00',225:'07.50',480:'16.00',555:'18.50',615:'20.50'}
 p=R/'keyframes'/f'{names[n]}.png' if n in names else R/f'assets/held-measure/{n:04d}.png'
 return p,np.array(Image.open(p).convert('RGB'))
def ease(p,n):
 if n=='hold':return 1 if p>=1 else 0
 if n=='easeIn':return p**3
 if n=='easeOut':return 1-(1-p)**3
 if n=='easeInOut':return 4*p**3 if p<.5 else 1-(-2*p+2)**3/2
 return p
def sample(l,k,t):
 ks=l.get('keyframes',{}).get(k)
 if not ks:return l.get(k,1 if k.startswith('scale') else 0)
 if t<=ks[0]['t']:return ks[0]['value']
 for a,b in zip(ks,ks[1:]):
  if t<=b['t']:return a['value']+(b['value']-a['value'])*ease((t-a['t'])/(b['t']-a['t']),b.get('ease','linear'))
 return ks[-1]['value']
def outline(n,roi,text,exclude=None,fill='#000000',alpha=None):
 p,ar=frame(n);x0,y0,x1,y1=roi
 if alpha is None:alpha=np.clip((253-ar[y0:y1,x0:x1].mean(2))/253,0,1)
 if exclude:
  for a,b,c,d in exclude:alpha[max(0,b-y0):min(y1-y0,d-y0),max(0,a-x0):min(x1-x0,c-x0)]=0
 d,stats=trace_alpha(alpha,x0,y0);record=dict(kind='native glyph outlines',semanticText=text,sourceFrame=n,sourceBounds=list(roi),sourceSHA256=hashlib.sha256(p.read_bytes()).hexdigest(),editability='Editable native outline contours; semantic copy retained, not live text.',**stats);ledger.append(record)
 return dict(id='held-outline-'+str(n)+'-'+str(len(ledger)),type='path',d=d,fill=fill,semanticText=text,sourceFrame=n,sourceBounds=list(roi),editability=record['editability'])
def artwork(n,roi,name,arr=None):
 p,ar=frame(n);x0,y0,x1,y1=roi;dest=A/(name+'.png');Image.fromarray(ar if arr is None else arr).crop(roi).save(dest);ledger.append(dict(kind='bounded original graphic artwork',semanticText=name,sourceFrame=n,sourceBounds=list(roi),asset='assets/held-art/'+dest.name,sourceSHA256=hashlib.sha256(p.read_bytes()).hexdigest(),editability='Independent graphic element; pixels and gradient are bitmap artwork.'))
 return dict(id='held-art-'+name,type='image',src='assets/held-art/'+dest.name,x=x0,y=y0,width=x1-x0,height=y1-y0,sourceFrame=n,sourceBounds=list(roi),editability='Bounded original graphic artwork; independent transform, bitmap gradient.')
def norm_at(parent,t,children):
 sx,sy=sample(parent,'scaleX',t),sample(parent,'scaleY',t);x,y=sample(parent,'x',t),sample(parent,'y',t);ox,oy=parent.get('originX',0),parent.get('originY',0)
 return dict(id=parent['id']+'-source-normalization',type='group',x=ox-(x+ox)/sx,y=oy-(y+oy)/sy,scaleX=1/sx,scaleY=1/sy,children=children)
byid={l['id']:l for l in scene['layers']}
intro=copy.deepcopy(byid['group-3']);intro['children']=[outline(15,(490,475,970,600),'Introducing'),artwork(15,(975,485,1425,590),'Photon-2.0-gradient')];intro['originX']=intro['originY']=0;intro['keyframes']={k:[] for k in ['x','y','scaleX','scaleY']}
for nn in range(15):
 aa=np.array(Image.open(R/f'assets/held-measure/dense-{nn:04d}.png').convert('RGB')).astype(float);yy,xx=np.where(aa.max(2)<210)
 if len(xx):
  sx=(xx.max()-xx.min()+1)/445;sy=(yy.max()-yy.min()+1)/83;vals=dict(x=float(xx.min()-509*sx),y=float(yy.min()-499*sy),scaleX=sx,scaleY=sy)
  for k,v in vals.items():intro['keyframes'][k].append(dict(t=nn/10+1/30,value=v))
# The exact canonical source anchor is preserved independently of the 10fps source-measurement samples.
for k,v in dict(x=0,y=0,scaleX=1,scaleY=1).items():
 intro['keyframes'][k]=sorted([q for q in intro['keyframes'][k] if q['t']!=.5]+[dict(t=.5,value=v)],key=lambda q:q['t'])
replacements[intro['id']]=intro
for lid,n,roi,text in [('text-9',105,(650,470,1620,605),'With just one click'),('text-10',135,(280,470,1430,605),'Your agent is everywhere')]:
 old=byid[lid];node=outline(n,roi,text);node.update(id=lid+'-source-outline',start=old['start'],end=old['end'],keyframes={'x':[{**k,'value':k['value']-sample(old,'x',n/30)} for k in old['keyframes']['x']]});replacements[lid]=node
# Measure whole-phrase glyph bounds through their native camera motion. App labels are excluded by their lower baseline.
def black_bounds(a):
 mask=(a.max(2)<210);mask[:475]=False;mask[605:]=False;labels,count=ndimage.label(mask,np.ones((3,3)));valid=np.zeros(mask.shape,bool)
 for li,sl in enumerate(ndimage.find_objects(labels),1):
  if not sl:continue
  yy,xx=sl
  if yy.start<550 and yy.stop<600 and np.count_nonzero(labels[sl]==li)>30:valid[sl]|=labels[sl]==li
 ys,xs=np.where(valid)
 return (int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)) if len(xs) else None
for lid,ref,lo,hi in [('text-9',105,28,41),('text-10',135,43,51)]:
 node=replacements[lid];_,ar=frame(ref);base=black_bounds(ar);ms=[]
 for nn in range(lo,hi+1):
  aa=np.array(Image.open(R/f'assets/held-measure/dense-{nn:04d}.png').convert('RGB'));b=black_bounds(aa)
  if not b:continue
  sx=(b[2]-b[0])/(base[2]-base[0]);sy=(b[3]-b[1])/(base[3]-base[1]);ms.append(dict(t=nn/10+1/30,x=b[0]-base[0]*sx,y=b[1]-base[1]*sy,scaleX=sx,scaleY=sy))
 ms.append(dict(t=ref/30,x=0,y=0,scaleX=1,scaleY=1));ms.sort(key=lambda m:m['t']);node['keyframes']={k:[dict(t=m['t'],value=m[k]) for m in ms] for k in ['x','y','scaleX','scaleY']};ledger.append(dict(kind='native phrase measured geometry',semanticText=node['semanticText'],measurements=ms))
free=copy.deepcopy(byid['group-27']);free['end']=8.0;free['children']=[outline(225,(350,470,1600,610),'And it’s / for everyone.',exclude=[(745,465,970,615)]),artwork(225,(745,475,965,595),'free-gradient')];replacements[free['id']]=free
reg=copy.deepcopy(byid['group-782']);reg['children']=[outline(480,(380,470,1410,610),'Even 10DLC registration'),artwork(480,(1415,485,1520,600),'registration-verified-badge')];replacements[reg['id']]=reg
old=byid['text-783'];node=outline(510,(780,470,1140,610),'On us.');node.update(id=old['id']+'-source-outline',start=old['start'],end=old['end']);replacements[old['id']]=node
cta=copy.deepcopy(byid['group-786']);cta['children']=[outline(555,(630,410,1280,545),'Try it today at'),artwork(555,(540,545,1380,650),'photon-codes-beta-gradient')];replacements[cta['id']]=cta
mark=copy.deepcopy(byid['group-790']);glyph=outline(615,(850,430,1075,650),'Photon three-lozenge mark');glyph.update(x=-960,y=-505);mark['children']=[glyph];replacements[mark['id']]=mark
# The pill is individually transformed according to its measured source color-mask bounds at 0.1s intervals.
p,ar=frame(60);rgb=ar.astype(float);blue=(rgb[:,:,2]-rgb[:,:,0]>35)&(rgb[:,:,2]>200)&(rgb[:,:,0]<220);lab,num=ndimage.label(blue,np.ones((3,3)));sl=max((s for s in ndimage.find_objects(lab) if s),key=lambda s:(s[0].stop-s[0].start)*(s[1].stop-s[1].start));yy,xx=sl;box=(xx.start-5,yy.start-5,xx.stop+5,yy.stop+5);clean=ar.copy()
# Cursor hides a small lower-right part of the symmetric glossy pill. Reconstruct only that occluded underlay by mirroring unoccluded left-side artwork.
mirror=(box[0]+box[2]-1);xa,ya,xb,yb=1100,540,1275,785
for x in range(xa,xb):
 mx=mirror-x
 if 0<=mx<1920:clean[ya:yb,x]=ar[ya:yb,mx]
art=artwork(60,box,'glossy-blue-pill-cursor-underlay-mirrored',clean);ledger[-1]['reconstruction']='Cursor-occluded underlay mirrored from symmetric left side; unseen original pixels are inferred.'
measure=[]
for n in range(13,41):
 pp=R/f'assets/held-measure/dense-{n:04d}.png'
 if not pp.exists():continue
 aa=np.array(Image.open(pp).convert('RGB')).astype(float);mask=(aa[:,:,2]-aa[:,:,0]>35)&(aa[:,:,2]>200)&(aa[:,:,0]<220);labels,num=ndimage.label(mask,np.ones((3,3)));candidates=[]
 for s in ndimage.find_objects(labels):
  if not s:continue
  y,x=s;w=x.stop-x.start;h=y.stop-y.start
  if w>100 and h>40 and 200<y.start<700:candidates.append((w*h,(x.start-5,y.start-5,x.stop+5,y.stop+5)))
 if candidates:
  b=max(candidates)[1];measure.append(dict(t=n/10+1/30,x=b[0],y=b[1],scaleX=(b[2]-b[0])/(box[2]-box[0]),scaleY=(b[3]-b[1])/(box[3]-box[1])))
measure.append(dict(t=2.,x=box[0],y=box[1],scaleX=1,scaleY=1));measure.sort(key=lambda m:m['t'])
pill={**art,'id':'group-6-source-pill','x':box[0],'y':box[1],'start':measure[0]['t'],'end':measure[-1]['t']+.1,'keyframes':{k:[dict(t=m['t'],value=m[k]) for m in measure] for k in ['x','y','scaleX','scaleY']}};replacements['group-6']=pill;ledger.append(dict(kind='measured pill motion',measurements=measure))
# Cursor remains a separate editable vector element above the pill.
roi=(1100,535,1275,785);a=np.clip((253-ar[roi[1]:roi[3],roi[0]:roi[2]].max(2).astype(float))/253,0,1);a[a<.6]=0
labels,num=ndimage.label(a>.6,np.ones((3,3)));areas=np.bincount(labels.ravel());areas[0]=0;keep=ndimage.binary_dilation(labels==areas.argmax(),iterations=3);a*=keep
# Source cursor includes separated diagonal black fragments at the outline; keep all dark components in its bounded silhouette.
a=np.clip((253-ar[roi[1]:roi[3],roi[0]:roi[2]].max(2).astype(float))/253,0,1);a[a<.65]=0;d,stats=trace_alpha(a);old=byid['group-8'];cursor=copy.deepcopy(old);cursor.update(id='group-8-source-cursor',x=roi[0],y=roi[1],scaleX=1,scaleY=1);cursor['keyframes']={k:[{**q,'value':q['value']-sample(old,k,2)+roi[j]} for q in old['keyframes'][k]] for j,k in enumerate(['x','y'])};cursor['children']=[dict(id='cursor-white-outline',type='path',d=d,fill='#000000',stroke='#FFFFFF',strokeWidth=7),dict(id='cursor-black-outline',type='path',d=d,fill='#000000')];replacements['group-8']=cursor;ledger.append(dict(kind='native cursor outlines',sourceFrame=60,sourceBounds=list(roi),**stats))
scene['layers']=[replacements.get(l['id'],l) for l in scene['layers']];scene['source']['notes']+=' Held source typography and Photon mark reconstructed as native semantic glyph outlines. Bounded original gradient words/pill/badge retained as independent artwork; cursor independent native path. Pill cursor-occluded underlay inferred by symmetry.'
(R/'scene-final-v4.json').write_text(json.dumps(scene,indent=2));(R/'held-graphics-provenance.json').write_text(json.dumps(dict(replacements=list(replacements),provenance=ledger,changed_intervals=[[0,8.23],[15.5,655/30]]),indent=2));print('Prepared held graphic replacements',len(replacements),flush=True)
