from pathlib import Path
from PIL import Image,ImageDraw
from scipy import ndimage
from concurrent.futures import ThreadPoolExecutor
from difflib import SequenceMatcher
import numpy as np,json,csv,re,subprocess,os,pickle,hashlib
R=Path('/workspace/imessage-recreations/references/01-photonhq');A=R/'assets/wall-art';M=A/'measure';OA=R/'assets/wall-ocr';OA.mkdir(exist_ok=True)
source=(R/'rebuild-walls-overlap.py').read_text();prefix=source[:source.index('ledger=[];new=[];diagnostics={}')];prefix=prefix.replace("mask=ar[:,:,:3].min(2)<246;mask[450:640,:]=False","mask=MASK_OVERRIDE.copy();mask[450:640,:]=False")
env={'MASK_OVERRIDE':None};exec(compile(prefix[:prefix.index('ims={n:')],'color-component-helper','exec'),env);phases=env['phases']+[dict(name='emails',base=300)];frames=env['frames'];component_fn=env['components'];pbase={p['name']:p['base'] for p in phases}

def masks(im):
 rgb=np.asarray(im).astype(np.float32)/255;r,g,b=rgb[:,:,0],rgb[:,:,1],rgb[:,:,2];lo=rgb.min(2);hi=rgb.max(2)
 return {'sms':(g>.76)&(r<.9)&(b<.95)&(g-r>.15)&(g-b>.10),'imessage':(b>.68)&(r<.68)&(b-r>.23)&(g>.30)&(g<.88),'whatsapp':(g>.83)&(r>.64)&(b>.5)&(b<.91)&(g-b>.065)&(g-r>.015),'telegram':(b>.84)&(g>.72)&(r>.62)&(b-r>.045)&(b-g<.15),'calls':hi<.68,'gray':(lo>.73)&(hi<.975)&((hi-lo)<.055)}
cache=A/'colored-components-thin-local.pkl'
if cache.exists():comps=pickle.loads(cache.read_bytes())
else:
 comps={}
 for i,n in enumerate(frames):
  im=Image.open(M/f'{n:04d}.png').convert('RGB');cc=[]
  for cls,mask in masks(im).items():
   mask=mask.copy();mask[450:640]=False;labels,count=ndimage.label(mask,np.ones((3,3)));areas=np.bincount(labels.ravel())
   for li,sl in enumerate(ndimage.find_objects(labels),1):
    if sl is None:continue
    yy,xx=sl;x0,y0,x1,y1=xx.start,yy.start,xx.stop,yy.stop;w=x1-x0;h=y1-y0;area=int(areas[li])
    if not((area>1200 and w>65 and h>6) or ((y0<3 or y1>1077) and area>200 and w>30 and h>1)):continue
    box=(max(0,x0-2),max(0,y0-2),min(1920,x1+2),min(1080,y1+2));tile=im.crop(box)
    cc.append(dict(box=box,area=area,w=box[2]-box[0],h=box[3]-box[1],finger=np.asarray(tile.resize((96,28),Image.Resampling.BILINEAR),dtype=np.float32)/255,**{'class':cls}))
  comps[n]=cc
  if i%15==0:print('Fast color components',i+1,'/',len(frames),flush=True)
 cache.write_bytes(pickle.dumps(comps,protocol=5))

