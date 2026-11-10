#!/usr/bin/env python3
"""Build or verify a complete offline inventory of this portable library.

No network, installed package, database or fixed workspace path is required.
Run `python3 tools/build_inventory.py` after the library has stopped changing.
Run `python3 tools/build_inventory.py --verify` to check its last snapshot.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
from datetime import datetime, timezone
import gzip
import hashlib
import json
import os
from pathlib import Path
import stat
import sys

DEFAULT_ROOT = Path(__file__).resolve().parents[1]
GENERATED = (
    'ALL-FILES.csv', 'ALL-FILES.json', 'ALL-FILES.json.gz', 'CODE.csv',
    'VIDEOS.csv', 'ANALYSIS.csv', 'AUDIO.csv', 'ASSETS.csv', 'index.html',
    'README.md', 'summary.json',
)
SKIP_DIRS = frozenset({'.git', '__pycache__', '.cache', '.pytest_cache',
                       '.mypy_cache', '.ruff_cache', 'node_modules', '.venv',
                       'venv', '.ssh', '.aws', '.azure'})
SECRET_NAMES = frozenset({'.git-credentials', '.npmrc', '.pypirc',
                          'credentials.json', 'secrets.json', 'token.json',
                          'tokens.json', 'id_rsa', 'id_ed25519'})
CODE_SUFFIXES = frozenset({'.py', '.js', '.mjs', '.cjs', '.jsx', '.ts', '.tsx',
                           '.html', '.css', '.scss', '.sh', '.bash', '.swift',
                           '.rs', '.go', '.lua', '.sql', '.glsl', '.frag',
                           '.vert', '.bat', '.ps1'})
VIDEO_SUFFIXES = frozenset({'.mp4', '.mov', '.webm', '.m4v', '.avi', '.mkv'})
AUDIO_SUFFIXES = frozenset({'.wav', '.mp3', '.m4a', '.aac', '.flac', '.ogg', '.aif', '.aiff'})
ASSET_SUFFIXES = frozenset({'.png', '.jpg', '.jpeg', '.webp', '.gif', '.svg',
                            '.avif', '.heic', '.ttf', '.otf', '.woff', '.woff2'})
ANALYSIS_PARTS = frozenset({'analysis', 'verification', 'comparisons',
                            'timeline-scans', 'source-studies', 'atlas',
                            'reports', 'release-evidence'})
CONFIG_NAMES = frozenset({'package.json', 'package-lock.json', 'requirements.txt',
                          'pyproject.toml', 'uv.lock', 'Cargo.toml', 'Cargo.lock',
                          'Dockerfile', 'Makefile', 'justfile', 'Procfile',
                          'CMakeLists.txt'})
FIELDS = ('relative_path', 'absolute_path_at_generation', 'category', 'roles',
          'bytes', 'sha256', 'integrity', 'file_type', 'archive_id',
          'video_role', 'is_code', 'is_video', 'is_analysis', 'is_audio',
          'is_asset', 'note')


def credential_name(name: str) -> bool:
    low = name.lower()
    if low in SECRET_NAMES:
        return True
    if low == '.env' or low.startswith('.env.'):
        return not any(x in low for x in ('example', 'sample', 'template'))
    return False


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as stream:
        while data := stream.read(1024 * 1024):
            h.update(data)
    return h.hexdigest()


def atomic_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + '.writing')
    tmp.write_text(text, encoding='utf-8')
    os.replace(tmp, path)


def classify(rel: str) -> dict:
    p = Path(rel)
    parts = set(p.parts)
    low = rel.lower()
    suffix = p.suffix.lower()
    is_video = suffix in VIDEO_SUFFIXES
    is_audio = suffix in AUDIO_SUFFIXES
    is_asset = suffix in ASSET_SUFFIXES
    is_analysis = bool(parts & ANALYSIS_PARTS) or any(x in p.name.lower() for x in
        ('audit', 'comparison', 'metrics', 'scan', 'provenance', 'peak-segments'))
    scene = p.name == 'scene.json' or ('scenes' in parts and suffix == '.json')
    is_code = suffix in CODE_SUFFIXES or scene or p.name in CONFIG_NAMES
    archive_part = 'resource-parts' in parts
    archive = suffix in {'.zip', '.tar', '.tgz', '.gz', '.7z'}
    if archive_part:
        category = 'archive-part'
    elif archive:
        category = 'archive'
    elif is_video:
        category = 'video'
    elif is_audio:
        category = 'audio'
    elif scene:
        category = 'complete-scene-data'
    elif is_analysis and not is_asset:
        category = 'analysis-and-evidence'
    elif is_code:
        category = 'source-code-and-runtime-config'
    elif is_asset:
        category = 'font' if suffix in {'.ttf', '.otf', '.woff', '.woff2'} else 'image-and-vector-asset'
    elif suffix in {'.md', '.txt', '.pdf', '.rtf'}:
        category = 'documentation-and-license'
    elif suffix in {'.json', '.csv', '.yaml', '.yml', '.toml', '.lock'}:
        category = 'data-and-configuration'
    else:
        category = 'other-library-file'
    roles = [label for label, yes in [('code', is_code), ('video', is_video),
             ('analysis', is_analysis), ('audio', is_audio), ('asset', is_asset)] if yes]
    if archive_part:
        roles.append('duplicate-fragment-of-assembled-archive')
    archive_id = ''
    if len(p.parts) > 1 and p.parts[0] in {'projects', 'resources'}:
        archive_id = p.parts[1]
    elif len(p.parts) > 2 and p.parts[:2] == ('archives', 'resource-parts'):
        archive_id = p.parts[2]
    elif p.parts and p.parts[0] == 'archives' and p.name.endswith('.zip'):
        archive_id = p.stem
    video_role = ''
    if is_video:
        if p.name == 'source.mp4' or ('references' in parts and 'deliverables' not in parts):
            video_role = 'original-reference-or-source'
        elif 'silent' in low:
            video_role = 'silent-picture-master'
        elif any(x in low for x in ('ui-audio', 'ui_audio', 'sound-preview', 'audio-preview')):
            video_role = 'ui-audio-preview-or-result'
        elif 'deliverables' in parts:
            video_role = 'finished-deliverable'
        else:
            video_role = 'retained-video-or-working-preview'
    return dict(category=category, roles=';'.join(roles), archive_id=archive_id,
                video_role=video_role, is_code=is_code, is_video=is_video,
                is_analysis=is_analysis, is_audio=is_audio, is_asset=is_asset)


def scan(root: Path) -> tuple[list[dict], list[dict], list[dict]]:
    rows, excluded, unstable = [], [], []
    generated = {'inventory/' + name for name in GENERATED}
    for directory, dirs, names in os.walk(root, followlinks=False):
        base = Path(directory)
        for name in list(dirs):
            path = base / name
            rel = path.relative_to(root).as_posix()
            if name in SKIP_DIRS:
                dirs.remove(name)
                excluded.append({'relative_path': rel + '/', 'reason': 'version-control, installed dependency, cache or credential directory'})
            elif path.is_symlink():
                dirs.remove(name)
                names.append(name)
        for name in names:
            path = base / name
            rel = path.relative_to(root).as_posix()
            if rel in generated or any(rel == g + '.writing' for g in generated):
                continue
            if name == '.git' or credential_name(name):
                excluded.append({'relative_path': rel, 'reason': 'version-control internals or credential filename'})
                continue
            if name.endswith(('.copying', '.assembling', '.extracting', '.writing', '.tmp')):
                excluded.append({'relative_path': rel, 'reason': 'incomplete transient write; rerun after writers finish'})
                continue
            info = path.lstat()
            row = {'relative_path': rel, 'absolute_path_at_generation': str(path),
                   **classify(rel), 'bytes': info.st_size, 'note': ''}
            if stat.S_ISLNK(info.st_mode):
                row.update(file_type='symlink', sha256='', integrity='metadata-only-symlink-not-followed',
                           note='Link target: ' + os.readlink(path))
            elif stat.S_ISREG(info.st_mode):
                hash_value = digest(path)
                after = path.stat()
                if (info.st_size, info.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
                    unstable.append({'relative_path': rel, 'reason': 'file changed during streaming hash'})
                    continue
                row.update(file_type='regular', sha256=hash_value, integrity='sha256-of-complete-file')
            else:
                excluded.append({'relative_path': rel, 'reason': 'not a regular file or symlink'})
                continue
            rows.append(row)
    for name in GENERATED:
        rel = 'inventory/' + name
        rows.append({'relative_path': rel, 'absolute_path_at_generation': str(root/rel),
                     'category': 'generated-inventory-index', 'roles': 'generated-index',
                     'bytes': '', 'sha256': '', 'integrity': 'metadata-only-generated-index',
                     'file_type': 'regular', 'archive_id': '', 'video_role': '',
                     'is_code': name == 'index.html', 'is_video': False,
                     'is_analysis': True, 'is_audio': False, 'is_asset': False,
                     'note': 'Listed without size/hash to avoid a recursive self-checksum cycle; regenerated from payload files.'})
    return sorted(rows, key=lambda x: x['relative_path']), excluded, unstable


def csv_text(rows: list[dict]) -> str:
    import io
    buffer = io.StringIO(newline='')
    writer = csv.DictWriter(buffer, fieldnames=FIELDS, lineterminator='\n')
    writer.writeheader()
    for row in rows:
        writer.writerow({key: row.get(key, '') for key in FIELDS})
    return buffer.getvalue()


def html_text(rows: list[dict], summary: dict) -> str:
    # Embed compact data: opening file:// needs no fetch(), server or web account.
    data = [[r['relative_path'], r['category'], r['bytes'], r['sha256'],
             r['roles'], r['integrity'], r['note']] for r in rows]
    embedded = json.dumps({'rows': data, 'root': summary['root_at_generation'],
                           'generated': summary['generated_utc']}, ensure_ascii=False,
                          separators=(',', ':')).replace('<', '\\u003c')
    return '''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Complete local file inventory</title><style>
:root{color-scheme:light;--paper:#f8f6ef;--ink:#292b25;--muted:#6c7065;--rule:#d7d8cc}*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:15px/1.5 system-ui,sans-serif}main{max-width:1500px;margin:auto;padding:32px 5%}h1{font:clamp(32px,5vw,58px)/1.1 Georgia,serif;font-weight:400;margin:22px 0}a{color:inherit;text-underline-offset:3px}p{max-width:1000px}.muted{color:var(--muted);font-size:13px}code{font:11px/1.5 ui-monospace,monospace;overflow-wrap:anywhere}.controls{display:grid;grid-template-columns:minmax(190px,1fr) 210px 180px;gap:12px;margin:26px 0 12px}label{display:grid;gap:6px;font-size:12px}input,select{font:inherit;padding:11px 12px;border:1px solid var(--rule);background:#fffef8;border-radius:5px;min-width:0}input:focus-visible,select:focus-visible,a:focus-visible{outline:2px solid #475e9d;outline-offset:3px}.links{display:flex;flex-wrap:wrap;gap:10px 20px;margin:20px 0}.links a{font-size:12px}table{border-collapse:collapse;width:100%;table-layout:fixed;font-size:12px}th,td{border-bottom:1px solid var(--rule);padding:12px 8px;vertical-align:top;text-align:left}th{font-size:10px;text-transform:uppercase;letter-spacing:.04em}th:first-child{width:56%}th:nth-child(2){width:17%}th:nth-child(3){width:12%}th:nth-child(4){width:15%}.file{display:block;overflow-wrap:anywhere;font:12px/1.5 ui-monospace,monospace}.sub{font-size:10px;color:var(--muted);display:block;margin-top:4px;overflow-wrap:anywhere}.hash{font:10px/1.5 ui-monospace,monospace;overflow-wrap:anywhere}button{font:inherit;padding:9px 15px;border:1px solid var(--rule);border-radius:4px;background:#fffef8;color:var(--ink);cursor:pointer}footer{padding:26px 0}.notice{border-block:1px solid var(--rule);padding:16px 0;font-size:12px}#empty{padding:25px 0}@media(max-width:700px){main{padding:22px 5%}.controls{grid-template-columns:1fr}table,tbody,tr,td{display:block}thead{display:none}tr{border-bottom:1px solid var(--rule);padding:10px 0}td{border:0;padding:5px 0}.hash:before{content:'SHA256: ';font-family:system-ui}.links{gap:10px 14px}}
</style></head><body><main>
<nav class="links"><a href="../START-HERE.md">Start here</a><a href="../catalog/index.html">Videos and full code viewer</a><a href="../reports/SKILL-CONTENTS-AND-GAPS.md">Skill contents and gaps</a><a href="README.md">Inventory rules</a></nav>
<h1>Every local library file.</h1>
<p>Search actual code, complete scene data, finished films, originals, frame analysis, UI sound, assets and archived history. All links use relative paths, so moving the entire folder preserves them. No internet request, external font or JavaScript library is required.</p>
<p class="muted" id="root"></p>
<div class="notice">Archive fragments are retained and labelled as duplicates of the assembled ZIP bytes. Generated inventory files are listed without size/hash to avoid recursive checksums. Version-control internals, installed dependencies, caches and credential files are excluded explicitly in <a href="summary.json">summary.json</a>.</div>
<div class="links"><a href="ALL-FILES.csv" download>All files · CSV</a><a href="ALL-FILES.json" download>All files · JSON</a><a href="CODE.csv" download>Code</a><a href="VIDEOS.csv" download>Videos</a><a href="ANALYSIS.csv" download>Analysis</a><a href="AUDIO.csv" download>Audio</a><a href="ASSETS.csv" download>Images and fonts</a></div>
<div class="controls"><label>Find any path, role, hash or filename<input id="query" type="search" placeholder="e.g. 05-linq, scene.json, render_pillow, frames.csv" autocomplete="off"></label><label>Resource type<select id="role"><option value="">All files</option><option value="code">Code and complete scenes</option><option value="video">Videos</option><option value="analysis">Analysis and evidence</option><option value="audio">Audio</option><option value="asset">Images, vectors and fonts</option><option value="duplicate-fragment-of-assembled-archive">Archive parts</option></select></label><label>Order<select id="order"><option value="path">File path</option><option value="largest">Largest first</option><option value="category">Category</option></select></label></div>
<p id="status" role="status" aria-live="polite" class="muted"></p>
<table><thead><tr><th>Actual relative file location</th><th>Category</th><th>Bytes</th><th>SHA256</th></tr></thead><tbody id="files"></tbody></table><p id="empty" hidden>No matching files.</p>
<footer><button id="more" type="button" hidden>Show 250 more</button><p class="muted">The full CSV/JSON contains every inventory row; the page initially shows at most 250 matching rows. Historical absolute paths inside old evidence files remain provenance labels. The file locations above are the actual restored paths.</p></footer>
<script id="inventory-data" type="application/json">''' + embedded + '''</script>
<script>
'use strict';
const data=JSON.parse(document.getElementById('inventory-data').textContent),$=id=>document.getElementById(id),rows=data.rows.map(r=>({r,search:r.join(' ').toLowerCase(),roles:r[4].split(';')}));
$('root').textContent='Snapshot: '+data.generated+' · current machine root when generated: '+data.root;
let limit=250,lastMatches=[];
const link=p=>'../'+p.split('/').map(encodeURIComponent).join('/');
function render(reset=true){if(reset)limit=250;const words=$('query').value.toLowerCase().trim().split(/\\s+/).filter(Boolean),role=$('role').value,order=$('order').value;
const found=rows.filter(x=>(!role||x.roles.includes(role))&&words.every(w=>x.search.includes(w)));
if(order==='largest')found.sort((a,b)=>(Number(b.r[2])||0)-(Number(a.r[2])||0)||a.r[0].localeCompare(b.r[0]));else if(order==='category')found.sort((a,b)=>a.r[1].localeCompare(b.r[1])||a.r[0].localeCompare(b.r[0]));
lastMatches=found;const fragment=document.createDocumentFragment();
for(const {r} of found.slice(0,limit)){const tr=document.createElement('tr'),path=document.createElement('td'),a=document.createElement('a');a.className='file';a.href=link(r[0]);a.textContent=r[0];path.append(a);if(r[6]){const n=document.createElement('span');n.className='sub';n.textContent=r[6];path.append(n);}const category=document.createElement('td');category.textContent=r[1];const bytes=document.createElement('td');bytes.textContent=r[2]===''?'generated index':Number(r[2]).toLocaleString();const hash=document.createElement('td');hash.className='hash';hash.textContent=r[3]||r[5];tr.append(path,category,bytes,hash);fragment.append(tr);}
$('files').replaceChildren(fragment);$('status').textContent=found.length.toLocaleString()+' matching files / '+rows.length.toLocaleString()+' indexed · showing '+Math.min(limit,found.length).toLocaleString();$('empty').hidden=found.length>0;$('more').hidden=found.length<=limit;}
let timer;$('query').addEventListener('input',()=>{clearTimeout(timer);timer=setTimeout(()=>render(),100)});$('role').addEventListener('change',()=>render());$('order').addEventListener('change',()=>render());$('more').addEventListener('click',()=>{limit+=250;render(false)});render();
</script></main></body></html>'''


def build(root: Path) -> dict:
    destination = root/'inventory'
    destination.mkdir(parents=True, exist_ok=True)
    rows, excluded, unstable = scan(root)
    generated = datetime.now(timezone.utc).isoformat(timespec='seconds')
    regular = [r for r in rows if r['integrity'] == 'sha256-of-complete-file']
    summary = {
        'schema_version': 1, 'generated_utc': generated,
        'root_at_generation': str(root), 'portable_path_authority': 'relative_path',
        'indexed_rows': len(rows), 'hashed_regular_files': len(regular),
        'hashed_bytes': sum(r['bytes'] for r in regular),
        'category_counts': dict(sorted(Counter(r['category'] for r in rows).items())),
        'role_counts': {role: sum(bool(r['is_'+role]) for r in rows)
                        for role in ('code', 'video', 'analysis', 'audio', 'asset')},
        'generated_metadata_only_files': ['inventory/'+n for n in GENERATED],
        'excluded_paths': sorted(excluded, key=lambda x:x['relative_path']),
        'unstable_files_not_indexed': unstable,
        'symlinks_not_followed': sum(r['file_type']=='symlink' for r in rows),
        'inventory_rules': [
            'Actual stable files in this library are inventoried; all file hashing streams at most 1 MiB per read.',
            'Generated inventory artifacts list their own paths but omit bytes/hashes to avoid recursive self-checksums.',
            'Installed dependencies/caches, version-control internals and credential filenames are excluded, not authored source.',
            'Archive parts and assembled ZIPs both remain listed; their bytes duplicate archive payload.',
            'Category is one label; is_code/is_video/is_analysis/is_audio/is_asset can overlap. Filtered CSVs use these flags.',
            'Absolute paths are current-machine conveniences, not dependencies. Relative paths remain valid after moving the folder.',
            'Re-run after all downloads/writers finish, and after adding, removing or editing files.',
        ],
    }
    result = {'schema_version': 1, 'root_at_generation': str(root),
              'generated_utc': generated, 'path_authority': 'relative_path',
              'rows': rows}
    encoded = json.dumps(result, ensure_ascii=False, indent=2)+'\n'
    atomic_text(destination/'ALL-FILES.json', encoded)
    gz_temp=destination/'ALL-FILES.json.gz.writing'
    with gz_temp.open('wb') as stream:
        with gzip.GzipFile(filename='', mode='wb', fileobj=stream, mtime=0) as compressed:
            compressed.write(encoded.encode('utf-8'))
    os.replace(gz_temp, destination/'ALL-FILES.json.gz')
    atomic_text(destination/'ALL-FILES.csv', csv_text(rows))
    for filename, flag in [('CODE.csv','is_code'), ('VIDEOS.csv','is_video'),
                           ('ANALYSIS.csv','is_analysis'), ('AUDIO.csv','is_audio'),
                           ('ASSETS.csv','is_asset')]:
        atomic_text(destination/filename, csv_text([r for r in rows if r[flag]]))
    atomic_text(destination/'summary.json',json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    atomic_text(destination/'index.html',html_text(rows,summary))
    readme = '''# Complete offline inventory

Open [index.html](index.html) for local search. [ALL-FILES.csv](ALL-FILES.csv) and [ALL-FILES.json](ALL-FILES.json) contain every inventory row. The same JSON is available compressed in [ALL-FILES.json.gz](ALL-FILES.json.gz). Filtered lists: [code and scene data](CODE.csv), [videos](VIDEOS.csv), [analysis](ANALYSIS.csv), [audio](AUDIO.csv), [images/vectors/fonts](ASSETS.csv).

Every stable authored/library file is listed with its actual relative path, current absolute path, byte count, complete streaming SHA256 and role flags. Complete scene JSON is code/data, not a missing separate application. Category is a single convenient label; roles overlap, so an HTML comparison can appear in both code and analysis. Filtered lists include duplicate archival copies and do not claim unique authored works.

Archive fragments under `archives/resource-parts/` are retained, explicitly labelled duplicates of assembled archive bytes. Directory entries themselves are not payload files. Symlinks are listed as metadata without following them outside the library. No network requests, external scripts, fonts or account are required to browse this index.

Generated inventory files list their own paths with `metadata-only-generated-index`, omitting their sizes and hashes to prevent a recursive self-checksum cycle. `.git` internals, installed dependency/cache directories and credential filenames are excluded. Temporary in-progress writes are excluded. Every observed exclusion and any unstable file is listed in [summary.json](summary.json); these are explicit scope boundaries, not hidden omissions. Historical absolute paths inside old research/scan reports remain original provenance labels; use the inventory's `relative_path` to locate restored files.

Generate a fresh snapshot after the library has stopped changing:

```bash
python3 tools/build_inventory.py
python3 tools/build_inventory.py --verify
```

These commands run from the library root; the helper derives that root from its own location, so it also works after the whole folder is moved. `--root /another/library` is available for explicit inspection. Verification checks every stored payload hash and flags added/missing/changed files; generated indexes are checked for existence, not self-hashed. Rebuild the inventory after intentional edits. No Python packages beyond the standard library are used.
'''
    atomic_text(destination/'README.md',readme)
    return summary


def verify(root: Path) -> dict:
    stored=json.loads((root/'inventory/ALL-FILES.json').read_text(encoding='utf-8'))
    missing, changed, generated_missing=[],[],[]
    expected=set()
    for row in stored['rows']:
        rel=row['relative_path'];expected.add(rel)
        p=(root/rel)
        # A hand-edited manifest cannot turn verification into an outside-root read.
        if Path(rel).is_absolute() or '..' in Path(rel).parts:
            raise ValueError('Unsafe inventory path: '+rel)
        if not p.parent.resolve().is_relative_to(root):
            changed.append(rel)
            continue
        if row['integrity']=='metadata-only-generated-index':
            if not p.is_file():generated_missing.append(rel)
        elif row['file_type']=='symlink':
            if not p.is_symlink():missing.append(rel)
            elif 'Link target: '+os.readlink(p)!=row['note']:changed.append(rel)
        elif p.is_symlink():changed.append(rel)
        elif not p.is_file():missing.append(rel)
        elif p.stat().st_size!=row['bytes'] or digest(p)!=row['sha256']:changed.append(rel)
    current, excluded, unstable=scan(root)
    added=sorted(r['relative_path'] for r in current if r['relative_path'] not in expected)
    ok=not(missing or changed or added or generated_missing or unstable)
    return {'status':'pass' if ok else 'fail','checked_rows':len(stored['rows']),
            'missing_files':missing,'changed_files':changed,'added_files':added,
            'missing_generated_indexes':generated_missing,'unstable_files':unstable,
            'excluded_paths_count':len(excluded)}


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=DEFAULT_ROOT)
    parser.add_argument('--verify',action='store_true')
    args=parser.parse_args();root=args.root.resolve()
    if not root.is_dir():raise ValueError('Library root is not a directory')
    result=verify(root) if args.verify else build(root)
    # Keep shell output compact; complete file paths remain in the written index.
    if args.verify:
        print(json.dumps(result,ensure_ascii=False,indent=2))
        if result['status']!='pass':sys.exit(1)
    else:
        print(json.dumps({k:result[k] for k in ('indexed_rows','hashed_regular_files',
              'hashed_bytes','role_counts','root_at_generation','unstable_files_not_indexed')},indent=2))
        if result['unstable_files_not_indexed']:sys.exit(2)


if __name__=='__main__':main()
