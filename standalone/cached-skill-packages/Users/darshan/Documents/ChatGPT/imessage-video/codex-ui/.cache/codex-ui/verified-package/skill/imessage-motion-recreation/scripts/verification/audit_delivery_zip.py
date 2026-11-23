#!/usr/bin/env python3
"""Stream-audit a delivery ZIP and its source-only nested skill ZIP.
No archive members are extracted. Only small checksum manifests and the bounded
compressed skill ZIP are held in memory. Optional --stage hashes existing files;
it never creates a second extracted tree.
"""
from pathlib import Path
import argparse,base64,hashlib,io,json,os,re,stat,tempfile,time,unicodedata,zipfile,zlib

ROOT=Path(__file__).resolve().parents[1]
CHUNK=1024*1024
MAX_MANIFEST=32*1024*1024
MAX_SKILL_ZIP=64*1024*1024
MAX_SKILL_RAW=256*1024*1024
FONT_EXT={'.otf','.ttf','.ttc','.otc','.woff','.woff2','.eot','.dfont','.pfb','.pfa'}
VIDEO_EXT={'.mp4','.m4v','.mov','.webm','.mkv','.avi','.mpeg','.mpg','.m2v','.mts','.m2ts','.flv','.3gp','.ogv'}
DATA_URI=re.compile(rb'data:((?:font|video)/[^;,\s\"\']+|application/(?:font-[^;,\s\"\']+|x-font-[^;,\s\"\']+|vnd\.ms-fontobject));base64,([A-Za-z0-9+/]{16,64})',re.I)


