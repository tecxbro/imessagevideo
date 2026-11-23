import ast,csv,hashlib,json,re,subprocess
from pathlib import Path
from html.parser import HTMLParser
from collections import Counter

p=Path.cwd()
project=Path('../..')
scene_path=project/'scenes/06-gallery/scene.json'
digest=lambda data:hashlib.sha256(data).hexdigest()
manual=set(Path('/tmp/imv-motion-audit.Zz5HS0/rene-reviewed.txt').read_text().splitlines())
class Probe(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags=Counter()
        self.video_sources=0
        self.meta_video=0
    def handle_starttag(self, name, attrs):
        fields=dict(attrs)
        self.tags[name]+=1
        if name=='video':self.video_sources+=bool(fields.get('src'))
        if name=='meta':self.meta_video+=fields.get('property','').startswith('og:video')
files=subprocess.check_output(['git','ls-files','-z','.']).decode().split('\0')
ref=subprocess.check_output(['git','rev-parse','HEAD']).decode().strip()
rows=[]
for filename in filter(None,files):
    path=Path(filename)
    raw=path.read_bytes()
    blob=subprocess.check_output(['git','rev-parse',ref+':./'+filename]).decode().strip()
    assert hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()==blob
    count=''; parsed=''; details=[]
    if path.suffix=='.mp4':
        parsed='native binary source, published common verification'
    else:
        data=raw.decode()
        lines=data.splitlines()
        count=len(lines)
        if path.suffix=='.py':
            tree=ast.parse(data,filename=filename)
            parsed='AST parse passes'
            definitions=[n.name for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))]
            if definitions:details.append('definitions '+', '.join(definitions))
        elif path.suffix=='.mjs':
            completed=subprocess.run(['node','--check',filename],capture_output=True)
            assert completed.returncode==0,filename
            parsed='Node syntax passes'
        elif path.suffix=='.html':
            probe=Probe();probe.feed(data)
            parsed='External page parsed'
            details.append('video tags with source '+str(probe.video_sources))
            details.append('Open Graph video metadata tags '+str(probe.meta_video))
        elif path.suffix=='.json':
            json.loads(data)
            parsed='JSON parse passes'
        elif path.suffix=='.md':
            parsed='Markdown read'
        else:
            raise ValueError(filename)
        for expression, kind in ((r'/workspace','historical workspace'),(r'outputs/06-gallery','historical outputs'),
            (r'(?i)\bnative\b','native frame'),(r'(?i)frame.{0,10}(range|scope)|scope|guard','scope'),
            (r'(?i)[.]png','PNG'),(r'(?i)ffmpeg|ffprobe','decoder'),(r'(?i)alpha|opacity|mask|blur|camera','layer optics')):
            n=sum(bool(re.search(expression,line)) for line in lines)
            if n:details.append(f'{kind}: {n}')
    coverage='full direct review' if filename in manual else 'all lines structurally parsed' if count else 'binary input'
    rows.append([filename,digest(raw),blob,len(raw),count,parsed,coverage,'; '.join(details)])
out=Path('/Users/darshan/Documents/ChatGPT/imessage-video/codex-trial/review/imv-v3/goal-audit/production-06-manifest.tsv')
with out.open('w') as f:
    w=csv.writer(f,delimiter='\t',lineterminator='\n')
    w.writerow(('path','sha256','git_blob','bytes','lines','verification','coverage','observations'));w.writerows(rows)
print(ref,len(rows),sum(int(a[4] or 0) for a in rows),Counter(a[5] for a in rows),Counter(a[6] for a in rows))
S=json.loads(scene_path.read_bytes())
layers=[]
def walk(nodes):
    for n in nodes:
        layers.append(n)
        walk(n.get('children',[]))
walk(S['layers'])
srcs={n['src'] for n in layers if n.get('src')}
font_paths={doc['src'] for doc in S.get('fonts',[])}
exists=lambda name:name.startswith('data:') or (scene_path.parent/name).is_file()
summary={
 'keys':list(S), 'internalRevisionLabel':S['rebuildRevision'],'sceneSHA256':digest(scene_path.read_bytes()),
 'sourceSHA256':digest(Path('source.mp4').read_bytes()),'nativeFPS':S['fps'],'duration':S['duration'],'picture':[S['width'],S['height']],
 'nodes':len(layers),'uniqueIds':len({n['id'] for n in layers}),'keyedNodes':sum(bool(n.get('keyframes')) for n in layers),
 'layerTypes':Counter(n['type'] for n in layers),'semanticCopyLabels':sum(bool(n.get('semanticText')) for n in layers),
 'liveText':[(n['id'],n.get('text')) for n in layers if n['type']=='text'],
 'imagePaths':len(srcs),'fontPaths':len(font_paths),'missingAssets':[name for name in sorted(srcs|font_paths) if not exists(name)],
 'largestImageNodes':sorted(((n['width']*n['height'], n['id'], n['width'], n['height']) for n in layers if n['type']=='image'),
                           reverse=True)[:8]
}
Path('/tmp/imv-motion-audit.Zz5HS0/rene-scene.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))
