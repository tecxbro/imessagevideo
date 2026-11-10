"""Bounded original rich-card texture poses only for its short local spring.
The scene keeps source-native card positions and independent sender/avatar/header.
"""
from pathlib import Path
from PIL import Image,ImageDraw
from scipy import ndimage
import json,copy,numpy as np
R=Path('/workspace/imessage-recreations/references/02-danieltian');P=R/'v11-middle-refinement.json';p=json.loads(P.read_text());N={n['id']:n for n in p['replacements']['group-1118']['children']};card=N['middle-airbnb-rich-card'];old=copy.deepcopy(card);A=R/'assets/v11-card-local-textures';A.mkdir(exist_ok=True);RUN=json.loads((R/'middle-body-runs.json').read_text());camera=[dict(t=int(k)/30,value=v['scale']) for k,v in RUN.items()];header=p['replacements']['group-1077'];children=[];records=[];base=Image.open(card['children'][0]['src']).convert('RGB')
def sample(ks,t):
 ks=sorted(ks,key=lambda q:q['t'])
 if t<=ks[0]['t']:return ks[0]['value']
 for a,b in zip(ks,ks[1:]):
  if t<=b['t']:return a['value']+(b['value']-a['value'])*(t-a['t'])/(b['t']-a['t'])
 return ks[-1]['value']
def st(node,k,t):return sample(node.get('keyframes',{}).get(k,[dict(t=0,value=node.get(k,1 if k.startswith('scale') else 0))]),t)
for n in range(838,871):
 t=n/30;a=Image.open(R/'assets/middle-every-frame'/f'source-{n:04d}.png').convert('RGB');aa=np.array(a).astype(float)
 if n>=843:
  l=round(st(old,'x',t));top=round(st(old,'y',t));w=round(old['children'][0]['width']*st(old,'scaleX',t));h=round(old['children'][0]['height']*st(old,'scaleY',t));box=[l,top,l+w,top+h]
 else:
  left=960-543*sample(camera,t);l0=max(0,int(left-8));r0=min(1920,int(left+450));y0=650;roi=aa[y0:,l0:r0];m=(roi.max(2)-roi.min(2)>12)&(roi.min(2)<235);lab,num=ndimage.label(ndimage.binary_closing(m,iterations=3),np.ones((3,3)));cc=[]
  for sl in ndimage.find_objects(lab):
   yy,xx=sl;w=xx.stop-xx.start;h=yy.stop-yy.start
   if w>12 and h>12:cc.append([xx.start+l0,yy.start+y0,xx.stop+l0,yy.stop+y0])
  if not cc:continue
  b=max(cc,key=lambda b:(b[2]-b[0])*(b[3]-b[1]));box=[max(l0,b[0]-15),max(y0,b[1]-15),min(r0,b[2]+15),min(1080,b[3]+15)];l,top,r,bot=box;w=r-l;h=bot-top
 texture=a.crop(box);matte=Image.new('L',(w,h));draw=ImageDraw.Draw(matte)
 def hb(b):return tuple([b[0]*st(header,'scaleX',t)+st(header,'x',t)-l,b[1]*st(header,'scaleY',t)+st(header,'y',t)-top,b[2]*st(header,'scaleX',t)+st(header,'x',t)-l,b[3]*st(header,'scaleY',t)+st(header,'y',t)-top])
 draw.ellipse(hb((835,46,1088,300)),fill=255);draw.rounded_rectangle(hb((690,258,1230,358)),radius=max(1,49*st(header,'scaleX',t)),fill=255)
 if matte.getbbox():texture.paste(base.resize((w,h),Image.Resampling.LANCZOS),(0,0),matte)
 path=A/f'card-spring-{n:04d}.png';texture.save(path);children.append(dict(id=f'v11-card-local-pose-{n}',type='group',x=l,y=top,start=t,end=(n+1)/30,children=[dict(id=f'v11-card-local-art-{n}',type='image',src=str(path),width=w,height=h,sourceFrame=n,sourceBounds=box,editability='Bounded original rich-link artwork for its brief local spring; bitmap internal text/texture, independently editable native pose.')]))
 records.append(dict(sourceFrame=n,sourceBounds=box,asset=str(path),hiddenHeaderUnderlayInferred=bool(matte.getbbox())))
held=copy.deepcopy(old);held['id']='v11-card-held-native-pose';held['start']=871/30;children.append(held);card.clear();card.update(id='middle-airbnb-rich-card',type='group',children=children,start=min(x['start'] for x in children),end=33.3,editability='Native independently posed rich-card layout. Brief838–870 local texture sequence preserves original UI deformation; held card after871 uses one authentic static artwork.')
p['provenance'].append(dict(kind='bounded local rich-link texture sequence',diagnosis='v11 rectangular affine fitting closed placement, but the photo/white panel/footer deform separately during the short original spring. Preserve original bounded card textures for838–870, never complete reference frames; sender/avatar/header remain independent native layers. Original header-covered underlay uses the declared clean held card.',poses=records));P.write_text(json.dumps(p,indent=2));print('Declared local card texture poses',len(records),flush=True)
