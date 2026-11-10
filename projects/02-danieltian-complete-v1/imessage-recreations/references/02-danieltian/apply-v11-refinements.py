"""Apply declared ID-scoped v11 patches; safe to compose with root's independent group-797 helper."""
from pathlib import Path
import json,copy,sys
R=Path(__file__).resolve().parent
if len(sys.argv)<3:raise SystemExit('Usage: apply-v11-refinements.py INPUT OUTPUT [PATCH ...]')
base=Path(sys.argv[1]).resolve();out=Path(sys.argv[2]).resolve();s=json.loads(base.read_text());names=sys.argv[3:] or [str(R/'v11-boundary-refinement.json'),str(R/'v11-middle-refinement.json'),str(R/'v11-end-refinement.json')]
def rebase(n,root):
 if isinstance(n,dict):
  if n.get('src') and not n['src'].startswith(('data:','http:','https:')):n['src']=str((root/n['src']).resolve())
  for v in n.values():rebase(v,root)
 elif isinstance(n,list):
  for v in n:rebase(v,root)
rebase(s,base.parent);applied=[]
for name in names:
 pp=Path(name).resolve();p=json.loads(pp.read_text());rebase(p,pp.parent);replacement=p.get('replacements',{});before={x['id'] for x in s['layers']};unknown=set(replacement)-before
 if unknown:raise ValueError(f'Patch IDs absent in input: {unknown}')
 s['layers']=[copy.deepcopy(replacement.get(n['id'],n)) for n in s['layers']]
 grads={q['id']:q for q in s.get('gradients',[])}
 for q in p.get('gradients',[]):grads[q['id']]=q
 s['gradients']=list(grads.values());applied.append(dict(patch=str(pp),ids=list(replacement),changedFrames=p.get('changed_frames')))
s.setdefault('source',{})['notes']+=' v11 every-frame diagnosis repair: measured native phone exit, isolated native magnifier/reasoning/query vector graphics, actual per-frame middle poses and semantic exits, newborn spring/typing/card states, and per-frame semantic end-phrase glyph entrance. Native outlines are not live text; bounded original book emoji remains bitmap. No full-source-frame image or source-video playback.'
s['v11AppliedScopedPatches']=applied;out.write_text(json.dumps(s,indent=2));print(json.dumps(dict(output=str(out),patches=applied),indent=2))
