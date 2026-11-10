"""Scoped source02 boundary repair after the every-frame v10 failure diagnosis.
No complete reference-frame bitmap or source-video layer is created.
"""
from pathlib import Path
from PIL import Image
from scipy import ndimage
import numpy as np,json,copy
from trace_glyphs import trace_alpha
R=Path('/workspace/imessage-recreations/references/02-danieltian');D=R/'assets/peak-v10-measure';S=json.loads((R/'scene-combined-v10.json').read_text());orig={l['id']:l for l in S['layers']};patch={};grads=[];ledger=[]
def ar(n):return np.array(Image.open(D/f'frame-{n:04d}.png').convert('RGB')).astype(float)
def sample(ks,t):
 if t<=ks[0]['t']:return ks[0]['value']
 for a,b in zip(ks,ks[1:]):
  if t<=b['t']:return a['value']+(b['value']-a['value'])*(t-a['t'])/(b['t']-a['t'])
 return ks[-1]['value']
def comps(mask):
 lab,num=ndimage.label(mask,np.ones((3,3)));areas=np.bincount(lab.ravel());out=[]
 for i,sl in enumerate(ndimage.find_objects(lab),1):
  if not sl:continue
  y,x=sl;out.append((int(areas[i]),i,[x.start,y.start,x.stop,y.stop]))
 return out,lab
# Preserve native phone elements through the actual upward exit; the source holds the phone beyond8.73.
g=copy.deepcopy(orig['group-995']);g['end']=266/30
for n in range(262,266):
 a=ar(n);cc,lab=comps((a[:,:,2]-a[:,:,0]>30)&(a[:,:,2]>180));bs=[(area,b) for area,i,b in cc if b[2]-b[0]>400 and b[3]-b[1]>40]
 if bs:
  b=max(bs)[1];g['keyframes']['y'].append(dict(t=n/30,value=-72.00160080732071+b[1]-248))
def extend(n):
 if abs(n.get('end',0)-8.73)<.001:n['end']=266/30
 for c in n.get('children',[]):extend(c)
extend(g)
# The source exit fades vertically, not as uniform opacity. Sample the dark phone rail as a native white gradient.
for n in range(260,266):
 a=ar(n);rail=a[:,310:350].min(2).min(1);stops=[]
 for y in range(0,1081,30):
  yy=min(1079,y);opacity=float(np.clip(rail[max(0,yy-2):min(1080,yy+3)].min()/253,0,1));stops.append(dict(offset=f'{y/1080*100:.5f}%',color='#FDFDFD',opacity=opacity))
 gid=f'peak-phone-white-exit-{n}';grads.append(dict(id=gid,type='linear',x1='0%',x2='0%',y1='0%',y2='100%',stops=stops));g.setdefault('children',[]).append(dict(id=f'peak-phone-exit-overlay-{n}',type='rect',x=0,y=-sample(g['keyframes']['y'],n/30),width=1920,height=1080,fill=f'url(#{gid})',start=n/30,end=(n+1)/30))
patch[g['id']]=g
# Reasoning first row begins only once the phone clears; later accepted rows remain unchanged.
r=copy.deepcopy(orig['reason-v5-measured-camera']);r['start']=266/30
for c in r['children']:
 c['end']=361/30
 if c['id']=='early-reasoning-row-0':
  c['start']=266/30;c['keyframes']['opacity']=[dict(t=266/30,value=.08),dict(t=267/30,value=.18),dict(t=268/30,value=.36),dict(t=269/30,value=.65),dict(t=270/30,value=1)];c['keyframes']['blur']=[dict(t=266/30,value=22),dict(t=267/30,value=16),dict(t=268/30,value=10),dict(t=269/30,value=5),dict(t=270/30,value=0)];baseY=sample(c['keyframes']['y'],9);c['keyframes']['y']=[dict(t=n/30,value=baseY+offset) for n,offset in [(266,211.27),(267,192.99),(268,162.10),(269,119.11)]]+c['keyframes']['y']
