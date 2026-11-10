from pathlib import Path
import importlib.util,json,hashlib,gc
root=Path('/workspace/imessage-recreations');spec=importlib.util.spec_from_file_location('conditioned',root/'engines/render_pillow.conditioning-experiment.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
targets=[('01-photonhq','final-v10'),('02-danieltian','final-v13'),('03-photon-mini','final-v18'),('04-poke','final-v19'),('05-linq','final-v13'),('06-gallery','final-v20'),('02-danieltian','final-v16'),('05-linq','final-v18'),('06-gallery','final-v22')]
reports=[]
for ref,rev in targets:
 p=root/'outputs'/ref/rev/'scene.json';s=json.loads(p.read_text());frames=round(s['duration']*s['fps']);changed=[];ids=set()
 for f in range(frames):
  before=s['layers'];after=m.condition_group_units(before,f/s['fps'],s['duration'])
  def differences(a,b):
   for x,y in zip(a,b):
    if x is not y:
     if x.get('scaleX')!=y.get('scaleX')or x.get('scaleY')!=y.get('scaleY'):ids.add(x['id'])
     differences(x.get('children',[]),y.get('children',[]))
  if any(a is not b for a,b in zip(before,after)):changed.append(f);differences(before,after)
  if f%250==0:print(json.dumps({'reference':ref,'revision':rev,'checked':f,'affected':len(changed)}),flush=True)
 ranges=[]
 for f in changed:
  if ranges and ranges[-1][1]==f-1:ranges[-1][1]=f
  else:ranges.append([f,f])
 row={'reference':ref,'revision':rev,'sceneSha256':hashlib.sha256(p.read_bytes()).hexdigest(),'frames':frames,'affectedFrames':len(changed),'ranges':ranges,'ids':sorted(ids)};reports.append(row);print(json.dumps(row),flush=True);del s;gc.collect()
(root/'outputs/alternative-methods/pillow-avatar-diagnosis/affected-scope-audit.json').write_text(json.dumps(reports,indent=2)+'\n')
