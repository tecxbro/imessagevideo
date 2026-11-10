"""Replace only a just-started read-only comparator with the validated batch path."""
from pathlib import Path
import os,signal,json,hashlib,subprocess,time
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/02-danieltian';RUNNER=199406;COMPARE=ROOT/'verification/final/02-danieltian/source-gsap-v14';SCAN=ROOT/'verification/timeline-scans/02-danieltian-v14';STATE=OUT/'v14-gsap-workflow.json';LOG=OUT/'v14-gsap-batch-handoff.json';MOVIE=OUT/'gsap.mp4';SIDECAR=Path(str(MOVIE)+'.render.json')
def procs():
 rows={}
 for p in Path('/proc').iterdir():
  if not p.name.isdigit():continue
  try:
   raw=(p/'stat').read_text();tail=raw[raw.rfind(')')+2:].split();cmd=(p/'cmdline').read_bytes().split(b'\0');rows[int(p.name)]={'state':tail[0],'ppid':int(tail[1]),'cmd':[x.decode(errors='replace')for x in cmd if x]}
  except(FileNotFoundError,PermissionError,ProcessLookupError):pass
 return rows
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def save(d):LOG.write_text(json.dumps(d,indent=2)+'\n')
print('Waiting for the existing encode/scan; production processes remain untouched.',flush=True)
while True:
 ps=procs();runner=ps.get(RUNNER)
 if not runner or runner['state']=='Z':
  state=json.loads(STATE.read_text())
  if state['stage']=='gate-measured-awaiting-visual-review':save({'action':'Existing exact-pixel comparison already completed; no repeat.'});print('Existing gate completed',flush=True);raise SystemExit(0)
  raise RuntimeError('Runner exited before planned comparator: '+state['stage'])
 assert any('run-browser-v14.py'in x for x in runner['cmd'])
 matches=[pid for pid,q in ps.items()if q['ppid']==RUNNER and any(x.endswith('verification/compare.py')for x in q['cmd'])and str(MOVIE)in q['cmd']]
 if matches:break
 time.sleep(.25)
pid=matches[0];partial=list((COMPARE/'frames').glob('*.jpg'))if(COMPARE/'frames').exists()else[]
if len(partial)>=4:
 save({'action':'Existing exact-pixel comparison had progressed; left uninterrupted.','imagesAlreadyWritten':len(partial)})
 while RUNNER in procs()and procs()[RUNNER]['state']!='Z':time.sleep(.25)
 assert json.loads(STATE.read_text())['stage']=='gate-measured-awaiting-visual-review';print('Existing gate completed unchanged',flush=True);raise SystemExit(0)
scan=json.loads((SCAN/'scan.json').read_text());meta=json.loads(SIDECAR.read_text());before=sha(MOVIE);assert scan['frames_scanned']==1360 and scan['candidateSHA256']==before and meta['encoding']['profile']=='full-range-bt709-v1';assert meta['encoding']['pictureSHA256']==before
children=[n for n,q in ps.items()if q['ppid']==pid]
for n in children+[pid]:
 try:os.kill(n,signal.SIGTERM)
 except ProcessLookupError:pass
while True:
 ps=procs()
 if RUNNER not in ps or ps[RUNNER]['state']=='Z':break
 time.sleep(.25)
assert sha(MOVIE)==before;record={'action':'Only the just-started read-only comparator was replaced by validated batch-native decoding.','terminatedComparatorPID':pid,'partialPreviewCount':len(partial),'productionCaptureOrEncoderCancelled':False,'sourceScanRepeated':False,'stablePictureSHA256':before,'parityEvidence':'verification/batch-native-decode-parity.json'};save(record);args=['python3','verification/compare.py',str(ROOT/'references/02-danieltian/source.mp4'),str(MOVIE),'--segments',str(SCAN/'peak-segments.json'),'--times','0','--batch-native','--out',str(COMPARE)];print('RUN',*args,flush=True);subprocess.run(args,cwd=ROOT,check=True);assert sha(MOVIE)==before;state=json.loads(STATE.read_text());state.update(stage='gate-measured-awaiting-visual-review',comparison=str(COMPARE/'report.json'),pictureSHA256=before,batchNativeHandoff=str(LOG));temp=STATE.with_name(STATE.name+'.tmp-'+str(os.getpid()));temp.write_text(json.dumps(state,indent=2)+'\n');temp.replace(STATE);record['completed']=True;record['comparison']=str(COMPARE/'report.json');record['pictureSHA256UnchangedAfter']=sha(MOVIE);save(record);print('Batch-native comparison completed without repeating encode/scan.',flush=True)
