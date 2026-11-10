from pathlib import Path
from PIL import Image
from scipy import ndimage
import numpy as np,json,re
R=Path('/workspace/imessage-recreations/references/02-danieltian');M=R/'assets/middle-measure';data=json.loads((R/'middle-measurements.json').read_text());out={}
def norm(s):return re.sub('[^a-z0-9]','',s.lower())
for ns,q in sorted(data.items(),key=lambda z:int(z[0])):
 n=int(ns)
 if n<630:continue
 choices=[c for c in q['components'] if c['cls']=='gray' and 390<c['box'][0]<700 and c['box'][2]-c['box'][0]>200 and c['box'][3]-c['box'][1]>70];left=min(c['box'][0] for c in choices) if choices else 417;scale=(960-left)/543;a=np.array(Image.open(M/f'source-{n:04d}.png').convert('RGB')).astype(float);x0=int(left+80*scale);x1=int(left+230*scale);reg=a[:,x0:x1];gray=(reg.min(2)>190)&(reg.max(2)<242)&(reg.max(2)-reg.min(2)<12);rows=gray.mean(1)>.15;rows=ndimage.binary_closing(rows,iterations=3);labels,num=ndimage.label(rows);runs=[]
 for sl in ndimage.find_objects(labels):
  yy=sl[0];h=yy.stop-yy.start
  if h<25:continue
  words=[w['text'] for w in q['words'] if yy.start<=sum(w['box'][1::2])/2<yy.stop and left-10<sum(w['box'][::2])/2<left+1100*scale];text=' '.join(words);tokens=[norm(w) for w in words];name=None
  if any('budget' in w for w in tokens):name='budget'
  elif n<780 and ('hey' in tokens or ('offsite' in tokens and 'tomorrow' in tokens)):name='kickoff'
  elif n<765 and any('airbnb' in w for w in tokens) and ('find' in tokens or 'tahoe' in tokens):name='airbnb-command'
  elif n<825 and any('lyft' in w for w in tokens):name='lyft-command'
  elif n<855 and any('resy' in w for w in tokens):name='resy-command'
  elif n>=865 and 'how' in tokens and 'about' in tokens:name='how-about'
  elif n>=945 and any('booked' in w for w in tokens):
   if 'photon' in tokens or 'xls' in tokens or 'harrison' in tokens:name='lyft-booked'
   elif 'sushi' in tokens:name='resy-booked'
   else:name='airbnb-booked'
  runs.append(dict(y=yy.start,height=h,text=text,name=name))
 out[ns]=dict(left=left,scale=scale,runs=runs);print(n/30,'L',left,'S',round(scale,4),[(r['y'],r['height'],r['name'],r['text']) for r in runs],flush=True)
(R/'middle-body-runs.json').write_text(json.dumps(out,indent=2))
