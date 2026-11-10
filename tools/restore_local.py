#!/usr/bin/env python3
"""Restore verified archive parts and extract complete private projects locally.

This helper contains no network client or credential. The agent supplies bytes
returned by the authorized Drive connector; subsequent local use is offline.
"""
from pathlib import Path
import argparse, hashlib, importlib.util, json, os, shutil

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT/'skill/imessage-motion-recreation/library/manifest.json'
def sha(p):
    with p.open('rb') as f: return hashlib.file_digest(f, 'sha256').hexdigest()
def manifest(): return json.loads(MANIFEST.read_text())
def part_path(ident, part): return ROOT/'archives/resource-parts'/ident/part['file_name']
def receipt_path(ident, number): return ROOT/'inventory/restore-receipts'/f'{ident}-{number:03d}.json'
def write_json(p, value):
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp=p.with_suffix(p.suffix+'.writing');tmp.write_text(json.dumps(value,indent=2)+'\n');os.replace(tmp,p)
def pending(limit):
    rows=[]
    for a in manifest()['archives']:
        for p in a['parts']:
            target=part_path(a['id'],p);receipt=receipt_path(a['id'],p['number'])
            if target.is_file() and target.stat().st_size==p['bytes'] and receipt.is_file(): continue
            rows.append({'archive_id':a['id'],'account_link_id':a['account_link_id'],**p})
    return rows[:limit]
def commit(ident,number,source):
    a=next(x for x in manifest()['archives'] if x['id']==ident)
    p=next(x for x in a['parts'] if x['number']==number)
    source=source.resolve()
    if not source.is_relative_to(Path('/workspace/attachments')): raise ValueError('Only a newly materialized attachment may be accepted/cleaned')
    if source.stat().st_size!=p['bytes'] or sha(source)!=p['sha256']: raise ValueError('Materialized download differs from archive registry; keeping diagnostic input')
    target=part_path(ident,p);target.parent.mkdir(parents=True,exist_ok=True)
    if target.exists():
        if sha(target)!=p['sha256']:raise ValueError('Existing part differs; refusing overwrite')
    else:
        tmp=target.with_suffix(target.suffix+'.copying');shutil.copyfile(source,tmp);os.replace(tmp,target)
    write_json(receipt_path(ident,number),{'archive_id':ident,'part':number,'relative_path':str(target.relative_to(ROOT)),'bytes':p['bytes'],'sha256':p['sha256'],'verified':True,'source_drive_id':p['drive_id']})
    source.unlink()
    return {'verified':ident,'part':number,'bytes':p['bytes']}
def extract_ready():
    helper=ROOT/'skill/imessage-motion-recreation/library/materialize.py'
    spec=importlib.util.spec_from_file_location('local_materialize',helper);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    results=[]
    for a in manifest()['archives']:
        proof=ROOT/'inventory/extractions'/f'{a["id"]}.json'
        if proof.is_file():continue
        if any(not part_path(a['id'],p).is_file() for p in a['parts']):continue
        archive=ROOT/'archives'/f'{a["id"]}.zip'
        if not archive.is_file():module.assemble(a,part_path(a['id'],a['parts'][0]).parent,None,archive)
        if archive.stat().st_size!=a['bytes'] or sha(archive)!=a['sha256']:raise ValueError('Assembled archive mismatch')
        destination=ROOT/('projects' if a.get('example') else 'resources')/a['id']
        result={'archive_id':a['id'],'archive_relative_path':str(archive.relative_to(ROOT)),'archive_sha256_verified':True,**module.extract(archive,destination)}
        result['destination_relative']=str(destination.relative_to(ROOT));write_json(proof,result);results.append(result)
    return results
def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=['pending','commit','extract-ready','progress']);p.add_argument('--limit',type=int,default=8);p.add_argument('--archive');p.add_argument('--part',type=int);p.add_argument('--source',type=Path);a=p.parse_args()
    if a.action=='pending':r=pending(a.limit)
    elif a.action=='commit':r=commit(a.archive,a.part,a.source)
    elif a.action=='extract-ready':r=extract_ready()
    else:
        m=manifest();receipts=list((ROOT/'inventory/restore-receipts').glob('*.json'));r={'verified_parts':len(receipts),'total_parts':sum(len(x['parts']) for x in m['archives']),'extracted_archives':len(list((ROOT/'inventory/extractions').glob('*.json')))}
    print(json.dumps(r))
if __name__=='__main__':main()
