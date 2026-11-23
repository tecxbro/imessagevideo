import ast,csv,hashlib,json,re,subprocess
from pathlib import Path
from html.parser import HTMLParser
from collections import Counter
from urllib.parse import urlparse

p=Path.cwd()
release=Path('../../scenes/05-linq/scene.json')
sha=lambda raw:hashlib.sha256(raw).hexdigest()
metadata=[]
class Probe(HTMLParser):
    def __init__(self):
        super().__init__()
        self.scripts=[]
        self.external=[]
        self.script=None
        self.script_start=None
    def handle_starttag(self, tag, attributes):
        d=dict(attributes)
        for k in ('src','href'):
            if d.get(k):self.external.append((tag,k,urlparse(d[k]).path))
        if tag=='script' and not d.get('src'):
            self.script=[]
            self.script_start=self.getpos()[0]
    def handle_data(self,data):
        if self.script is not None:self.script.append(data)
    def handle_endtag(self,tag):
        if tag=='script' and self.script is not None:
            self.scripts.append((self.script_start,self.getpos()[0],''.join(self.script)))
            self.script=None
            self.script_start=None

manual = {name for name in '''analysis.md steps.md steps-rebuild.md steps-root-boarding-v18.md
steps-root-cash-control-v19.md steps-root-four-handoff.md steps-root-late.md
steps-root-white-pawn-v19.md compose_final_v20.py gate_promote_menu_aa4_v20.py
apply-root-cash-plane-v20.py verify_primary_v20.py verify_html_v20.py
build_transition_v10.py measure_object_poses_v10.py native_components.py subset_fonts.py
prepare_composers_v19.py refine_composers_v19.py prepare_restaurant_bottom_v20.py
propose_quantized_cash_alpha_v20.py quarantine_menu_aa4_v20.py fit-gallery-root.py
apply-root-four-handoff.py build-root-boarding-detail-v18.py apply-root-boarding-detail-v18.py
analyze_browser_parity_v20.py apply-restaurant-bottom-v20.py run_g20_gate.sh run_h20_export.sh'''.split()}
manual.update(Path('/tmp/imv-motion-audit.Zz5HS0/linq-extra-reviewed.txt').read_text().splitlines())
manual.update({'source.json','asset-provenance-boarding-detail-v18.json',
               'assets/apple-font-access-denied.html','assets/apple-font-css-access-denied.html'})
files=subprocess.check_output(['git','ls-files','-z','.']).decode().split('\0')
gitref=subprocess.check_output(['git','rev-parse','HEAD']).decode().strip()
for item in filter(None,files):
    raw=Path(item).read_bytes()
    blob=subprocess.check_output(['git','rev-parse',gitref+':./'+item]).decode().strip()
    calc=hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()
    assert calc==blob, item
    suffix=Path(item).suffix
    rows=None
    role=''
    status=''
    details=[]
    if suffix=='.mp4':
        role='original reference input'
        status='native video metadata and authored-scope samples, see shared verification'
        details.append('binary')
    else:
        data=raw.decode()
        rows=data.splitlines()
        role='historical authoring' if suffix in ('.py','.mjs','.sh') else 'historical notes or metadata'
        if suffix=='.py':
            try:
                module=ast.parse(data,filename=item)
            except SyntaxError as exc:
                status=f'syntax error at {exc.lineno}:{exc.offset} {exc.msg}'
            else:
                status='AST read'
                definitions=[n.name for n in module.body if isinstance(n,(ast.FunctionDef,ast.ClassDef,ast.AsyncFunctionDef))]
                if definitions:details.append('definitions '+', '.join(definitions))
                names=[(getattr(n.func,'id',None) or getattr(n.func,'attr',None)) for n in ast.walk(module) if isinstance(n,ast.Call)]
                for name in ('write_text','write_bytes','unlink','rename','replace','copy2','save','open','run','check_output','load','read_text','read_bytes','assert_equal'):
                    if name in names:details.append(f'{name}×{names.count(name)}')
        elif suffix in ('.mjs','.sh'):
            command=['node','--check',item] if suffix=='.mjs' else ['bash','-n',item]
            tested=subprocess.run(command,capture_output=True,text=True)
            status='syntax passes' if tested.returncode==0 else 'syntax failed'
        elif suffix=='.json':
            json.loads(data)
            status='JSON parse'
        elif suffix=='.html':
            items=Probe()
            items.feed(data)
            role='acquisition response, not a UI' if item.startswith('assets/') else 'frozen LinkedIn acquisition page'
            status='HTML parse'
            details.append(f'{len(items.external)} href/src attributes, {len(items.scripts)} inline scripts')
        elif suffix=='.md':
            status='Markdown line scan'
        for pattern,flag in ((r'/workspace','old-workspace'),(r'\boutputs/05-linq','old-outputs'),
            (r'(?i)\bnative\b','native'),(r'(?i)\b(?:target|scope|guard|checkpoint)\b','scope'),
            (r'(?i)\.png\b','image'),(r'(?i)ffmpeg|ffprobe','decoder'),
            (r'(?i)\b(?:alpha|opacity|blur|camera|mask)\b','layers')):
            count=sum(bool(re.search(pattern,line)) for line in rows)
            if count:details.append(f'{flag} lines {count}')
    metadata.append([item,role,len(raw),sha(raw),len(rows) if rows is not None else '',status,
                     'all lines read and scanned, full direct review' if item in manual else
                     'all lines read and scanned' if rows is not None else 'binary input',
                     '; '.join(details)])
with Path('/Users/darshan/Documents/ChatGPT/imessage-video/codex-trial/review/imv-v3/goal-audit/production-05-manifest.tsv').open('w') as f:
    w=csv.writer(f,delimiter='\t',lineterminator='\n')
    w.writerow(('path','role','bytes','sha256','lines','structural read','coverage','observations'))
    w.writerows(metadata)
print(f'{gitref}: {len(metadata)} tracked files, {sum(row[4] or 0 for row in metadata)} text lines, all blob hashes verified')
print(Counter(row[5] for row in metadata))
S=json.loads(release.read_bytes())
class Summary:
    def __init__(self):
        self.types=Counter()
        self.src=set()
        self.ids=[]
        self.semantic=[]
        self.rasters=[]
        self.live_text=[]
        self.animated=0
    def walk(self,nodes):
        for node in nodes:
            self.types[node['type']]+=1
            self.ids.append(node['id'])
            if node.get('keyframes'): self.animated+=1
            if node.get('src'):
                self.src.add(node['src'])
                self.rasters.append((node.get('width',0)*node.get('height',0),node['id'],node['width'],node['height'],node['src']))
            if node.get('semanticText'):self.semantic.append(node['semanticText'])
            if node['type']=='text':self.live_text.append((node['id'],node.get('text')))
            self.walk(node.get('children',[]))
M=Summary(); M.walk(S['layers'])
print(json.dumps({'keys':sorted(S),'source_sha':sha(Path('source.mp4').read_bytes()),
    'scene_sha':sha(release.read_bytes()),'duration':S['duration'],'fps':S['fps'],
    'nodes':sum(M.types.values()),'unique_ids':len(set(M.ids)),
    'types':M.types,'animated':M.animated,'asset_refs':len(M.src),
    'relative_unresolved':sum(not (release.parent/name).exists() for name in M.src if not name.startswith(('data:','http'))),
    'semantic_text':len(M.semantic),'top_rasters':sorted(M.rasters,reverse=True)[:4],
    'live_text':M.live_text[:12],'fonts':len(S.get('fonts',[]))},indent=2))
