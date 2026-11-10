from pathlib import Path
import json,copy,hashlib
import numpy as np
from PIL import Image,ImageDraw
from scipy import ndimage

ROOT=Path('/workspace/imessage-recreations');REF=ROOT/'references/02-danieltian';N=REF/'phonebook-native';AS=REF/'assets/phonebook-measured';AS.mkdir(exist_ok=True)
base=np.array(Image.open(N/'14.50.png').convert('RGB'));final=Image.open(N/'17.50.png').convert('RGB');bg=253
times=[13.7,14,14.5,15,15.5,16,16.5,16.8,17,17.2,17.4]
frames={t:np.array(Image.open(N/f'track-{i:02}.png').convert('RGB')) for i,t in enumerate(times,1)};frames[17.5]=np.array(final)
for i,t in enumerate([14.1,14.2,14.3,14.4],1):frames[t]=np.array(Image.open(N/f'early-{i:02}.png').convert('RGB'))
gray_frames={t:a.mean(2) for t,a in frames.items()}
ledger=[]

def save_art(name,image,frame,box,purpose):
 p=AS/(name+'.png');image.save(p);ledger.append(dict(file=str(p.relative_to(REF)),source_frame=frame,source_bounds=box,purpose=purpose,sha256=hashlib.sha256(p.read_bytes()).hexdigest()));return str(p.relative_to(REF))
def img(id,src,x,y,w,h,**kw):return dict(type='image',id='pb-'+id,src=src,x=x,y=y,width=w,height=h,**kw)
def track(pairs):return [dict(t=float(t),value=float(v),ease='linear') for t,v in pairs]
def rows_for(a):
 g=a.mean(2);m=g<245;ys=np.where(m.sum(1)>15)[0];runs=[]
 for y in ys:
  if not runs or y>runs[-1][1]+4:runs.append([int(y),int(y)])
  else:runs[-1][1]=int(y)
 return [q for q in runs if q[1]-q[0]>20]

# The source animates spacing independently of glyph size, rather than a uniform camera.
poses=[(13.82,.54,.28,.70,1),(14,.777,.737,.865,1),(14.5,1,1,1,1),(15,1.095,1.014,1.013,1),(15.5,1.15,1.025,1.026,1),(16,1.177,1.035,1.034,1),(16.5,1.195,1.041,1.039,1),(16.8,1.2,1.043,1.04,1),(17,1.2,1.043,1.04,1)]
early_fit=json.loads((N/'early-grid-fit.json').read_text())
for q,fx in zip(early_fit,[.905,.945,.975,.995]):poses.append((q['t'],q['column_spacing'],(540-q['row_centers'][0])/(540-147),fx,1))
poses.sort()
row_samples={14:[249.5,331.5,430,539.5,649,745.5,827.5],14.5:[147,278,408,539.5,671,801,931.5]}
row_samples.update({q['t']:q['row_centers'] for q in early_fit})
def row_y(r,t,fallback):
 keys=sorted(row_samples)
 if t<keys[0] or t>keys[-1]:return fallback
 for a,b in zip(keys,keys[1:]):
  if a<=t<=b:
   p=(t-a)/(b-a);return row_samples[a][r]*(1-p)+row_samples[b][r]*p
 return row_samples[keys[-1]][r]
def pose_at(t):
 for a,b in zip(poses,poses[1:]):
  if a[0]<=t<=b[0]:
   p=(t-a[0])/(b[0]-a[0]);return tuple(a[j]+p*(b[j]-a[j]) for j in range(1,5))
 return poses[0][1:] if t<poses[0][0] else poses[-1][1:]

