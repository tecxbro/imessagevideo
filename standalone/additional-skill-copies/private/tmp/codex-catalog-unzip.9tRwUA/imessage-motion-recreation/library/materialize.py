#!/usr/bin/env python3
"""Plan authenticated retrieval, join verified parts, and safely extract a pack.

Drive reads happen through the connected MCP tools, not through public URLs or
embedded credentials. Download each listed part first, then pass its local path.
"""
from pathlib import Path,PurePosixPath
import argparse,hashlib,json,os,shutil,stat,zipfile

HERE=Path(__file__).resolve().parent
def sha(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def record(manifest,ident):
    for item in manifest['archives']:
        if item['id']==ident:return item
    raise ValueError('Unknown archive: '+ident)
def plan(item):
    return {'archive':item['id'],'bytes':item['bytes'],'sha256':item['sha256'],
            'connection':item.get('account_link_id'),
            'instructions':['Use google_drive.get_file_metadata to confirm the file MIME/size/permissions.','Use google_drive.fetch(download_raw_file=true, include_base64=false) for each observed Drive URL.','Use the top-level authenticated file_uri; for a sediment://file_ reference call download_file with the bare file ID. Every part is at most24MiB.','Do not paste signed download URLs into the skill or logs.','Copy/record the returned local part paths, then run this script assemble with --part-map or --parts-dir.'],
            'parts':[{k:p[k] for k in ['number','file_name','bytes','sha256','drive_id','drive_url']} for p in item['parts']]}
def assemble(item,parts_dir,part_map,out):
    lookup={int(k):Path(v) for k,v in (json.loads(part_map.read_text()).items() if part_map else [])}
    total=0;out.parent.mkdir(parents=True,exist_ok=True);temp=out.with_suffix(out.suffix+'.assembling');h=hashlib.sha256()
    try:
        with temp.open('wb') as target:
            for part in item['parts']:
                source=lookup.get(part['number']) or (parts_dir/part['file_name'] if parts_dir else None)
                if source is None or not source.is_file():raise FileNotFoundError('Missing materialized part '+str(part['number']))
                if source.stat().st_size!=part['bytes'] or sha(source)!=part['sha256']:raise ValueError('Part checksum mismatch '+str(source))
                with source.open('rb') as stream:
                    while data:=stream.read(1024*1024):target.write(data);h.update(data);total+=len(data)
        if total!=item['bytes'] or h.hexdigest()!=item['sha256']:raise ValueError('Assembled archive differs from registry')
        os.replace(temp,out)
    finally:temp.unlink(missing_ok=True)
    return out
def extract(archive,destination):
    destination=destination.resolve();destination.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(archive) as z:
        entries=z.infolist();needed=sum(e.file_size for e in entries)
        if needed>shutil.disk_usage(destination).free:raise ValueError(f'Need {needed} free bytes for extracted content; choose a larger working volume')
        checks_name=next((n for n in z.namelist() if n.endswith('/PACK-CHECKSUMS.json')),None)
        checks=json.loads(z.read(checks_name)) if checks_name else None
        prefix=checks_name.rsplit('/',1)[0]+'/' if checks_name else None
        seen=set()
        for e in entries:
            path=PurePosixPath(e.filename);mode=stat.S_IFMT(e.external_attr>>16)
            if path.is_absolute() or '..' in path.parts or '\\' in e.filename or mode==stat.S_IFLNK or e.filename in seen:raise ValueError('Unsafe archive path '+e.filename)
            seen.add(e.filename)
            # Complementary packs have different checksum maps. Keep those as
            # separate receipts so font/audio packs can join one working project.
            if e.filename==checks_name:
                receipt=hashlib.sha256(z.read(e)).hexdigest()+'-PACK-CHECKSUMS.json'
                target=(destination/'.library-receipts'/receipt).resolve()
            else:target=(destination/e.filename).resolve()
            if not target.is_relative_to(destination):raise ValueError('Archive escapes destination')
            if e.is_dir():target.mkdir(parents=True,exist_ok=True);continue
            data=z.read(e)
            if checks is not None and e.filename!=checks_name:
                rel=e.filename.removeprefix(prefix)
                if rel not in checks or hashlib.sha256(data).hexdigest()!=checks[rel]:raise ValueError('Payload checksum mismatch '+e.filename)
            if target.exists():
                if sha(target)!=hashlib.sha256(data).hexdigest():raise ValueError('Existing file differs; use an isolated destination: '+str(target))
                continue
            target.parent.mkdir(parents=True,exist_ok=True);temp=target.with_suffix(target.suffix+'.extracting');temp.write_bytes(data);os.replace(temp,target)
    return {'files':len(entries),'expanded_bytes':needed,'destination':str(destination),'all_entry_crcs_read':True,'pack_checksums_verified':checks is not None}
def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=['list','plan','assemble','verify']);p.add_argument('--manifest',type=Path,default=HERE/'manifest.json');p.add_argument('--archive');p.add_argument('--parts-dir',type=Path);p.add_argument('--part-map',type=Path);p.add_argument('--out',type=Path);p.add_argument('--extract-to',type=Path);a=p.parse_args();m=json.loads(a.manifest.read_text())
    if a.action=='list':print(json.dumps([{'id':x['id'],'bytes':x['bytes'],'category':x['category']} for x in m['archives']],indent=2));return
    item=record(m,a.archive)
    if a.action=='plan':print(json.dumps(plan(item),indent=2));return
    if not a.out:raise ValueError('--out is required')
    if a.action=='assemble':assemble(item,a.parts_dir,a.part_map,a.out)
    if a.out.stat().st_size!=item['bytes'] or sha(a.out)!=item['sha256']:raise ValueError('Archive differs from registry')
    result={'archive':item['id'],'bytes':item['bytes'],'sha256':item['sha256'],'verified':True}
    if a.extract_to:result['extraction']=extract(a.out,a.extract_to)
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
