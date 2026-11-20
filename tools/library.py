#!/usr/bin/env python3
"""Find and verify the complete local library. No network client or credentials."""
from pathlib import Path
import argparse, csv, hashlib, json, sys

ROOT=Path(__file__).resolve().parents[1]
REGISTRY=ROOT/'LOCAL-LIBRARY.json'
ORIGINAL=ROOT/'skill/imessage-motion-recreation/library/manifest.json'


def dataset_archives():
    registry = ROOT / 'datasets/imessage/registry'
    for manifest in sorted(registry.glob('*/manifest.json')):
        archive = json.loads(manifest.read_text())['archive']
        archive_id = f'dataset-{manifest.parent.name}'
        yield {
            'id': archive_id,
            'category': 'dataset',
            'archive_path': f'archives/{archive_id}.zip',
            'bytes': archive['bytes'],
            'sha256': archive['sha256'],
            'extracted_path': f'resources/{archive_id}',
            'parts': [
                {
                    'path': (manifest.parent / part['name']).relative_to(ROOT).as_posix(),
                    'bytes': part['bytes'],
                    'sha256': part['sha256'],
                }
                for part in archive['parts']
            ],
        }


def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def index():
    old=json.loads(ORIGINAL.read_text());archives=[];examples=[]
    for a in old['archives']:
        prefix=('projects/' if a.get('example') else 'resources/')+a['id']
        archives.append({'id':a['id'],'category':a['category'],'archive_path':'archives/'+a['id']+'.zip','bytes':a['bytes'],'sha256':a['sha256'],'extracted_path':prefix,'parts':[{'path':'archives/resource-parts/'+a['id']+'/'+p['file_name'],'bytes':p['bytes'],'sha256':p['sha256']} for p in a['parts']]})
    archives.extend(dataset_archives())
    for e in old['examples']:
        base='projects/'+e['complete_project_archive']+'/imessage-recreations'
        def entry(x):return {'path':base+'/'+x['project_path'],'bytes':x['bytes'],'sha256':x['sha256']}
        examples.append({'id':e['id'],'title':e['title'],'archive_id':e['complete_project_archive'],'project_root':base,'scene':entry(e['scene']),'source':entry(e['original_reference']),'movies':[{'method':r['method'],**entry(r),'entry_wrapper':base+'/'+r['entry_wrapper'],'full_source_files':[base+'/'+p for p in r['full_source_files']]} for r in e['finished_results']],'analysis':base+'/'+e['source_frame_analysis'],'authoring_code':base+'/'+e['retained_authoring_code'],'historical_scene_label':e['scene']['original_working_path']})
    result={'schema_version':1,'storage':'local-checkout','root':'.','requires_drive_for_normal_use':False,'viewer':'catalog/index.html','file_browser':'inventory/index.html','all_files':'inventory/ALL-FILES.csv','skill':'skill/imessage-motion-recreation/SKILL.md','archives':archives,'examples':examples,'limits':['Run the offline local chunk sync before opening derived archive/oversized scene files.','Pinned third-party rendering dependencies require separate installation.','New-company online research requires internet unless sufficient local evidence is supplied.','Figma is unvalidated; historical numeric comparisons do not certify perfect identity.']}
    REGISTRY.write_text(json.dumps(result,indent=2)+'\n');return result
def load():return json.loads(REGISTRY.read_text())
def locate(query):
    library = load()
    query = query.casefold()
    matches = [
        {**example, 'absolute_project_root': str(ROOT / example['project_root'])}
        for example in library['examples']
        if query in ' '.join((example['id'], example['archive_id'], example['title'])).casefold()
    ]
    covered = {example['archive_id'] for example in matches}
    matches.extend(
        archive for archive in library['archives']
        if query in archive['id'].casefold() and archive['id'] not in covered
    )
    return matches
def verify(all_files=False):
    m=load();checked={};errors=[]
    for a in m['archives']:
        checked[a['archive_path']]=a
        for p in a['parts']:checked[p['path']]=p
    for e in m['examples']:
        for p in [e['scene'],e['source'],*e['movies']]:checked[p['path']]=p
        if not (ROOT/e['analysis']).is_file():errors.append('Missing analysis: '+e['analysis'])
        for movie in e['movies']:
            for name in [movie['entry_wrapper'],*movie['full_source_files']]:
                if not (ROOT/name).is_file():errors.append('Missing code: '+name)
    if all_files:
        inventory=ROOT/m['all_files']
        if not inventory.is_file():raise ValueError('Generate the inventory first: python tools/build_inventory.py')
        with inventory.open(newline='') as f:
            for row in csv.DictReader(f):
                name=row.get('relative_path') or row.get('path')
                digest=row.get('sha256','')
                if name and len(digest)==64:checked[name]={'bytes':int(row.get('bytes',row.get('size_bytes',row.get('size',0)))),'sha256':digest}
    for name,expect in checked.items():
        p=ROOT/name
        if not p.is_file():errors.append('Missing: '+name);continue
        if p.stat().st_size!=expect['bytes']:errors.append('Size differs: '+name);continue
        if sha(p)!=expect['sha256']:errors.append('SHA256 differs: '+name)
    result={'status':'pass' if not errors else 'fail','files_hashed':len(checked),'archive_count':len(m['archives']),'registered_parts':sum(len(a['parts']) for a in m['archives']),'examples':len(m['examples']),'errors':errors,'internet_used':False}
    print(json.dumps(result,indent=2));return not errors
def historical(query):
    q=query.removeprefix('/workspace/imessage-recreations/');m=load();hits=[]
    for e in m['examples']:
        if q==e['historical_scene_label']:hits.append(str(ROOT/e['scene']['path']))
        for prefix in ['references/'+e['id']+'/','deliverables/'+e['id']+'/']:
            if q.startswith(prefix):
                p=ROOT/e['project_root']/q
                if p.exists():hits.append(str(p))
    return {'historical_label':query,'local_paths':hits,'note':'Historical provenance files remain unchanged. An unresolved historical path may describe a superseded measurement/cache rather than a retained runtime dependency.'}
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['index','list','where','find','verify','resolve-historical']);p.add_argument('query',nargs='?');p.add_argument('--all-files',action='store_true');a=p.parse_args()
    if a.action=='index':r=index();print(json.dumps({'indexed_archives':len(r['archives']),'indexed_examples':len(r['examples'])}));return
    if a.action=='verify':sys.exit(0 if verify(a.all_files) else 1)
    if a.action=='list':r=[{'id':e['id'],'title':e['title'],'root':e['project_root']} for e in load()['examples']]
    elif a.action=='where':
        if not a.query:p.error('where requires a query')
        r=locate(a.query)
    elif a.action=='resolve-historical':
        if not a.query:p.error('resolve-historical requires a path')
        r=historical(a.query)
    else:
        if not a.query:p.error('find requires a query')
        q=a.query.casefold();r=[str(x.relative_to(ROOT)) for x in ROOT.rglob('*') if x.is_file() and '.git' not in x.parts and q in str(x.relative_to(ROOT)).casefold()]
    print(json.dumps(r,indent=2))
if __name__=='__main__':main()