nums=[];g=base.mean(2);mask=g<244;rowbounds=[(125,169),(256,300),(387,429),(519,560),(650,692),(779,823),(909,954)]
for r,(y0,y1) in enumerate(rowbounds):
 xs=np.where(mask[y0:y1+1].any(0))[0];spans=[]
 for x in xs:
  if not spans or x>spans[-1][1]+30:spans.append([int(x),int(x)])
  else:spans[-1][1]=int(x)
 cy=(y0+y1)/2
 for c,(x0,x1) in enumerate(spans):
  pad=2;box=[max(0,x0-pad),y0-pad,min(1920,x1+pad+1),y1+pad+1];a=base[box[1]:box[3],box[0]:box[2]].astype(float);ink=np.maximum(0,bg-a.mean(2));peak=max(1,float(np.percentile(ink[ink>4],90)));alpha=np.uint8(np.clip(ink/peak,0,1)*255);rgba=np.zeros((*alpha.shape,4),np.uint8);rgba[:,:,3]=alpha
  src=save_art(f'number-r{r}-c{c}',Image.fromarray(rgba),435,box,'Individual original phone-number glyph artwork; internal copy is bitmap, not live text.')
  nominal=(-165 if r%2==0 else 60)+450*c;w,h=box[2]-box[0],box[3]-box[1]
  positions=[];ys=[];sx=[];sy=[];opacity=[]
  for t,C,Y,Fx,Fy in poses:
   px=960+(nominal-960)*C+(box[0]-nominal)*Fx;py=row_y(r,t,540+(cy-540)*Y)+(box[1]-cy)*Fy
   positions.append((t,px));ys.append((t,py));sx.append((t,Fx));sy.append((t,Fy))
   if t in frames and t>=14:
    target=gray_frames[t];aw=max(1,round(w*Fx));ah=max(1,round(h*Fy));aa=np.asarray(Image.fromarray(alpha).resize((aw,ah),Image.Resampling.BILINEAR)).astype(float)/255
    roi_x,roi_y=round(px),round(py);xa,ya=max(0,roi_x),max(0,roi_y);xb,yb=min(1920,roi_x+aw),min(1080,roi_y+ah)
    if xb>xa and yb>ya:
     sub=target[ya:yb,xa:xb];ink=np.clip(bg-sub,0,bg)
     if t>=16:ink=np.where(sub>160,ink,0)
     den=aa[ya-roi_y:yb-roi_y,xa-roi_x:xb-roi_x].sum()*bg
     value=float(np.clip(ink.sum()/max(1,den),0,1))
    else:value=peak/bg
    if t<14.5:value*=max(0,min(1,(t-14)/.5))
   else:value=0 if t<=13.82 or t>=17 else peak/bg
   opacity.append((t,value))
  # Preserve the exact base-frame alpha, then fade the original field before the result stack.
  opacity=[(t,peak/bg if t==14.5 else v) for t,v in opacity];opacity.append((17.05,0))
  nums.append(img(f'number-{r}-{c}',src,box[0],box[1],w,h,start=13.82,end=17.05,keyframes={'x':track(positions),'y':track(ys),'scaleX':track(sx),'scaleY':track(sy),'opacity':track(opacity)}))

# Early field uses different character spacing; scaling the later word textures cannot
# reproduce that shape. Independently bounded cell artwork preserves the earlier state.
early=[];early_image=Image.fromarray(frames[14]);early_rows=[(228,271),(311,352),(410,450),(520,559),(628,670),(724,767),(804,851)]
for r,(y0,y1) in enumerate(early_rows):
 cy=(y0+y1)/2
 for c in range(-1,7):
  nominal=(-165 if r%2==0 else 60)+450*c;center14=960+(nominal-960)*.777
  x0=max(0,round(center14-450*.777/2));x1=min(1920,round(center14+450*.777/2))
  if x1<=x0:continue
  box=[x0,max(0,y0-2),x1,min(1080,y1+3)];src=save_art(f'early-r{r}-c{c}',early_image.crop(box),420,box,'Bounded original number-field cell; preserves earlier character spacing, individually animated, bitmap internal copy.')
  xx=[];yy=[];sx=[];op=[];source_gray=np.asarray(early_image.crop(box).convert('L')).astype(float);source_ink=np.clip(bg-source_gray,0,bg);core_ink=source_ink[source_ink>4];p0=float(np.percentile(core_ink,90)/bg) if core_ink.size else .2
  for t,C,Y,Fx,Fy in poses:
   if t>14.5:break
   ratio=Fx/.865;px=960+(nominal-960)*C+(x0-center14)*ratio;py=row_y(r,t,540+(cy-540)*Y/.737)+(box[1]-cy)
   xx.append((t,px));yy.append((t,py));sx.append((t,ratio))
   if t in gray_frames and t>=14:
    aw=max(1,round((x1-x0)*ratio));ah=box[3]-box[1];temp=np.asarray(early_image.crop(box).convert('L').resize((aw,ah),Image.Resampling.BILINEAR)).astype(float);ix,iy=round(px),round(py);xa,ya=max(0,ix),max(0,iy);xb,yb=min(1920,ix+aw),min(1080,iy+ah)
    mass=np.clip(bg-gray_frames[t][ya:yb,xa:xb],0,bg).sum();reference_mass=np.clip(bg-temp[ya-iy:yb-iy,xa-ix:xb-ix],0,bg).sum();ratio_mass=mass/max(1,reference_mass);m=min(1,ratio_mass*p0);lam=max(0,min(1,(t-14)/.5));value=float(np.clip((1-lam)*ratio_mass/max(.05,1-lam*m),0,1))
   else:value=0
   op.append((t,value))
  early.append(img(f'early-{r}-{c}',src,x0,box[1],x1-x0,box[3]-box[1],start=13.82,end=14.5,keyframes={'x':track(xx),'y':track(yy),'scaleX':track(sx),'opacity':track(op)}))

