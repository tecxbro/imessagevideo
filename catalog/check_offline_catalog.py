#!/usr/bin/env python3
"""Check actual offline source bytes, links, selectors and retained media paths."""
from pathlib import Path
from html.parser import HTMLParser
import hashlib, json, re, subprocess

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skill/imessage-motion-recreation'
HTML = Path(__file__).with_name('index.html')
text = HTML.read_text()
data = json.loads(re.search(r'<script[^>]+id="library-data"[^>]*>(.*?)</script>', text, re.S)[1])
manifest = json.loads((SKILL / 'library/manifest.json').read_text())
examples = {x['id']: x for x in manifest['examples']}

class Document(HTMLParser):
    def __init__(self): super().__init__(); self.links=[]; self.ids=[]
    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs)
        if 'id' in attrs: self.ids.append(attrs['id'])
        for key in ['src','href']:
            if key in attrs: self.links.append({'tag':tag,'attribute':key,'value':attrs[key]})

doc=Document();doc.feed(text)
external=[x for x in doc.links if x['value'].startswith(('https:','http:','//'))]
assert not external, external
assert len(doc.ids)==len(set(doc.ids)), 'Duplicate element ID'
used_ids=set(re.findall(r"\$\('([^']+)'\)",text[text.index("'use strict';"):]))
assert not used_ids-set(doc.ids), 'Missing DOM elements'
assert len(data['films'])==6 and len(data['methods'])==5 and len(data['files'])==9
assert 'DATA.publicBase' not in text and 'DATA.driveFolder' not in text
assert "const url=f.projectRoot+'/deliverables/'" in text
assert "$('reference-video').src=original" in text
for f in data['files']:
    raw=f['source'].encode()
    assert len(raw)==f['bytes']
    assert hashlib.sha256(raw).hexdigest()==f['sha256']
    assert raw==(SKILL/f['skillPath']).read_bytes()
for script in re.findall(r'<script(?:\s[^>]*)?>(.*?)</script>',text,re.S):
    if script.lstrip().startswith('{'): continue
    subprocess.run(['node','-e','new Function(process.argv[1]);',script],check=True,capture_output=True)

paths=[]
def check(value,kind,expected_bytes=None):
    if not value or value.startswith(('data:','#')):return
    path=(HTML.parent/value.split('#')[0]).resolve()
    assert path.is_relative_to(ROOT), 'Escaping local library path: '+value
    row={'kind':kind,'relative_url':value,'local_path':str(path.relative_to(ROOT)),'exists':path.exists()}
    if expected_bytes is not None and path.is_file():
        row['expected_bytes']=expected_bytes;row['actual_bytes']=path.stat().st_size
        assert row['expected_bytes']==row['actual_bytes'], 'Media size mismatch: '+str(path)
    paths.append(row)
for x in doc.links:check(x['value'],'static '+x['tag']+'/'+x['attribute'])
for film in data['films']:
    example=examples[film['id']];base=film['projectRoot']+'/'
    for movie in example['finished_results']:check(base+movie['project_path'],'finished movie',movie['bytes'])
    check(base+example['original_reference']['project_path'],'original reference',example['original_reference']['bytes'])
    check(base+example['scene']['project_path'],'complete scene',example['scene']['bytes'])
    check(base+example['source_frame_analysis'],'measured analysis')
    check(base+'README-COMPLETE-EXAMPLE.md','project readme')
    for item in data['files']:check(base+item['path'],'actual project renderer')
    for study in film['studies']:check(study['url'],'local visual atlas')
missing=[x for x in paths if not x['exists']]
result={'status':'pass' if not missing else 'pending-restoration','film_count':6,'rendering_methods':5,'full_embedded_source_files':9,'all_embedded_source_hashes_match_actual_skill_files':True,'all_inline_scripts_parse':True,'all_referenced_dom_ids_present':True,'automatic_external_html_urls':external,'checked_local_links':len(paths),'missing_local_links':missing,'checked_paths':paths,'interactive_browser_qa':'Not claimed. Managed browser file and inherited-proxy loopback policy restrictions were already diagnosed; this check does not disable or bypass them.'}
Path(__file__).with_name('validation.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='checked_paths'},indent=2))