r['end']=375/30
# Search is an actual large native magnifier that shrinks to a capsule, not an early full query.
search=copy.deepcopy(orig['group-1007']);search['start']=361/30;search['end']=13;search['children']=[];search.pop('keyframes',None);search.update(x=0,y=0,originX=0,originY=0,scaleX=1,scaleY=1,rotation=0,opacity=1)
for n in range(361,375):
 a=ar(n);mask=(a.max(2)<220)&(a.max(2)-a.min(2)<16);cc,lab=comps(mask);large=[(area,i,b) for area,i,b in cc if area>350 and b[2]-b[0]>25 and b[3]-b[1]>25]
 if not large:continue
 maximum=max(q[0] for q in large);chosen=[q for q in large if q[0]>maximum*.12 and (q[2][2]-q[2][0]>50 or q[2][3]-q[2][1]>50)]
 ring=np.isin(lab,[i for area,i,b in chosen]);values=a[ring];v,cnt=np.unique(values.astype('uint8'),axis=0,return_counts=True);fill=v[cnt.argmax()];near=ndimage.binary_dilation(ring,iterations=2);alpha=np.clip((253-a.mean(2))/(253-float(fill.mean())),0,1)*near;dd,stats=trace_alpha(alpha);search['children'].append(dict(id=f'peak-native-magnifier-{n}',type='path',d=dd,fill='#'+''.join(f'{x:02x}' for x in fill),start=n/30,end=(n+1)/30,semanticGraphic='Search magnifier ring and handle',sourceFrame=n,editability='Native vector silhouette; frame-specific local deformation is an editable outline, not analytic circle geometry.'))
 # Only the pale reasoning glyphs inside/behind this element are reconstructed here; dark ring pixels are excluded.
 gray=(a.min(2)>max(140,float(fill.mean())+35))&(a.max(2)<252)&(a.max(2)-a.min(2)<12)&~ndimage.binary_dilation(ring,iterations=1);gc,gl=comps(gray);ids=[i for area,i,b in gc if 2<area<4000 and b[2]-b[0]<180 and b[3]-b[1]<150];sel=np.isin(gl,ids)
 if sel.any():
  vals=a[sel];vv,ct=np.unique(vals.astype('uint8'),axis=0,return_counts=True);f=vv[ct.argmax()];aa=np.clip((253-a.mean(2))/max(1,253-float(f.mean())),0,1)*ndimage.binary_dilation(sel,iterations=1);d,st=trace_alpha(aa);r['children'].append(dict(id=f'peak-reasoning-exit-glyphs-{n}',type='path',d=d,fill='#'+''.join(f'{x:02x}' for x in f),start=n/30,end=(n+1)/30,semanticText='Checking what I know about Photon...;9 people;880 Harrison St;Loves sushi;Offsite tomorrow. What do we need?;A place to stay;Rides;Food;Let me find agents who can help...',sourceFrame=n,editability='Individual pale source glyph contours during the magnifier exit, not live text.'))
 ledger.append(dict(kind='native magnifier and separate reasoning glyph exit',sourceFrame=n,ringComponentBounds=[b for area,i,b in chosen],nativeContourStats=stats))
# The following query reveal is decomposed into its bounded native border and individual original glyph silhouettes.
for n in range(375,390):
 a=ar(n);mask=(a.max(2)<247)&(a.max(2)-a.min(2)<20);cc,lab=comps(mask);group=[]
 for area,i,b in cc:
  l,t,rr,bb=b
  if area<2 or not(420<t<680) or rr<400 or l>1600 or rr-l>1500 or bb-t>180:continue
  # Isolated border/copy components; nothing outside the query's measured central band is traced.
  sel=lab[t:bb,l:rr]==i;roi=a[t:bb,l:rr];vals=roi[sel];vv,ct=np.unique(vals.astype('uint8'),axis=0,return_counts=True);f=vv[ct.argmax()];aa=np.clip((253-roi.mean(2))/max(1,253-float(f.mean())),0,1)*ndimage.binary_dilation(sel,iterations=1);d,st=trace_alpha(aa,l,t);group.append(dict(id=f'peak-query-glyph-{n}-{i}',type='path',d=d,fill='#'+''.join(f'{x:02x}' for x in f),semanticText='Searching the Agent Phone Book...',sourceFrame=n,sourceBounds=b,editability='Native query border/glyph contour; partial original reveal retained.'))
 search['children'].append(dict(id=f'peak-query-reveal-{n}',type='group',children=group,start=n/30,end=(n+1)/30));ledger.append(dict(kind='native individual search border and glyph reveal',sourceFrame=n,componentCount=len(group)))
patch[r['id']]=r;patch[search['id']]=search
(R/'v11-boundary-refinement.json').write_text(json.dumps(dict(replacements=patch,gradients=grads,changed_frames=[[260,389]],provenance=ledger),indent=2));print('v11 boundary roots',list(patch),flush=True)
