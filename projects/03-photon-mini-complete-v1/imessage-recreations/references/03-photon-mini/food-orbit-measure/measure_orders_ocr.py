from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import subprocess,csv,io,json,re,os,time
R=Path('/workspace/imessage-recreations/references/03-photon-mini');D=R/'food-orbit-measure';env={**os.environ,'OMP_THREAD_LIMIT':'1'}
def run(n):
 path=R/'lunch-native'/f'{n-609:03d}.png';raw=subprocess.run(['tesseract',str(path),'stdout','--psm','11','tsv'],capture_output=True,check=True,env=env).stdout.decode();rows=csv.DictReader(io.StringIO(raw),delimiter='\t');found=[]
 for q in rows:
  text=q['text'].strip()
  if re.sub('[^A-Za-z]','',text)!='Order' or float(q['conf'])<15:continue
  l,t,w,h=[int(q[k]) for k in ['left','top','width','height']];found.append(dict(text=text,confidence=float(q['conf']),bbox=[l,t,l+w,t+h]))
 return n,found
out={};start=time.time()
with ThreadPoolExecutor(max_workers=2) as pool:
 for n,found in pool.map(run,range(730,800)):
  out[str(n)]=found
  if n%10==0:print(n,len(found),'elapsed',round(time.time()-start,1),flush=True)
  (D/'order-ocr-progress.json').write_text(json.dumps(out))
(D/'order-ocr-measurements.json').write_text(json.dumps(out,indent=2));print('Order OCR complete',round(time.time()-start,1),flush=True)
