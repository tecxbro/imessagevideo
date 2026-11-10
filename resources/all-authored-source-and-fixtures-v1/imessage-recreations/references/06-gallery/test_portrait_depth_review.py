from pathlib import Path
import json,copy,sys,numpy as np
from PIL import Image
R=Path('/workspace/imessage-recreations');P=R/'verification/fidelity-review/06-portrait614';BASE=R/'outputs/06-gallery/final-v20';sys.path.insert(0,str(R/'engines'));import render_pillow as rp
S=json.load(open(P/'prototype.scene.json'));rp.register_fonts(S,str(BASE));ref=np.array(Image.open(P/'source/000614.png'),dtype=float);rows=[]
for names in [['95'],['81'],['95','81'],['95','87'],['93'],['77']]:
 q=copy.deepcopy(S);moving=[n for n in q['layers']if n.get('semanticPhotoId')in ['rene-final11-group-'+x for x in names]and n.get('start',0)<=614/30<n.get('end',99)];q['layers']=[n for n in q['layers']if n not in moving];idx=next(i for i,n in enumerate(q['layers'])if n['id']=='rene-portrait-v18-614-79');q['layers'][idx+1:idx+1]=moving;im=rp.render(q,614/30,str(BASE));cost=float(abs(np.array(im,dtype=float)-ref).mean());r=dict(names=names,fullMAE=cost);rows.append(r);print(r,flush=True);im.save(P/('depth-'+','.join(names)+'.png'))
 if cost==min(v['fullMAE']for v in rows):(P/'depth-best.scene.json').write_text(json.dumps(q,indent=2))
(P/'depth-tests.json').write_text(json.dumps(rows,indent=2))
