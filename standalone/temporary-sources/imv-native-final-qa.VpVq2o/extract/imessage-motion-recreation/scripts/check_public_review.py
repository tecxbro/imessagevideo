from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor,as_completed
import json,hashlib,time,sys
root=Path(sys.argv[2]) if len(sys.argv)>2 else Path.cwd();base=sys.argv[1].rstrip('/');dist=root/'dist'
films=json.loads((dist/'videos.json').read_text());media_root=Path(sys.argv[3]) if len(sys.argv)>3 else root.parent/'message-motion-originals/dist';paths=[v['source'] for v in films]+[p for v in films for p in v['methods'].values()];originals={v['source']:media_root/v['sourcePath'] for v in films}
results=[]
def check(path):
 local=originals.get(path,dist/path);size=local.stat().st_size;start=min(1024*1024,size-1024);end=start+1023
 req=Request(urljoin(base+'/',path),headers={'Range':f'bytes={start}-{end}','User-Agent':'Mozilla/5.0'})
 with urlopen(req,timeout=60) as response:
  status=response.status;headers={k.lower():v for k,v in response.headers.items()};h=hashlib.sha256();received=0;sample=b''
  while chunk:=response.read(128*1024):h.update(chunk);received+=len(chunk);sample+=chunk if status==206 else b''
 if status==206:
  with local.open('rb') as f:f.seek(start);expected=f.read(1024)
  matches=sample==expected and headers.get('content-range')==f'bytes {start}-{end}/{size}'
 else:
  with local.open('rb') as f:expected_sha=hashlib.file_digest(f,'sha256').hexdigest()
  matches=status==200 and received==size and h.hexdigest()==expected_sha
 return {'path':path,'status':status,'content_type':headers.get('content-type'),'content_range':headers.get('content-range'),'received_bytes':received,'expected_bytes':size,'picture_file_bytes_equal':matches,'delivery':'range' if status==206 else 'complete MP4; player loads it into a seekable Blob','pass':matches and headers.get('content-type','').startswith('video/mp4')}

with urlopen(Request(base+'/',headers={'User-Agent':'Mozilla/5.0'}),timeout=45) as r:
 html=r.read();homepage={'status':r.status,'final_url':r.url,'expected_gallery':b'message studies' in html and b'film-data' in html,'source_bytes_equal':html==(dist/'index.html').read_bytes()}
with ThreadPoolExecutor(max_workers=4) as pool:
 for future in as_completed({pool.submit(check,p):p for p in paths}):
  try:results.append(future.result())
  except Exception as e:results.append({'pass':False,'error':str(e)})
report={'base':base,'homepage':homepage,'media':sorted(results,key=lambda x:x.get('path','')),'passed':sum(r['pass'] for r in results),'total':len(paths),'pass':homepage['status']==200 and homepage['expected_gallery'] and all(r['pass'] for r in results),'notice':'Unauthenticated exact media delivery checks, not an interactive browser playback test. This gateway ignores Range and returns full MP4 bodies; the player loads complete videos into local Blob URLs for seeking.'}
(root/'verification/public-delivery.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='media'},indent=2));print(json.dumps([r for r in results if not r['pass']],indent=2));sys.exit(0 if report['pass'] else 1)
