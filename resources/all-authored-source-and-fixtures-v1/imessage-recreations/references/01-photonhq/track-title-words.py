from pathlib import Path
import sys,json,csv,re,numpy as np
from PIL import Image
from difflib import SequenceMatcher
sys.path.insert(0,'/workspace/imessage-recreations/references/02-danieltian')
from trace_glyphs import trace_alpha
R=Path('/workspace/imessage-recreations/references/01-photonhq');M=R/'assets/wall-art/measure';scene=json.loads((R/'scene-wall-v4.json').read_text())
phases=[('sms',270,8.2,9.5,['10,000+','SMS']),('emails',300,9.5,10.666667,['100,000+','emails']),('calls',336,10.666667,11.666667,['8000+','voice','minutes']),('imessage',372,11.666667,12.966667,['Unlimited','iMessage']),('whatsapp',408,12.966667,14.2,['Unlimited','WhatsApp']),('telegram',444,14.2,15.5,['Unlimited','Telegram'])]
frames=sorted(int(p.stem) for p in M.glob('*.tsv') if p.stem.isdigit());words={}
def norm(s):return re.sub('[^a-z0-9]','',s.lower())
def matches(a,b):
 a,b=norm(a),norm(b)
 if any(c.isdigit() for c in b):return a==b
 return a==b or SequenceMatcher(None,a,b).ratio()>.78
for n in frames:
 result=[]
 for w in csv.DictReader((M/f'{n:04d}.tsv').open(),delimiter='\t'):
  if not w['text'].strip():continue
  try:conf=float(w['conf'])
  except:continue
  x,y,ww,h=[int(w[k]) for k in ['left','top','width','height']]
  if conf>=0 and 465<y<620 and h<130 and y+h<650:result.append(dict(text=w['text'],box=(x,y,x+ww,y+h),confidence=conf))
 words[n]=result
new=[];ledger=[];fullcopies=[]
for name,base,start,end,tokens in phases:
 fullcopies.append(' '.join(tokens));a=np.asarray(Image.open(M/f'{base:04d}.png').convert('RGB'))
 for wi,token in enumerate(tokens):
  choices=[w for w in words[base] if matches(w['text'],token)]
  if not choices:raise ValueError('Missing canonical heading word '+token)
  bw=max(choices,key=lambda w:w['confidence']);x0,y0,x1,y1=bw['box'];x0=max(0,x0-3);y0=max(0,y0-3);x1=min(1920,x1+3);y1=min(1080,y1+3);alpha=np.clip((253-a[y0:y1,x0:x1,0].astype(float))/253,0,1);yy,xx=np.where(alpha>.5);ink=(int(xx.min()+x0),int(yy.min()+y0),int(xx.max()+x0+1),int(yy.max()+y0+1));d,stats=trace_alpha(alpha,x0,y0);ms=[]
  for n in frames:
   t=n/30
   if t<start-.25 or t>end+.25:continue
   if token=='Unlimited' and not(start<=t<end):continue
   cand=[w for w in words[n] if matches(w['text'],token)]
   if not cand:continue
   w=max(cand,key=lambda w:w['confidence']);bb=w['box'];im=np.asarray(Image.open(M/f'{n:04d}.png').convert('RGB'));l=max(0,bb[0]-3);top=max(465,bb[1]-3);r=min(1920,bb[2]+3);bot=min(640,bb[3]+3);ar=np.clip((253-im[top:bot,l:r,0].astype(float))/253,0,1);ys,xs=np.where(ar>.35)
   if not len(xs):continue
   box=(int(xs.min()+l),int(ys.min()+top),int(xs.max()+l+1),int(ys.max()+top+1));sx=(box[2]-box[0])/(ink[2]-ink[0]);sy=(box[3]-box[1])/(ink[3]-ink[1]);opacity=float(np.quantile(ar[ar>.2],.95)) if np.any(ar>.2) else 0
   ms.append(dict(t=t,x=box[0]-ink[0]*sx,y=box[1]-ink[1]*sy,scaleX=sx,scaleY=sy,opacity=opacity,sourceBounds=list(box),ocr=w['text']))
  if not any(abs(m['t']-base/30)<.001 for m in ms):ms.append(dict(t=base/30,x=0,y=0,scaleX=1,scaleY=1,opacity=1,sourceBounds=list(ink),ocr=token))
  ms.sort(key=lambda m:m['t']);first,last=ms[0],ms[-1];left=max(start-.20,first['t']-.06);right=min(end+.20,last['t']+.06)
  if token=='Unlimited':left=start;right=end
  tracks={p:[dict(t=m['t'],value=m[p]) for m in ms] for p in ['x','y','scaleX','scaleY','opacity']};tracks['opacity']=[dict(t=left,value=0)]+tracks['opacity']+[dict(t=right,value=0)]
  new.append(dict(id=f'source-heading-word-{name}-{wi}',type='path',d=d,fill='#000000',start=left,end=right,keyframes=tracks,semanticText=token,sourceFrame=base,sourceBounds=list(ink),editability='Native editable glyph outlines with per-word measured geometry/opacity; not live font text.'))
  ledger.append(dict(id=new[-1]['id'],semanticText=token,sourceFrame=base,sourceBounds=list(ink),observations=ms,**stats))
remove=[]
for l in scene['layers']:
 semantic=l.get('semanticText',l.get('text',''))
 if semantic in fullcopies and l.get('type') in ['text','path']:remove.append(l['id'])
scene['layers']=[l for l in scene['layers'] if l['id'] not in remove and not l['id'].startswith('source-heading-word-')]+new;scene['source']['notes']+=' Native heading words now carry independently measured source ink bounds and opacity through phase changes, including source counter/descriptor timing; original-copy outlines and semantic provenance retained.'
(R/'scene-wall-v4.json').write_text(json.dumps(scene,indent=2));(R/'title-word-tracking.json').write_text(json.dumps(ledger,indent=2));print('Measured native heading word tracks',len(new),'replaced old headings',len(remove))
