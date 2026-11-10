from pathlib import Path
import subprocess,json,hashlib,time
R=Path('/workspace/imessage-recreations');P=R/'verification/fidelity-review/01-intro';scene=R/'outputs/01-photonhq/final-v5/scene.json';out=R/'outputs/01-photonhq/gsap.mp4';scan=R/'verification/timeline-scans/01-photonhq-v5';qa=R/'verification/final/01-photonhq/source-gsap';commands=[['node','engines/render.mjs','--method','gsap','--scene',str(scene),'--out',str(out),'--frames-dir','outputs/01-photonhq/frames-gsap','--ranges','0:239,518:554'],['python3','verification/scan_timeline.py','references/01-photonhq/source.mp4',str(out),'--out',str(scan),'--peaks','24'],['python3','verification/compare.py','references/01-photonhq/source.mp4',str(out),'--segments',str(scan/'peak-segments.json'),'--out',str(qa),'--background','255,255,255']]
status={'scene':str(scene),'scene_sha256':hashlib.sha256(scene.read_bytes()).hexdigest(),'ranges':[[0,239],[518,554]],'commands':commands,'completed':[]}
for i,cmd in enumerate(commands):
 status['active']=i;status['state']='running';(P/'gsap-pipeline-status.json').write_text(json.dumps(status,indent=2))
 with (P/f'gsap-stage-{i}.log').open('w') as log:result=subprocess.run(cmd,cwd=R,stdout=log,stderr=subprocess.STDOUT)
 if result.returncode:status['state']='failed';status['exit_code']=result.returncode;(P/'gsap-pipeline-status.json').write_text(json.dumps(status,indent=2));raise SystemExit(result.returncode)
 status['completed'].append(i)
status['state']='complete';status['active']=None;(P/'gsap-pipeline-status.json').write_text(json.dumps(status,indent=2));print(json.dumps(status))