def ocr(n):
 path=M/f'{n:04d}-normalized.tsv'
 if not path.exists():
  im=Image.open(M/f'{n:04d}.png').convert('RGB');rgb=np.asarray(im).astype(float)/255;mm=masks(im);mono=np.full(rgb.shape[:2],255,dtype=np.uint8)
  # White-on-color captions need explicit inversion; full-frame adaptive thresholding had missed SMS/blue copy.
  for cls in ['sms','imessage']:
   interior=ndimage.binary_fill_holes(mm[cls]);ink=interior&(rgb.min(2)>.72);mono[ink]=0
  for cls in ['gray','whatsapp','telegram']:
   interior=ndimage.binary_fill_holes(mm[cls]);ink=interior&(rgb.max(2)<.65);mono[ink]=0
  for co in comps[n]:
   if co['class']!='calls' or co['w']/co['h']<1.8:continue
   x0,y0,x1,y1=co['box'];xa=x0+int(co['w']*.17);xb=x0+int(co['w']*.70);ya=y0+int(co['h']*.15);yb=y0+int(co['h']*.90);reg=rgb[ya:yb,xa:xb];mono[ya:yb,xa:xb][reg.min(2)>.70]=0
  normalized=M/f'{n:04d}-normalized.png';Image.fromarray(mono).save(normalized)
  task_env=os.environ.copy();task_env['OMP_THREAD_LIMIT']='1'
  proc=subprocess.run(['tesseract',str(normalized),str(M/f'{n:04d}-normalized'),'-l','eng','--psm','11','tsv'],env=task_env,capture_output=True,text=True)
  if proc.returncode:raise RuntimeError(proc.stderr)
 words=[]
 for row in csv.DictReader(path.open(),delimiter='\t'):
  try:conf=float(row['conf'])
  except:continue
  text=row.get('text','').strip()
  if conf<30 or not text:continue
  x,y,w,h=[int(row[k]) for k in ['left','top','width','height']];words.append(dict(text=text,conf=conf,x=x,y=y,w=w,h=h))
 return n,words
with ThreadPoolExecutor(max_workers=3) as pool:ocr_words=dict(pool.map(ocr,frames))
print('OCR complete',len(frames),flush=True)

def key_for(words):
 toks=[]
 lines=[]
 for w in sorted(words,key=lambda q:q['y']+q['h']/2):
  cy=w['y']+w['h']/2;line=min(lines,key=lambda q:abs(q['cy']-cy)) if lines else None
  if line is None or abs(line['cy']-cy)>max(12,max(w['h'],line['height'])*.6):line={'cy':cy,'height':w['h'],'words':[]};lines.append(line)
  line['words'].append(w);line['cy']=float(np.mean([q['y']+q['h']/2 for q in line['words']]))
 ordered=[w for line in sorted(lines,key=lambda q:q['cy']) for w in sorted(line['words'],key=lambda q:q['x'])]
 for w in ordered:
  tok=re.sub('[^a-z]','',w['text'].lower())
  if len(tok)<2 or tok in ['am','pm','vv','nn','ll']:continue
  toks.append(tok)
 return ''.join(sorted(toks)),toks
observations=[]
for n,cc in comps.items():
 for ci,co in enumerate(cc):
  x0,y0,x1,y1=co['box']
  if co['h']>225 or co['w']<90 or co['h']<25:continue
  email_border=co['class']=='gray' and co['area']/(co['w']*co['h'])<.25 and co['w']/co['h']>2.8 and co['h']>35
  if co['area']/(co['w']*co['h'])<.25 and not email_border:continue
  if co['class']=='gray' and not email_border:
   duplicate=False
   for q in cc:
    if q['class'] in ['gray','calls']:continue
    a,b,c,d=q['box'];ix=max(0,min(x1,c)-max(x0,a));iy=max(0,min(y1,d)-max(y0,b));inter=ix*iy;union=co['w']*co['h']+q['w']*q['h']-inter
    if inter/max(1,union)>.85:duplicate=True;break
   if duplicate:continue
  if co['class']!='gray' and co['w']/co['h']<1.6:continue
  ww=[w for w in ocr_words[n] if x0<=w['x']+w['w']/2<x1 and y0<=w['y']+w['h']/2<y1]
  key,tokens=key_for(ww)
  if len(key)<4:continue
  observations.append(dict(n=n,ci=ci,key=key,tokens=tokens,confidence=float(np.mean([w['conf'] for w in ww])) if ww else 0,co=co,email_border=email_border))
