from pathlib import Path
import subprocess,json,numpy as np,math
from PIL import Image
R=Path('/workspace/imessage-recreations/references/01-photonhq');A=R/'assets/wall-art';A.mkdir(parents=True,exist_ok=True)
# Integer source frame indices; each measured output timestamp is n/30.
phases=[dict(name='sms',start=7.95,end=9.9,nominal_start=8.2,nominal_end=9.5,base=270,frames=list(range(240,301,3))),dict(name='calls',start=10.35,end=12.1,nominal_start=10.666667,nominal_end=11.666667,base=336,frames=list(range(312,364,3))),dict(name='imessage',start=11.35,end=13.4,nominal_start=11.666667,nominal_end=12.966667,base=372,frames=list(range(342,405,3))),dict(name='whatsapp',start=12.65,end=14.6,nominal_start=12.966667,nominal_end=14.2,base=408,frames=list(range(378,441,3))),dict(name='telegram',start=13.95,end=15.8,nominal_start=14.2,nominal_end=15.5,base=444,frames=list(range(420,475,3)))]
frames=sorted(set(sum([p['frames']+[p['base']] for p in phases],[])))
cache=A/'measure';cache.mkdir(exist_ok=True)
missing=[n for n in frames if not (cache/f'{n:04d}.png').exists()]
if missing:
 filt='select='+ '+'.join(f'eq(n\\,{n})' for n in missing)
 subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(R/'source.mp4'),'-vf',filt,'-vsync','0','-threads','1',str(cache/'extract-%03d.png')],check=True)
 for i,n in enumerate(missing,1):(cache/f'extract-{i:03d}.png').rename(cache/f'{n:04d}.png')

def components(im):
 ar=np.asarray(im);mask=ar[:,:,:3].min(2)<246;mask[450:640,:]=False
 # Run-length component labeling. Same bubble body remains connected around white glyph holes.
 parent=[];bounds=[];area=[];prior=[]
 def find(x):
  while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
  return x
 def union(a,b):
  a,b=find(a),find(b)
  if a!=b:parent[b]=a
 for y,line in enumerate(mask):
  v=np.diff(np.r_[False,line,False].astype(np.int8));starts=np.flatnonzero(v==1);ends=np.flatnonzero(v==-1);cur=[];j=0
  for x0,x1 in zip(starts,ends):
   idx=len(parent);parent.append(idx);bounds.append([int(x0),y,int(x1),y+1]);area.append(int(x1-x0));cur.append((int(x0),int(x1),idx))
   while j<len(prior) and prior[j][1]<x0:j+=1
   q=j
   while q<len(prior) and prior[q][0]<=x1:
    if prior[q][1]>=x0:union(idx,prior[q][2])
    q+=1
  prior=cur
 groups={}
 for i,b in enumerate(bounds):
  root=find(i)
  if root not in groups:groups[root]=b+[area[i]]
  else:
   g=groups[root];g[0]=min(g[0],b[0]);g[1]=min(g[1],b[1]);g[2]=max(g[2],b[2]);g[3]=max(g[3],b[3]);g[4]+=area[i]
 out=[]
 for b in groups.values():
  x0,y0,x1,y1,n=b;w=x1-x0;h=y1-y0
  if (n>1600 and w>65 and h>35) or ((y0<3 or y1>1077) and n>200 and w>30 and h>1):
   box=(max(0,x0-2),max(0,y0-2),min(1920,x1+2),min(1080,y1+2));tile=im.crop(box)
   out.append(dict(box=box,area=n,w=box[2]-box[0],h=box[3]-box[1],finger=np.asarray(tile.resize((96,28),Image.Resampling.BILINEAR),dtype=np.float32)/255))
 return sorted(out,key=lambda q:(q['box'][1],q['box'][0]))

