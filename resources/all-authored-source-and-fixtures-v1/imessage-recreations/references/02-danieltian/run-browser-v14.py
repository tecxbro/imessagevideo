"""Bounded browser export using each completedV13 sidecar's actual lossless cache."""
from pathlib import Path
import json,hashlib,os,subprocess,argparse,time,shutil
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/02-danieltian';SCENE=OUT/'final-v14/scene.json';BASE_SHA='a896028ccd61f354f4177d231d4e790eee16107c48ab6243c0394133edf98796';RANGES='175:179,436:524,548:597';CAPTURE=set(range(175,180))|set(range(436,525))|set(range(548,598));SCENE_SHA='72dc439bb13119889fc13bdb65bccd48c4e9eb75c8b4af7e8deba69cd592416a'
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb')as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def write(p,d):
 tmp=p.with_name(p.name+'.tmp-'+str(os.getpid()));tmp.write_text(json.dumps(d,indent=2)+'\n');tmp.replace(p)
def fact(p):
 s=p.stat();return[s.st_ino,s.st_size,s.st_mtime_ns]
def run(args):
 print('RUN',*map(str,args),flush=True);subprocess.run(list(map(str,args)),cwd=ROOT,check=True)
p=argparse.ArgumentParser();p.add_argument('--method',choices=['gsap','remotion','html'],required=True);p.add_argument('--gate',action='store_true');a=p.parse_args();proof=json.loads((OUT/'final-v14/combined-scope-proof.json').read_text());assert proof['targetSha256']==SCENE_SHA and proof['changedFrames']==144 and not proof['changedOutsideCaptureUnion'];assert sha(SCENE)==SCENE_SHA
method=a.method;movie=OUT/(method+'.mp4');sidecar=Path(str(movie)+'.render.json');meta=json.loads(sidecar.read_text());assert meta['sceneSHA256']==BASE_SHA and meta['frames']==1360;cache=Path(meta['frameDirectory']);facts={str(f):fact(cache/f'{f:06d}.png')for f in range(1360)};history=OUT/'iterations/browser-v13-before-v14';history.mkdir(parents=True,exist_ok=True)
for source in[movie,sidecar]:
 target=history/source.name
 if target.exists():assert sha(target)==sha(source)
 else:os.link(source,target)
statefile=OUT/('v14-'+method+'-workflow.json');state={'method':method,'scene':str(SCENE),'sceneSHA256':SCENE_SHA,'previousSceneSHA256':BASE_SHA,'actualFrameDirectory':str(cache),'captureRanges':[[175,179],[436,524],[548,597]],'captureFrames':144,'cacheBefore':facts,'stage':'capturing','startedAtUnix':time.time()};write(statefile,state)
run(['node','engines/render.mjs','--method',method,'--scene',SCENE,'--out',movie,'--frames-dir',cache,'--ranges',RANGES]);newmeta=json.loads(sidecar.read_text());assert newmeta['sceneSHA256']==SCENE_SHA;outside=[f for f in range(1360)if f not in CAPTURE and facts[str(f)]!=fact(cache/f'{f:06d}.png')];assert not outside;state['outsideCacheFramesUntouched']=1216;state['stage']='captured';write(statefile,state)
if a.gate:
 assert method=='gsap';run(['python3','scripts/final_encode.py','--only','02-danieltian','--methods','gsap']);state['stage']='encoded-final-pc709';write(statefile,state);scan=ROOT/'verification/timeline-scans/02-danieltian-v14';compare=ROOT/'verification/final/02-danieltian/source-gsap-v14';source=ROOT/'references/02-danieltian/source.mp4';run(['python3','verification/scan_timeline.py',source,movie,'--out',scan,'--peaks','24']);state['stage']='full-source-scan-completed';state['scan']=str(scan/'scan.json');write(statefile,state);run(['python3','verification/compare.py',source,movie,'--segments',scan/'peak-segments.json','--fps','1','--times','0','--batch-native','--out',compare]);state['stage']='gate-measured-awaiting-visual-review';state['comparison']=str(compare/'report.json');state['pictureSHA256']=sha(movie);write(statefile,state)
else:state['stage']='captured-v14-awaiting-global-final-encode';state['pictureSHA256']=sha(movie);write(statefile,state)
print(json.dumps({k:v for k,v in state.items()if k!='cacheBefore'}),flush=True)
