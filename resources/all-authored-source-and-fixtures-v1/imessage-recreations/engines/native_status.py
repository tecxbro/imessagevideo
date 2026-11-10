#!/usr/bin/env python3
"""Inspect native completion evidence and retained capture progress without rendering."""
import json
from pathlib import Path
from run_alternative_batch import ROOT,engine_hash,active_worker,current_engine

def main():
 rows=[]
 for name,revision in json.loads((ROOT/'engines/native-queue.json').read_text()):
  for method in ['pillow','motion-canvas']:
   out=ROOT/'outputs'/name/(method+'.mp4');sidecar=Path(str(out)+'.render.json');m=json.loads(sidecar.read_text()) if sidecar.exists() else {};cache=out.parent/'cache'/method;frames=list(cache.glob('*.png'));target=out.parent/revision/'scene.json';actual=Path(m['scene']) if m.get('scene') else None
   compatibility=[row['reason'] for row in json.loads((ROOT/'engines/native-engine-compatibility.json').read_text()).get('entries',[]) if row['method']==method and row['fromEngineSha256']==m.get('engineSha256') and row['toEngineSha256']==engine_hash(method) and row['sceneSha256']==m.get('sceneSha256')] if (ROOT/'engines/native-engine-compatibility.json').exists() else []
   rows.append({'capture_engine_sha256':m.get('engineSha256'),'current_engine_sha256':engine_hash(method),'engine_compatibility_reason':compatibility,'reference':name,'method':method,'target_revision':revision,'completed_revision':actual.parent.name if actual else None,'current_engine':current_engine(m,method),'current_input':actual==target,'retained_png_count':len(frames),'last_retained_frame':max((int(p.stem) for p in frames),default=None),'worker_pid':active_worker(out,method),'encoded_frames':m.get('frames'),'known_issues':m.get('knownIssues',[])})
 print(json.dumps(rows,indent=2))
if __name__=='__main__':main()
