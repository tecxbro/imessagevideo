"""Wait actual primaries, encode PC709, scan final delivered pictures, then parity."""
from pathlib import Path
import json,time,subprocess,concurrent.futures,os
root=Path(__file__).parents[2];os.chdir(root);sha='57ed887caf7357a79e1f18c00b06934f2eeda864e555c739f1ab8965cc1b5cd9';start=time.time()
while True:
 ready=True
 for method in ['remotion','gsap']:
  f=Path(f'outputs/04-poke/{method}.mp4.render.json')
  try:m=json.loads(f.read_text());ready=ready and m['sceneSHA256']==sha and m['frames']==1283
  except (OSError,ValueError,KeyError):ready=False
 if ready:break
 if time.time()-start>1800:raise TimeoutError('Actual V16 primaries not complete; no encoding attempted')
 time.sleep(5)
print('Actual V16 primary metadata complete',flush=True)
def run(args):
 print('Starting '+str(args),flush=True);subprocess.run(args,check=True,env={**os.environ,'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1'});print('Finished '+str(args),flush=True)
run(['python3','scripts/final_encode.py','--state','references/04-poke/encoding-state-v16.json','--only','04-poke','--methods','gsap'])
def sourcegate():
 run(['python3','verification/scan_timeline.py','references/04-poke/source.mp4','outputs/04-poke/gsap.mp4','--out','verification/timeline-scans/04-poke-v16','--peaks','24'])
 run(['python3','verification/compare.py','references/04-poke/source.mp4','outputs/04-poke/gsap.mp4','--segments','verification/timeline-scans/04-poke-v16/peak-segments.json','--times','0','--batch-native','--out','verification/final/04-poke/source-gsap-v16'])
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
 a=ex.submit(sourcegate);b=ex.submit(run,['python3','scripts/final_encode.py','--state','references/04-poke/encoding-state-v16.json','--only','04-poke','--methods','remotion']);a.result();b.result()
fps=30000/1001;frames=[512,513,540,560,575,583,617,618,629,659,664,671,758];p=Path('outputs/04-poke/qa-v16-parity-segments.json');p.write_text(json.dumps([dict(name=f'native-{n}',reference_start=n/fps,candidate_start=n/fps,duration=.001)for n in frames],indent=2))
run(['python3','verification/compare.py','outputs/04-poke/remotion.mp4','outputs/04-poke/gsap.mp4','--segments',str(p),'--times','0','--batch-native','--out','outputs/04-poke/qa-v16-engine-parity'])
print('V16 source/PC/parity gate complete; visual peak review still required',flush=True)
