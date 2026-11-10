"""Independent prototype for the short glass-cluster formation; canonical v11 is untouched.
Native title/pill contours + bounded original3D circle artwork, separate from all other UI.
"""
from pathlib import Path
from PIL import Image,ImageDraw
from scipy import ndimage
from trace_glyphs import trace_alpha
import json,numpy as np,copy
R=Path('/workspace/imessage-recreations/references/02-danieltian');D=R/'assets/header-formation-measure';A=R/'assets/header-formation-art';A.mkdir(exist_ok=True);BASE=R/'scene-final-v11.json';s=json.loads(BASE.read_text());N={n['id']:n for n in s['layers']};head=copy.deepcopy(N['group-1077']);fly=copy.deepcopy(N['group-1068']);ledger=[]
def ar(path):return np.array(Image.open(path).convert('RGB')).astype(float)
def greenbox(a):
 mask=(a[:,:,1]>220)&(a[:,:,0]<190)&(a[:,:,2]<150);mask[:,1300:]=False;mask[:,:600]=False;mask[650:]=False;lab,num=ndimage.label(mask,np.ones((3,3)));out=[]
 for sl in ndimage.find_objects(lab):
  yy,xx=sl;w=xx.stop-xx.start;h=yy.stop-yy.start
  if w>25 and h>25:out.append([xx.start,yy.start,xx.stop,yy.stop])
 return max(out,key=lambda b:(b[2]-b[0])*(b[3]-b[1]))
def sample(ks,t):
 ks=sorted(ks,key=lambda q:q['t'])
 if t<=ks[0]['t']:return ks[0]['value']
 for a,b in zip(ks,ks[1:]):
  if t<=b['t']:return a['value']+(b['value']-a['value'])*(t-a['t'])/(b['t']-a['t'])
 return ks[-1]['value']
def state(n,k,t):return sample(n.get('keyframes',{}).get(k,[dict(t=0,value=n.get(k,1 if k.startswith('scale') else 0))]),t)
baseG=greenbox(ar(R/'assets/middle-measure/source-0675.png'));baseW=baseG[2]-baseG[0]
for c in head['children']:c['start']=630/30
for n in range(598,630):
 a=ar(D/f'frame-{n:04d}.png');t=n/30;black=(a.max(2)<180)&(a.max(2)-a.min(2)<22);black[:100]=False;black[700:]=False;black[:,:420]=False;black[:,1500:]=False;counts=black.sum(1);dense=ndimage.binary_closing(counts>max(4,counts.max()*.1),iterations=3);rlab,rnum=ndimage.label(dense);runs=[sl[0] for sl in ndimage.find_objects(rlab)];run=max(runs,key=lambda q:counts[q].sum());black[:max(0,run.start-2)]=False;black[min(1080,run.stop+2):]=False;yy,xx=np.where(black)
 if not len(xx):continue
 l,top,r,bot=int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1);gb=greenbox(a);scale=(gb[2]-gb[0])/baseW;radius=126.5*scale;cx=961.5;cy=(top+bot)/2-134.5*scale;halo=18*scale;cb=[max(0,round(cx-radius-halo)),max(0,round(cy-radius-halo)),min(1920,round(cx+radius+halo)),min(1080,round(cy+radius+halo))];w=cb[2]-cb[0];h=cb[3]-cb[1];img=Image.fromarray(a.astype('uint8')).crop(cb).convert('RGBA');matte=Image.new('L',(w*4,h*4));ImageDraw.Draw(matte).ellipse((0,0,w*4-1,h*4-1),fill=255);img.putalpha(matte.resize((w,h),Image.Resampling.LANCZOS));path=A/f'circle-{n:04d}.png';img.save(path)
 # Native semantic title contours, independent of the original sphere texture.
 roi=a[top:bot,l:r];alpha=np.clip((253-roi.mean(2))/253,0,1);alpha*=ndimage.binary_dilation(black[top:bot,l:r],iterations=1);d,stats=trace_alpha(alpha,l,top);glyph=dict(id=f'formation-title-copy-{n}',type='path',d=d,fill='#000000',semanticText='Team Offsite, Oct 10',sourceFrame=n,sourceBounds=[l,top,r,bot])
 # Native pale backplate silhouette, isolated to the title band; sphere artwork overlays the material overlap.
 pad=round(55*scale);pb=[max(0,l-pad),max(0,top-round(24*scale)),min(1920,r+pad),min(1080,bot+round(26*scale))];reg=a[pb[1]:pb[3],pb[0]:pb[2]];m=(reg.min(2)>200)&(reg.max(2)<250)&(reg.max(2)-reg.min(2)<12);vals=reg[m];v,c=np.unique(vals.astype('uint8'),axis=0,return_counts=True);fill=v[c.argmax()] if len(v) else np.array([240,240,240]);aa=np.clip((253-reg.mean(2))/max(1,253-float(fill.mean())),0,1)*ndimage.binary_dilation(m,iterations=1);pd,ps=trace_alpha(aa,pb[0],pb[1]);plate=dict(id=f'formation-title-plate-{n}',type='path',d=pd,fill='#'+''.join(f'{v:02x}' for v in fill),semanticGraphic='Glass title capsule backplate',sourceFrame=n,sourceBounds=pb)
 circle=dict(id=f'formation-circle-art-{n}',type='image',src=str(path),x=cb[0],y=cb[1],width=w,height=h,sourceFrame=n,sourceBounds=cb,editability='Bounded original glass-cluster3D texture during its short formation; inner logo/material/refraction details are bitmap. Native circle pose and lifetime remain separate from title/background/messages.')
 sx,sy=state(head,'scaleX',t),state(head,'scaleY',t);early=dict(id=f'formation-native-pose-{n}',type='group',x=-state(head,'x',t)/sx,y=-state(head,'y',t)/sy,scaleX=1/sx,scaleY=1/sy,start=t,end=(n+1)/30,children=[plate,glyph,circle]);head['children'].append(early);ledger.append(dict(frame=n,titleBounds=[l,top,r,bot],circleBounds=cb,greenBounds=gb,scale=scale,asset=str(path)))
head['start']=598/30;fly['end']=598/30
p=dict(replacements={'group-1068':fly,'group-1077':head},changed_frames=[[598,629]],provenance=[dict(kind='Independent prototype: local glass-cluster formation',diagnosis='Settled675 inner-logo poses were shown before the source logo orbit finished, overlapping the outgoing flight. Retire flights at598 and pose the circle3D artwork independently from native title/backplate silhouettes only for598–629. All630+ header/chat states are preserved.',measurements=ledger,editability='Native title/backplate vector outlines; original bounded sphere texture has bitmap internal3D logos/refraction and any refracted copy. No complete-frame image or source-video layer.')]);(R/'header-formation-prototype.json').write_text(json.dumps(p,indent=2));s['layers']=[copy.deepcopy(p['replacements'].get(l['id'],l)) for l in s['layers']];(R/'scene-header-formation-prototype.json').write_text(json.dumps(s,indent=2));print('Prepared bounded circle/native title prototype',len(ledger),flush=True)
