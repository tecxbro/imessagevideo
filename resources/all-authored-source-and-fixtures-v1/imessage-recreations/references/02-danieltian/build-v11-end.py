"""Repair measured word birth/settling during the final phone-book phrase.
Only native semantic glyph contours and independently posed original book emoji.
"""
from pathlib import Path
from PIL import Image
from scipy import ndimage
import numpy as np,json,copy
from trace_glyphs import trace_alpha
R=Path('/workspace/imessage-recreations/references/02-danieltian');D=R/'assets/peak-end-every-frame';A=R/'assets/v11-end-art';A.mkdir(exist_ok=True);S=json.loads((R/'scene-combined-v10.json').read_text());orig={l['id']:l for l in S['layers']};children=[];poses=[];ledger=[]
def ar(n):return np.array(Image.open(D/f'source-{n:04d}.png').convert('RGB')).astype(float)
def bookbox(a):
 color=(a.max(2)-a.min(2)>22)&(a.min(2)<220);color[:420]=False;color[700:]=False;lab,num=ndimage.label(ndimage.binary_dilation(color,iterations=3),np.ones((3,3)));out=[]
 for i,sl in enumerate(ndimage.find_objects(lab),1):
  if not sl:continue
  y,x=sl;w=x.stop-x.start;h=y.stop-y.start
  if 10<w<160 and 10<h<160:out.append([x.start,y.start,x.stop,y.stop])
 return max(out,key=lambda b:(b[2]-b[0])*(b[3]-b[1])) if out else None
base=bookbox(ar(1080));base=[base[0]-4,base[1]-4,base[2]+4,base[3]+4];path=A/'original-book-emoji.png';Image.fromarray(ar(1080).astype('uint8')).crop(base).save(path)
for n in range(1030,1130):
 a=ar(n);bb=bookbox(a);mask=(a.max(2)-a.min(2)<25)&(a.max(2)<230);mask[:400]=False;mask[950:]=False
 if bb:mask[max(0,bb[1]-7):bb[3]+7,max(0,bb[0]-7):bb[2]+7]=False;poses.append(dict(t=n/30,x=bb[0]-4,y=bb[1]-4,scaleX=(bb[2]-bb[0]+8)/(base[2]-base[0]),scaleY=(bb[3]-bb[1]+8)/(base[3]-base[1])))
 yy,xx=np.where(mask)
 if not len(xx):continue
 l,t,r,b=int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1);roi=a[t:b,l:r];sel=mask[t:b,l:r];vals=roi[sel];v,c=np.unique(vals.astype('uint8'),axis=0,return_counts=True);fill=v[c.argmax()];alpha=np.clip((253-roi.mean(2))/max(1,253-float(fill.mean())),0,1)*ndimage.binary_dilation(sel,iterations=1);d,stats=trace_alpha(alpha,l,t);children.append(dict(id=f'peak-end-copy-{n}',type='path',d=d,fill='#'+''.join(f'{x:02x}' for x in fill),start=n/30,end=(n+1)/30,semanticText='Your iMessage agent now has a phone book.',sourceFrame=n,sourceBounds=[l,t,r,b],editability='Native per-frame semantic glyph contours preserve word entrance/settling; shapes are editable but not live font text.'));ledger.append(dict(sourceFrame=n,sourceBounds=[l,t,r,b],**stats))
if poses:children.append(dict(id='peak-book-emoji-pose',type='group',children=[dict(id='peak-book-original-emoji',type='image',src=str(path),width=base[2]-base[0],height=base[3]-base[1],sourceFrame=1080,sourceBounds=base)],start=poses[0]['t'],end=1130/30,keyframes={k:[dict(t=m['t'],value=m[k]) for m in poses] for k in ['x','y','scaleX','scaleY']}))
p=dict(replacements={'text-1159-outlined':dict(id='text-1159-outlined',type='group',children=children,start=1030/30,end=1130/30),'group-1163':dict(id='group-1163',type='group',children=[],start=35.3,end=37.65)},changed_frames=[[1030,1129]],provenance=[dict(kind='Native phone-book phrase word entrance and settling after v10 peak diagnosis',semanticText='Your iMessage agent now has a phone book.',glyphMeasurements=ledger,bookSourceFrame=1080,bookSourceBounds=base,bookPoses=poses,diagnosis='A single held36s outline had prematurely revealed later words and ignored the continuing camera/word settling. Source/native peak35.9 showed an approximately24px translation error. Use measured per-frame native glyph contours and independent original emoji pose; no complete source-frame image or source-video layer.')]);(R/'v11-end-refinement.json').write_text(json.dumps(p,indent=2));print('Prepared native end word states',len(ledger),'book poses',len(poses),flush=True)