ims={n:Image.open(cache/f'{n:04d}.png').convert('RGB') for n in frames};comps={n:components(im) for n,im in ims.items()}
ledger=[];new=[];diagnostics={}
for ph in phases:
 base=ph['base'];bc=comps[base]
 # Cluster corresponding row centers. Edge-clipped rows are retained independently.
 rows=[]
 for co in bc:
  cy=(co['box'][1]+co['box'][3])/2
  row=next((r for r in rows if abs(r['cy']-cy)<55),None)
  if row is None:row={'cy':cy,'components':[]};rows.append(row)
  row['components'].append(co)
 diagnostics[ph['name']]={'base_frame':base,'rows':[]}
 # Estimate affine component correspondence and uniform scale per row, at each measured moment.
 for ri,row in enumerate(rows):
  children=[]
  for ci,co in enumerate(row['components']):
   box=co['box'];name=f"{ph['name']}-row{ri}-bubble{ci}.png";ims[base].crop(box).save(A/name)
   children.append(dict(id=f"art-{ph['name']}-{ri}-{ci}",type='image',src='assets/wall-art/'+name,x=box[0],y=box[1],width=co['w'],height=co['h']))
   ledger.append(dict(asset='assets/wall-art/'+name,source_frame=base,source_time=base/30,pixel_box=box,kind='single original static bubble/call-strip artwork; bitmap text; independently animated'))
  measurements=[]
  for n in ph['frames']:
   matches=[]
   for co in row['components']:
    x0,y0,x1,y1=co['box']
    if x0<5 or x1>1915 or y0<4 or y1>1076:continue
    candidates=[]
    for other in comps[n]:
     ox0,oy0,ox1,oy1=other['box'];ratio=other['w']/co['w'];hr=other['h']/co['h']
     if ox0<5 or ox1>1915 or oy0<4 or oy1>1076:continue
     if not(.65<ratio<1.45 and .7<hr<1.4 and abs(hr-ratio)<.12):continue
     if abs((oy0+oy1)/2-(y0+y1)/2)>110:continue
     if abs((ox0+ox1)/2-(x0+x1)/2)>750*abs(n-base)/30+80:continue
     err=float(np.mean((co['finger']-other['finger'])**2))
     candidates.append((err,other))
    if candidates:
     err,other=min(candidates,key=lambda q:q[0])
     if err<.005:
      matches.append(dict(err=err,base=co,other=other))
   if matches:
    matches=sorted(matches,key=lambda q:q['err'])[:4]
    matches=[m for m in matches if m['err']<=matches[0]['err']*3+.0005]
    ss=float(np.median([m['other']['w']/m['base']['w'] for m in matches]))
    tx=float(np.median([m['other']['box'][0]-ss*m['base']['box'][0] for m in matches]));ty=float(np.median([m['other']['box'][1]-ss*m['base']['box'][1] for m in matches]))
    measurements.append(dict(t=n/30,scale=ss,x=tx,y=ty,matches=len(matches),error=float(np.mean([m['err'] for m in matches]))))
  if not any(abs(m['t']-base/30)<.001 for m in measurements):measurements.append(dict(t=base/30,scale=1,x=0,y=0,matches=0,error=0))
  measurements.sort(key=lambda m:m['t'])
  # Low-evidence edge rows borrow robust scale/velocity from interior row later.
  row['measurements']=measurements;row['children']=children;row['direct_measurements']=[dict(m) for m in measurements if m.get('matches',0)>0]
 for ri,row in enumerate(rows):
  ms=row['measurements']
  if len(ms)<3:
   donor=max(rows,key=lambda r:len(r['measurements']));ms=[dict(m) for m in donor['measurements']]
  # Remove implausible jumps caused by matching a different same-colored bubble.
  clean=[]
  for m in ms:
   if abs(m['scale']-1)>.3:continue
   if abs(m['t']-base/30)>.001:
    peers=[q for rr in rows for q in rr['measurements'] if abs(q['t']-m['t'])<.001 and q.get('error',1)<.005]
    if peers and (abs(m['scale']-float(np.median([q['scale'] for q in peers])))>.025 or abs(m['x']-float(np.median([q['x'] for q in peers])))>100):continue
   clean.append(m)
  ms=clean or [dict(t=base/30,scale=1,x=0,y=0,matches=0,error=0)]
  if not any(abs(m['t']-base/30)<.001 for m in ms):ms.append(dict(t=base/30,scale=1,x=0,y=0,matches=0,error=0));ms.sort(key=lambda m:m['t'])
  def extrapolate(t,left):
   if len(ms)<2:return dict(t=t,scale=1,x=0,y=0)
   a,b=(ms[0],ms[1]) if left else (ms[-2],ms[-1]);fac=(t-a['t'])/(b['t']-a['t']);return dict(t=t,**{p:a[p]+fac*(b[p]-a[p]) for p in ['scale','x','y']})
  if ms[0]['t']>ph['start']+.001:ms.insert(0,extrapolate(ph['start'],True))
  if ms[-1]['t']<ph['end']-.001:ms.append(extrapolate(ph['end'],False))
  tracks={p:[dict(t=m['t'],value=m[v],ease='linear') for m in ms] for p,v in [('x','x'),('y','y'),('scaleX','scale'),('scaleY','scale')]}
  direct=[m for m in row['direct_measurements'] if m.get('error',1)<.005]
  if len(direct)<2:direct=[m for m in ms if m.get('matches',0)>0 and m.get('error',1)<.005]
  first=min((m['t'] for m in direct),default=base/30);last=max((m['t'] for m in direct),default=base/30)
  visible_start=max(ph['start'],min(ph['nominal_start'],first-.18));visible_end=min(ph['end'],max(ph['nominal_end'],last+.18))
  tracks['opacity']=[dict(t=visible_start,value=0),dict(t=first,value=1,ease='easeOut'),dict(t=last,value=1),dict(t=visible_end,value=0,ease='easeIn')]
  tracks['blur']=[dict(t=visible_start,value=11),dict(t=first,value=0,ease='easeOut'),dict(t=last,value=0),dict(t=visible_end,value=11,ease='easeIn')]
  new.append(dict(id=f"wall-art-{ph['name']}-row{ri}",type='group',start=visible_start,end=visible_end,children=row['children'],keyframes=tracks))
  diagnostics[ph['name']]['rows'].append(dict(row=ri,base_center_y=row['cy'],component_count=len(row['children']),measurements=ms,direct_measurements=row['direct_measurements'],visible_start=visible_start,visible_end=visible_end))

scene=json.loads((R/'scene.json').read_text());layers=scene['layers']
# Remove only previous approximate SMS/call/iMessage/WhatsApp/Telegram native walls. Native center titles remain.
intervals={(8.2,9.55),(10.666667,11.7),(11.666667,12.98),(12.966667,14.23),(14.2,15.53)}
removed=[];retained=[]
for l in layers:
 if l.get('type')=='group' and (l.get('start'),l.get('end')) in intervals:
  removed.append(l['id'])
 else:retained.append(l)
# Layer order: all wall artwork behind native titles; phases don't overlap except boundary blends.
scene['layers']=new+retained
scene['source']['notes'] += ' Hybrid wall refinement: individual original static bubble/call-strip artwork, including bitmap text, segmented from declared base frames. Per-row translation/scale fitted by component correspondence across measured source frames; no full-frame image layers or source-video playback.'
(R/'scene-wall-v4.json').write_text(json.dumps(scene,indent=2));(R/'wall-art-provenance.json').write_text(json.dumps({'assets':ledger,'removed_old_wall_layers':removed,'changed_intervals':[[7.95,9.9],[10.35,15.8]],'fitting':diagnostics},indent=2))
print('Wall assets',len(ledger),'row groups',len(new),'removed old groups',len(removed))