# Retain the exact controlled UI body but expose each agent/camera/control independently.
capsules=[];cap_templates={};caps=[('Lyft',(658,431,1262,548)),('Airbnb',(658,581,1262,698)),('Resy',(658,731,1262,848))]
plus=np.array(Image.open(REF/'keyframes/16.50.png').convert('RGB'))[241:294,619:672];plus_src=save_art('plus',Image.fromarray(plus),495,[619,241,672,294],'Original plus control artwork in independent editable layer.')
check_src=save_art('green-check',final.crop((1161,452,1239,531)),525,[1161,452,1239,531],'Original checked-control artwork in independent editable layer.')

def capsule_boxes(a):
 g=a.mean(2);m=(g>185)&(g<247);lab,n=ndimage.label(m);found=[]
 for v,b in enumerate(ndimage.find_objects(lab),1):
  if b is None:continue
  yy,xx=b;w=xx.stop-xx.start;h=yy.stop-yy.start
  if 400<w<900 and 65<h<170:found.append([xx.start,yy.start,w,h])
 return found
def color_center(a,name):
 R,G,B=a[:,:,0],a[:,:,1],a[:,:,2]
 if name=='Lyft':m=(R>150)&(G<100)&(B>130)
 elif name=='Airbnb':m=(R>170)&(G<115)&(B>65)&(B<170)
 else:m=(R>170)&(G<100)&(B<90)
 lab,n=ndimage.label(m);best=None
 for v,b in enumerate(ndimage.find_objects(lab),1):
  if b is None:continue
  yy,xx=b;w=xx.stop-xx.start;h=yy.stop-yy.start
  if 25<w<120 and 25<h<120:
   score=np.count_nonzero(lab[b]==v)
   if best is None or score>best[0]:best=(score,(xx.start+xx.stop)/2,(yy.start+yy.stop)/2)
 return best[1:] if best else None

