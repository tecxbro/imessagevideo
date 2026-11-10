"""Verify public audio delivery bytes; this is not a browser playback test."""
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urljoin
from datetime import datetime, timezone
import hashlib
import json

MAIN = Path('/workspace/sites/message-motion')
MEDIA = Path('/workspace/sites/message-motion-originals')
ORIGINS = {MAIN: 'https://message-motion-studio.orchidhq.chatgpt.site/',
           MEDIA: 'https://message-motion-originals.orchidhq.chatgpt.site/'}
tasks = []
for root, patterns in [(MAIN,['index.html','review.html','styles.css','sound.html','sound-lab.js','sound-lab.css','sound-data.json','imessage-motion-recreation-skill.zip','audio-new/**/*']),
                       (MEDIA,['bridge.html','audio-previews/**/*'])]:
    for pattern in patterns:
        for path in (root/'dist').glob(pattern):
            if path.is_file(): tasks.append((root,path))

def check(item):
    root,path=item
    rel=path.relative_to(root/'dist').as_posix()
    url=urljoin(ORIGINS[root],rel)
    digest=hashlib.sha256(); size=0; header=b''
    with urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=60) as response:
        status=response.status
        content_type=response.headers.get('Content-Type','').lower()
        while block:=response.read(256*1024):
            if not header: header=block[:16]
            digest.update(block); size+=len(block)
    local=hashlib.file_digest(path.open('rb'),'sha256').hexdigest()
    is_mp4=header[4:8]==b'ftyp'
    mime_ok=(path.suffix!='.mp4' or content_type.startswith('video/mp4') and is_mp4) and (path.suffix!='.m4a' or content_type.startswith(('audio/','video/mp4','application/octet-stream')) and is_mp4)
    return {'url':url,'status':status,'content_type':content_type,'bytes':size,'sha256':digest.hexdigest(),
            'player_blob_type':'audio/mp4' if path.suffix=='.m4a' else 'video/mp4' if path.suffix=='.mp4' else None,
            'media_container_valid':is_mp4 if path.suffix in ['.mp4','.m4a'] else None,
            'pass':status==200 and size==path.stat().st_size and digest.hexdigest()==local and mime_ok}

results=[]
with ThreadPoolExecutor(max_workers=4) as pool:
    for f in as_completed({pool.submit(check,item):item for item in tasks}):
        try: results.append(f.result())
        except Exception as e: results.append({'pass':False,'error':str(e)})
report={'checked_utc':datetime.now(timezone.utc).isoformat(),'pass':all(r['pass'] for r in results),
        'passed':sum(r['pass'] for r in results),'total':len(tasks),'results':sorted(results,key=lambda r:r.get('url','')),
        'browser_playback_test':False,'scope':'Unauthenticated whole-file HTTP200 delivery and exact SHA256 of every new public audio/video/kit plus the Soundlab entry files; native browser startup was unavailable.'}
(MAIN/'verification/ui-public-delivery.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='results'},indent=2))
print(json.dumps([r for r in results if not r['pass']],indent=2))
raise SystemExit(0 if report['pass'] else 1)
