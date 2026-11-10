"""Retained-cache source update with actual per-method provenance and final coherent encode."""
from pathlib import Path
import argparse,hashlib,json,os,subprocess,time,shutil
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'outputs/02-danieltian'
SCENE=OUT/'final-v16/scene.json'
BASES={'gsap':'ff896ac0fe8ab53b2301d7f55349438cc2efe1d2c2d088730c36a02588302a25','remotion':'a896028ccd61f354f4177d231d4e790eee16107c48ab6243c0394133edf98796','html':'a896028ccd61f354f4177d231d4e790eee16107c48ab6243c0394133edf98796'}
def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb')as file:
        for block in iter(lambda:file.read(1024*1024),b''):h.update(block)
    return h.hexdigest()
def write(path,value):
    temporary=path.with_name(path.name+'.tmp-'+str(os.getpid()))
    temporary.write_text(json.dumps(value,indent=2)+'\n')
    temporary.replace(path)
def fact(path):
    stat=path.stat()
    return[stat.st_ino,stat.st_size,stat.st_mtime_ns]
def run(arguments):
    print('RUN',*map(str,arguments),flush=True)
    subprocess.run(list(map(str,arguments)),cwd=ROOT,check=True)
parser=argparse.ArgumentParser()
parser.add_argument('--method',choices=list(BASES),required=True)
parser.add_argument('--gate',action='store_true')
args=parser.parse_args()
method=args.method
proof=json.loads((OUT/'final-v16'/('scope-from-v15.json'if method=='gsap'else'scope-from-v13.json')).read_text())
sceneSHA=sha(SCENE)
assert proof['targetSha256']==sceneSHA and proof['baseSha256']==BASES[method]and not proof['changedOutsideCaptureUnion']
movie=OUT/(method+'.mp4')
sidecar=Path(str(movie)+'.render.json')
metadata=json.loads(sidecar.read_text())
assert metadata['sceneSHA256']==BASES[method]and metadata['frames']==1360
cache=Path(metadata['frameDirectory'])
ranges=proof['conservativeCaptureRanges']
capture={frame for first,last in ranges for frame in range(first,last+1)}
assert len(capture)==(57 if method=='gsap'else 261)
assert proof['changedFrames']==len(capture)
facts={str(frame):fact(cache/f'{frame:06d}.png')for frame in range(1360)}
history=OUT/'iterations'/('browser-v15-before-v16'if method=='gsap'else'browser-v13-before-v16')
history.mkdir(parents=True,exist_ok=True)
for source in[movie,sidecar]:
    destination=history/source.name
    if destination.exists():assert sha(destination)==sha(source)
    else:os.link(source,destination)
statefile=OUT/f'v16-{method}-workflow.json'
state={'method':method,'scene':str(SCENE),'sceneSHA256':sceneSHA,'previousSceneSHA256':BASES[method],'actualFrameDirectory':str(cache),'captureRanges':ranges,'captureFrames':len(capture),'cacheBefore':facts,'stage':'capturing','startedAtUnix':time.time()}
write(statefile,state)
run(['node','engines/render.mjs','--method',method,'--scene',SCENE,'--out',movie,'--frames-dir',cache,'--ranges',','.join(f'{first}:{last}'for first,last in ranges)])
metadata=json.loads(sidecar.read_text())
assert metadata['sceneSHA256']==sceneSHA
changedOutside=[frame for frame in range(1360)if frame not in capture and facts[str(frame)]!=fact(cache/f'{frame:06d}.png')]
assert not changedOutside,changedOutside
state['outsideCacheFramesUntouched']=1360-len(capture)
state['stage']='captured'
write(statefile,state)
run(['python3','scripts/final_encode.py','--only','02-danieltian','--methods',method])
state['stage']='encoded-final-pc709'
state['pictureSHA256']=sha(movie)
write(statefile,state)
if args.gate:
    assert method=='gsap'
    source=ROOT/'references/02-danieltian/source.mp4'
    scan=ROOT/'verification/timeline-scans/02-danieltian-v16'
    compare=ROOT/'verification/final/02-danieltian/source-gsap-v16'
    run(['python3','verification/scan_timeline.py',source,movie,'--out',scan,'--peaks','24'])
    state['stage']='full-source-scan-completed'
    state['scan']=str(scan/'scan.json')
    write(statefile,state)
    run(['python3','verification/compare.py',source,movie,'--segments',scan/'peak-segments.json','--fps','1','--times','0','--batch-native','--out',compare])
    state['stage']='gate-measured-awaiting-visual-review'
    state['comparison']=str(compare/'report.json')
    write(statefile,state)
print(json.dumps({key:value for key,value in state.items()if key!='cacheBefore'}),flush=True)