def sha_file(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as source:
        for chunk in iter(lambda:source.read(CHUNK),b''):h.update(chunk)
    return h.hexdigest()


def path_error(name):
    if not name or '\\' in name or name.startswith('/') or re.match(r'^[A-Za-z]:',name):return 'absolute, empty or backslash path'
    if any(ord(c)<32 or ord(c)==127 for c in name):return 'control character in path'
    for part in name.split('/'):
        if part in ('','.','..'):return 'empty/dot/traversal path component'
        if ':' in part or part.endswith((' ','.')):return 'nonportable path component'
        if re.fullmatch(r'(?i)(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\..*)?',part):return 'reserved device path component'
    return None


def unique_object(pairs):
    result={}
    for key,value in pairs:
        if key in result:raise ValueError('Duplicate checksum key: '+key)
        result[key]=value
    return result


def manifest_bytes(raw):
    result=json.loads(raw,object_pairs_hook=unique_object)
    if not isinstance(result,dict):raise ValueError('Checksums must be a JSON object')
    for name,digest in result.items():
        if not isinstance(name,str) or path_error(name):raise ValueError('Unsafe checksum path: '+str(name))
        if not isinstance(digest,str) or not re.fullmatch('[0-9a-f]{64}',digest):raise ValueError('Invalid SHA256 for '+name)
    if 'checksums.json' in result:raise ValueError('Root checksum manifest must exclude only itself')
    return result


def content_kind(header):
    if header[:4] in (b'OTTO',b'ttcf',b'wOFF',b'wOF2',b'true',b'typ1',b'\x00\x01\x00\x00'):return 'font binary signature'
    if header[4:8]==b'ftyp' or header.startswith((b'\x1aE\xdf\xa3',b'FLV',b'\x00\x00\x01\xba',b'\x00\x00\x01\xb3')):return 'video/container signature'
    if header.startswith(b'RIFF') and header[8:12]==b'AVI ':return 'AVI video signature'
    return None


def source_payload_issues(name,header):
    issues=[]
    if any(s.lower() in FONT_EXT|VIDEO_EXT for s in Path(name).suffixes):issues.append('font/video filename extension')
    kind=content_kind(header)
    if kind:issues.append(kind)
    return issues


def verify_coverage(manifest,hashes):
    wanted=set(manifest);actual=set(hashes)-{'checksums.json'}
    missing=sorted(wanted-actual);unhashed=sorted(actual-wanted)
    mismatch=sorted(name for name in wanted&actual if hashes[name]!=manifest[name])
    return {'passed':not(missing or unhashed or mismatch),'manifestEntries':len(manifest),'hashedPayloadEntries':len(actual),
        'missingEntries':missing,'unhashedEntries':unhashed,'sha256Mismatches':mismatch}


def audit_zip(packed,prefix,*,source_only=False,captures=None,source_tree=None):
    """Verify each ZIP stream; names, manifest and SHA use relative paths."""
    errors=[];rows=[];hashes={};buffers={};infos=packed.infolist();seen=set();portable_seen={};capture_limits={'checksums.json':MAX_MANIFEST,**(captures or {})}
    if path_error(prefix) or '/' in prefix:raise ValueError('ZIP prefix must be one safe directory name')
    if source_only and sum(i.file_size for i in infos)>MAX_SKILL_RAW:raise ValueError('Source-only skill exceeds bounded uncompressed size')
    for info in infos:
        name=info.filename;relative=None;row={'name':name,'bytes':info.file_size,'compressedBytes':info.compress_size,'crc32Expected':f'{info.CRC:08x}'}
        problem=path_error(name)
        if info.orig_filename!=name:problem='NUL-truncated entry name'
        if not name.startswith(prefix+'/'):problem='entry outside required root prefix'
        if problem:errors.append({'entry':name,'problem':problem})
        else:relative=name[len(prefix)+1:];row['relativePath']=relative
        if name in seen:errors.append({'entry':name,'problem':'duplicate ZIP entry name'})
        seen.add(name);portable=unicodedata.normalize('NFC',name).casefold()
        if portable in portable_seen and portable_seen[portable]!=name:errors.append({'entry':name,'problem':'case/Unicode extraction collision','other':portable_seen[portable]})
        portable_seen[portable]=name
        mode=(info.external_attr>>16)&0xffff;row['unixMode']=oct(mode)
        if info.is_dir() or info.external_attr&0x10 or stat.S_IFMT(mode)!=stat.S_IFREG:errors.append({'entry':name,'problem':'entry is not a proven regular file'})
        if info.flag_bits&1:errors.append({'entry':name,'problem':'encrypted ZIP entry'})
        if info.compress_type not in (zipfile.ZIP_STORED,zipfile.ZIP_DEFLATED):errors.append({'entry':name,'problem':'unexpected compression method'})
        policy=source_only or (relative is not None and source_tree is not None and relative.startswith(source_tree+'/'))
        if policy:
            for issue in source_payload_issues(name,b''):errors.append({'entry':name,'problem':issue})
        capture_limit=capture_limits.get(relative);capture=bytearray() if capture_limit and info.file_size<=capture_limit else None
        if capture_limit and capture is None:errors.append({'entry':name,'problem':'captured metadata/archive exceeds memory bound'})
        digest=hashlib.sha256();crc=0;size=0;tail=b'';first=True;embedded=set()
        try:
            with packed.open(info) as source:
                for chunk in iter(lambda:source.read(CHUNK),b''):
                    size+=len(chunk);digest.update(chunk);crc=zlib.crc32(chunk,crc)
                    if capture is not None:
                        if size>capture_limit:raise ValueError('Payload exceeded capture bound')
                        capture.extend(chunk)
                    if policy:
                        if first:
                            kind=content_kind(chunk[:32])
                            if kind:errors.append({'entry':name,'problem':kind})
                        for match in DATA_URI.finditer(tail+chunk):
                            encoded=match[2];encoded=encoded[:len(encoded)//4*4]
                            try:signature=base64.b64decode(encoded,validate=True)
                            except ValueError:continue
                            kind=content_kind(signature)
                            if kind:embedded.add('embedded '+match[1].decode('ascii',errors='replace')+' '+kind)
                        tail=chunk[-256:]
                    first=False
            row.update(crc32Actual=f'{crc&0xffffffff:08x}',sha256=digest.hexdigest(),bytesRead=size,crcVerified=(crc&0xffffffff)==info.CRC and size==info.file_size)
            if not row['crcVerified']:errors.append({'entry':name,'problem':'CRC/decoded-size mismatch'})
            if relative is not None:hashes[relative]=digest.hexdigest()
            if capture is not None:buffers[relative]=bytes(capture)
        except (OSError,ValueError,RuntimeError,zipfile.BadZipFile,zlib.error) as error:
            row.update(bytesRead=size,crcVerified=False,error=str(error));errors.append({'entry':name,'problem':'entry stream/CRC failure','detail':str(error)})
        for issue in sorted(embedded):errors.append({'entry':name,'problem':issue})
        rows.append(row)
    coverage=None
    try:
        manifest=manifest_bytes(buffers['checksums.json']);coverage=verify_coverage(manifest,hashes)
        if not coverage['passed']:errors.append({'problem':'checksum coverage or SHA mismatch','coverage':coverage})
    except (KeyError,ValueError,UnicodeError,json.JSONDecodeError) as error:
        errors.append({'problem':'invalid/missing root checksum manifest','detail':str(error)})
    return {'passed':not errors,'prefix':prefix,'entryCount':len(infos),'crcVerifiedEntries':sum(r.get('crcVerified',False) for r in rows),
        'decodedBytes':sum(r.get('bytesRead',0) for r in rows),'coverage':coverage,'entries':rows,'errors':errors,'_hashes':hashes,'_buffers':buffers}


def check_stage(stage,hashes):
    stage=Path(stage).resolve()
    if not (stage/'checksums.json').is_file():raise ValueError('Stage has no root checksums.json')
    files=set();errors=[]
    for current,dirs,names in os.walk(stage,followlinks=False):
        for name in dirs+names:
            path=Path(current)/name
            if path.is_symlink():errors.append({'entry':str(path.relative_to(stage)),'problem':'stage symlink'})
        for name in names:
            path=Path(current)/name
            if path.is_file() and not path.is_symlink():files.add(str(path.relative_to(stage)))
    missing=sorted(set(hashes)-files);extra=sorted(files-set(hashes));mismatch=[]
    for name in sorted(files&set(hashes)):
        if sha_file(stage/name)!=hashes[name]:mismatch.append(name)
    return {'passed':not(errors or missing or extra or mismatch),'path':str(stage),'fileCount':len(files),'missingEntries':missing,'extraEntries':extra,'sha256Mismatches':mismatch,'errors':errors}


def audit_delivery(archive,*,stage=None,prefix='imessage-recreations',skill_prefix='imessage-motion-recreation'):
    archive=Path(archive);started=time.monotonic();before=archive.stat();archive_hash=sha_file(archive);skill_name='imessage-motion-recreation-skill.zip';skill_tree='skill/'+skill_prefix;skill_manifest=skill_tree+'/checksums.json'
    with zipfile.ZipFile(archive) as packed:
        outer=audit_zip(packed,prefix,captures={skill_name:MAX_SKILL_ZIP,skill_manifest:MAX_MANIFEST},source_tree=skill_tree)
    errors=[{'area':'outer',**e} for e in outer['errors']];hashes=outer.pop('_hashes');buffers=outer.pop('_buffers');nested=None;expanded=None;representations=False
    try:
        if skill_manifest not in hashes:raise ValueError('Outer root manifest must include nested skill checksums')
        expanded_hashes={name[len(skill_tree)+1:]:digest for name,digest in hashes.items() if name.startswith(skill_tree+'/')}
        expanded=verify_coverage(manifest_bytes(buffers[skill_manifest]),expanded_hashes)
        if not expanded['passed']:errors.append({'area':'expandedSkill','problem':'skill-folder manifest mismatch','coverage':expanded})
        with zipfile.ZipFile(io.BytesIO(buffers[skill_name])) as packed:nested=audit_zip(packed,skill_prefix,source_only=True)
        nested_hashes=nested.pop('_hashes');nested.pop('_buffers')
        errors.extend({'area':'nestedSkill',**e} for e in nested['errors'])
        representations=expanded_hashes==nested_hashes
        if not representations:errors.append({'area':'skill','problem':'expanded skill folder and installable ZIP differ'})
    except (KeyError,ValueError,zipfile.BadZipFile) as error:errors.append({'area':'skill','problem':str(error)})
    stage_report=check_stage(stage,hashes) if stage else None
    if stage_report and not stage_report['passed']:errors.append({'area':'stage','problem':'stage differs from ZIP','details':stage_report})
    after=archive.stat();unchanged=(before.st_ino,before.st_size,before.st_mtime_ns)==(after.st_ino,after.st_size,after.st_mtime_ns)
    if not unchanged:errors.append({'area':'archive','problem':'archive changed during audit'})
    return {'passed':not errors,'archive':str(archive.resolve()),'archiveSHA256':archive_hash,'archiveBytes':before.st_size,'archiveUnchangedDuringAudit':unchanged,'seconds':time.monotonic()-started,
        'outer':outer,'expandedSkill':expanded,'nestedSkill':nested,'skillRepresentationsIdentical':representations,'stage':stage_report,'errors':errors,
        'notice':'Every ZIP payload is streamed for CRC and SHA; exact manifest coverage excludes only each archive root checksums.json. Outer nested skill checksums remain hashed. Skill folder/installable ZIP match and reject font/video extensions, signatures and embedded font/video dataURI payloads. No members are extracted. This checks artifact integrity/portability, not source-video fidelity or legal classification of arbitrary opaque binary data.'}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--archive',type=Path,required=True);parser.add_argument('--stage',type=Path);parser.add_argument('--out',type=Path,default=ROOT/'verification/packaging-audit/zip-audit.json');args=parser.parse_args()
    if args.out.resolve()==args.archive.resolve() or (args.stage and args.out.resolve().is_relative_to(args.stage.resolve())):raise ValueError('Audit report must be outside the ZIP and sealed stage')
    try:report=audit_delivery(args.archive,stage=args.stage)
    except Exception as error:report={'passed':False,'archive':str(args.archive),'errors':[{'problem':'audit could not complete','detail':str(error)}]}
    args.out.parent.mkdir(parents=True,exist_ok=True);descriptor,pending=tempfile.mkstemp(prefix='.zip-audit-',dir=args.out.parent)
    try:
        with os.fdopen(descriptor,'w') as output:json.dump(report,output,indent=2);output.write('\n')
        os.replace(pending,args.out)
    finally:Path(pending).unlink(missing_ok=True)
    print(json.dumps({'passed':report['passed'],'archiveSHA256':report.get('archiveSHA256'),'entries':report.get('outer',{}).get('entryCount'),'errors':report['errors'],'report':str(args.out)},indent=2));return not report['passed']

if __name__=='__main__':raise SystemExit(main())
