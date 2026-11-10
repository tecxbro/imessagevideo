from pathlib import Path
import json,hashlib,os,html,sys
root=Path('/workspace/sites/message-motion');proof=json.loads((root/'verification/public-delivery.json').read_text())
if not proof.get('pass'):raise RuntimeError('Public delivery must pass before replacing local entrypoints')
url=proof['base']+'/'
page='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="refresh" content="0;url=URL"><title>message studies — open the public gallery</title><style>*{box-sizing:border-box}body{margin:0;background:#fefdfb;color:#2a2a24;font-family:Georgia,serif;min-height:100vh;display:grid;place-items:center;padding:30px}main{max-width:600px;text-align:center}small{font:11px 'Courier New',monospace;color:#8a877b}h1{font-size:62px;letter-spacing:-3px;font-weight:400;line-height:1.05;margin:25px 0}p{font-size:17px;line-height:1.5;color:#7b796f}a{display:inline-block;margin:22px 0;padding:15px 24px;border-radius:30px;color:#fefdfb;background:#2a2a24;text-decoration:none;font:13px Arial,sans-serif}.old{background:transparent;color:#7b796f;text-decoration:underline;font:11px Arial,sans-serif;padding:5px;margin:10px}</style></head><body><main><small>message studies / 06 films / 30 recreations</small><h1>the films have<br><em>a new home.</em></h1><p>The complete collection now plays on a public website. Open the gallery to watch, switch methods, or compare with the originals.</p><a href="URL" target="_blank" rel="noopener">open the public gallery ↗</a><br><a href="review.before-public.html" class="old">archived local review</a></main></body></html>'''.replace('URL',html.escape(url,quote=True))
updates=[]
for folder in [Path('/workspace/imessage-recreations'),Path('/workspace/imessage-recreations/delivery-package-final')]:
 p=folder/'review.html';backup=folder/'review.before-public.html'
 if not backup.exists():backup.write_bytes(p.read_bytes())
 oldsha=hashlib.sha256(backup.read_bytes()).hexdigest();tmp=p.with_suffix('.html.tmp');tmp.write_text(page);os.replace(tmp,p)
 record={'public_url':url,'original_review':'review.before-public.html','original_review_sha256':oldsha,'current_review_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'why':'The public origin serves the complete video collection; local preview access to relative MP4 paths varies by client.','public_media_checks':{'passed':proof['passed'],'total':proof['total']},'previous_delivery_zip_unchanged':True,'notice':'This is a post-delivery edit to the HTML entrypoint. Earlier stage checksums describe the original frozen delivery; the existing delivery ZIP is preserved.'}
 (folder/'public-review-update.json').write_text(json.dumps(record,indent=2)+'\n');updates.append({'path':str(p),**record})
(root/'verification/local-review-updates.json').write_text(json.dumps(updates,indent=2)+'\n')
print(json.dumps({'updated':len(updates),'public_url':url}))
