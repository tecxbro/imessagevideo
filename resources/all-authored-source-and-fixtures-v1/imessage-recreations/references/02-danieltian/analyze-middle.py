from pathlib import Path
from PIL import Image,ImageDraw
from scipy import ndimage
from concurrent.futures import ThreadPoolExecutor
import numpy as np,csv,json,subprocess,os
R=Path('/workspace/imessage-recreations/references/02-danieltian');M=R/'assets/middle-measure'
def job(p):
 n=int(p.stem.split('-')[-1]);a=np.array(Image.open(p).convert('RGB')).astype(float);lo=a.min(2);hi=a.max(2);gray=(lo>170)&(hi<246)&((hi-lo)<18);blue=(a[:,:,2]-a[:,:,0]>70)&(a[:,:,2]>190)&(a[:,:,1]>90)&(a[:,:,0]<120);green=(a[:,:,1]>220)&(a[:,:,0]<190)&(a[:,:,2]<150);chroma=(hi-lo>65)&(lo<190)&(hi>150);out=[]
 for cls,mask in [('gray',gray),('blue',blue),('green',green),('chroma',chroma)]:
  mask=ndimage.binary_closing(mask,iterations=2);lab,c=ndimage.label(mask,np.ones((3,3)));areas=np.bincount(lab.ravel())
  for li,sl in enumerate(ndimage.find_objects(lab),1):
   if not sl:continue
   y,x=sl;w=x.stop-x.start;h=y.stop-y.start;area=int(areas[li])
   if cls in ['gray','blue']:
    if not(w>100 and h>35 and area>1800):continue
   elif not(w>25 and h>25 and area>250):continue
   out.append(dict(cls=cls,box=[x.start,y.start,x.stop,y.stop],area=area,fill=area/(w*h)))
 # Blue outgoing text is normalized to black on white so OCR can identify it alongside native gray message text.
 mono=np.full(a.shape[:2],255,dtype=np.uint8);mono[a.max(2)<170]=0;interior=ndimage.binary_fill_holes(blue);mono[interior&(a.min(2)>180)]=0
 norm=M/f'ocr-{n:04d}.png';tsv=M/f'ocr-{n:04d}.tsv'
 if not tsv.exists():
  Image.fromarray(mono).save(norm);e=os.environ.copy();e['OMP_THREAD_LIMIT']='1';subprocess.run(['tesseract',str(norm),str(tsv.with_suffix('')),'--psm','11','tsv'],env=e,capture_output=True,check=True)
 words=[]
 for q in csv.DictReader(tsv.open(),delimiter='\t'):
  try:conf=float(q['conf'])
  except:continue
  if conf<25 or not q['text'].strip():continue
  x,y,w,h=[int(q[k]) for k in ['left','top','width','height']];words.append(dict(text=q['text'],conf=conf,box=[x,y,x+w,y+h]))
 return n,dict(components=out,words=words)
with ThreadPoolExecutor(max_workers=3) as ex:result=dict(ex.map(job,sorted(M.glob('source-*.png'))))
(R/'middle-measurements.json').write_text(json.dumps(result,indent=2))
for n,q in sorted(result.items()):
 bodies=[]
 for c in q['components']:
  if c['cls'] not in ['gray','blue']:continue
  x,y,r,b=c['box'];words=[w['text'] for w in q['words'] if x<sum(w['box'][::2])/2<r and y<sum(w['box'][1::2])/2<b];bodies.append((c['cls'],c['box'],' '.join(words)))
 print(n/30,bodies,flush=True)
