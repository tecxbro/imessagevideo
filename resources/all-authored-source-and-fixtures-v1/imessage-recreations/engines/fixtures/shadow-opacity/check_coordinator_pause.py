"""New holds while lock-waiting must not launch or occupy the native slot."""
from pathlib import Path
import tempfile,time,multiprocessing,json,sys
root=Path(__file__).resolve().parents[3];sys.path.insert(0,str(root/'engines'));from run_alternative_batch import method_slot

def waiter(folder):
 folder=Path(folder)
 with method_slot('pause-fixture',lambda:not(folder/'held').exists()):
  (folder/'started').write_text('started')

def main():
 with tempfile.TemporaryDirectory()as tmp:
  p=Path(tmp)
  with method_slot('pause-fixture'):
   child=multiprocessing.Process(target=waiter,args=(tmp,));child.start();time.sleep(.2);(p/'held').write_text('new source gate')
  time.sleep(.4);assert not(p/'started').exists(),'Queued reference launched while newly held'
  start=time.monotonic()
  with method_slot('pause-fixture'):free_latency=time.monotonic()-start
  assert free_latency<1,'Held reference occupied the slot'
  (p/'held').unlink();child.join(6);assert child.exitcode==0 and(p/'started').exists(),'Job did not resume after gate release'
  report={'newPauseAfterLockWaitRespected':True,'otherReferenceSlotLatencySeconds':free_latency,'resumedAfterRelease':True,'productionRendererLaunched':False};Path(__file__).with_name('coordinator-pause-report.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
 (root/'engines/.native-pause-fixture.lock').unlink(missing_ok=True)
if __name__=='__main__':main()
