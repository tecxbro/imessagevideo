from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
from urllib.request import Request,urlopen
from datetime import datetime,timezone
import hashlib,json
root=Path('/workspace/sites/message-motion');base='https://message-motion-studio.orchidhq.chatgpt.site/'
paths=[p for p in (root/'dist/director').rglob('*') if p.is_file()]
paths += [root/'dist'/n for n in ['index.html','review.html','sound.html','styles.css','imessage-motion-recreation-skill.zip','references/ui-audio-workflow.md']]
def check(path):
 rel=path.relative_to(root/'dist').as_posix();url=base+rel+('?v=2' if rel=='imessage-motion-recreation-skill.zip' else '')
 h=hashlib.sha256();size=0
 with urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=45) as response:
  status=response.status;mime=response.headers.get('Content-Type')
  while data:=response.read(256*1024):h.update(data);size+=len(data)
 expected=hashlib.file_digest(path.open('rb'),'sha256').hexdigest()
 return {'path':rel,'status':status,'content_type':mime,'bytes':size,'sha256':h.hexdigest(),'pass':status==200 and size==path.stat().st_size and h.hexdigest()==expected}
results=[]
with ThreadPoolExecutor(max_workers=4) as pool:
 for future in as_completed({pool.submit(check,p):p for p in paths}):
  try:results.append(future.result())
  except Exception as e:results.append({'pass':False,'error':str(e)})
report={'utc':datetime.now(timezone.utc).isoformat(),'pass':all(r['pass'] for r in results),'passed':sum(r['pass'] for r in results),'total':len(paths),'scope':'Unauthenticated HTTP exact byte verification, not interactive browser QA','results':sorted(results,key=lambda x:x.get('path',''))}
(root/'verification/director-public-delivery.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='results'},indent=2));print(json.dumps([r for r in results if not r['pass']],indent=2))
raise SystemExit(0 if report['pass'] else 1)