# Seed neutral gray captions at each phase's own held frame, then classify overlap observations semantically.
seeds={p['name']:[] for p in phases}
for o in observations:
 if o['co']['class']=='gray':
  for p in phases:
   if abs(o['n']-p['base'])<=3:seeds[p['name']].append(o['key'])
def similar(a,b):
 if a==b:return 1.
 if min(len(a),len(b))<5:return 0.
 return SequenceMatcher(None,a,b).ratio()
allowed={'sms':(8,9.9),'calls':(10.35,12.1),'imessage':(11.35,13.4),'whatsapp':(12.65,14.6),'telegram':(13.95,15.8),'emails':(9.3,10.9)}
for o in observations:
 cls=o['co']['class'];t=o['n']/30
 if o.get('email_border'):
  if not(9.3<=t<=10.9):continue
  phase='emails'
 elif cls!='gray':phase=cls
 else:
  choices=[(max((similar(o['key'],s) for s in seeds[name]),default=0),name) for name,(st,en) in allowed.items() if st<=t<=en and name!='emails']
  if not choices:continue
  score,phase=max(choices)
  if score<.6:phase=min((name for name,(st,en) in allowed.items() if st<=t<=en and name!='emails'),key=lambda name:abs(o['n']-pbase[name]))
 if phase not in allowed or not(allowed[phase][0]<=t<=allowed[phase][1]):continue
 o['phase']=phase
clusters=[]
for o in sorted((o for o in observations if 'phase' in o),key=lambda q:(q['co']['class']=='gray',abs(q['n']-pbase[q['phase']]),-q['confidence'])):
 def same_trajectory(c):
  nearest=min(c['obs'],key=lambda q:abs(q['n']-o['n']));a=nearest['co']['box'];b=o['co']['box'];dx=abs((a[0]+a[2]-b[0]-b[2])/2);dy=abs((a[1]+a[3]-b[1]-b[3])/2)
  if nearest['n']==o['n'] and (dx>5 or dy>5):return False
  return dy<180 and dx<max(180,o['co']['w']*.65)
 choices=[(similar(o['key'],c['key']),c) for c in clusters if c['phase']==o['phase'] and c['class_name']==o['co']['class'] and same_trajectory(c)]
 score,cl=max(choices,key=lambda q:q[0]) if choices else(0,None)
 if score>=.78:cl['obs'].append(o)
 else:clusters.append(dict(key=o['key'],phase=o['phase'],class_name=o['co']['class'],obs=[o]))
# OCR line-top ordering and partial word errors can split one physical element. Merge consistent nearby geometry across adjacent native samples.
parent=list(range(len(clusters)))
def find(i):
 while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
 return i
records=[]
for ci,c in enumerate(clusters):
 for o in c['obs']:records.append((o['n'],ci,o))
records.sort(key=lambda q:q[0])
for i,(n,ci,o) in enumerate(records):
 x0,y0,x1,y1=o['co']['box'];w=x1-x0;h=y1-y0
 for nn,cj,q in records[max(0,i-90):i]:
  if n-nn>3 or n==nn or find(ci)==find(cj):continue
  if clusters[ci]['phase']!=clusters[cj]['phase'] or clusters[ci]['class_name']!=clusters[cj]['class_name']:continue
  a,b,c,d=q['co']['box'];ww=c-a;hh=d-b
  if .8<ww/w<1.25 and .6<hh/h<1.5 and abs((a+c-x0-x1)/2)<max(70,w*.08) and abs((b+d-y0-y1)/2)<min(35,max(h,hh)*.35):parent[find(cj)]=find(ci)
merged={}
for i,c in enumerate(clusters):
 root=find(i)
 if root not in merged:merged[root]=dict(c,obs=[])
 merged[root]['obs'].extend(c['obs'])
