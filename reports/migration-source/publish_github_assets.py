#!/usr/bin/env python3
"""Migration publisher for the explicitly authorized private GitHub repository.

Uses the authenticated gh CLI; never stores credentials or signed URLs.
Resume checks actual remote asset names/sizes/digests before uploading again.
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse, hashlib, json, re, subprocess, sys

ROOT=Path(__file__).resolve().parents[1]
REPO='tecxbro/imessagevideo';TAG='complete-library-v1';PLAN=ROOT/'GITHUB-ASSETS.json'
def run(args):
    p=subprocess.run(['gh',*args],cwd=ROOT,text=True,capture_output=True)
    if p.returncode:raise RuntimeError(re.sub(r'(https?://[^\s?]+)\?[^\s]+',r'\1?REDACTED',p.stderr.strip())[:2000])
    return p.stdout
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(data):
    tmp=PLAN.with_suffix('.json.writing');tmp.write_text(json.dumps(data,indent=2)+'\n');tmp.replace(PLAN)
def prepare():
    old=json.loads((ROOT/'skill/imessage-motion-recreation/library/manifest.json').read_text());assets=[]
    for a in old['archives']:
        assets.append({'file_name':a['id']+'.zip','path':'archives/'+a['id']+'.zip','bytes':a['bytes'],'sha256':a['sha256'],'role':'archive','archive_id':a['id']})
        for p in a['parts']:assets.append({'file_name':p['file_name'],'path':'archives/resource-parts/'+a['id']+'/'+p['file_name'],'bytes':p['bytes'],'sha256':p['sha256'],'role':'part','archive_id':a['id']})
    for name in ['imessage-motion-complete-skill-v3.zip','release-verification-v3.zip']:
        p=ROOT/'archives'/name;assets.append({'file_name':name,'path':'archives/'+name,'bytes':p.stat().st_size,'sha256':sha(p),'role':'snapshot'})
    if len({a['file_name'] for a in assets})!=len(assets):raise ValueError('Duplicate release asset names')
    data={'schema_version':1,'repository':REPO,'release_tag':TAG,'storage':'private GitHub Release assets for archives and oversized raw scene data; normal source/media/evidence in Git','reason':'GitHub LFS rejected upload because account exceeded its LFS budget. No LFS budget/visibility change made.','restore_command':'python3 tools/sync_library.py','assets':assets}
    save(data);return data
def release():
    # An unpublished release without a created Git tag is absent from the
    # releases/tags endpoint. Resolve its observed ID from the release list.
    pages=json.loads(run(['api',f'repos/{REPO}/releases?per_page=100','--paginate','--slurp']))
    found=[x for page in pages for x in page if x['tag_name']==TAG]
    if len(found)!=1:raise ValueError('Expected exactly one release with the declared tag')
    return found[0]
def remote_assets(rel):
    pages=json.loads(run(['api',f'repos/{REPO}/releases/{rel["id"]}/assets?per_page=100','--paginate','--slurp']))
    return {x['name']:x for page in pages for x in page}
def matches(a,r):
    if r['size']!=a['bytes'] or r.get('state')!='uploaded':return False
    digest=r.get('digest')
    if digest and digest!='sha256:'+a['sha256']:raise ValueError('Remote SHA256 differs: '+a['file_name'])
    return True
def publish(workers):
    data=json.loads(PLAN.read_text());rel=release();known=remote_assets(rel)
    pending=[]
    for a in data['assets']:
        p=ROOT/a['path']
        if not p.is_file() or p.stat().st_size!=a['bytes'] or sha(p)!=a['sha256']:raise ValueError('Local asset differs: '+a['path'])
        if a['file_name'] in known:
            if not matches(a,known[a['file_name']]):raise ValueError('Existing remote asset differs; refusing clobber: '+a['file_name'])
        else:pending.append(a)
    print(json.dumps({'already_uploaded':len(data['assets'])-len(pending),'pending':len(pending),'release_id':rel['id']}),flush=True)
    failures=[]
    with ThreadPoolExecutor(max_workers=workers) as pool:
        fs={pool.submit(run,['release','upload',TAG,'--repo',REPO,str(ROOT/a['path'])]):a for a in pending}
        for f in as_completed(fs):
            a=fs[f]
            try:f.result();print(json.dumps({'uploaded':a['file_name'],'bytes':a['bytes']}),flush=True)
            except Exception as e:failures.append({'asset':a['file_name'],'error':str(e)});print(json.dumps(failures[-1]),flush=True)
    current=remote_assets(rel)
    for a in data['assets']:
        x=current.get(a['file_name'])
        if x and matches(a,x):a.update(github_asset_id=x['id'],github_api_url=x['url'],github_download_url=x['browser_download_url'],github_digest=x.get('digest'),github_uploaded=True,github_size_verified=True,github_sha256_verified=x.get('digest')=='sha256:'+a['sha256'])
    data.update(github_release_id=rel['id'],github_release_url=rel['html_url'],uploaded_assets=sum(bool(a.get('github_uploaded')) for a in data['assets']),server_sha256_verified_assets=sum(bool(a.get('github_sha256_verified')) for a in data['assets']),release_draft=rel['draft'])
    save(data)
    print(json.dumps({'uploaded_assets':data['uploaded_assets'],'server_sha256_verified_assets':data['server_sha256_verified_assets'],'failures':failures}),flush=True)
    return not failures and data['uploaded_assets']==len(data['assets'])
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['prepare','upload','status']);p.add_argument('--workers',type=int,default=3);a=p.parse_args()
    if a.action=='prepare':d=prepare();print(json.dumps({'assets':len(d['assets']),'bytes':sum(x['bytes'] for x in d['assets'])}));return
    if a.action=='status':print(json.dumps(release(),indent=2));return
    sys.exit(0 if publish(a.workers) else 1)
if __name__=='__main__':main()
