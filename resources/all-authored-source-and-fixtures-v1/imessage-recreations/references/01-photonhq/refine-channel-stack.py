from pathlib import Path
from PIL import Image
from scipy import ndimage
import sys,numpy as np,json
sys.path.insert(0,'/workspace/imessage-recreations/references/02-danieltian')
from trace_glyphs import trace_alpha
R=Path('/workspace/imessage-recreations/references/01-photonhq');A=R/'assets/held-art';scene=json.loads((R/'scene-final-v4.json').read_text());records={};ledger=[]
for n in range(44,66):
 a=np.array(Image.open(R/f'assets/held-measure/dense-{n:04d}.png').convert('RGB')).astype(float);mask=(a.max(2)-a.min(2)>50)&(a.min(2)<220)&(a.max(2)>140);mask=ndimage.binary_closing(mask,iterations=3);lab,num=ndimage.label(mask,np.ones((3,3)));boxes=[]
 for s in ndimage.find_objects(lab):
  if not s:continue
  y,x=s;w=x.stop-x.start;h=y.stop-y.start
  if w>25 and h>25 and .6<w/h<1.5:boxes.append((x.start,y.start,x.stop,y.stop))
 records[n]=sorted(boxes,key=lambda b:b[1])
new=[]
for row,name in enumerate(['iMessage','Whatsapp','Telegram','SMS','Email','Phone Call']):
 base=55 if row<5 else 62;b=records[base][row];p=R/f'assets/held-measure/dense-{base:04d}.png';a=np.array(Image.open(p).convert('RGB'));artbox=(b[0]-5,b[1]-5,b[2]+5,min(1080,b[3]+5));dest=A/f'channel-{row}.png';Image.fromarray(a).crop(artbox).save(dest);ch=[dict(id=f'channel-icon-{row}',type='image',src='assets/held-art/'+dest.name,x=artbox[0]-b[0],y=artbox[1]-b[1],width=artbox[2]-artbox[0],height=artbox[3]-artbox[1])]
 x0,y0,x1,y1=b[2]+6,max(0,b[1]-15),min(1920,b[2]+600),min(1080,b[3]+30);alpha=np.clip((253-a[y0:y1,x0:x1].mean(2))/253,0,1);d,stats=trace_alpha(alpha,x0-b[0],y0-b[1]);ch.append(dict(id=f'channel-label-{row}',type='path',d=d,fill='#000000',semanticText=name,sourceFrame=base*3+1,editability='Native source glyph outlines; original source label can be partially wiped.'))
 ms=[];widths=[]
 for n,boxes in records.items():
  # Until6.3 all entered icons retain their original top-to-bottom order. Later remaining icons are the bottom three rows.
  ix=row if n<=63 else row-3
  if ix<0 or ix>=len(boxes):continue
  q=boxes[ix];sx=(q[2]-q[0])/(b[2]-b[0]);sy=(q[3]-q[1])/(b[3]-b[1]);aa=np.array(Image.open(R/f'assets/held-measure/dense-{n:04d}.png').convert('RGB'));xa=q[2]+5;ya=max(0,q[1]-12);xb=min(1920,int(q[2]+600*sx));yb=min(1080,q[3]+25);ink=aa[ya:yb,xa:xb].max(2)<205;ys,xs=np.where(ink);visible=(xs.max()+1+xa-q[0])/sx if len(xs) else (q[2]-q[0])/sx
  ms.append(dict(t=n/10+1/30,x=q[0],y=q[1],scaleX=sx,scaleY=sy));widths.append(dict(t=n/10+1/30,value=float(visible)))
 if not ms:continue
 tracks={k:[dict(t=m['t'],value=m[k]) for m in ms] for k in ['x','y','scaleX','scaleY']}
 # A native clipping rectangle reproduces the observed progressive label wipe.
 label=ch[-1];ch[-1]=dict(id=f'channel-label-clip-{row}',type='group',clip={'x':0,'y':-30,'width':900,'height':220},children=[label],keyframes={'opacity':[dict(t=m['t'],value=1 if w['value']>b[2]-b[0]+10 else 0) for m,w in zip(ms,widths)]})
 # Text clip widths animate on a dedicated group; same measured transform as the corresponding icon.
 ch[-1]['clip']['width']=900
 ch[-1]['keyframes']['scaleX']=[dict(t=w['t'],value=max(1,w['value'])/900) for w in widths]
 label['keyframes']={'scaleX':[dict(t=w['t'],value=900/max(1,w['value'])) for w in widths]}
 new.append(dict(id=f'measured-channel-row-{row}',type='group',children=ch,start=ms[0]['t']-.1,end=ms[-1]['t']+.05,keyframes=tracks,semanticText=name));ledger.append(dict(row=row,semanticText=name,canonicalSourceFrame=base*3+1,sourceBounds=list(b),measurements=ms,labelVisibleWidths=widths,**stats))
scene['layers']=[l for l in scene['layers'] if l['id']!='group-23' and not l['id'].startswith('measured-channel-row-')]+new;(R/'scene-final-v4.json').write_text(json.dumps(scene,indent=2));(R/'channel-stack-provenance.json').write_text(json.dumps(ledger,indent=2));print('Measured independent channel rows',len(new))