clusters=[c for c in merged.values() if len({o['n'] for o in c['obs']})>=2]
scene=json.loads((R/'scene-wall-v4.json').read_text());new=[];ledger=[]
claimed={(o['n'],o['ci']) for c in clusters for o in c['obs']};inferred_claims=set()
def fit_alpha(template,observed):
 d=1-template;e=1-observed;median=np.median(template[5:23,6:90],axis=(0,1));weight=(np.max(np.abs(template-median),axis=2)<.09)&(np.max(d,axis=2)>.04);weight=weight if weight.sum()>100 else np.max(d,axis=2)>.04;den=float(np.sum(d[weight]**2));a=float(np.clip(np.sum(d[weight]*e[weight])/den,.05,1)) if den>0 else 1
 err=float(np.mean((observed[weight]-(1-a+a*template[weight]))**2)) if weight.any() else 1
 return a,err

for c in clusters:
 phase=c['phase'];base=pbase[phase]
 def quality(o):
  co=o['co'];x0,y0,x1,y1=co['box'];full=x0>3 and y0>3 and x1<1917 and y1<1077
  return (10000 if o['n']==base and full else 0)+(400 if full else 0)+min(co['h'],160)*o['confidence']/100-abs(o['n']-base)*.2
 canonical=max(c['obs'],key=quality);co=canonical['co'];box=co['box'];im=Image.open(M/f'{canonical["n"]:04d}.png').convert('RGB');tile=im.crop(box).convert('RGBA');body=masks(tile.convert('RGB'))[c['class_name']];body=ndimage.binary_fill_holes(ndimage.binary_closing(body,iterations=1));body=ndimage.binary_dilation(body,iterations=1);rgba=np.array(tile);rgba[:,:,3]=body.astype(np.uint8)*255
 if phase=='emails':
  w,h=tile.size;matte=Image.new('L',(w*4,h*4));draw=ImageDraw.Draw(matte);full=max(w,h*5);left=-(full-w) if box[0]<4 else 1;right=full if box[2]>1916 else w-1
  draw.rounded_rectangle((left*4,4,right*4,(h-1)*4),radius=(h-2)*2,fill=255);rgba[:,:,3]=np.asarray(matte.resize((w,h),Image.Resampling.LANCZOS))
 tile=Image.fromarray(rgba)
 digest=hashlib.sha256((phase+c['class_name']+c['key']+str(round((box[1]+box[3])/320))+str(round((box[0]+box[2])/800))).encode()).hexdigest()[:12];filename=f'{phase}-{digest}.png';tile.save(OA/filename)
 # Infer only short unreadable flip spans around a semantic OCR track, using unclaimed same-material components near its predicted geometry.
 direct=sorted(c['obs'],key=lambda o:o['n']);augment=[]
 def predict(n):
  before=[o for o in direct if o['n']<=n];after=[o for o in direct if o['n']>=n]
  if before and after:a,b=before[-1],after[0]
  elif before:a,b=direct[-2:]
  else:a,b=direct[:2]
  f=(n-a['n'])/(b['n']-a['n']) if b['n']!=a['n'] else 0
  aa=a['co']['box'];bb=b['co']['box'];return tuple(aa[k]+f*(bb[k]-aa[k]) for k in range(4))
 for n in frames:
  if any(o['n']==n for o in direct) or n<direct[0]['n']-9 or n>direct[-1]['n']+9:continue
  if not(allowed[phase][0]<=n/30<=allowed[phase][1]):continue
  px0,py0,px1,py1=predict(n);cx,cy=(px0+px1)/2,(py0+py1)/2;candidates=[]
  for ci,q in enumerate(comps[n]):
   if (n,ci) in claimed or (n,ci) in inferred_claims:continue
   if q['class']!=c['class_name']:continue
   x0,y0,x1,y1=q['box'];xr=q['w']/co['w'];yr=q['h']/co['h'];dx=(x0+x1)/2-cx;dy=(y0+y1)/2-cy
   if not(.5<xr<1.7 and .035<yr<1.8) or abs(dx)>max(140,co['w']*.30) or abs(dy)>110:continue
   alpha,err=fit_alpha(co['finger'],q['finger']);score=err+.000001*(dx*dx+dy*dy)
   if err<.05:candidates.append((score,err,alpha,ci,q))
  if candidates:
   score,err,alpha,ci,q=min(candidates,key=lambda z:z[0]);inferred_claims.add((n,ci));augment.append(dict(n=n,ci=ci,key=c['key'],tokens=canonical['tokens'],confidence=0,co=q,inferred=True,fit_alpha=alpha,fit_error=err))
 byframe={}
 for o in c['obs']+augment:
  if o['n'] not in byframe or o['confidence']>byframe[o['n']]['confidence']:byframe[o['n']]=o
 ms=[]
 for n,o in sorted(byframe.items()):
  bb=o['co']['box'];ms.append(dict(t=n/30,x=bb[0],y=bb[1],scaleX=o['co']['w']/co['w'],scaleY=o['co']['h']/co['h'],opacity=fit_alpha(co['finger'],o['co']['finger'])[0],ocr=o['key'],inferred=o.get('inferred',False)))
 # Canonical identity from OCR prevents color/size confusions. Interpolate only the measured per-element geometry.
 first,last=ms[0],ms[-1];start=max(allowed[phase][0],first['t']-.055);end=min(allowed[phase][1],last['t']+.055);tracks={p:[dict(t=m['t'],value=m[p]) for m in ms] for p in ['x','y','scaleX','scaleY']}
 for t,m in [(start,first),(end,last)]:
  ss=m['scaleY']*.2;yy=m['y']+(m['scaleY']-ss)*co['h']/2;tracks['x'].append(dict(t=t,value=m['x']));tracks['y'].append(dict(t=t,value=yy));tracks['scaleX'].append(dict(t=t,value=m['scaleX']));tracks['scaleY'].append(dict(t=t,value=ss))
 for p in tracks:tracks[p].sort(key=lambda q:q['t'])
 tracks['opacity']=[dict(t=start,value=0)]+[dict(t=m['t'],value=m['opacity']) for m in ms]+[dict(t=end,value=0)]
 node=dict(id=f'ocr-wall-{phase}-{digest}',type='image',src='assets/wall-ocr/'+filename,x=box[0],y=box[1],width=co['w'],height=co['h'],start=start,end=end,keyframes=tracks,semanticText=' '.join(canonical['tokens']),sourceFrame=canonical['n'],sourceBounds=list(box),editability='Individual original UI artwork; bitmap copy; OCR identifies semantic element, position/scale/visibility independently editable.')
 new.append(node);ledger.append(dict(id=node['id'],semanticText=node['semanticText'],phase=phase,class_name=c['class_name'],sourceFrame=canonical['n'],sourceBounds=list(box),asset=node['src'],observations=ms))
# Layer phases chronologically; within a phase, keep source vertical order.
new.sort(key=lambda l:(pbase[next(x['phase'] for x in ledger if x['id']==l['id'])],l['y'],l['x']))
retained=[l for l in scene['layers'] if not(l['id'].startswith('wall-art-') or l['id'].startswith('wall-element-') or l['id'].startswith('ocr-wall-')) and not(l.get('type')=='group' and any('notification-art-' in c.get('src','') for c in l.get('children',[])))];scene['layers']=[l for l in retained if l['id'].startswith('edge-restore-')]+new+[l for l in retained if not l['id'].startswith('edge-restore-')]
scene['source']['notes']+=' Semantic OCR wall tracking separates body color masks before component labeling, preventing overlapping green/blue bubbles from merging. Canonical artwork is chosen from the clearest complete observation; per-element source-box geometry handles staggered flips/visibility.'
(R/'scene-wall-v4.json').write_text(json.dumps(scene,indent=2));(R/'wall-ocr-provenance.json').write_text(json.dumps(ledger,indent=2));print('Semantic wall assets',len(new),flush=True)
