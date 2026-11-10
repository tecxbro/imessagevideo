"""Idempotently convert lifetime-only gates into composable field patches."""
from pathlib import Path
import json
R=Path(__file__).resolve().parent;p=R/'title-elements-proposals.json';d=json.loads(p.read_text());d['fieldPatches']={'rene-v16-introducing':{'end':321/30},'rene-v16-mascot':{'end':321/30},'rene-v16-Rene':{'end':321/30},'g-1239':{'start':597/30}}
for id in d['fieldPatches']:d['replacements'].pop(id,None)
d['provenance']['composition']='Only lifetime fields of existing Introducing/mascot/Rene/g-1239 roots are patched on the input; their current children/keyframes remain intact so independently merged camera/art changes cannot be overwritten.';p.write_text(json.dumps(d,indent=2));print(p)
