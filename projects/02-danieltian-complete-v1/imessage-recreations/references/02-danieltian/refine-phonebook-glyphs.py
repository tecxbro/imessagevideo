"""Refine the brief number-field unfold using measured individual glyph poses."""
from pathlib import Path
import json,copy,hashlib
import numpy as np
from PIL import Image

R=Path('/workspace/imessage-recreations/references/02-danieltian');N=R/'phonebook-native';A=R/'assets/phonebook-glyphs';A.mkdir(exist_ok=True)
scene=json.loads((R/'scene-v6-phonebook.json').read_text());base=np.array(Image.open(N/'14.50.png').convert('RGB'));bg=253
fits=json.loads((N/'early-grid-fit.json').read_text());data={q['t']:(np.array(Image.open(N/f'early-{i:02}.png').convert('RGB')),q['column_spacing'],q['row_centers']) for i,q in enumerate(fits,1)}
data[14.5]=(base,1,[147,278,408,539.5,671,801,931.5]);grays={t:a.mean(2) for t,(a,_,_) in data.items()}
byid={l['id']:l for l in scene['layers']};created=[];proof=[];ledger=[]

def glyphs(gray,r,c,C,centers):
 nominal=(-165 if r%2==0 else 60)+450*c;center=960+(nominal-960)*C;cy=centers[r]
 x0=max(0,round(center-225*C));x1=min(1920,round(center+225*C));y0=max(0,round(cy-26));y1=min(1080,round(cy+26));z=gray[y0:y1,x0:x1]
 peak=max(0,float(bg-np.percentile(z,5)));mask=z<(bg-.28*peak);xs=np.where(mask.sum(0)>=2)[0];spans=[]
 for x in xs:
  if not spans or x>spans[-1][1]+1:spans.append([int(x),int(x)])
  else:spans[-1][1]=int(x)
 result=[]
 for lo,hi in spans:
  # Neighboring phone numbers can enter the cell ROI while the field unfolds.
  # These clipped fragments touch the cell edge; they are not extra target glyphs.
  if lo<=1 or hi>=z.shape[1]-2:continue
  ys=np.where(mask[:,lo:hi+1].any(1))[0]
  if len(ys):result.append([x0+lo,y0+int(ys.min()),x0+hi+1,y0+int(ys.max())+1])
 return result,peak

def keys(pairs):return [dict(t=float(t),value=float(v),ease='linear') for t,v in pairs]
for r in range(7):
 for c in range(1,5 if r%2==0 else 4):
  observations={}
  for t,(_,C,centers) in data.items():observations[t]=glyphs(grays[t],r,c,C,centers)
  counts={t:len(v[0]) for t,v in observations.items()};n=counts[14.5]
  if n<12 or any(v!=n for v in counts.values()):proof.append(dict(row=r,column=c,status='kept original cell',counts=counts));continue
  late=byid.get(f'pb-number-{r}-{c}');early=byid.get(f'pb-early-{r}-{c}')
  if not late or not early:continue
  late_keys=late['keyframes']['opacity'];keep=[k for k in late_keys if k['t']>=14.5];late['keyframes']['opacity']=keys([(13.82,0),(14.4,0)])+keep
  old=early['keyframes']['opacity'];at14=next(k['value'] for k in old if k['t']==14);early['keyframes']['opacity']=keys([(13.82,0),(14,at14),(14.1,0),(14.5,0)])
  for j,box in enumerate(observations[14.5][0]):
   pad=2;crop=[box[0]-pad,box[1]-pad,box[2]+pad,box[3]+pad];raw=base[crop[1]:crop[3],crop[0]:crop[2]].mean(2);peak=observations[14.5][1];alpha=np.uint8(np.clip((bg-raw)/max(1,peak),0,1)*255);pixels=np.zeros((*alpha.shape,4),np.uint8);pixels[:,:,3]=alpha;p=A/f'r{r}-c{c}-glyph{j:02}.png';Image.fromarray(pixels).save(p)
   posx=[];posy=[];scalex=[];scaley=[];opacity=[]
   for t,(boxes,pv) in sorted(observations.items()):
    target=boxes[j];sx=(target[2]-target[0])/(box[2]-box[0]);sy=(target[3]-target[1])/(box[3]-box[1]);posx.append((t,target[0]-pad*sx));posy.append((t,target[1]-pad*sy));scalex.append((t,sx));scaley.append((t,sy));opacity.append((t,pv/bg))
   first=14.1;m=opacity[-1][1];opacity=[(14,0)]+[(t,v) for t,v in opacity if t<=14.4]+[(14.45,.5*m/max(.1,1-.5*m)),(14.5,0)]
   node=dict(type='image',id=f'pb-glyph-r{r}-c{c}-{j}',src=str(p.relative_to(R)),x=crop[0],y=crop[1],width=crop[2]-crop[0],height=crop[3]-crop[1],start=14,end=14.5,keyframes=dict(x=keys(posx),y=keys(posy),scaleX=keys(scalex),scaleY=keys(scaley),opacity=keys(opacity)))
   created.append(node);ledger.append(dict(file=node['src'],source_frame=435,source_bounds=crop,row=r,column=c,glyph_index=j,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),purpose='Individual phone-number glyph artwork; measured poses at14.1–14.5s preserve changing character spacing, not live text.'))
  proof.append(dict(row=r,column=c,status='per-glyph pose refinement',glyphs=n,counts=counts))
scene['layers']+=created
scene['source']['notes']+=' The early phone-number unfold has independently measured per-glyph artwork poses to preserve changing character spacing; bitmap glyphs remain individually transform-editable but are not live text. Source bounds and rejected ambiguous counts are logged.'
out=R/'scene-v6-phonebook-glyphs.json';out.write_text(json.dumps(scene,indent=2));(R/'phonebook-glyph-refinement.json').write_text(json.dumps(dict(output=str(out),changed_frames=[420,434],created_layers=len(created),words=proof,assets=ledger,notice='Diagnostic candidate until native comparison confirms improvement; ambiguous glyph counts retain the prior measured cell.'),indent=2));print(json.dumps(dict(output=str(out),new_glyph_layers=len(created),words_refined=sum(p['status']=='per-glyph pose refinement' for p in proof))))