cap_measures={}
for name,box in caps:
 art=final.crop(box);d=ImageDraw.Draw(art);d.ellipse((495,13,587,108),fill=(253,253,253));src=save_art('capsule-'+name.lower(),art,525,list(box),'Original bounded agent capsule artwork, checked control removed; capsule transform and controls animate independently.')
 pts=[]
 for t in times+[17.5]:
  if t<15:continue
  a=frames[t];center=color_center(a,name)
  if center:
   candidates=[q for q in capsule_boxes(a) if q[0]<=center[0]<=q[0]+q[2] and q[1]<=center[1]<=q[1]+q[3]]
   if candidates:
    q=min(candidates,key=lambda q:abs(q[2]-600)+abs(q[3]-115));x,y,w,h=q
   else:x,y,w,h=center[0]-60,center[1]-60,604,117
   pts.append((t,float(x),float(y),float(w/604),float(h/117)))
 if not pts:raise RuntimeError('No measured capsule '+name)
 cap_measures[name]=pts
 # Logos become visible in the original around15.3s; source results are held until the measured17s collapse.
 st=max(15.1,pts[0][0]-.12);end=18.35
 keys={k:track([(st,pts[0][j])]+[(v[0],v[j]) for v in pts]+[(18.2,pts[-1][j])]) for k,j in [('x',1),('y',2),('scaleX',3),('scaleY',4)]}
 keys['opacity']=track([(st,0),(st+.1,1),(18.15,1),(end,0)])
 # Independent checked-state timing; native controls preserve the source selection sequence.
 at={'Lyft':17.17,'Airbnb':17.0,'Resy':17.27}[name]
 children=[img(name.lower()+'-body',src,0,0,604,117),img(name.lower()+'-plus',plus_src,511,31,53,53,keyframes={'opacity':track([(st,1),(at-.08,1),(at,0)])}),img(name.lower()+'-check',check_src,503,21,78,79,keyframes={'opacity':track([(st,0),(at-.03,0),(at+.08,1)]),'scaleX':track([(st,.15),(at-.03,.15),(at+.1,1)]),'scaleY':track([(st,.15),(at-.03,.15),(at+.1,1)])},originX=39,originY=39)]
 capsules.append(dict(type='group',id='pb-capsule-'+name.lower(),start=st,end=end,children=children,keyframes=keys))

# A faded fourth provider is present in the source field but is not selected.
ghost=Image.open(REF/'keyframes/16.50.png').convert('RGB').crop((1203,211,1800,328));ghost_src=save_art('uber-eats-ghost',ghost,495,[1203,211,1800,328],'Bounded original unselected Uber Eats capsule artwork.')
capsules.insert(0,img('uber-eats',ghost_src,1203,211,597,117,start=15.45,end=16.85,keyframes={'opacity':track([(15.45,0),(15.65,1),(16.5,1),(16.85,0)])}))
search_src=save_art('result-search',final.crop((415,274,1506,396)),525,[415,274,1506,396],'Original bounded search capsule artwork; bitmap internal copy disclosed.')
result_search=img('result-search',search_src,415,274,1091,122,start=17.15,end=18.35,keyframes={'opacity':track([(17.15,0),(17.45,1),(18.15,1),(18.35,0)])})

basepath=REF/'scene-v5-ui.json';scene=json.loads(basepath.read_text());removed=[];kept=[]
for l in scene['layers']:
 cs=l.get('children',[]);text_values=[q.get('text') for q in cs if q.get('type')=='text']
 is_numbers=len(cs)==35 and cs and str(cs[0].get('text','')).startswith('+1 (')
 is_agent=l.get('type')=='group' and any(v in ['Lyft','Airbnb','Resy'] for v in text_values) and 15<=l.get('start',0)<16
 if is_numbers or is_agent:removed.append(l['id'])
 else:kept.append(l)
scene['layers']=kept+early+nums+capsules+[result_search]
scene['source']['notes']+=' Phone-book refinement uses individually declared original phone-number/capsule artwork; internal bitmap copy is not live text. Independent native layout spacing, glyph scale, capsule poses, controls and lifetimes are measured from source frames; no source-video or full-frame asset is used. Early edge clipping and intermediate flips remain measured approximations.'
out=REF/'scene-v6-phonebook.json';out.write_text(json.dumps(scene,indent=2));(REF/'phonebook-refinement.json').write_text(json.dumps(dict(base=str(basepath),output=str(out),removed_node_ids=removed,added_node_ids=[l['id'] for l in early+nums+capsules+[result_search]],changed_frame_ranges=[[409,550]],capsule_measurements=cap_measures,grid_pose_columns=['t','column_spacing','row_spacing','glyph_x_scale','glyph_y_scale'],grid_poses=poses,assets=ledger,notice='Measured prototype pending native frame comparison; bitmap internal copy is declared, not live text.'),indent=2));print(json.dumps(dict(output=str(out),removed=removed,numbers=len(nums),early_cells=len(early)),indent=2))
